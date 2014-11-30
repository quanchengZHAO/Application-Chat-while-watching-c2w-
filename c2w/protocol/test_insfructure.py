from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor 
import logging
import ctypes
import struct
from table_UDP import *
from c2w.main.constants import ROOM_IDS
from c2w.main.client_model import c2wClientModel
from c2w.main.user import c2wUser
from c2w.main.movie import c2wMovie

def test_buffer(buf, seqNum):
    print "This is the  " + str(seqNum) + "  message"
    print buf.raw.encode("hex")

def test_datagram(header, data):
    print
    print
    print
    print
    print
    print
    print
    print "The header is  "
    print header
    print "The date is  "
    print data
    print
    print
    print
    print
    print
    print

