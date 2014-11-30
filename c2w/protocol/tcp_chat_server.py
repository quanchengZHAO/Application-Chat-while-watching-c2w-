# -*- coding: utf-8 -*-
from twisted.internet.protocol import Protocol
from twisted.internet import reactor
from c2w.main.server_proxy import c2wServerProxy
from table_UDP import *
from server_funcion_UDP import *
from c2w.main.constants import ROOM_IDS
from c2w.main.user import c2wUser
from c2w.main.movie import c2wMovie
import logging
import ctypes
import struct
import math
import types
from test_insfructure import *
#"Importer la classe des clients ?"

logging.basicConfig()
moduleLogger = logging.getLogger('c2w.protocol.tcp_chat_server_protocol')



class c2wTcpChatServerProtocol(Protocol):

    def __init__(self, serverProxy, clientAddress, clientPort):
        """
        :param serverProxy: The serverProxy, which the protocol must use
            to interact with the user and movie store (i.e., the list of users
            and movies) in the server.
        :param clientAddress: The IP address (or the name) of the c2w server,
            given by the user.
        :param clientPort: The port number used by the c2w server,
            given by the user.

        Class implementing the UDP version of the client protocol.

        .. note::
            You must write the implementation of this class.

        Each instance must have at least the following attribute:

        .. attribute:: serverProxy

            The serverProxy, which the protocol must use
            to interact with the user and movie store in the server.

        .. attribute:: clientAddress

            The IP address (or the name) of the c2w server.

        .. attribute:: clientPort

            The port number used by the c2w server.

        .. note::
            You must add attributes and methods to this class in order
            to have a working and complete implementation of the c2w
            protocol.

        .. note::
            The IP address and port number of the client are provided
            only for the sake of completeness, you do not need to use
            them, as a TCP connection is already associated with only
            one client.
        """
        self.clientAddress = clientAddress
        self.clientPort = clientPort
        self.serverProxy = serverProxy
        self.userList = []
        self.movieList = {}
	self.packets = ''

   
    def sendRequestTest(self, userID, buf):
	if self.serverProxy.getUserById(userID).userChatInstance.countRetransmit < 3 :
	    self.serverProxy.getUserById(userID).userChatInstance.transport.write(buf)
	    self.serverProxy.getUserById(userID).userChatInstance.countRetransmit += 1
	    self.serverProxy.getUserById(userID).userChatInstance.flag_ACK = reactor.callLater(2, self.sendRequestTest, userID, buf)
    
    def sendMovieList(self, movieList, userId):
	print "we get the movie list is : ", movieList
        count  = 0
        length = 0
        for movie in movieList :
            print "movie is : ", movie
            length = length + 2 +len(movie[2])
            count += 1
            if length > 65562 :
                buf_movieList =  SendMovieList(length, 0, self.seqNum, movieList[0 : count], userId)
                count  = 0
                length = 0
                movieList = movieList[count : ]
                self.sendRequestTest(userId, buf_movieList)
            else :
                pass
        buf_movieList =  SendMovieList(length, 0, self.seqNum, movieList, userId)
        self.sendRequestTest(userId, buf_movieList)  
    
    def updateUserList(self, roomName):
	print
	print "the userlist to update is : ", roomName
	print 
	self.userList = self.serverProxy.getUserList()
	print "we get the all use list", self.userList
	if roomName == ROOM_IDS.MAIN_ROOM :
	    userList = GetUserList(self.userList, ROOM_IDS.MAIN_ROOM)    
	    if len(userList) == 0 :
		print "in the room ", roomName, " has no unses now"
		pass
	    else :
		self.forwardUserList(userList, roomName)
	else : 	
	    userList = GetUserList(self.userList, roomName)
	    if len(userList) == 0 :
		print "in the room ", roomName, " has no unses now"
		pass
	    else :
		self.forwardUserList(userList, roomName)
    
    def forwardUserList(self, userList, userChatRoom):
        print 
        print "we get the userList in the UpdateUserList is : ", userList, "in the ", userChatRoom, "have the number of user is", len(userList)
        print 
        if userChatRoom == ROOM_IDS.MAIN_ROOM :
            RT = RT_MainRoom
        else :
            RT = RT_MovieRoom
	if userChatRoom == ROOM_IDS.MAIN_ROOM :  ## only send the uselist to the statut of 128
	    for user in userList:
		if user[2] == (0b10000000) : 
		    userId = user[1]
		    print "userName in the userList to be updated is : ", user[3],  userId, user[2]
		    self.segmentUserList(userId, RT, userList, self.serverProxy.getUserById(userId).userChatInstance.seqNum)
		else :
		    pass
	else :
	    for user in userList:
		userId = user[1]
		print "userName in the userList to be updated is : ", user[3],  userId, user[2]
		self.segmentUserList(userId, RT, userList, self.serverProxy.getUserById(userId).userChatInstance.seqNum)
		

    def segmentUserList(self, userID, RT, userList, seqNum):    
        print "start forwardUserList"
        count  = 0
        length = 0
        for user in userList:
            userN = user[3]
            length = length + 3 +len(userN)
            count += 1
            if length > 65562 :
                buf_userList = sendUserList(0, seqNum, userID, RT, length, userList[0 : length])
                count  = 0
                length = 0
                userList = userList[count : ]
                self.sendRequestTest(userID, buf_userList)
            else :
                pass
        buf_userList = sendUserList(0, seqNum, userID, RT, length, userList[0 : length])
        self.sendRequestTest(userID, buf_userList)   
	    
    def forwardMessge(self, userList, sourceID, movieTitle, publicMessage) :
        if movieTitle == ROOM_IDS.MAIN_ROOM :
            movieId = ROOM_IDS.MAIN_ROOM
            RT = RT_MainRoom
	    for user in userList:
		print user
		print user[2] == 128
		if user[1] != sourceID and (user[2] == 128):
		    print ""
		    print "the user to recive the message is : ", user
		    userId = user[1]
		    buf_MesFor = packetBuffer(TYPE_MessageForword + RT, self.serverProxy.getUserById(userId).userChatInstance.seqNum, userId, sourceID, publicMessage)
		    self.sendRequestTest(userId, buf_MesFor.raw) 
		else:
		    pass
        else :
            movieId = self.serverProxy.getMovieByTitle(movieTitle).movieId
            RT = RT_MovieRoom
	    for user in userList:
		print
		print "the user to receive the message is : ", user
		if user[1] != sourceID :
		    userId = user[1]
		    buf_MesFor = packetBuffer(TYPE_MessageForword + RT, self.serverProxy.getUserById(userId).userChatInstance.seqNum, userId, sourceID, publicMessage)
		    self.sendRequestTest(userId, buf_MesFor.raw) 
		else:
		    pass
	    
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

    def dataReceived(self,datagram):
        """
        :param data: The message received from the server
        :type data: A string of indeterminate length

        Twisted calls this method whenever new data is received on this
        connection.
      	 """
	self.packets += datagram
	while self.packets != 0:
	    datagGram = self.handleTCPpacket(self.packets)
	    if datagGram == None: ### still miss some data
		return
	    else : #### at least we get a whole message
		header = datagGram[0]
		data = datagGram[1]
		test_datagram(header, data)
		userId = header[2]
		if userId == 0:
		    pass
		else :
		    chatInstance = self.serverProxy.getUserById(userId).userChatInstance
		
		#######################  receive a request of login #######################
		if header[0] & FLAG_test_TYPE == TYPE_Login:

		    if self.serverProxy.userExists(data):
			print "user already exist"
			buf_err = packetBuffer(TYPE_Error+RT_NotApplicable+ACK, 0, self.serverProxy.getUserByName(data).userId, 0, Error_Code_Serveur['Invalid message'])
			self.transport.write(buf_err.raw)
		    elif len(self.serverProxy.getUserList()) > 255:
			buf_err = packetBuffer(TYPE_Error+RT_NotApplicable+ACK, 0, 0, 0, Error_Code_Serveur['Server has reached its capacity'])
			self.transport.write(buf_err.raw)
		    elif 1:
			userName_tem = data
			self.serverProxy.addUser(userName_tem, ROOM_IDS.MAIN_ROOM, self, self.clientAddress)  ## add the user##
			userId = self.serverProxy.getUserByName(userName_tem).userId
			chatInstance = self.serverProxy.getUserById(userId).userChatInstance
			chatInstance.seqNum = 0
			chatInstance.flag_ACK = ''
			chatInstance.countRetransmit = 0
			print "after the login request, we get the parametre as : ", "self.seqNum[userId] ", chatInstance.seqNum, "self.flag_ACK[userId] ", chatInstance.flag_ACK, "self.countRetransmit[userId] ",  chatInstance.countRetransmit
			
			chatInstance.transport.write(sendACK(header, userId))    
			movieList = getMovieList(self.serverProxy.getMovieList())
			chatInstance.movieTitle = ROOM_IDS.MAIN_ROOM
			chatInstance.serverProxy.updateUserChatroom(self.serverProxy.getUserById(userId).userName, chatInstance.movieTitle)
			chatInstance.sendMovieList(movieList, userId) ### send movie list ####
			print chatInstance.seqNum
			
		#################   envoyer userlist suivant MovieList ACK   ################
		if (header[0] & ACK == ACK) and (header[0] & FLAG_test_TYPE == TYPE_MovieList) and (chatInstance.seqNum == header[1]):
		    print "we receive a movielist ACK sucessfully"
		    print
		    chatInstance.flag_ACK.cancel()
		    chatInstance.countRetransmit= 0
		    chatInstance.seqNum = addSequenceNumber(chatInstance.seqNum)
		   
		    self.updateUserList(chatInstance.movieTitle)
		    
		#################### to stop the UserList transfer  ##########################
		if (header[0] & ACK == ACK) and (header[0] & FLAG_test_TYPE == TYPE_UserList) and (chatInstance.seqNum == header[1]):
		    chatInstance.flag_ACK.cancel()
		    chatInstance.countRetransmit = 0
		    print "after the userlist ACK, the self.countRetransmit[userId] should be 0 !!!!===  ", chatInstance.countRetransmit
		    chatInstance.seqNum = addSequenceNumber(chatInstance.seqNum)
		
		################### to stop the public message forward ########################
		if (header[0] & ACK == ACK) and (header[0] & FLAG_test_TYPE == TYPE_MessageForword) and (chatInstance.seqNum == header[1]): 
		    chatInstance.flag_ACK.cancel()
		    chatInstance.countRetransmit = 0
		    print "after the publicMessage Forward ACK, the self.countRetransmit[userId] should be 0 !!!!===  ", chatInstance.countRetransmit
		    chatInstance.seqNum = addSequenceNumber(chatInstance.seqNum)
		
		################ when receive a require to enter a room  ######################
		if header[0] & FLAG_test_TYPE == TYPE_RoomRes :
		    print "we receive a message of room require"
		    ################# the user wants to enter the main
		    if header[0] & RT_NotApplicable == RT_MovieRoom : 
			print
			print " the client wants to enter a movie room"
			print " the movie room ID is : " + str(header[3])
			movieID = header[3]
			moviePortNum = self.serverProxy.getMovieById(movieID).moviePort                
			movieIP = self.serverProxy.getMovieById(movieID).movieIpAddress
			movieIn = getMovieInformation(moviePortNum, movieIP)
			chatInstance.movieTitle = self.serverProxy.getMovieById(movieID).movieTitle
			buf_movieACK = packetBuffer(header[0]+ ACK, header[1], userId, header[3], movieIn.raw)
			print
			print "the room request ACK is : ", movieIn.raw 
			print "the buffer of ACK together is : ", buf_movieACK.raw
			chatInstance.transport.write(buf_movieACK.raw)
			print
			print "the movie the client wants to watch is : ", userId, chatInstance.movieTitle
			print
			self.serverProxy.startStreamingMovie(chatInstance.movieTitle)
			############### Update the userlist ########
			self.serverProxy.updateUserChatroom(self.serverProxy.getUserById(userId).userName, chatInstance.movieTitle)
			    
			self.updateUserList(ROOM_IDS.MAIN_ROOM)
			self.updateUserList(chatInstance.movieTitle)
		    
		    #################### if the user wants to enter a main room #############           
		    elif header[0] & RT_NotApplicable == RT_MainRoom:
			print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
			print " the client wants to enter the main room"
			movieRoomLeave = chatInstance.movieTitle
			chatInstance.movieTitle=ROOM_IDS.MAIN_ROOM
			chatInstance.transport.write(sendACK(header, userId))
			self.serverProxy.stopStreamingMovie(movieRoomLeave)
			################# update the userlist #############
			self.serverProxy.updateUserChatroom(self.serverProxy.getUserById(userId).userName, chatInstance.movieTitle)
	
			self.updateUserList(ROOM_IDS.MAIN_ROOM)
			self.updateUserList(movieRoomLeave)			
		
		################### receive a message of quit the application #######################
		if header[0] & FLAG_test_TYPE == TYPE_Disconnection:
		    chatInstance.transport.write(sendACK(header, userId))
		    self.serverProxy.removeUser(self.serverProxy.getUserById(userId).userName)
		    
		    self.updateUserList(ROOM_IDS.MAIN_ROOM)
		
		################### receive a message of publid message ###########################
		if header[0] & FLAG_test_TYPE == TYPE_Message:
		    print
		    chatInstance.transport.write(sendACK(header, userId))
		    if header[0] & RT_NotApplicable == RT_MovieRoom : #### this is a public chat in the movie room
			print
			print "we get a public message require in the movie room"
			self.userList = self.serverProxy.getUserList()
			userListMovieRoom = GetUserList(self.userList, chatInstance.movieTitle) ### find the userlist in the same movie room
			print "the users to receive the public message is : ", userListMovieRoom, "the room is", chatInstance.movieTitle
			self.forwardMessge(userListMovieRoom, userId, chatInstance.movieTitle, data)
			
		    elif header[0] & RT_NotApplicable == RT_MainRoom : ### this is a public chat in the main room
			print
			print "we get a public message require in the main room "
			self.userList = self.serverProxy.getUserList()
			
			userListMovieRoom = GetUserList(self.userList, chatInstance.movieTitle) ### find the userlist in the same movie room
			print "the userlist to get the public message is : ", userListMovieRoom
			self.forwardMessge(userListMovieRoom, userId, chatInstance.movieTitle, data)
		    
		    else : ### unexpect error, send error message
			buf_err = packetBuffer(TYPE_Error+RT_NotApplicable+ACK, 0, 0, 0, Error_Code_Serveur['Invalid message'])
			chatInstance.transport.write(buf_err.raw)
			self.checkUserListNone(userListMainRoom, ROOM_IDS.MAIN_ROOM)
