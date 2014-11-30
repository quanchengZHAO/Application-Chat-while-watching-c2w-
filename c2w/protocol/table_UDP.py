#!/usr/bin/env python

FRG = 0x80
ACK = 0x40

TYPE_Login = 0x0
TYPE_Disconnection = 0x3c
TYPE_Message = 0x4
TYPE_RoomRes = 0x20
TYPE_LeavePrivate = 0x1c
TYPE_MovieList = 0xc
TYPE_UserList = 0x14
TYPE_MessageForword = 0x30
TYPE_PrivateChat = 0x28
TYPE_LeavePricateFor = 0x24
TYPE_AYT = 0X18
TYPE_Error = 0x38

RT_MainRoom = 0x0
RT_MovieRoom = 0x1
RT_PrivateCHat = 0x2
RT_NotApplicable = 0x3

FLAG_test_TYPE = 0x3c
UserStatutMainRoom = 0x80

Error_Code_Client = { 0x1 : 'Username not availabe',
               0x2 : 'Id does not exist',
               0x3 : 'Server has reached its capacity',
               0x4 : 'Message too long',
               0x5 : 'Private chat request rejected',
               0x6 : 'Invalid message'}
Error_Code_Serveur = { 'Username not availabe' : 0x1,
               'Id does not exist' : 0x2,
               'Server has reached its capacity' : 0x3,
               'Message too long' : 0x4,
               'Private chat request rejected' : 0x5,
               'Invalid message' : 0x6}