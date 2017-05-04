#!/usr/bin/env python

import MySQLdb as mdb

con = mdb.connect('localhost', 'siemstress', 'siems2bfine', 'siemstressdb');

with con: 

    cur = con.cursor()
    cur.execute("SELECT * FROM Entries")

    rows = cur.fetchall()

    for row in rows:
        print row
