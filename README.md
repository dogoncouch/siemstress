# siemstress
A very basic Security Information and Event Management system (SIEM)

## Index

- [Introduction](#introduction)
  - [Description](#description)
  - [Installing](#installing)
- Tools
  - [siemparse](#siemparse)
  - [siemquery](#siemquery)
  - [siemtrigger](#siemtrigger)
- [Copyright](#copyright)

## Introduction

## Description
Siemstress is a suite of CLI tools to parse events into an SQL database, query the data, and trigger events based on configured rules.

## Installing

Requirements: git, python-setuptools, python-mysqldb, logdissect (>=2.0)

    git clone https://github.com/dogoncouch/siemstress.git
    cd siemstress
    sudo make all

### Database Setup
siemstress is developed and tested using MariaDB as an SQL server. You will need to create a database, and a user with permissions on it.

## Siemparse
`siemparse` parses lines from standard input into a siemstress database.

### Usage

```

usage: siemparse [-h] [--version] [--clear] [--force] [-q] [-c CONFIG]
                 [-s SECTION] [-z TZONE]

optional arguments:
  -h, --help  show this help message and exit
  --version   show program's version number and exit
  --clear     delete the SQL table for selected section
  --force     really delete the table
  -c CONFIG   set the config file
  -s SECTION  set the config section
  -z TZONE    set the offset to UTC (e.g. '+0500')

```

### Examples
    tail -n 0 -f /var/log/messages | siemparse
    tail -n 0 -f /var/log/auth.log | siemparse -s auth

### Config
The default siemstress config file location is `/etc/siemstress.conf` (`config/siemstress.conf` if working in the repository).

## Siemquery
`siemquery` performs database queries on a siemstress database.

### Usage

```

usage: siemquery [-h] [--version] [-c CONFIG] [-s SECTION] [--verbose]
                 [--silent] [--json JSON] [--table TABLE] [--last LAST]
                 [--range START-FINISH] [--id ID] [--shost HOST]
                 [--sport PORT] [--dhost HOST] [--dport PORT]
                 [--process PROCESS] [--pid PID] [--protocol PROTOCOL]
                 [--grep PATTERN] [--rshost HOST] [--rsport PORT]
                 [--rdhost HOST] [--rdport PORT] [--rprocess PROCESS]
                 [--rpid PID] [--rprotocol PROTOCOL] [--rgrep PATTERN]

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  -c CONFIG             set the config file
  -s SECTION            set the config section
  --verbose             print SQL queries
  --silent              silence table output to terminal
  --json JSON           set a JSON output file

query options:
  --table TABLE         set a table to query
  --last LAST           match a preceeding time range (5m, 24h, etc)
  --range START-FINISH  match a date range (format: YYmmddHHMMSS)
  --id ID               match an event ID
  --shost HOST          match a source host
  --sport PORT          match a source port
  --dhost HOST          match a destination host
  --dport PORT          match a destination port
  --process PROCESS     match a source process
  --pid PID             match a source Process ID
  --protocol PROTOCOL   match a protocol
  --grep PATTERN        match a pattern
  --rshost HOST         filter out a source host
  --rsport PORT         filter out a source port
  --rdhost HOST         filter out a destination host
  --rdport PORT         filter out a destination port
  --rprocess PROCESS    filter out a source process
  --rpid PID            filter out a source Process ID
  --rprotocol PROTOCOL  filter out a protocol
  --rgrep PATTERN       filter out a pattern

```

### Examples
    siemquery --last 6h
    siemquery --last 20m -s auth --process sshd --process systemd-logind --grep fail
    siemquery --range 20170726020000-20170726050000 -s auth --grep fail

### Notes
CLI arguments that are not time-related can be used more than once (except config/section). The default config file is the same as siemstress.

## Siemtrigger
`siemtrigger` triggers SIEM events based on siemstress database analysis.

### Usage

```

usage: siemtrigger.py [-h] [--version] [-c CONFIG]

optional arguments:
  -h, --help  show this help message and exit
  --version   show program's version number and exit
  -c CONFIG   set the config file

```

### Examples

    siemtrigger -c config/siemtrigger.conf

### Config
The default siemtrigger config file location is `/etc/siemtrigger.conf` (`config/siemstress.conf` if working in the repository). `siemtrigger.conf` loads rules from files in a conf directory.

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
