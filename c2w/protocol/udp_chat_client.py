# -*- coding: utf-8 -*-
from twisted.internet.protocol import DatagramProtocol
from c2w.main.lossy_transport import LossyTransport
from twisted.internet import reactor
from c2w.main.constants import ROOM_IDS
from c2w.main.client_model import c2wClientModel
from table_UDP import *
import logging
import ctypes
import struct
from client_function_udp import *
from c2w.main.user import c2wUser
from c2w.main.movie import c2wMovie
from c2w.main.client_model import c2wClientModel
from test_insfructure import *
import types

logging.basicConfig()
moduleLogger = logging.getLogger('c2w.protocol.udp_chat_client_protocol')



class c2wUdpChatClientProtocol(DatagramProtocol):

    def __init__(self, serverAddress, serverPort, clientProxy, lossPr):
        """
        :param serverAddress: The IP address (or the name) of the c2w server,
            given by the user.
        :param serverPort: The port number used by the c2w server,
            given by the user.
        :param clientProxy: The clientProxy, which the protocol must use
            to interact with the Graphical User Interface.

        Class implementing the UDP version of the client protocol.

        .. note::
            You must write the implementation of this class.

        Each instance must have at least the following attributes:

        .. attribute:: serverAddress

            The IP address (or the name) of the c2w server.

        .. attribute:: serverPort

            The port number used by the c2w server.

        .. attribute:: clientProxy

            The clientProxy, which the protocol must use
            to interact with the Graphical User Interface.

        .. attribute:: lossPr

            The packet loss probability for outgoing packets.  Do
            not modify this value!  (It is used by startProtocol.)

        .. note::
            You must add attributes and methods to this class in order
            to have a working and complete implementation of the c2w
            protocol.
        """

        self.serverAddress = serverAddress
        self.serverPort = serverPort
        self.clientProxy = clientProxy
	self.c2wClientModel = c2wClientModel()
        self.lossPr = lossPr
        self.userID = ''
        self.SeqNum = 0
        self.countRetransmit = 0
        self.flag_ACK = None
        self.movieList = []
	self.movieListModel = []
        self.userList = []
        self.userID = ''
	self.movieListReceived = 0
	self.movieTitle = ROOM_IDS.MAIN_ROOM
	self.timeGetUserList = 0
	self.users = {}


    def startProtocol(self):
        """
        DO NOT MODIFY THE FIRST TWO LINES OF THIS METHOD!!
        """
        self.transport = LossyTransport(self.transport, self.lossPr)
        DatagramProtocol.transport = self.transport

    def sendLoginRequestOIE(self, userName):
        """
        :param string userName: The user name that the user has typed.

        The controller calls this function as soon as the user clicks on
        the login button.
        """
        moduleLogger.debug('loginRequest called with username=%s', userName)
	print userName, " wants to enter the mainroom and the length is : ", len(userName)
	if len(userName) >30 :
	    self.clientProxy.connectionRejectedONE(Error_Code_Client[str(0x1)])
	else : 
	    buf_logIn = ctypes.create_string_buffer(6 + len(userName))
	    struct.pack_into('>BBBBH'+str(len(userName))+'s',buf_logIn ,0 ,TYPE_Login + RT_NotApplicable, 0x0, 0x0, 0x0, len(userName), userName)
            self.sendRequest(buf_logIn.raw)


    def sendRequest(self, buf):
	print type(buf)
        if self.countRetransmit < 3:
            self.transport.write(buf, (self.serverAddress, self.serverPort))
            print "Now in retransmit and the number of retransmit is" + str(self.countRetransmit)
            self.flag_ACK = reactor.callLater(2, self.sendRequest, buf)
            self.countRetransmit += 1
        else:
            self.clientProxy.connectionRejectedONE('No response from the server')
               
    def sendChatMessageOIE(self, message):
        """
        :param message: The text of the chat message.
        :type message: string

        Called **by the controller**  when the user has decided to send
        a chat message

        .. note::
           This is the only function handling chat messages, irrespective
           of the room where the user is.  Therefore it is up to the
           c2wChatClientProctocol or to the server to make sure that this
           message is handled properly, i.e., it is shown only by the
           client(s) who are in the same room.
	   
	   And in the destination field, it contains the corresponding movieId
        """
	if len(message) > 140 :
	    self.clientProxy.connectionRejectedONE(Error_Code_Client[str(0x4)])
	if self.movieTitle == ROOM_IDS.MAIN_ROOM :
	    RT = RT_MainRoom
	    buf_Message = packetBuffer(TYPE_Message + RT, self.SeqNum, self.userID, 0, message)	    
	else :
	    RT = RT_MovieRoom
	    buf_Message = packetBuffer(TYPE_Message + RT, self.SeqNum, self.userID, self.c2wClientModel.getMovieByTitle(self.movieTitle).movieId, message)
	self.sendRequest(buf_Message)

    def sendJoinRoomRequestOIE(self, roomName):
        """
        :param roomName: The room name (or movie title.)

        Called **by the controller**  when the user
        has clicked on the watch button or the leave button,
        indicating that she/he wants to change room.

        .. warning:
            The controller sets roomName to
            c2w.main.constants.ROOM_IDS.MAIN_ROOM when the user
            wants to go back to the main room.
        """
        if roomName == ROOM_IDS.MAIN_ROOM: ## the client wants to escape to the main room
            self.sendRequest(packetBuffer(TYPE_RoomRes, self.SeqNum, self.userID, 0, None))
	    self.movieTitle = ROOM_IDS.MAIN_ROOM
        else:
            roomID = self.c2wClientModel.getMovieByTitle(roomName).movieId
	    self.movieTitle = roomName
	    print "the room request is : ", self.movieTitle, roomName
            self.sendRequest(packetBuffer(TYPE_RoomRes+RT_MovieRoom, self.SeqNum, self.userID, roomID, None))

    def sendLeaveSystemRequestOIE(self):
        """
        Called **by the controller**  when the user
        has clicked on the leave button in the main room.
        """
        buf_leaveSystem = packetBuffer(TYPE_Disconnection, self.SeqNum, self.userID, 0, None)
	self.sendRequest(buf_leaveSystem)
	
    def addMovie(self, header, data, userAdd):
	if header[0] & FRG == FRG :
	    movies = unpackMovieList(data)
            self.movieList += movies[0]
	    self.movieListModel += movies[1]
	    for movie in self.movieListModel:
		self.c2wClientModel.addMovie(movie[0],movie[1],movie[2],movie[3])
	    self.movieListModel = []
            self.transport.write(packetBuffer(header[0]+ACK, header[1], header[2], 0, None), userAdd)
        else:
            movies = unpackMovieList(data)
            self.movieList += movies[0]
	    self.movieListModel += movies[1]
	    for movie in self.movieListModel:
		self.c2wClientModel.addMovie(movie[0],movie[1],movie[2],movie[3])
	    self.movieListModel = []
            self.transport.write(packetBuffer(header[0]+ACK, header[1], header[2], 0, None), userAdd)
	    
    def addUser(self, header, data, userAdd):
	if header[0] & FRG == FRG : # it's a framing
	    self.userList += unpackUserList(self.movieTitle, data)
	    self.transport.write(packetBuffer(header[0]+ACK, header[1], header[2], 0, None), (host, port))
	else:
	    print
	    print "now the movieroom is : ", self.movieTitle
	    print
	    users = unpackUserList(self.movieTitle, data)
	    self.userList += unpackUserList(self.movieTitle, data)
	    self.users = mapUserIn(self.users, data)
	    if self.movieListReceived == 0 :
		self.clientProxy.initCompleteONE(self.userList, self.movieList)
		self.userList = []
		self.movieListReceived = 1
	    elif 1:
		print "self.movieListReceived          ", self.movieListReceived
		self.clientProxy.setUserListONE(self.userList)
		self.userList = []
	    self.transport.write(packetBuffer(header[0]+ACK, header[1], header[2], 0, None), userAdd)

	
    def datagramReceived(self, datagram, (host, port)):
        """
        :param string datagram: the payload of the UDP packet.
        :param host: the IP address of the source.
        :param port: the source port.

        Called **by Twisted** when the client has received a UDP
        packet.
        """
	
        header = struct.unpack_from('>BBBBH', datagram)
        data = datagram[6:]
        test_datagram(header, data)

