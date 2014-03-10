#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2013-2014, NewAE Technology Inc
# All rights reserved.
#
# Find this and more at newae.com - this file is part of the chipwhisperer
# project, http://www.assembla.com/spaces/chipwhisperer
#
#    This file is part of chipwhisperer.
#
#    chipwhisperer is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    chipwhisperer is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with chipwhisperer.  If not, see <http://www.gnu.org/licenses/>.
#=================================================
import sys
import time

from PySide.QtCore import *
from PySide.QtGui import *

try:
    from pyqtgraph.parametertree import Parameter, ParameterTree, ParameterItem, registerParameterType
except ImportError:
    print "ERROR: PyQtGraph is required for this program"
    sys.exit()
    
from openadc.ExtendedParameter import ExtendedParameter
from TargetTemplate import TargetTemplate

import ftd2xx as ft

class ChipWhispererComm(object):
    CODE_READ = 0x80
    CODE_WRITE = 0xC0

    ADDR_STATUS = 49
    ADDR_FIFO = 50

    FLAG_RESET = 0x01
    FLAG_WRFULL = 0x02
    FLAG_RDEMPTY = 0x04

    def setOpenADC(self, oadc):
        self.oa = oadc

    def reset(self):
        self.oa.sendMessage(self.CODE_WRITE, self.ADDR_STATUS, [self.FLAG_RESET], Validate=False)
        time.sleep(0.05)
        self.oa.sendMessage(self.CODE_WRITE, self.ADDR_STATUS, [0x00], Validate=False)

    def con(self):
        if self.oa is None:
            print "No OpenADC?"
            return

        # Reset AES Core
        self.oa.sendMessage(self.CODE_WRITE, self.ADDR_STATUS, [self.FLAG_RESET], Validate=False)
        self.oa.sendMessage(self.CODE_WRITE, self.ADDR_STATUS, [0x00], Validate=False)

        return True

    def disconnect(self):
        return

    def flush(self):
        while (self.readStatus() & self.FLAG_RDEMPTY) != self.FLAG_RDEMPTY:
            self.oa.sendMessage(self.CODE_READ, self.ADDR_FIFO, Validate=False)

    def readStatus(self):
        b = self.oa.sendMessage(self.CODE_READ, self.ADDR_STATUS, Validate=False)
        return b[0]

    def writeMsg(self, msg):

        for b in msg:
            # while (self.readStatus() & self.FLAG_WRFULL) == self.FLAG_WRFULL:
            #    pass

            self.oa.sendMessage(self.CODE_WRITE, self.ADDR_FIFO, [b], Validate=False)

    def readMsg(self, nbytes):

        msg = bytearray()

        for i in range(0, nbytes):
            if self.readStatus() & self.FLAG_RDEMPTY:
                pass

            b = self.oa.sendMessage(self.CODE_READ, self.ADDR_FIFO, Validate=False)
            msg.append(b[0])

        return msg

    def write(self, address, MSB, LSB):
        msg = bytearray(5)

        msg[0] = 0x01;
        msg[1] = (address >> 8) & 0xFF;  # MSB
        msg[2] = address & 0xFF;  # LSB
        msg[3] = MSB;
        msg[4] = LSB;

        # msg = bytearray(strmsg)
        # print "Write: %x %x %x %x %x"%(msg[0],msg[1],msg[2],msg[3],msg[4])

        self.writeMsg(msg)

    def read(self, address):
        self.flush()
        msg = bytearray(3)
        msg[0] = 0x00;
        msg[1] = (address >> 8) & 0xFF;  # MSB
        msg[2] = address & 0xFF;  # LSB
        self.writeMsg(msg)
        # print "Write: %x %x %x"%(msg[0],msg[1],msg[2]),

        msg = self.readMsg(2)

        # print " Read: %x %x"%(msg[0],msg[1])

        # Order = MSB, LSB
        return msg

    def close(self):
        pass

class FTDIComm(object):

    def __init__(self):
        super(FTDIComm, self).__init__()
        self.serNo = "FTWQ8BMIA"

    def flush(self):
        num = self.sasebo.getQueueStatus()
        if num > 0:
            self.sasebo.read(num)

    def write(self, address, MSB, LSB):
        msg = bytearray(5)

        msg[0] = 0x01;
        msg[1] = (address >> 8) & 0xFF;  # MSB
        msg[2] = address & 0xFF;  # LSB
        msg[3] = MSB;
        msg[4] = LSB;

        strmsg = str(msg);

        # msg = bytearray(strmsg)
        # print "Write: %x %x %x %x %x"%(msg[0],msg[1],msg[2],msg[3],msg[4])

        self.sasebo.write(strmsg)

    def read(self, address):
        self.flush()
        msg = bytearray(3)
        msg[0] = 0x00;
        msg[1] = (address >> 8) & 0xFF;  # MSB
        msg[2] = address & 0xFF;  # LSB
        self.sasebo.write(str(msg))
        # print "Write: %x %x %x"%(msg[0],msg[1],msg[2]),
        msg = self.sasebo.read(2)
        msg = bytearray(msg)

        # print " Read: %x %x"%(msg[0],msg[1])

        # Order = MSB, LSB
        return msg

    def read128(self, address):
        self.flush()
        msg = bytearray(3 * 8)
        for i in range(0, 8):
            msg[i * 3] = 0x00;
            msg[i * 3 + 1] = (address >> 8) & 0xFF;
            msg[i * 3 + 2] = (address & 0xFF) + (i * 2);
        self.sasebo.write(str(msg))
        msg = self.sasebo.read(16)
        return bytearray(msg)

    def close(self):
        self.sasebo.close()

    def setOpenADC(self, oadc):
        pass

    def setSerial(self, ser):
        self.serNo = ser

    def con(self):
        try:
            self.sasebo = ft.openEx(self.serNo)
        except ft.ftd2xx.DeviceError, e:
            self.sasebo = None
            print "Failed to find device: %s" % str(e)
            return False

        self.sasebo.setTimeouts(1000, 1000)

        return True

    def disconnect(self):
        return
               
