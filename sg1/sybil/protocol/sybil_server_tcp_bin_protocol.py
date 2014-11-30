# -*- coding: utf-8 -*-
from twisted.internet.protocol import Protocol 
import ctypes
import struct
import time
import types

class SybilServerTcpBinProtocol(Protocol):

    def __init__(self, sybilBrain):
        self.sybilBrain = sybilBrain

    def dataReceived(self, datagram):
	print "I've got a datagram"
	TIME = list(struct.unpack_from('L',datagram[0:4]))
	TIME_trans = long(str(TIME[0]))
	msg = datagram[6:]
	response = self.sybilBrain.generateResponse(msg)
	longueur = len(response) 
	print response
	print str(longueur)
	longueurTotale = longueur + 6 
      	buf = ctypes.create_string_buffer(longueurTotale)
	struct.pack_into('LH'+str(longueur)+'s',buf,0,TIME_trans,longueur,response)
	self.transport.write(buf.raw)
	
