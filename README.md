# SiemStress Security Information and Event Management
A very basic Security Information and Event Management system

## Index

- [siemstress](#siemstress)
- [siemquery](#siemquery)

## siemstress

### Notes
siemstress is a tool to parse syslog lines from standard input into an SQL database.

### Usage

```

usage: siemstress.py [-h] [--version] [-c CONFIG] [-s SECTION] [-z TZONE]

optional arguments:
  -h, --help  show this help message and exit
  --version   show program's version number and exit
  -c CONFIG   set the config file
  -s SECTION  set the config section
  -z TZONE    set the offset to UTC (e.g. '+0500')

```

### Example
tail -n 0 -f /var/log/messages | ./siemstress.py

## siemquery

### Notes
siemquery is a command line utility that queries a siemstress SQL database.

### Usage

```

usage: siemquery.py [-h] [--version] [-c CONFIG] [-s SECTION] [-z TZONE]

optional arguments:
  -h, --help  show this help message and exit
  --version   show program's version number and exit
  -c CONFIG   set the config file
  -s SECTION  set the config section
  -z TZONE    set the offset to UTC (e.g. '+0500')

```

### Example
./siemquery.py
