from twisted.internet.protocol import DatagramProtocol
#from c2w.main.lossy_transport import LossyTransport
from twisted.internet import reactor 
from table_UDP import *
import logging
import ctypes
import struct
from c2w.main.constants import ROOM_IDS
from c2w.main.client_model import c2wClientModel
from c2w.main.user import c2wUser
from c2w.main.movie import c2wMovie
from test_insfructure import *

def addSequenceNumber(sequenceNumber):
    sequenceNumber += 1
    if sequenceNumber == 256:
        sequenceNumber = 0
    return sequenceNumber

def sendACK(seqNum, header, UserId):
    print "we send an ACK of the type of message " + str(header[0]) 
    buf_ACK = ctypes.create_string_buffer(6)
    struct.pack_into('>BBBBH', buf_ACK, 0, (header[0]+ACK) or RT_NotApplicable, seqNum, UserId, 0x0, 0x0)

    return buf_ACK.raw

def packetBuffer(Header1, SeqNum, userID, desID, data):
    if data == None:
        buf = ctypes.create_string_buffer(6)
        struct.pack_into('>BBBBH', buf, 0, Header1, SeqNum, userID, desID, 0)
    else:
        buf = ctypes.create_string_buffer(6 + len(data))
        struct.pack_into('>BBBBH'+str(len(data))+'s', buf, 0, Header1, SeqNum, userID, desID, len(data), data)
    return buf.raw

def unpackMovieList(data):
    movieList = []
    movieListModel = []

    while len(data)> 0 :
        length = struct.unpack_from('B', data[0])[0]
        MovieData = struct.unpack_from('BB'+str(length) + 's', data[0:2+length])
        movieList += [(MovieData[2], '123.22.134.21', '00' ),]
        movieListModel += [(MovieData[2], '123.22.134.21', '0',  MovieData[1])]
        data = data[2+length:] 
    return [movieList, movieListModel]


def unpackUserList(roomName, data):
    userList = []
    print "we get the userlist and start to unpack usrlist", data
  
    while len(data)> 0 :
        length = struct.unpack_from('B', data[0])[0]
        UserData = struct.unpack_from('BBB'+str(length) + 's', data[0:3+length])
        if UserData[2] == 0b10000000 : 
            userList += [(UserData[3], ROOM_IDS.MAIN_ROOM),]
        elif UserData[2] == 0b00000000 :
            if roomName == ROOM_IDS.MAIN_ROOM :
                userList += [(UserData[3], 'Great Guy'),]
            else :
                userList += [(UserData[3], roomName),]
        data=data[3+length:]
    return userList

def mapUserIn(users, data):
    while len(data)> 0 :
        length = struct.unpack_from('B', data[0])[0]
        UserData = struct.unpack_from('BBB'+str(length) + 's', data[0:3+length])
        userAlreadyIn = 0
        users[UserData[1]] = UserData[3]
        data=data[3+length:]
    return users


def unpackMovieInformation(data):
    print
    print 'buffer of information of ACK : ', data,  len(data),  type(data)
    moviePN, lenIP = struct.unpack_from('>HB', data)
    print moviePN, lenIP
    movieIN = struct.unpack_from('>HB' + str(lenIP)+'s', data)
    return movieIN
