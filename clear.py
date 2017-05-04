#!/usr/bin/env python

import MySQLdb as mdb

con = mdb.connect('localhost', 'siemstress', 'siems2bfine',
        'siemstressdb')
with con:
    cur = con.cursor()

    cur.execute('DROP TABLE IF EXISTS Entries')

    cur.execute('CREATE TABLE IF NOT EXISTS Entries(Id INT PRIMARY KEY AUTO_INCREMENT, DateStamp BIGINT(14) UNSIGNED, Host NVARCHAR(25), Process NVARCHAR(25), PID MEDIUMINT UNSIGNED, Message NVARCHAR(2000))')

