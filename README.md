# siemstress
A very basic Security Information and Event Management system (SIEM)

## Description
siemstress is a CLI tool to parse syslog lines from standard input into an SQL database. Siemquery is a CLI tool to query the data.

## Installing

Requirements: git, python-setuptools, python-mysqldb, logdissect (>=2.0)

    git clone https://github.com/dogoncouch/siemstress.git
    cd siemstress
    sudo make all

### Database Setup
siemstress is developed and tested using MariaDB as an SQL server. You will need to create a database, and a user with permissions on it.

### Config
The default siemstress config file location is `/etc/siemstress.conf` (`config/siemstress.conf` if working in the repository).

## Siemstress

### Usage

```

usage: siemstress [-h] [--version] [--clear] [--force] [-q] [-c CONFIG]
                  [-s SECTION] [-z TZONE]

optional arguments:
  -h, --help  show this help message and exit
  --version   show program's version number and exit
  --clear     delete the SQL table for selected section
  --force     really delete the table
  -q          query the SQL table for selected section
  -c CONFIG   set the config file
  -s SECTION  set the config section
  -z TZONE    set the offset to UTC (e.g. '+0500')

```

### Examples
    tail -n 0 -f /var/log/messages | siemstress
    tail -n 0 -f /var/log/auth.log | siemstress -s auth

## Siemquery

### Usage

```

usage: siemquery [-h] [--version] [-c CONFIG] [-s SECTION] [--simple]
                 [--table TABLE] [--last LAST] [--range START-FINISH]
                 [--shost HOST] [--process PROCESS] [--grep PATTERN]

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  -c CONFIG             set the config file
  -s SECTION            set the config section
  --table TABLE         set a table to query
  --last LAST           match a preceeding time range (5m, 24h, etc)
  --range START-FINISH  match a date range (format: YYmmddHHMMSS)
  --shost HOST          match a source host
  --process PROCESS     match a source process
  --grep PATTERN        match a pattern

```

### Examples
    siemquery --last 6h
    siemquery --last 20m -s auth --process sshd --process systemd-logind --grep fail
    siemquery --range 20170726020000-20170726050000 -s auth --grep fail

### Notes
CLI arguments that are not time-related can be used more than once (except config/section).

## Copyright
MIT License

Copyright (c) 2017 Dan Persons (dpersonsdev@gmail.com)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
