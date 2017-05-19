# siemstress
A very basic Security Information and Event Management system

## Notes
siemstress is a CLI tool to parse syslog lines from standard input into an SQL database, and query the data.

## Usage

```

usage: siemstress [-h] [--version] [--clear] [-q] [-c CONFIG] [-s SECTION]
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
    tail -n 0 -f /var/log/messages | siemstress
    tcpdump | siemstress -s tcpdump
    siemstress -q -s tcpdump

## Config
The default siemstress config file location is `/etc/siemstress.conf` (`config/siemstress.conf` if working in the repository).

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