####################  Receive an ACK de login  #####################

    	if (header[0] & ACK == ACK) and (header[1] & self.SeqNum == self.SeqNum):
	    self.flag_ACK.cancel()
            self.SeqNum += addSequenceNumber(self.SeqNum)
	    self.countRetransmit = 0
	    
            if header[0] & FLAG_test_TYPE == TYPE_Login : ## login ACK
                self.userID = header[2]
		
	    if header[0] & FLAG_test_TYPE == TYPE_RoomRes : ## enter room ACK
		if self.movieTitle == ROOM_IDS.MAIN_ROOM :
		    self.clientProxy.joinRoomOKONE()
		    pass
		else :
		    movieIn = unpackMovieInformation(data)
		    print movieIn,  type(movieIn)
		    print self.movieTitle, movieIn[2], movieIn[0]
		    self.clientProxy.updateMovieAddressPort(self.movieTitle, movieIn[2], movieIn[0])
		self.clientProxy.joinRoomOKONE()
		
	    if header[0] & FLAG_test_TYPE == TYPE_Disconnection :
		self.clientProxy.leaveSystemOKONE()

###################  Receive a movieList  #######################

        if header[0] & FLAG_test_TYPE == TYPE_MovieList:
	    self.addMovie(header, data, (host, port))	    
                            
###################  Receive a userList  ########################
        if header[0] & FLAG_test_TYPE == TYPE_UserList:
	    self.timeGetUserList += 1
	    print "self.timeGetUserList is : ", self.timeGetUserList
	    self.addUser(header, data, (host, port))

############## Receive a message forward message #################
	if header[0] & FLAG_test_TYPE == TYPE_MessageForword:
	    self.transport.write(packetBuffer(header[0]+ACK, header[1], header[2], 0, None), (host, port))
	    print
	    print "to ensure the function is right, print the userlist for the fuction TYPE_MessageForword"
	    print self.userList
	    print
	    self.clientProxy.chatMessageReceivedONE(self.users[header[3]], data)
	    
##################### Receive a eroro message ######################
	if header[0] & FLAG_test_TYPE == TYPE_Error:
	    error = struct.unpack_from('>B', data)
	    print
	    print "we get the code of error is : ", error, error[0], type(error[0]), type(error)
	    self.clientProxy.connectionRejectedONE(Error_Code_Client[error[0]])	    
