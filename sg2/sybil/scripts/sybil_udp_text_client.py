#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import argparse
import subprocess
import os

parser = argparse.ArgumentParser(description='Sybil Client (UDP Text Version)')
parser.add_argument('-p', '--port', dest='server_port', type=int,
                    help='The port number to be used for listening.')
parser.add_argument('-e', '--debug',
                    dest='debugFlag',
                    help='Raise the log level to debug',
                    action="store_true",
                    default=False)
parser.add_argument("-m", "--machine", dest="host", type=str,
                    help="the server name or IP address to connect to")
parser.add_argument('-t', '--text-user-interface',
                    dest='text_user_interface',
                    help='Use the text version of the user interface.',
                    action="store_true")
options = parser.parse_args()
sybilPath = '~stockrsm/res302/sybil/main'
cmdLine = [os.path.join(os.path.expanduser(sybilPath),
                        'sybil_udp_text_client.py')]
if options.server_port is not None:
    cmdLine.append('-p ' + str(options.server_port))
if options.host is not None:
    cmdLine.append('-m ' + options.host)
if options.text_user_interface:
    cmdLine.append('-t')
if options.debugFlag:
    cmdLine.append('-e')
    print 'about to call: ', cmdLine
try:
    retcode = subprocess.call(cmdLine)
except KeyboardInterrupt:
    pass  # ignore CTRL-C
