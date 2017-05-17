#!/usr/bin/env python

import MySQLdb as mdb


class SiemQuery:

    def __init__(self):

        self.args = None
        self.config = None
        # To Do: finish, import modules, etc

    def get_args(self):
        """Set config options"""

        config = ConfigParser.ConfigParser()
        if os.path.isfile('/etc/siemstress.conf'):
            myconf = ('/etc/siemstress.conf')
        else: myconf = 'siemstress.conf'
        config.read(myconf)

        self.arg_parser.add_argument('--version', action = 'version',
                version = '%(prog)s ' + str(__version__))
        self.arg_parser.add_argument('-c',
                action = 'store', dest = 'config',
                default = '/etc/siemstress.conf',
                help = ('set the config file'))
        self.arg_parser.add_argument('-s',
                action = 'store', dest = 'confsection',
                default = 'default',
                help = ('set the config section'))
        self.arg_parser.add_argument('-z',
                action = 'store', dest = 'tzone',
                help = ("set the offset to UTC (e.g. '+0500'"))



    def get_config(self):
        """Read the config file"""

        self.args = self.arg_parser.parse_args()

        config = ConfigParser.ConfigParser()
        if os.path.isfile(self.args.config):
            myconf = (config))
        else: myconf = 'siemstress.conf'
        config.read(myconf)

        self.server = config.get('siemstress', 'server')
        self.user = config.get('siemstress', 'user')
        self.password = config.get('siemstress', 'password')
        self.database = config.get('siemstress', 'database')
        self.table = config.get(self.args.confsection, 'table')
        # self.parser = config.get(self.args.confsection, 'parser')



    def run_query(config)
        
        con = mdb.connect('localhost', 'siemstress', 'siems2bfine',
                'siemstressdb');
        
        with con: 
        
            cur = con.cursor()
            cur.execute("SELECT * FROM Entries")

            rows = cur.fetchall()
    
            desc = cur.description

            print "%4s %16s %10s %10s %10s %s" % (desc[0][0], desc[7][0],
                    desc[12][0], desc[16][0], dest[17][0], dest[18][0])
            for row in rows:
                print "%4s %16s %10s %10s %10s %s" % row[0], row[7], row[12],
                row[16], row[17], row[18]
