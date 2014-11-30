#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import argparse
import subprocess
import os

parser = argparse.ArgumentParser(description='Sybil Sever (UDP Text Version)')
parser.add_argument('-p', '--port', dest='server_port', type=int,
                    help='The port number to be used for listening.')
parser.add_argument('-e', '--debug',
                    dest='debugFlag',
                    help='Raise the log level to debug',
                    action="store_true",
                    default=False)

options = parser.parse_args()
sybilPath = '~stockrsm/res302/sybil/main'
cmdLine = [os.path.join(os.path.expanduser(sybilPath),
                        'sybil_udp_text_server.py')]
if options.server_port is not None:
    cmdLine.append('-p ' + str(options.server_port))
if options.debugFlag:
    cmdLine.append('-e')
    print 'about to call: ', cmdLine
try:
    retcode = subprocess.call(cmdLine)
except KeyboardInterrupt:
    pass  # ignore CTRL-C
