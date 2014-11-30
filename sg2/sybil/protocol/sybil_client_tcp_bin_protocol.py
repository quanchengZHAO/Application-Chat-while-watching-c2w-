# -*- coding: utf-8 -*
from twisted.internet.protocol import Protocol
import ctypes
import struct
import time

class SybilClientTcpBinProtocol(Protocol):
    def connectionMade(self):
        """
        The Graphical User Interface (GUI) needs this function to know
        when to display the request window.

        DO NOT MODIFY IT.
        """
        self.clientProxy.connectionSuccess()

    def __init__(self, sybilProxy):
        """
        :param proxy: A reference to the SybilProxy (you need to use it
            to interact with the user interface of the client).
        :type proxy: instance of
             :py:class:`~c2w_main.c2w_client_proxy.c2wClientProxy`

        The class implementing the Sybil client protocol.  It must have
        the following attribute:

        .. attribute:: proxy

            The reference to the SybilCientProxy (instance of the
            :py:class:`~c2w_main.c2w_client_proxy.c2wClientProxy` class).

        .. warning::
            All interactions between the client protocol and the user
            interface *must* go through the SybilClientProxy.  In other
            words you must call one of the methods of
            :py:class:`~c2w_main.c2w_client_proxy.c2wClientProxy` whenever
            you would like the user interface to do something.

        .. note::
            You have to implement this class.  You should add any attribute
            and method that you see fit to this class.


        """        
	self.clientProxy = sybilProxy
     
    def sendRequest(self, line):
        """
        :param line: the text of the question from the user interface
        :type line: string

        This function must send the request to the server.
        """
	TIME = int(time.time())        
	longueur = len(line) 
	longueurTotale = longueur + 6 
      	buf = ctypes.create_string_buffer(longueurTotale)
	struct.pack_into('LH'+str(longueur)+'s',buf,0,TIME,longueur,line)
	self.transport.write(buf.raw)
	print "on envoie bien"
	
    def dataReceived(self,datagram): 
	print "Datagram  received"
	TIME,longueurini = struct.unpack_from('LH',datagram)	
	msg = datagram [6:]
	if longueurini == len(msg):
	    print "la longueur est bonne"
	    self.clientProxy.responseReceived(msg)
	else:
	    print "Fail !!  "
	    mesg = "Désolé, la transmission n'est pas bonne "
	    self.transport.write(mesg)
	
