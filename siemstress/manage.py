#!/usr/bin/env python

#_MIT License
#_
#_Copyright (c) 2017 Dan Persons (dpersonsdev@gmail.com)
#_
#_Permission is hereby granted, free of charge, to any person obtaining a copy
#_of this software and associated documentation files (the "Software"), to deal
#_in the Software without restriction, including without limitation the rights
#_to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#_copies of the Software, and to permit persons to whom the Software is
#_furnished to do so, subject to the following conditions:
#_
#_The above copyright notice and this permission notice shall be included in all
#_copies or substantial portions of the Software.
#_
#_THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#_IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#_FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#_AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#_LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#_OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#_SOFTWARE.

from siemstress import __version__
#import time
#from datetime import datetime
#import re
#import os
import MySQLdb as mdb
import json



class SIEMMgr:

    def __init__(self, db):
        """Initialize the SIEM manager"""

        self.db = db
        self.table = None


    def import_rules(self, importfile):
        """Import rules from a JSON file"""
        
        with open(importfile, 'r') as f:
            rules = json.loads(f.read())

        # Create table if it doesn't exist:
        con = mdb.connect(self.db['server'], self.db['user'],
            self.db['password'], self.db['database'])
        with con:
            cur = con.cursor()
            for table in rules:
                cur.execute('CREATE TABLE IF NOT EXISTS ' + \
                        table + \
                        '(Id INT PRIMARY KEY AUTO_INCREMENT, ' + \
                        'RuleName NVARCHAR(25), ' + \
                        'IsEnabled BOOLEAN, Severity TINYINT, ' + \
                        'TimeInt INT, EventLimit INT, ' + \
                        'SQLQuery NVARCHAR(1000), ' + \
                        'SourceTable NVARCHAR(25), ' + \
                        'OutTable NVARCHAR(25), ' + \
                        'Message NVARCHAR(1000))')
            cur.close()
        con.close()
        
        con = mdb.connect(self.db['server'], self.db['user'],
            self.db['password'], self.db['database'])
        with con:
            cur = con.cursor()
            for table in rules:
                # Set up SQL insert statement:
                insertstatement = 'INSERT INTO ' + table + \
                        '(RuleName, IsEnabled, Severity, ' + \
                        'TimeInt, EventLimit, SQLQuery, ' + \
                        'SourceTable, OutTable, Message) VALUES ' + \
                        '(%s, %s, %s, %s, %s, %s, %s, %s, %s)'


                for rule in rules[table]:
                    cur.execute(insertstatement, (rule['RuleName'],
                        rule['IsEnabled'], rule['Severity'],
                        rule['TimeInt'], rule['EventLimit'], 
                        rule['SQLQuery'], rule['SourceTable'],
                        rule['OutTable'], rule['Message']))
            cur.close()
        con.close()


    def export_rules(self, tables, exportfile):
        """Export rules from a table into a JSON file"""

        rules = {}
        con = mdb.connect(self.db['server'], self.db['user'],
            self.db['password'], self.db['database'])
        with con:
            cur = con.cursor(mdb.cursors.DictCursor)
            for table in tables:
                cur.execute('SELECT * FROM ' + table)
                rules[table] = cur.fetchall()
            cur.close()
        con.close()

        with open(exportfile, 'w') as f:
            f.write(json.dumps(rules, indent=2, sort_keys=True,
                separators=(',', ': ')) + '\n')



    def import_helpers(self, importfile):
        """Import helperss from a JSON file"""
        
        with open(importfile, 'r') as f:
            helpers = json.loads(f.read())

        # Create table if it doesn't exist:
        con = mdb.connect(self.db['host'], self.db['user'],
                self.db['password'], self.db['database'])
        with con:
            cur = con.cursor()
            for table in helpers:
                cur.execute('CREATE TABLE IF NOT EXISTS ' + \
                        table + \
                        '(Id INT PRIMARY KEY AUTO_INCREMENT, ' + \
                        'var_name NVARCHAR(25), ' + \
                        'reg_exp NVARCHAR(200))')
            cur.close()
        con.close()
        
        con = mdb.connect(self.db['host'], self.db['user'],
                self.db['password'], self.db['database'])
        with con:
            cur = con.cursor()
            for table in helpers:
                # Set up SQL insert statement:
                insertstatement = 'INSERT INTO ' + table + \
                        '(var_name, reg_exp) VALUES ' + \
                        '(%s, %s)'

                for h in helpers[table]:
                    cur.execute(insertstatement, (h['var_name'],
                        h['reg_exp']))
            cur.close()
        con.close()


    def export_helpers(self, tables, exportfile):
        """Export helpers SQL tables into a JSON file"""

        helpers = {}
        con = mdb.connect(self.db['host'], self.db['user'],
                self.db['password'], self.db['database'])
        with con:
            cur = con.cursor(mdb.cursors.DictCursor)
            for table in tables:
                cur.execute('SELECT * FROM ' + table)
                helpers[table] = cur.fetchall()
            cur.close()
        con.close()

        with open(exportfile, 'w') as f:
            f.write(json.dumps(helpers, indent=2, sort_keys=True,
                separators=(',', ': ')) + '\n')



    def clear_table(self, tables, force=False):
        """Clear SQL tables"""

        if force:

            con = mdb.connect(self.db['host'], self.db['user'],
                    self.db['password'], self.db['database'])
            with con:
                cur = con.cursor()
        
                for table in tables:
                    cur.execute('DROP TABLE IF EXISTS ' + table)

                cur.close()
            con.close()

        # To Do: raise an error here:
        else: print("Use --force if you really want to drop table (" + \
                table + ")")
