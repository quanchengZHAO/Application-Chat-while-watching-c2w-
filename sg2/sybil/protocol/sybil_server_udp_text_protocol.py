# -*- coding: utf-8 -*-
from twisted.internet.protocol import DatagramProtocol
import time 

class SybilServerUdpTextProtocol(DatagramProtocol):

    def __init__(self, sybilBrain):
        self.sybilBrain = sybilBrain

    def datagramReceived(self, datagram, address):
	print "I got a datagram", datagram
	TIME = datagram.partition(': ')[0]
	response = self.sybilBrain.generateResponse(datagram)
	self.transport.write(TIME+": "+response, address)
	
