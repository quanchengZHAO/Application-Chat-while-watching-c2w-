# -*- coding: utf-8 -*-
from twisted.internet.protocol import DatagramProtocol 
from twisted.internet import reactor
import ctypes
import struct
import time
import types
import math

class SybilServerTimerUdpBinProtocol(DatagramProtocol):

    def __init__(self, sybilBrain):
        self.sybilBrain = sybilBrain

    def datagramReceived(self, datagram, address):
	print "I got a datagram"
	TIME,longueur_request = struct.unpack_from('LH',datagram)
	print type(TIME)
	print type(longueur_request)
	#TIME_trans = long(str(TIME[0]))
	TIME_attend = math.ceil(math.log(longueur_request))
	print longueur_request
	print TIME_attend
	msg = datagram[6:]
	response = self.sybilBrain.generateResponse(msg)
	longueur = len(response) 
	print response
	print str(longueur)
	longueurTotale = longueur + 6
      	buf = ctypes.create_string_buffer(longueurTotale)
	struct.pack_into('LH'+str(longueur)+'s',buf,0,TIME,longueur,response)
	reactor.callLater(TIME_attend, self.transport.write, buf, address)
	#self.transport.write(buf,address)
	
