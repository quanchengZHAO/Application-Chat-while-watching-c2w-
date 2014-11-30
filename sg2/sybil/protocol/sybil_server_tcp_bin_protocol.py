# -*- coding: utf-8 -*
from twisted.internet.protocol import Protocol
import ctypes
import struct
import time

class SybilServerTcpBinProtocol(Protocol):

    def __init__(self, sybilBrain):
        self.sybilBrain = sybilBrain
	self.buf = ctypes.create_string_buffer()
    def dataReceived(self, datagram):
	print "I got a datagram"
	self.buf = datagram 
	if len(datagram) > 6:
	    
	     





TIME_trans,longueurini = struct.unpack_from('LH',datagram)
	msg = datagram[6:]
	if longueurini == len(msg) : 
	    print "la longueur est bonne"
	    response = self.sybilBrain.generateResponse(msg)
	    longueur = len(response) 
	    print response
	    print str(longueurini)
	    longueurTotale = longueurini + 6 
      	    buf = ctypes.create_string_buffer(longueurTotale)
	    struct.pack_into('LH'+str(longueurini)+'s',buf,0,TIME_trans,longueurini,response)
	    self.transport.write(buf.raw)
	    print "ca marche bien"
	else:
	    print "fail !!"
  	    mesg =  " Ton message n'est pas bien arrivé "
	    longueur = len(mesg)
	    longueurTotal = longueur + 6
	    buf = ctypes.create_string_buffer(longueurTotal)
            struct.pack_into('LH'+str(longueur)+'s',buf,0,TIME_trans,longueur,mesg)
	    self.transport.write(buf.raw)
	 
