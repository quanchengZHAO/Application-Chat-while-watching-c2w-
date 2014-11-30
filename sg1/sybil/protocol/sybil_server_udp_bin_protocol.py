# -*- coding: utf-8 -*-
from twisted.internet.protocol import DatagramProtocol 
import ctypes
import struct
import time
import types

class SybilServerUdpBinProtocol(DatagramProtocol):

    def __init__(self, sybilBrain):
        self.sybilBrain = sybilBrain

    def datagramReceived(self, datagram, address):
	print "I got a datagram"
	TIME = list(struct.unpack_from('L',datagram[0:4]))
	TIME_trans = long(str(TIME[0]))
	print TIME
	print str(TIME[0])
	print TIME_trans
	print type(TIME)
	print type(TIME_trans)
	print 
	msg = datagram[6:]
	response = self.sybilBrain.generateResponse(msg)
	longueur = len(response) 
	print response
	print str(longueur)
	longueurTotale = longueur + 6 
      	buf = ctypes.create_string_buffer(longueurTotale)
	struct.pack_into('LH'+str(longueur)+'s',buf,0,TIME_trans,longueur,response)
	self.transport.write(buf,address)
	
