# -*- coding: utf-8 -*-
from twisted.internet.protocol import DatagramProtocol
from c2w.main.lossy_transport import LossyTransport
from twisted.internet import reactor
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

class c2wUdpChatServerProtocol(DatagramProtocol):

    def __init__(self, serverProxy, lossPr):
        """
        :param serverProxy: The serverProxy, which the protocol must use
            to interact with the user and movie store (i.e., the list of users
            and movies) in the server.
        :param lossPr: The packet loss probability for outgoing packets.  Do
            not modify this value!

        Class implementing the UDP version of the client protocol.

        .. note::
            You must write the implementation of this class.

        Each instance must have at least the following attribute:

        .. attribute:: serverProxy

            The serverProxy, which the protocol must use
            to interact with the user and movie store in the server.

        .. attribute:: lossPr

            The packet loss probability for outgoing packets.  Do
            not modify this value!  (It is used by startProtocol.)

        .. note::
            You must add attributes and methods to this class in order
            to have a working and complete implementation of the c2w
            protocol.
        """
        self.serverProxy = serverProxy
        self.lossPr = lossPr
        self.userList = []
        self.movieList = {}
        self.seqNum = {}
        self.flag_ACK = {}
        self.countRetransmit = {}
        self.movieTitle = {}
        self.flag = 0

    def startProtocol(self):
        """
        DO NOT MODIFY THE FIRST TWO LINES OF THIS METHOD!!
        """
        self.transport = LossyTransport(self.transport, self.lossPr)
        DatagramProtocol.transport = self.transport

    def sendRequestTest(self, userID, buf, (host, port)):
        if self.countRetransmit[userID] < 3:
            self.transport.write(buf, (host, port))
            self.countRetransmit[userID] += 1
            print "self.countRetransmit[userID] in the sendRequestTest is : ", self.countRetransmit[userID]
            self.flag_ACK[userID] = reactor.callLater(2, self.sendRequestTest, userID, buf, (host, port))

    def sendMovieList(self, movieList, userId, userAddress):
        print "we get the movie list is : ", movieList
        count  = 0
        length = 0
        for movie in movieList :
            print "movie is : ", movie
            length = length + 2 +len(movie[2])
            count += 1
            if length > 65562 :
                buf_movieList =  SendMovieList(length, 0, self.seqNum[userId], movieList[0 : count], userId)
                count  = 0
                length = 0
                movieList = movieList[count : ]
                self.sendRequestTest(userId, buf_movieList, userAddress)
            else :
                pass
        buf_movieList =  SendMovieList(length, 0, self.seqNum[userId], movieList, userId)
        self.sendRequestTest(userId, buf_movieList, userAddress)           

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
		    self.segmentUserList(userId, RT, userList, self.seqNum[userId],self.serverProxy.getUserById(userId).userAddress)
		else :
		    pass
	else :
	    for user in userList:
		userId = user[1]
		print "userName in the userList to be updated is : ", user[3],  userId, user[2]
		self.segmentUserList(userId, RT, userList, self.seqNum[userId], self.serverProxy.getUserById(userId).userAddress)

    def segmentUserList(self, userID, RT, userList, seqNum, userAddress):    
        print "start forwardUserList"
        print "before the forward userlist, the print self.countRetransmit[userId] should be 0 !!!!===  ", self.countRetransmit[userID]
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
                self.sendRequestTest(userID, buf_userList, userAddress)
            else :
                pass
        buf_userList = sendUserList(0, seqNum, userID, RT, length, userList[0 : length])
        self.sendRequestTest(userID, buf_userList, userAddress)    
            
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
		    buf_MesFor = packetBuffer(TYPE_MessageForword + RT, self.seqNum[userId], userId, sourceID, publicMessage)
		    self.sendRequestTest(userId, buf_MesFor.raw, self.serverProxy.getUserById(userId).userAddress) 
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
		    buf_MesFor = packetBuffer(TYPE_MessageForword + RT, self.seqNum[userId], userId, sourceID, publicMessage)
		    self.sendRequestTest(userId, buf_MesFor.raw, self.serverProxy.getUserById(userId).userAddress) 
		else:
		    pass
	    

    def datagramReceived(self, datagram, (host, port)):
        """
        :param string datagram: the payload of the UDP packet.
        :param host: the IP address of the source.
        :param port: the source port.

        Called **by Twisted** when the server has received a UDP
        packet.
        """
        header = struct.unpack_from('>BBBBH', datagram)
        userId = header[2]
        data = datagram[6:]
        test_datagram(header, data)
        
