from twisted.internet.protocol import DatagramProtocol
from c2w.main.lossy_transport import LossyTransport
from table_UDP import *
import logging
import ctypes
import struct
import math
import types
from c2w.main.constants import ROOM_IDS
from test_insfructure import *

def addSequenceNumber(sequenceNumber):
    sequenceNumber += 1
    if sequenceNumber == 256:
        sequenceNumber = 0
    return sequenceNumber

def sendACK(header, UserId):
    print "we will response an ACK of the message : " + str(header[0])
    buf_ACK = ctypes.create_string_buffer(6)
    struct.pack_into('>BBBBH', buf_ACK, 0, (header[0]+ACK) or RT_NotApplicable, header[1], UserId, 0x0, 0x0)

    print "the data of ACK message is :"
    print  buf_ACK.raw 
    return buf_ACK.raw

def packetBuffer(Header1, SeqNum, userID, desID, data):
    if data == None:
        buf = ctypes.create_string_buffer(6)
        struct.pack_into('>BBBBH', buf, 0, Header1, SeqNum, userID, desID, 0)
    elif type(data) == int :
        print "data is a int or long : ", data, type(data)
        buf = ctypes.create_string_buffer(7)
        struct.pack_into('>BBBBHB', buf, 0, Header1, SeqNum, userID, desID, 1, data)
    else:
        print
        print "pack buffer data = ", data, type(data)
        print "len(data) : ", len(data)
        buf = ctypes.create_string_buffer(6 + len(data))
        struct.pack_into('>BBBBH'+str(len(data))+'s', buf, 0, Header1, SeqNum, userID, desID, len(data), data)
    return buf

def getMovieList(MovieList):
    temp = []
    for MovieListO in MovieList:
        temp += [(len(MovieListO.movieTitle),MovieListO.movieId,MovieListO.movieTitle)]
    print "we get the movie list as : ", temp
    return temp

def SendMovieList(len_movieList, type_FRG, seqNum, movieList, userId):  
    header = ctypes.create_string_buffer(6)
    moviebuff = ''
    for i in range(0,len(movieList)):
        buff = ctypes.create_string_buffer(2+len(movieList[i][2]))
        struct.pack_into('>BB'+str(len(movieList[i][2]))+'s', buff, 0, movieList[i][0], movieList[i][1], movieList[i][2])
        moviebuff = moviebuff + buff.raw
    struct.pack_into('>BBBBH', header, 0, (type_FRG + TYPE_MovieList + RT_NotApplicable), seqNum, userId, 0x0, len_movieList)
    return header.raw + moviebuff

def GetUserList(UserList, UserChatRoom): #get the userlist in the same roon
    temp = []
    userInRoom = 0
    if UserChatRoom == ROOM_IDS.MAIN_ROOM:
        print "UserChatRoom == ROOM_IDS.MAIN_ROOM and we need to get all the users' information"
        for user in UserList:
            if user.userChatRoom == ROOM_IDS.MAIN_ROOM :
                userInRoom += 1
                UserListS = (0b10000000)
                UserName = user.userName
                temp += [(len(UserName), user.userId, UserListS, UserName),]
            else :
                UserListS = (0b0000000)
                UserName = user.userName
                temp += [(len(UserName), user.userId, UserListS, UserName),]
        if userInRoom == 0 :
            temp = []
    else :
        print "UserChatRoom is not the ROOM_IDS.MAIN_ROOM"
        UserListS = (0b00000000)
        for user in UserList:
            if user.userChatRoom == UserChatRoom :
                userInRoom += 1
                UserName = user.userName
                temp += [(len(UserName), user.userId, UserListS, UserName),]
            else :
                pass
        if userInRoom == 0 :
            temp = []
    print
    print "from the function of GetUserList : ", temp
    print
    return temp

def sendUserList(type_FRG, seqNum, userID, RT, len_userList, userList):
    header = ctypes.create_string_buffer(6)
    struct.pack_into('>BBBBH', header, 0, type_FRG+TYPE_UserList+RT, seqNum, userID, 0x0, len_userList)
    userBuffer = ''
    for i in range(0,len(userList)):
        buff = ctypes.create_string_buffer(3+len(userList[i][3]))
        struct.pack_into('>BBB'+str(len(userList[i][3]))+'s', buff, 0, userList[i][0], userList[i][1], userList[i][2], userList[i][3])
        userBuffer += buff.raw
    return header.raw + userBuffer

def getMovieInformation(moviePortNum, movieIP):
    print "the parametre of the movie is  :   ", moviePortNum, movieIP
    print movieIP, type(movieIP), len(movieIP)
    buf_movieIn = ctypes.create_string_buffer(3 + len(movieIP))
    struct.pack_into('>HB'+str(len(movieIP))+'s', buf_movieIn, 0, moviePortNum, len(movieIP), movieIP)
    return buf_movieIn

