# -*- coding: utf-8 -*-
from twisted.internet.protocol import Protocol
from twisted.internet import reactor
import logging
import ctypes
import struct
import types
from array import array
from c2w.main.user import c2wUser
from c2w.main.movie import c2wMovie
from test_insfructure import *
from table_UDP import *
from client_function_udp import *

logging.basicConfig()
moduleLogger = logging.getLogger('c2w.protocol.tcp_chat_client_protocol')




class c2wTcpChatClientProtocol(Protocol):

    def __init__(self, clientProxy, serverAddress, serverPort):
        """
        :param clientProxy: The clientProxy, which the protocol must use
            to interact with the Graphical User Interface.
        :param serverAddress: The IP address (or the name) of the c2w server,
            given by the user.
        :param serverPort: The port number used by the c2w server,
            given by the user.

        Class implementing the UDP version of the client protocol.

        .. note::
            You must write the implementation of this class.

        Each instance must have at least the following attribute:

        .. attribute:: clientProxy

            The clientProxy, which the protocol must use
            to interact with the Graphical User Interface.

        .. attribute:: serverAddress

            The IP address (or the name) of the c2w server.

        .. attribute:: serverPort

            The port number used by the c2w server.

        .. note::
            You must add attributes and methods to this class in order
            to have a working and complete implementation of the c2w
            protocol.
        """
        self.serverAddress = serverAddress
        self.serverPort = serverPort
        self.clientProxy = clientProxy
	self.c2wClientModel = c2wClientModel()
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
	self.packets = ''

    def sendRequest(self, buf):
        if self.countRetransmit < 3:
            self.transport.write(buf)
            print "Now in retransmit and the number of retransmit is" + str(self.countRetransmit)
            self.flag_ACK = reactor.callLater(2, self.sendRequest, buf)
            self.countRetransmit += 1
        else:
            self.clientProxy.connectionRejectedONE('No response from the server')
    
    def sendLoginRequestOIE(self, userName):
        """
        :param string userName: The user name that the user has typed.

        The controller calls this function after the TCP connection 
        with the server has been successfully established.
        """	
	moduleLogger.debug('loginRequest called with username=%s', userName)
	print userName, " wants to enter the mainroom and the length is : ", len(userName)
	if len(userName) >30 :
	    self.clientProxy.connectionRejectedONE(Error_Code_Client[0x1])
	else :
	    buf_logIn = packetBuffer(TYPE_Login + RT_NotApplicable, self.SeqNum, 0, 0, userName)
	    self.sendRequest(buf_logIn)

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
        """
        if len(message) > 140 :
	    self.clientProxy.connectionRejectedONE(Error_Code_Client[0x4])   
	elif self.movieTitle == ROOM_IDS.MAIN_ROOM :
	    print "~~~~~~~~send a message in the main room~~~~~~~~~~~~~~"
	    RT = RT_MainRoom
	    buf_Message = packetBuffer(TYPE_Message + RT, self.SeqNum, self.userID, 0, message)	    
	else :
	    print "~~~~~~~~send a message in the private room~~~~~~~~~~~~~~"
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
	    print "~~~~~~~~~~~~~~~~~~~~~~~~~~"
	    print "the client wants to enter the main room"
            self.sendRequest(packetBuffer(TYPE_RoomRes, self.SeqNum, self.userID, 0, None))
	    self.movieTitle = ROOM_IDS.MAIN_ROOM
        else: 
            roomID = self.c2wClientModel.getMovieByTitle(roomName).movieId
	    self.movieTitle = roomName
	    print "the room request is : ", self.movieTitle, roomID
            self.sendRequest(packetBuffer(TYPE_RoomRes+RT_MovieRoom, self.SeqNum, self.userID, roomID, None))     

    def sendLeaveSystemRequestOIE(self):
        """
        Called **by the controller**  when the user
        has clicked on the leave button in the main room.
        """
        buf_leaveSystem = packetBuffer(TYPE_Disconnection, self.SeqNum, self.userID, 0, None)
	self.sendRequest(buf_leaveSystem)
    
    def addMovie(self, header, data):
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
            self.transport.write(packetBuffer(header[0]+ACK, header[1], header[2], 0, None))
	    
    def addUser(self, header, data):
	if header[0] & FRG == FRG : # it's a framing
	    self.userList += unpackUserList(self.movieTitle, data)
	    self.transport.write(packetBuffer(header[0]+ACK, header[1], header[2], 0, None))
	else:
	    print
	    print "now the movieroom to add users is : ", self.movieTitle
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
	    self.transport.write(packetBuffer(header[0]+ACK, header[1], header[2], 0, None))
    
    def handleTCPpacket(self, packets):
	if len(packets) < 6 :
	    return
	else :
	    dataLengthT  = struct.unpack_from('>H', packets, 4)[0:1]
	    dataLength = dataLengthT[0]
	    if dataLength > len(packets[6:]) :
		return
	    else :
		header = struct.unpack_from('>BBBBH',packets)
		message = packets[6 : 6 + dataLength]		
		self.packets = self.packets[6 + dataLength :]
		return [header, message]   
			    
    def dataReceived(self, data):
        """
        :param data: The message received from the server
        :type data: A string of indeterminate length

        Twisted calls this method whenever new data is received on this
        connection.
        """
	##################### framming fuction ########################
	self.packets += data
	print "now we get the new data : ", self.packets
	""""
	no matter how many information is stocked in the data
	we must get all the information
	if the data is sent by 1by1, using retrun to get the rest datas
	if the data is sent by 2in1, using judge the lenth of self.packets to ensure we get all the parts of the two messages
	if the data is betweent 1 to 2, first to get the first whole message, using return to get the other data
	until we get the rest for the second message
	"""
		
	while self.packets != 0:
	    datagram = self.handleTCPpacket(self.packets)
	    if datagram == None: ### still miss some data
		return
	    else : #### at least we get a whole message
		header = datagram[0]
		dataMes = datagram[1]
		test_datagram(header, dataMes)
		######################## an ack message ############################
		if (header[0] & ACK == ACK) and (header[1] & self.SeqNum == self.SeqNum):
		    self.flag_ACK.cancel()
		    self.SeqNum += addSequenceNumber(self.SeqNum)
		    self.countRetransmit = 0
		
		    if header[0] & FLAG_test_TYPE == TYPE_Login : ## login ACK
			self.userID = header[2]
		    
		    if header[0] & FLAG_test_TYPE == TYPE_RoomRes : ## enter room ACK
			if self.movieTitle == ROOM_IDS.MAIN_ROOM :
			    pass
			else :
			    movieIn = unpackMovieInformation(dataMes)
			    print
			    print "WE GET THE movie information ",movieIn,  type(movieIn)
			    print self.movieTitle, movieIn[2], movieIn[0]
			    print
			    self.clientProxy.updateMovieAddressPort(self.movieTitle, movieIn[2], movieIn[0])
			self.clientProxy.joinRoomOKONE()
		    
		if header[0] & FLAG_test_TYPE == TYPE_Disconnection : #### disconnect room ACK
		    self.clientProxy.leaveSystemOKONE()
		    
		###################  Receive a movieList  #######################
		if header[0] & FLAG_test_TYPE == TYPE_MovieList:
		    self.addMovie(header, dataMes)
		    
		###################  Receive a userList  ########################
		if header[0] & FLAG_test_TYPE == TYPE_UserList:
		    self.timeGetUserList += 1
		    print "self.timeGetUserList is : ", self.timeGetUserList
		    self.addUser(header, dataMes)
		
		############## Receive a message forward message #################
		if header[0] & FLAG_test_TYPE == TYPE_MessageForword:
		    print ""
		    self.transport.write(packetBuffer(header[0]+ACK, header[1], header[2], 0, None))
		    print
		    print "to ensure the function is right, print the userlist for the fuction TYPE_MessageForword"
		    print self.userList
		    print
		    self.clientProxy.chatMessageReceivedONE(self.users[header[3]], dataMes)
			
		##################### Receive a eroro message ######################
		if header[0] & FLAG_test_TYPE == TYPE_Error:
		    error = struct.unpack_from('>B', dataMes)
		    print
		    print "we get the code of error is : ", error, error[0], type(error[0]), type(error)
		    self.clientProxy.connectionRejectedONE(Error_Code_Client[error[0]])	  
