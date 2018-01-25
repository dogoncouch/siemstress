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


    def create_event_table(self, table, intstamps=False):
        """Create a table for events"""
        con = mdb.connect(self.db['host'], self.db['user'],
                self.db['password'], self.db['database'])
        with con:
            cur = con.cursor(mdb.cursors.DictCursor)
            if intstamps:
                cur.execute('CREATE TABLE IF NOT EXISTS ' + table + \
                        '(id INT PRIMARY KEY AUTO_INCREMENT, ' + \
                        'parsed_at TIMESTAMP(6), ' + \
                        'date_stamp TIMESTAMP(6), ' + \
                        'date_stamp_utc TIMESTAMP(6), ' + \
                        't_zone NVARCHAR(5), '+ \
                        'raw_text NVARCHAR(1280), ' + \
                        'facility TINYINT UNSIGNED, ' + \
                        'severity TINYINT UNSIGNED, ' + \
                        'source_host NVARCHAR(32), ' + \
                        'source_port NVARCHAR(6), ' + \
                        'dest_host NVARCHAR(32), ' + \
                        'dest_port NVARCHAR(6), ' + \
                        'source_process NVARCHAR(24), ' + \
                        'source_pid MEDIUMINT UNSIGNED, ' + \
                        'protocol NVARCHAR(12), ' + \
                        'message NVARCHAR(1024), '
                        'extended NVARCHAR(1024), ' + \
                        'parsed_on NVARCHAR(32), ' + \
                        'source_path NVARCHAR(200))')
            else:
                cur.execute('CREATE TABLE IF NOT EXISTS ' + table + \
                        '(id INT PRIMARY KEY AUTO_INCREMENT, ' + \
                        'parsed_at TIMESTAMP(6), ' + \
                        'date_stamp TIMESTAMP(6), ' + \
                        'date_stamp_utc TIMESTAMP(6), ' + \
                        't_zone NVARCHAR(5), '+ \
                        'raw_text NVARCHAR(1280), ' + \
                        'facility TINYINT UNSIGNED, ' + \
                        'severity TINYINT UNSIGNED, ' + \
                        'source_host NVARCHAR(32), ' + \
                        'source_port NVARCHAR(6), ' + \
                        'dest_host NVARCHAR(32), ' + \
                        'dest_port NVARCHAR(6), ' + \
                        'source_process NVARCHAR(24), ' + \
                        'source_pid MEDIUMINT UNSIGNED, ' + \
                        'protocol NVARCHAR(12), ' + \
                        'message NVARCHAR(1024), '
                        'extended NVARCHAR(1024), ' + \
                        'parsed_on NVARCHAR(32), ' + \
                        'source_path NVARCHAR(200))')
            cur.execute('SELECT * FROM ' + self.helpers)
            helpers = cur.fetchall()
            cur.close()
        con.close()


    def create_ruleevent_table(self, table):
        """Create a table for rule events"""
        con = mdb.connect(self.db['host'], self.db['user'],
                self.db['password'], self.db['database'])
        with con:
            cur = con.cursor()
            cur.execute('CREATE TABLE IF NOT EXISTS ' + table + \
                    '(id INT PRIMARY KEY AUTO_INCREMENT, ' + \
                    'date_stamp TIMESTAMP, ' + \
                    'date_stamp_utc TIMESTAMP, ' + \
                    't_zone NVARCHAR(5), ' + \
                    'source_rule NVARCHAR(25), ' + \
                    'severity TINYINT UNSIGNED, ' + \
                    'source_table NVARCHAR(25), ' + \
                    'event_limit INT UNSIGNED, ' + \
                    'event_count INT UNSIGNED, ' + \
                    'magnitude INT UNSIGNED, ' + \
                    'time_int INT UNSIGNED, ' + \
                    'message NVARCHAR(1000))')
            cur.close()
        con.close()



    def create_rule_table(self, table):
        """Create a table for rules"""
        con = mdb.connect(self.db['host'], self.db['user'],
            self.db['password'], self.db['database'])
        with con:
            cur = con.cursor()
            cur.execute('CREATE TABLE IF NOT EXISTS ' + \
                    table + \
                    '(id INT PRIMARY KEY AUTO_INCREMENT, ' + \
                    'name NVARCHAR(32), ' + \
                    'desc NVARCHAR(200), ' + \
                    'is_enabled BOOLEAN, severity TINYINT, ' + \
                    'severity TINYINT UNSIGNED, '
                    'time_int INT UNSIGNED, event_limit INT UNSIGNED, ' + \
                    'sql_query NVARCHAR(1024), ' + \
                    'source_table NVARCHAR(32), ' + \
                    'out_table NVARCHAR(32), ' + \
                    'message NVARCHAR(1024))')
            cur.close()
        con.close()
        

    def import_rules(self, importfile):
        """Import rules from a JSON file"""
        
        with open(importfile, 'r') as f:
            rules = json.loads(f.read())

        # Create the table if it doesn't exist
        con = mdb.connect(self.db['host'], self.db['user'],
            self.db['password'], self.db['database'])
        with con:
            cur = con.cursor()
            for table in rules:
                cur.execute('CREATE TABLE IF NOT EXISTS ' + \
                        table + \
                        '(id INT PRIMARY KEY AUTO_INCREMENT, ' + \
                        'name NVARCHAR(32), ' + \
                        'desc NVARCHAR(200), ' + \
                        'is_enabled BOOLEAN, severity TINYINT, ' + \
                        'time_int INT, event_limit INT, ' + \
                        'sql_query NVARCHAR(1024), ' + \
                        'source_table NVARCHAR(32), ' + \
                        'out_table NVARCHAR(32), ' + \
                        'message NVARCHAR(1024))')
            cur.close()
        con.close()
        
        con = mdb.connect(self.db['host'], self.db['user'],
            self.db['password'], self.db['database'])
        with con:
            cur = con.cursor()
            for table in rules:
                # Set up SQL insert statement:
                insertstatement = 'INSERT INTO ' + table + \
                        '(name, desc, is_enabled, severity, ' + \
                        'time_int, event_limit, sql_query, ' + \
                        'source_table, out_table, message) VALUES ' + \
                        '(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'


                for rule in rules[table]:
                    cur.execute(insertstatement, (
                        rule['name'], rule['desc'],
                        rule['is_enabled'], rule['severity'],
                        rule['time_int'], rule['event_limit'], 
                        rule['sql_query'], rule['source_table'],
                        rule['out_table'], rule['message']))
            cur.close()
        con.close()


    def export_rules(self, tables, exportfile):
        """Export rules from a table into a JSON file"""

        rules = {}
        con = mdb.connect(self.db['host'], self.db['user'],
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



    def create_helper_table(self, table):
        """Create a table for parse helpers"""
        con = mdb.connect(self.db['host'], self.db['user'],
                self.db['password'], self.db['database'])
        with con:
            cur = con.cursor()
            cur.execute('CREATE TABLE IF NOT EXISTS ' + \
                    table + \
                    '(id INT PRIMARY KEY AUTO_INCREMENT, ' + \
                    'name NVARCHAR(32), ' + \
                    'desc NVARCHAR(200), ' + \
                    'var_name NVARCHAR(24), ' + \
                    'reg_exp NVARCHAR(200))')
            cur.close()
        con.close()
        

    def import_helpers(self, importfile):
        """Import helperss from a JSON file"""
        
        with open(importfile, 'r') as f:
            helpers = json.loads(f.read())

        con = mdb.connect(self.db['host'], self.db['user'],
                self.db['password'], self.db['database'])
        with con:
            cur = con.cursor()
            for table in helpers:
                cur.execute('CREATE TABLE IF NOT EXISTS ' + \
                        table + \
                        '(id INT PRIMARY KEY AUTO_INCREMENT, ' + \
                        'name NVARCHAR(32), ' + \
                        'desc NVARCHAR(200), ' + \
                        'var_name NVARCHAR(24), ' + \
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
                        '(name, desc, var_name, reg_exp)' + \
                        'VALUES (%s, %s %s, %s)'

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



    def clear_table(self, tables):
        """Clear SQL tables"""

        con = mdb.connect(self.db['host'], self.db['user'],
                self.db['password'], self.db['database'])
        with con:
            cur = con.cursor()
        
            for table in tables:
                cur.execute('DROP TABLE IF EXISTS ' + table)

            cur.close()
        con.close()
