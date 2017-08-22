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
import siemstress.trigger
import threading
import os
from argparse import ArgumentParser
import ConfigParser


class SiemTriggerCore:

    def __init__(self):
        """Initialize trigger engine"""

        self.args = None
        self.arg_parser = ArgumentParser()

        self.server = None
        self.user = None
        self.password = None
        self.database = None



    def get_args(self):
        """Set argument options"""

        self.arg_parser.add_argument('--version', action = 'version',
                version = '%(prog)s ' + str(__version__))
        self.arg_parser.add_argument('-c',
                action = 'store', dest = 'config',
                default = '/etc/siemstress/siemtrigger.conf',
                help = ('set the config file'))
        # self.arg_parser.add_argument('-z',
        #         action = 'store', dest = 'tzone',
        #         help = ("set the offset to UTC (e.g. '+0500')"))

        self.args = self.arg_parser.parse_args()



    def get_config(self):
        """Read the config file"""

        config = ConfigParser.ConfigParser()
        if os.path.isfile(self.args.config):
            myconf = (config)
        else: myconf = 'config/siemtrigger.conf'
        config.read(myconf)

        # Read /etc/triggers.d/*.conf in a for loop

        self.server = config.get('siemstress', 'server')
        self.user = config.get('siemstress', 'user')
        self.password = config.get('siemstress', 'password')
        self.database = config.get('siemstress', 'database')
        confdir = config.get('siemstress', 'confdir')
        if confdir.startswith('/'):
            self.confdir = confdir
        else:
            self.confdir = os.path.dirname(os.path.realpath(myconf)) + \
                    '/' + confdir

        for conffile in os.listdir(self.confdir):
            if conffile.endswith('.conf')
                conflet = config.read(self.confdir + conffile)
                
                # Each section is a rule.
                self.rules = {}
                for s in conflet.sections():
                    rule = {}
                    rule['name'] = s
                    rule['sqlquery'] = config.get(s, 'sqlquery')
                    rule['interval'] = config.get(s, 'interval')
                    rule['limit'] = config.get(s, 'limit')
                    rule['outtable'] = config.get(s, 'outtable')
                    rule['message'] = config.get(s, 'message')
                    idtags = config.get(s, 'idtags')
                    if idtags == 'On': rule['idtags'] = True
                    else: rule['idtags'] = False
                    self.rules[s] = rule



    def start_triggers(self):
        """Start siemstress event triggers"""

        # Start one thread per rule:
        threads = {}
        for r in self.rules:
            thread = threading.Thread(name=r['name'],
                    target=siemstress.trigger.start_rule)
            thread.start(self.server, self.user, self.password,
                    self.database, r)



    def run_triggers(self):
        """Start trigger engine"""
        try:
            self.get_args()
            self.get_config()
            self.start_triggers()

        except KeyboardInterrupt:
            pass
        # except Exception as err:
        #     print('Error: ' + str(err))

    
    
def main():
    parser = SiemTrigger()
    parser.run_triggers()


if __name__ == "__main__":
    parser = SiemTrigger()
    parser.run_triggers()
