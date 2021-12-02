#!/usr/bin/env python

###
## ensure that all requirements are installed and all directories exist
###
import datetime, os, sys, subprocess, json, time

print('installation of requirements ...', file=sys.stderr)
subprocess.check_call( [sys.executable, '-m', 'pip'] + 'install -r requirements.txt'.split(), stdout=open(os.devnull, 'wb') )
print('... finished.', file=sys.stderr)
print('', file=sys.stderr)

###
## import dotenv
###
from dotenv import load_dotenv
load_dotenv()

###
## get variables from env
###
scope     = os.getenv( 'SCOPE', 'A' ).split( ',' )
fqdn      = os.getenv( 'HOST' )
po_recip  = json.loads( os.getenv( 'PUSHOVER', '[]' ))
inwx_user = os.getenv( 'USER' )
inwx_pass = os.getenv( 'PASS' )
lensleep  = os.getenv( 'SLEEP', 60 )
dns_srvrs = json.loads( os.getenv( 'DNSSRV', '[]' ))
date_f    = "%d.%m.%Y %H:%M.%S"

###
## set timezone
###
os.environ['TZ'] = os.getenv( 'TIMEZONE', 'Europe/Berlin' )
try:
    time.tzset()
except:
    push_msg( 'ERROR on setting timezone {}'.format( os.getenv( 'TZ' ) ), 2 )

###
## prepare database
###

import pathlib, sqlite3, yoyo

curpath        = str( pathlib.Path().resolve() )
dbfile         = '{}/{}'.format( curpath, 'inwx.sqlite' )
migrations_dir = '{}/{}'.format( curpath, 'db_migrations' )
dbback         = 'sqlite:///{}'.format( dbfile )

# ensure DB file exists
if not os.path.isfile( dbfile ):
    open( dbfile, 'w' ).close()

# ensure all DB migrations are applied
backend    = yoyo.get_backend( dbback )
migrations = yoyo.read_migrations( migrations_dir )
backend.apply_migrations( backend.to_apply( migrations ))

###
## functions to be defined
###
import pushover
def push_msg( msg, prio=0, expire=3600, retry=60 ):
    if len( po_recip ) > 0:
        for recipient in po_recip:
            pushover.init( recipient[ 'token' ] )
            pushover.Client( recipient[ 'user_key' ] ).send_message( msg, title="DynDNS {}".format( fqdn ), priority=prio, expire=expire, retry=retry )

# id INT, type VARCHAR(4), value VARCHAR(128), date
def insert_new( itype, value ):
    insert   = 'INSERT INTO dyndns_updates (`id`, `type`, `value`, `date`) VALUES (?,?,?,?);'
    getIdSql = 'SELECT MAX( id ) FROM dyndns_updates;'

    dbcon = sqlite3.connect( dbfile )

    cur = dbcon.cursor()
    cur.execute( getIdSql )
    max_id = cur.fetchone()[0]
    if max_id == None:
        max_id = 0

    entry = [
        max_id + 1,
        itype,
        value,
        datetime.datetime.now().strftime( date_f )
    ]

    cur = dbcon.cursor()
    cur.execute( insert, entry )
    dbcon.commit()
    dbcon.close()

###
## check current DNS value, get public IP and update if necessary
###
import requests, dns.resolver
from INWX.Domrobot import ApiClient

public_checks = {
    'A':    'https://api.ipify.org',
    'AAAA': 'https://api64.ipify.org',
}
api_keys = {
    'A':    'ipAddress',
    'AAAA': 'ipAddressV6',
}

change   = {}
old_data = {}

while True:

    for s in scope:
        if s not in api_keys:
            push_msg( 'ERROR: {} is not a valid record in scope for this DynDNS action!'.format( s ), 2 )
        else:
            public_ip   = requests.get( public_checks[ s ] ).content.decode( 'utf8' )

            if len( dns_srvrs ) > 0:
                resolver = dns.resolver.Resolver()
                resolver.nameservers = dns_srvrs
                current_dns = resolver.resolve( fqdn, s )
            else:
                current_dns = dns.resolver.resolve( fqdn, s )

            if len( current_dns ) > 1:
                rs = ''
                for cd in current_dns:
                    rs += '\n* {}'.format( str( cd ) )
                push_msg( 'ERROR: Multiple DNS entries for {} records!\n\nResults returned:{}\n\nPublic IP is: {}'.format( s, rs, public_ip ), 2 )

            current_dns = str( current_dns[ 0 ] )

            if public_ip != current_dns:
                change[ api_keys[ s ] ] = public_ip
                old_data[ s ]           = {
                    'current': current_dns,
                    'new'    : public_ip,
                }

    if len( change ) > 0:
        api_client   = ApiClient( api_url=ApiClient.API_LIVE_URL, debug_mode=False )
        login_result = api_client.login( inwx_user, inwx_pass )
        if login_result[ 'code' ] == 1000:
            # login was successful
            dyndnsupdate = api_client.call_api(
                api_method='dyndns.updateRecord',
                method_params=change
            )
            if dyndnsupdate[ 'code' ] == 1000:
                for c, val in change.items():
                    s = list( api_keys.keys())[ list( api_keys.values()).index( c ) ]
                    insert_new( s, val )
                    push_msg( 'Updated {} record to {} – current DNS was {}'.format( s, val, old_data[ s ][ 'current' ] ) )
            else:
                push_msg( 'ERROR: Updating DynDNS was not successfull.\nChange object would have been:\n\n{}'.format( json.dumps( old_data ) ), 2 )
        else:
            push_msg( 'ERROR: Login to INWX was not successfull.\nChange object would have been:\n\n{}'.format( json.dumps( old_data ) ), 2 )
        # empty the change data objects
        change   = {}
        old_data = {}

    time.sleep( lensleep )