class SakuraG(TargetTemplate):
     
    def setupParameters(self): 
        self.hw = None

        ssParams = [{'name':'Connection via:', 'key':'conn', 'type':'list', 'values':{'ChipWhisperer Integrated':ChipWhispererComm(), 'FTDI Stand-Alone':FTDIComm()}, 'set':self.setConn},
                    {'name':'Reset FPGA', 'key':'reset', 'type':'action', 'action':self.reset, 'visible':False},
                    {'name':'USB Serial #:', 'key':'serno', 'type':'list', 'values':['Press Refresh'], 'visible':False},
                    {'name':'Enumerate Attached Devices', 'key':'pushsno', 'type':'action', 'action':self.refreshSerial, 'visible':False},
                   ]
        self.params = Parameter.create(name='Target Connection', type='group', children=ssParams)
        ExtendedParameter.setupExtended(self.params, self)      
        self.oa = None
        self.fixedStart = True

        self.hw = self.findParam('conn').value()
                    
    def setOpenADC(self, oadc):
        self.oa = oadc
        
    def setConn(self, con):
        self.hw = con
        if hasattr(self.hw, 'setSerial'):
            self.findParam('serno').show()
            self.findParam('pushsno').show()
        else:
            self.findParam('serno').hide()
            self.findParam('serno').hide()

    def refreshSerial(self):
        serialnames = ft.listDevices()
        if serialnames == None:
            serialnames = [" No Connected Devices "]

        self.findParam('serno').setLimits(serialnames)
        self.findParam('serno').setValue(serialnames[0])
#        self.paramListUpdated.emit(self.paramList())

    def con(self):   
        self.hw = self.findParam('conn').value()
        self.hw.setOpenADC(self.oa)

        if hasattr(self.hw, 'setSerial'):
            # For SAKURA-G normally we use 'A' channel
            ser = self.findParam('serno').value()

            if ser.endswith('A') is False:
                print "WARNING: Normally SAKURA-G uses 'A' ending in serial number"

            self.hw.setSerial(ser)

        hwok = self.hw.con()

        if hasattr(self.hw, 'reset'):
            self.findParam('reset').show()
        else:
            self.findParam('reset').hide()

        if hwok:
            # Init
            self.init()
        
        return hwok

    def reset(self):
        if self.hw:
            if hasattr(self.hw, 'reset'):
                self.hw.reset()

    def disconnect(self):
        if self.hw:
            self.hw.disconnect()

    def close(self):
        if self.hw:
            self.hw.close()

    def init(self):
        #Select AES
        self.hw.write(0x0004, 0x00, 0x01)
        self.hw.write(0x0006, 0x00, 0x00)

        #Reset AES module
        self.hw.write(0x0002, 0x00, 0x04)
        self.hw.write(0x0002, 0x00, 0x00)

        #Select AES output
        self.hw.write(0x0008, 0x00, 0x01)
        self.hw.write(0x000A, 0x00, 0x00)

    def setModeEncrypt(self):
        self.hw.write(0x000C, 0x00, 0x00)

    def setModeDecrypt(self):
        self.hw.write(0x000C, 0x00, 0x01)

    def checkEncryptionKey(self, key):
        #SAKURA-G AES Example has fixed first 9 bytes
        if self.fixedStart:
            for i in range(0,9):
                key[i] = i                
        return key 

    def loadEncryptionKey(self, key):
        """Encryption key is bytearray"""

        if key:                
            self.hw.write(0x0100, key[0], key[1])
            self.hw.write(0x0102, key[2], key[3])
            self.hw.write(0x0104, key[4], key[5])
            self.hw.write(0x0106, key[6], key[7])
            self.hw.write(0x0108, key[8], key[9])
            self.hw.write(0x010A, key[10], key[11])
            self.hw.write(0x010C, key[12], key[13])
            self.hw.write(0x010E, key[14], key[15])

        #Generate key schedule
        self.hw.write(0x0002, 0x00, 0x02)

        #Wait for done
        while self.isDone() == False:
            continue

    def loadInput(self, inputtext):
        self.hw.write(0x0140, inputtext[0], inputtext[1])
        self.hw.write(0x0142, inputtext[2], inputtext[3])
        self.hw.write(0x0144, inputtext[4], inputtext[5])
        self.hw.write(0x0146, inputtext[6], inputtext[7])
        self.hw.write(0x0148, inputtext[8], inputtext[9])
        self.hw.write(0x014A, inputtext[10], inputtext[11])
        self.hw.write(0x014C, inputtext[12], inputtext[13])
        self.hw.write(0x014E, inputtext[14], inputtext[15])

    def isDone(self):
        result = self.hw.read(0x0002)

        if result[0] == 0x00 and result[1] == 0x00:
            return True
        else:
            return False

    def readOutput(self):        
        return self.hw.read128(0x0180)

    def setMode(self, mode):
        if mode == "encryption":
            self.hw.write(0x000C, 0x00, 0x00)
        elif mode == "decryption":
            self.hw.write(0x000C, 0x00, 0x01)
        else:
            print "Wrong mode!!!!"

    def go(self):
        self.hw.write(0x0002, 0x00, 0x01)
