# siemstress
A very basic Security Information and Event Management system

# Notes
siemstress is a tool to parse syslog lines from standard input into an SQL database.

# Usage
    usage: siemstress.py [-h] [--version] [-s SERVER] [-d DATABASE] [-t TABLE]
                         [-u USERNAME] [-p PASSWORD]
    
    optional arguments:
      -h, --help   show this help message and exit
      --version    show program's version number and exit
      -s SERVER    set the SQL server
      -d DATABASE  set the SQL database
      -t TABLE     set the SQL table
      -u USERNAME  set the SQL username
      -p PASSWORD  set the SQL password

# Example
tail -n 0 -f /var/log/auth.log | ./siemstress.py
