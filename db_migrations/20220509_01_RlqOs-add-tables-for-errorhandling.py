"""
add tables for errorhandling
"""

from yoyo import step

__depends__ = {'20211201_01_Adhx7-create-table-dyndns_updates'}

steps = [
    step("CREATE TABLE dyndns_error (id INT, error TEXT, date VARCHAR(128), PRIMARY KEY (id))"),
    step("CREATE TABLE dyndns_keyvalue (`key` VARCHAR(256), value TEXT, PRIMARY KEY ( `key` ) )"),
]
