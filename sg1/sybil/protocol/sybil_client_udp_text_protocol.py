# -*- coding: utf-8 -*-
from twisted.internet.protocol import DatagramProtocol
import time

class SybilClientUdpTextProtocol(DatagramProtocol):

    def __init__(self, sybilProxy, port, host):

        """
        :param proxy: A reference to the SybilProxy (you need to use it
            to interact with the user interface of the client).
        :type proxy: instance of
             :py:class:`~c2w_main.c2w_client_proxy.c2wClientProxy`

        :param port: The server port number
        :type int:

        :param host: The *IP address* of the server
        :type string:

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
        self.server_host = host
        self.server_port = port
        self.clientProxy = sybilProxy

    def sendRequest(self, line):
        """
        :param line: the text of the question from the user interface
        :type line: string

        This function must send the request to the server.
        """
  
  
        TIME = str(int(time.time())) + ": " + line
        address = (self.server_host,self.server_port)
        self.transport.write(TIME,address)

    def datagramReceived(self,datagram,host):
        self.clientProxy.responseReceived(datagram)