#######################  receive a request of login #######################
        if header[0] & FLAG_test_TYPE == TYPE_Login:

            if self.serverProxy.userExists(data):
                if header[1] ==  0:
                    print "header [0] is : ", header[0]
                    self.transport.write(packetBuffer(header[0]+ACK, 0, 1, 0, None),(host, port))
                    buf_err = packetBuffer(TYPE_Error+RT_NotApplicable+ACK, 0, self.serverProxy.getUserByName(data).userId, 0, Error_Code_Serveur['Username not availabe'])
                    self.transport.write(buf_err.raw,(host, port))
                else :
                    print "user already exist"
                    buf_err = packetBuffer(TYPE_Error+RT_NotApplicable+ACK, 0, self.serverProxy.getUserByName(data).userId, 0, Error_Code_Serveur['Invalid message'])
                    self.transport.write(buf_err.raw,(host, port))
            elif len(self.serverProxy.getUserList()) > 255:
                buf_err = packetBuffer(TYPE_Error+RT_NotApplicable+ACK, 0, 0, 0, Error_Code_Serveur['Server has reached its capacity'])
                self.transport.write(buf_err.raw,(host, port))
            elif 1:
                userName_tem = data
                self.serverProxy.addUser(userName_tem, ROOM_IDS.MAIN_ROOM, None, (host, port))  ## add the user##
                userId = self.serverProxy.getUserByName(userName_tem).userId
                
                self.seqNum[userId] = 0
                self.flag_ACK[userId] = ''
                self.countRetransmit[userId] = 0
                print "after the login request, we get the parametre as : ", "self.seqNum[userId] ", self.seqNum[userId], "self.flag_ACK[userId] ", self.flag_ACK[userId], "self.countRetransmit[userId] ",  self.countRetransmit[userId]                
                print
                self.transport.write(sendACK(header, userId),(host, port))    
                movieList = getMovieList(self.serverProxy.getMovieList())
                self.movieTitle[userId] = ROOM_IDS.MAIN_ROOM
                self.serverProxy.updateUserChatroom(self.serverProxy.getUserById(userId).userName, self.movieTitle[userId])
                self.sendMovieList(movieList, userId, (host, port)) ### send movie list ####

#################   envoyer userlist suivant MovieList ACK   ################
        if (header[0] & ACK == ACK) and (header[0] & FLAG_test_TYPE == TYPE_MovieList):
            if self.seqNum[userId] == header[1]:
                
                print "we receive a movielist ACK sucessfully"
                print
                self.flag_ACK[userId].cancel()
                self.countRetransmit[userId]= 0
                self.seqNum[userId] = addSequenceNumber(self.seqNum[userId])
                
                self.updateUserList(self.movieTitle[userId])
                                    
#################### to stop the UserList transfer  ##########################
        if (header[0] & ACK == ACK) and (header[0] & FLAG_test_TYPE == TYPE_UserList) and (self.seqNum[userId] == header[1]):
            self.flag_ACK[userId].cancel()
            self.countRetransmit[userId] = 0
            print "after the userlist ACK, the self.countRetransmit[userId] should be 0 !!!!===  ", self.countRetransmit[userId]
            self.seqNum[userId] = addSequenceNumber(self.seqNum[userId])
                
################### to stop the public message forward ########################
        if (header[0] & ACK == ACK) and (header[0] & FLAG_test_TYPE == TYPE_MessageForword) and (self.seqNum[userId] == header[1]):    
            self.flag_ACK[userId].cancel()
            self.countRetransmit[userId] = 0
            print "after the publicMessage Forward ACK, the self.countRetransmit[userId] should be 0 !!!!===  ", self.countRetransmit[userId]
            self.seqNum[userId] = addSequenceNumber(self.seqNum[userId])

