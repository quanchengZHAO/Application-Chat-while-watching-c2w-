# -*- coding: utf-8 -*-
from twisted.internet.protocol import DatagramProtocol

class SybilServerUdpTextProtocol(DatagramProtocol):

    def __init__(self, sybilBrain):
        self.sybilBrain = sybilBrain

    def datagramReceived(self,datagram,address):
        resp = self.sybilBrain.generateResponse(datagram)
        send = str(datagram.partition(':')[0]) + ':' + resp
        
        print send
        self.transport.write(send,address)

