# siemstress
A very basic Security Information and Event Management system (SIEM)

## Index

- [Introduction](#introduction)
  - [Description](#description)
  - [Overview](#overview)
    - [Database](#database)
    - [JSON output](#json-output)
    - [Design principals](#design-principals)
    - [The future](#the-future)
- [Installing](#installing)
  - [Database setup](#database-setup)
  - [Config](#config)
- [Tools](#tools)
  - [siemparse](#siemparse)
  - [siemquery](#siemquery)
  - [siemtrigger](#siemtrigger)
- [Copyright](#copyright)

## Introduction

### Description
Siemstress is a lightweight but powerful security information and event management (SIEM) system. It uses a database and a suite of CLI tools for managing log events, and automating event analysis. It comes with three programs: siemparse, siemquery, and siemtrigger.

### Overview

#### Database
Siemstress uses a database (MariaDB) to store the following information:

- Parsed events - Parsed events are syslog (or other) events from files that are being watched by siemparse. Each event represents one line in a log file.
![Parsed event table screenshot](https://github.com/dogoncouch/siemstress/blob/master/doc/images/events.png)

- Helpers - Helpers are used to help siemparse pull dynamically configurable attributes from events. Events created by helpers are stored in the `Extended` column of parsed events. This is useful for identifying IP addresses, user names, temperatures, file names, or other data that siemstress doesn't parse automatically.
![Helper table screenshot](https://github.com/dogoncouch/siemstress/blob/master/doc/images/helpers.png)

- Rules - Rules are conditions that are used by siemtrigger to evaluate tables of parsed events. So far there is only one type of rule: the limit rule. Limit rules have a set of criteria, a time interval, and an event limit. If there are more events in a time interval that meet these criteria than the set limit, a SIEM event is created using the message defined by the rule. Rules also have a severity attribute, which works like syslog severity; 0 is the most severe, and 7 is the least (the specific syslog severity levels are not used).
![Rule table screenshot](https://github.com/dogoncouch/siemstress/blob/master/doc/images/rules.png)

- SIEM events - SIEM events are created by rules that evaluate events. They are stored in separate tables that are meant to be monitored. Each SIEM event has a magnitude, which is calculated using rule severity, and the ratio of event count to the rule's event limit. SIEM events also contain a list of source event IDs.
![SIEM event table screenshot](https://github.com/dogoncouch/siemstress/blob/master/doc/images/SIEMevents.png)

#### JSON output
`siemquery` terminal output does not show all attributes. To view all attributes, including the extended attributes parsed by helpers, use the `--json` option to store the output in a JSON file. This can also be useful for data visualization and manipulation using programs like Jupyter.
![JSON file screenshot](https://github.com/dogoncouch/siemstress/blob/master/doc/images/events-json.png)

#### Design principals
Siemstress is designed to parse data, and organize it into prioritized, manageable streams of relevant information. One of the goals is to remain as simple as possible. Parsing data from specific applications is left to user configurable parse helpers, and user interfaces beyond the command line are left to other programs.

Siemstress was originally designed as a basis for artificial intelligence research, and has since been used for network security, physical security, and data collection.

#### The future
Siemstress is still under development. In the future, it will include more rule types, state tables, and a more streamlined process for starting and stopping all of its services. It may include an optional web interface, but the intention is to stay UI agnostic.

## Installing

See the latest instructions on the [releases page](https://github.com/dogoncouch/siemstress/releases).

### Database Setup
siemstress is developed and tested using MariaDB as an SQL server. You will need to create a database, and a user with permissions on it.

### Config
The default siemstress config file location is `/etc/siemstress/db.conf` (`config/db.conf` if working in the repository). This file contains information needed to connect to the database. There is also a section config file in the same directory called `sections.conf` that contains information about tables.

## Tools

### Siemparse
`siemparse` is a CLI tool to parse log lines from a log file or standard input into a siemstress database.

#### Options

```

usage: siemparse [-h] [--version] [--clear] [--force] [--import FILE]
                 [--export FILE] [--table TABLE] [-c CONFIG] [-s SECTION]
                 [-z TZONE]
                 [file]

positional arguments:
  file           set a file to follow

optional arguments:
  -h, --help     show this help message and exit
  --version      show program's version number and exit
  --clear        delete the SQL table for selected section
  --force        really delete the table
  --import FILE  set a JSON file to import helpers
  --export FILE  set a JSON file to export helpers
  --table TABLE  set a helper table to export
  -c CONFIG      set the config file
  -s SECTION     set the config section
  -z TZONE       set the offset to UTC (e.g. '+0500')

```

#### Examples
    siemparse /var/log/messages
    siemparse -s auth /var/log/auth.log

### Siemquery
`siemquery` is a CLI tool to query a siemstress database.

#### Options

```

usage: siemquery [-h] [--version] [-c CONFIG] [-s SECTION] [--verbose]
                 [--silent] [--rule] [--json FILE] [--table TABLE]
                 [--last LAST] [--range START-FINISH] [--id ID]
                 [--shost HOST] [--sport PORT] [--dhost HOST]
                 [--dport PORT] [--process PROCESS] [--pid PID]
                 [--protocol PROTOCOL] [--grep PATTERN] [--rshost HOST]
                 [--rsport PORT] [--rdhost HOST] [--rdport PORT]
                 [--rprocess PROCESS] [--rpid PID] [--rprotocol PROTOCOL]
                 [--rgrep PATTERN]

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  -c CONFIG             set the config file
  -s SECTION            set the config section
  --verbose             print SQL statement used for query
  --silent              silence table output to terminal
  --rule                set rule query mode
  --json FILE           set a JSON output file

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

#### Examples
    siemquery --last 6h --json events.json
    siemquery --last 20m -s auth --process sshd --process systemd-logind --grep fail
    siemquery --range 20170726020000-20170726050000 -s auth --grep fail

#### Notes
Arguments under `query options` that are not time-related can be used more than once.

### Siemtrigger
`siemtrigger` is a CLI tool to trigger SIEM events based on siemstress database analysis.

#### Options

```

usage: siemtrigger [-h] [--version] [-c CONFIG] [--table TABLE] [--oneshot]
                   [--import FILE] [--export FILE]

optional arguments:
  -h, --help     show this help message and exit
  --version      show program's version number and exit
  -c CONFIG      set the config file
  --table TABLE  set a rule table
  --oneshot      check database once and exit
  --import FILE  set a JSON file to import rules
  --export FILE  set a JSON file to export rules

```

#### Examples

    siemtrigger --import config/example_rules.json
    siemtrigger --table RULESAuth

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
