# siemstress
A very basic Security Information and Event Management system

## Notes
siemstress is a CLI tool to parse syslog lines from standard input into an SQL database, and query the data.

## Usage

```

usage: siemstress.py [-h] [--version] [--clear] [-q] [-c CONFIG] [-s SECTION]
                     [-z TZONE]

optional arguments:
  -h, --help  show this help message and exit
  --version   show program's version number and exit
  --clear     delete the SQL table for selected section
  -q          query the SQL table for selected section
  -c CONFIG   set the config file
  -s SECTION  set the config section
  -z TZONE    set the offset to UTC (e.g. '+0500')

```

## Examples
    tail -n 0 -f /var/log/messages | ./siemstress.py
    tcpdump | ./siemstress.py -s tcpdump
    siemstress.py -q -s tcpdump

## Config
The default siemstress config file location is `/etc/siemstress.conf` (`config/siemstress.conf` if working in the repository).
