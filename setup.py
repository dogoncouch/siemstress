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
"""
Siemstress
----------

Siemstress is a very basic Security Information and Event Management system (SIEM). It can parse syslog lines from standard input into an SQL database, and query the data.

Options
```````

::

    usage: siemstress [-h] [--version] [--clear] [-q] [-c CONFIG] [-s SECTION]
                      [-z TZONE]
    
    optional arguments:
      -h, --help  show this help message and exit
      --version   show program's version number and exit
      --clear     delete the SQL table for selected section
      -q          query the SQL table for selected section
      -c CONFIG   set the config file
      -s SECTION  set the config section
      -z TZONE    set the offset to UTC (e.g. '+0500')


Links
`````

* `Releases <https://github.com/dogoncouch/siemstress/releases/>`_
* `Usage <https://github.com/dogoncouch/siemstress/blob/master/README.md>`_
* `Changelog <https://github.com/dogoncouch/siemstress/blob/master/CHANGELOG.md>`_
* `Development source <https://github.com/dogoncouch/siemstress/>`_

"""

from setuptools import setup
from os.path import join
from sys import prefix
from siemstress import __version__

ourdata = [(join(prefix, 'share/man/man1'), ['doc/siemstress.1']),
        ('/etc/siemstress', ['config/siemstress.conf']),
        (join(prefix, 'share/doc/siemstress'), ['README.md', 'LICENSE',
            'CHANGELOG.md'])]

setup(name = 'siemstress', version = str(__version__),
        description = 'A very basic Security Information and Event Management system (SIEM)',
        long_description = __doc__,
        author = 'Dan Persons', author_email = 'dpersonsdev@gmail.com',
        url = 'https://github.com/dogoncouch/siemstress',
        download_url = 'https://github.com/dogoncouch/siemstress/archive/v' + str(__version__) + '.tar.gz',
        keywords = ['log', 'syslog', 'analysis', 'forensics', 'security',
            'cli', 'secops', 'sysadmin', 'forensic-analysis',
            'log-analysis', 'log-analyzer', 'log-viewer', 'log-analytics',
            'log-management', 'log-collector', 'log-monitoring'],
        packages = ['siemstress', 'siemquery'],
        entry_points = \
                { 'console_scripts': [ 'siemstress = siemstress.core:main',
                    'siemquery = siemquery.core:main' ]},
        data_files = ourdata,
        classifiers = ["Development Status :: 2 - Pre-Alpha",
            "Environment :: Console",
            "Intended Audience :: System Administrators",
            "License :: OSI Approved :: MIT License",
            "Natural Language :: English",
            "Operating System :: POSIX",
            "Programming Language :: Python :: 2",
            "Topic :: System :: Systems Administration"])
