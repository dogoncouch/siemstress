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

from datetime import datetime
import fileinput
import MySQLdb as mdb



class LiveParser:
    def __init__:
        self.sqlstatement = 'INSERT INTO Auth (DateStamp, Host, Process, PID, Message) VALUES (?, ?, ?, ?, ?)'

        self.date_format = \
                re.compile(r"^([A-Z][a-z]{2}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2}\s+\S+\s+\S+\[?\d*?\]?):")
        # nohost_format = \
        #         re.compile(r"^([A-Z][a-z]{2}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2}\s+\S+\[?\d*\]?):")


    def parselog()
        recent_datestamp = '9999999999'
        # NOTE: The following password is on a publicly available git repo.
        # This should only be used for development purposes on closed
        # systems.
        con = mdb.connect('localhost', 'siemstress', 'siems2bfine',
                'siemstressdb')

        with con:
            cur = con.cursor(mdb.cursors.DictCursor)

            while true:
                lines = fileinput.input()
                if lines:
                    for line in lines:
                        # Do the parsing
                        ourline = line.rstrip()
                        # if options.nohost:
                        #     match = re.findall(nohost_format, ourline)
                        # else:
                        #     match = re.findall(self.date_format, ourline)
                        match = re.findall(self.date_format, ourline)
                        if match:
                            attr_list = str(match[0]).split(' ')
                            try:
                                attr_list.remove('')
                            except ValueError:
                                pass
                
                            # Account for lack of source host:
                            # if options.nohost: attr_list.insert(3, None)
                
                            # Get the date stamp (without year)
                            months = {'Jan':'01', 'Feb':'02', 'Mar':'03', \
                                    'Apr':'04', 'May':'05', 'Jun':'06', \
                                    'Jul':'07', 'Aug':'08', 'Sep':'09', \
                                    'Oct':'10', 'Nov':'11', 'Dec':'12'}
                            int_month = months[attr_list[0].strip()]
                            daydate = str(attr_list[1].strip()).zfill(2)
                            timelist = str(str(attr_list[2]).replace(':',''))
                            datestamp_noyear = str(int_month) + str(daydate) + \
                                    str(timelist)
                            
                            # Check for Dec-Jan jump and set the year:
                            if int(datestamp_noyear) < int(recent_datestamp):
                                entryyear = str(datetime.now().year)
                            recent_datestamp = datestamp_noyear
                            
                            # Split source process/PID
                            sourceproclist = attr_list[4].split('[')
                            
                            # Set our attributes:
                            message = rawtext[len(match):]
                            sourcehost = attr_list[3]
                            sourceproc = sourceproclist[0]
                            if len(sourceproclist) > 1:
                                sourcepid = sourceproclist[1].strip(']')
                            datestamp_noyear = date_stamp_noyear
                            datestamp = entryyear + datestamp_noyear
                            
                            # Put our attributes in our table:
                            cur.execute(self.sqlstatement,
                                    (datestamp, sourceproc, sourcehost,
                                        sourcepid, message))
                
                        else:
                            # No match!?
                            # To Do: raise an error here.
                            print('No Match: ' + ourline)
                    
                    else:
                        # No lines
                        pass



if __name__ = "__main__":
    parser = LiveParser()
    parser.parselog()
