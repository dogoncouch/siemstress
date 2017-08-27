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

# MariaDB connection module, for testing purposes
# Usage:
# import siemstress.util
# db = siemstress.util.SiemConnect()
# rows = db.x('select * from Auth')
# db.x('drop table if exists Auth')


import MySQLdb as mdb


class SiemConnect:

    def __init__(self, server='127.0.0.1', user='siemstress',
            password='siems2bfine', database='siemstressdb'):
    self.server = server
    self.user = user
    self.password = password
    self.database = database
    self.con = None
    self.cur = None

    self.connect()


    def connect(self):
        self.con = mdb.connect(self.server, self.user, self.password,
                self.database)
        self.cur = con.cursor(mdb.cursors.DictCursor)

    def disconnect(self):
        self.cur.close()
        self.con.close()


    def x(self, statement):
        self.cur.execute(statement)
        if statement.startswith('SELECT') or statement.startswith('select'):
            return cur.fetchall
        else:
            return
