# siemstress
A very basic Security Information and Event Management system

# Notes
siemstress is a tool to parse syslog lines from standard input into an SQL database.

# Usage
usage: siemstress.py [-h] [--version] [-s SQLSERVER] [-d SQLDB] [-u SQLUSER]
                     [-p SQLP]

optional arguments:
  -h, --help    show this help message and exit
  --version     show program's version number and exit
  -s SQLSERVER  set the SQL server
  -d SQLDB      set the SQL database
  -u SQLUSER    set the SQL username
  -p SQLP       set the SQL password

# Example
tail -f /var/log/auth.log | ./siemstress.py
