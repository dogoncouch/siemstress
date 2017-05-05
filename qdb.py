#!/usr/bin/env python

import MySQLdb as mdb

con = mdb.connect('localhost', 'siemstress', 'siems2bfine', 'siemstressdb');

with con: 

    cur = con.cursor()
    cur.execute("SELECT * FROM Entries")

    rows = cur.fetchall()

    desc = cur.description

    print "%4s %14s %10s %10s %10s %s" % (desc[0][0], desc[1][0],
            desc[2][0], desc[3][0], desc[4][0], desc[5][0])
    for row in rows:
        print "%4s %14s %10s %10s %10s %s" % row