################ when receive a require to enter a room  ######################
        if header[0] & FLAG_test_TYPE == TYPE_RoomRes :
            """"
            when we receive a room require, if is a main room require,
            send ACK and the user in the mainroom
            when a client wants to enter a movie room
            in the ACK, it contains the message of movie (port number and movie IP address)
            """
            print "we receive a message of room require"
            if header[0] & RT_NotApplicable == RT_MovieRoom:
                print 
                print " the client wants to enter a movie room"
                print " the movie room ID is : " + str(header[3])
                movieID = header[3]
                moviePortNum = self.serverProxy.getMovieById(movieID).moviePort                
                movieIP = self.serverProxy.getMovieById(movieID).movieIpAddress
                movieIn = getMovieInformation(moviePortNum, movieIP)
                self.movieTitle[userId] = self.serverProxy.getMovieById(movieID).movieTitle
                buf_movieACK = packetBuffer(header[0]+ ACK, header[1], userId, header[3], movieIn.raw)
                self.transport.write(buf_movieACK,(host, port))
                print
                print "the movie the client wants to watch is : ", userId, self.movieTitle[userId]
                print
                self.serverProxy.startStreamingMovie(self.movieTitle[userId])
                ############### Update the userlist ########
                
                self.serverProxy.updateUserChatroom(self.serverProxy.getUserById(userId).userName, self.movieTitle[userId])
			    
		self.updateUserList(ROOM_IDS.MAIN_ROOM)
		self.updateUserList(self.movieTitle[userId])
                
            #################### if the user wants to enter a main room #############           
            elif header[0] & RT_NotApplicable == RT_MainRoom:
                print " the client wants to enter the main room"
                movieRoomLeave = self.movieTitle[userId]
                self.movieTitle[userId]=ROOM_IDS.MAIN_ROOM
                self.transport.write(sendACK(header, userId),(host, port))
                self.serverProxy.stopStreamingMovie(movieRoomLeave)
                ################# update the userlist #############
                
                self.serverProxy.updateUserChatroom(self.serverProxy.getUserById(userId).userName, self.movieTitle[userId])
	
		self.updateUserList(ROOM_IDS.MAIN_ROOM)
		self.updateUserList(movieRoomLeave)	
                
################### receive a message of quit the application #######################

        if header[0] & FLAG_test_TYPE == TYPE_Disconnection:
            self.transport.write(sendACK(header, userId),(host, port))
            self.serverProxy.removeUser(self.serverProxy.getUserById(userId).userName)
            ############# Update usrlist only in the main room #############
            self.updateUserList(ROOM_IDS.MAIN_ROOM)
            
################### receive a message of publid message ###########################

        if header[0] & FLAG_test_TYPE == TYPE_Message:
            self.transport.write(sendACK(header, userId),(host, port))
            if header[0] & RT_NotApplicable == RT_MovieRoom : #### this is a public chat in the movie room
                print
                print "we get a public message require in the movie room"
                self.userList = self.serverProxy.getUserList()
                userListMovieRoom = GetUserList(self.userList, self.movieTitle[userId]) ### find the userlist in the same movie room
                print "the users to receive the public message is : ", userListMovieRoom, "the room is", self.movieTitle[userId]
                self.forwardMessge(userListMovieRoom, userId, self.movieTitle[userId], data)
                
            elif header[0] & RT_NotApplicable == RT_MainRoom : ### this is a public chat in the main room
                print
                print "we get a public message require in the main room "
                self.userList = self.serverProxy.getUserList()
                
                userListMovieRoom = GetUserList(self.userList, self.movieTitle[userId]) ### find the userlist in the same movie room
                print "the userlist to get the public message is : ", 
                self.forwardMessge(userListMovieRoom, userId, self.movieTitle[userId], data)
            
            else : ### unexpect error, send error message
                buf_err = packetBuffer(TYPE_Error+RT_NotApplicable+ACK, 0, 0, 0, Error_Code_Serveur['Invalid message'])
                self.transport.write(buf_err.raw,(host, port))
                