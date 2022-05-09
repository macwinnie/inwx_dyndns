# INWX DynDNS Python script

This repo is hosting a small python script to maintain DynDNS IPs with INWX.

It's easy to run it within a docker container like that:

```sh
docker run -v $(pwd):/project -d -w /project python /project/main.py
```

Ensure to maintain the environmental variables or bind a `.env` variable file!

## environmental variables

There is a `.env.example` which lists all available environmental variables. They are all also listed here:

| env                   | default               | change recommended | description |
| --------------------- | --------------------- |:------------------:| ----------- |
| `TIMEZONE`            | `Europe/Berlin`       | yes                | Timezone used for all dates logged within the script |
| `HOST`                | NAV                   | yes                | INWX DynDNS hostname / FQDN for which DNS records are to be maintained by this script |
| `USER`                | NAV                   | yes                | INWX DynDNS user |
| `PASS`                | NAV                   | yes                | INWX DynDNS user password |
| `SCOPE`               | `A`                   | yes                | scope of DynDNS check – comma separated list of `A` and / or `AAAA`. Don't forget to enable IPv6 for your Docker-Container if your scope includes `AAAA` ;) |
| `PUSHOVER`            | `[]`                  | yes                | JSON string representing a list of PushOver token. The list may contain multiple dictionaries consisting by the two keys `user_key` and `token`. |
| `SLEEP`               | `60`                  | no                 | The script runs within an infinity loop – and sleeps for this amount of seconds between every run. |
| `DNSSRV`              | `[]`                  | yes                | JSON list (!) of DNS servers / DNS resolvers to reflect for DNS lookup |
| `JSON_INDENT`         | `3`                   | yes                | Indention for JSON string reported (and stored) at error states |
| `ERROR_TOLERANCE`     | `3`                   | yes                | send push notification after `n` errors occuring in a row |
