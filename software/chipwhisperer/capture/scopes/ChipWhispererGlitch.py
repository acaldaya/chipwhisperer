#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2013-2014, NewAE Technology Inc
# All rights reserved.
#
# Authors: Colin O'Flynn
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
from functools import partial
import time

from PySide.QtCore import *
from PySide.QtGui import *

import PartialReconfiguration as pr

try:
    from pyqtgraph.parametertree import Parameter
except ImportError:
    print "ERROR: PyQtGraph is required for this program"
    sys.exit()

from openadc.ExtendedParameter import ExtendedParameter

glitchaddr = 51    
CODE_READ       = 0x80
CODE_WRITE      = 0xC0

# sign extend b low bits in x
# from "Bit Twiddling Hacks"
def SIGNEXT(x, b):
    m = 1 << (b - 1)
    x = x & ((1 << b) - 1)
    return (x ^ m) - m

class ChipWhispererGlitch(QObject):
    paramListUpdated = Signal(list)
             
    def __init__(self, showScriptParameter=None):
        paramSS = [
                {'name':'Clock Source', 'type':'list', 'values':{'Target IO-IN':0}, 'value':0},
                {'name':'Glitch Width (as % of period)', 'key':'width', 'type':'float', 'limits':(0, 100), 'step':0.39062, 'readonly':True, 'value':0, 'set':self.updatePartialReconfig},
                {'name':'Glitch Width (fine adjust)', 'key':'widthfine', 'type':'int', 'limits':(-255, 255), 'set':self.setGlitchWidthFine},
                {'name':'Glitch Offset (as % of period)', 'key':'offset', 'type':'float', 'limits':(0, 100), 'step':0.39062, 'readonly':True, 'value':0, 'set':self.updatePartialReconfig},
                {'name':'Glitch Offset (fine adjust)', 'key':'offsetfine', 'type':'int', 'limits':(-255, 255), 'set':self.setGlitchOffsetFine},
                {'name':'Glitch Trigger', 'type':'list', 'values':{'Capture Trigger':1, 'Manual':0, 'Continous':2}, 'value':0, 'set':self.setGlitchTrigger, 'get':self.glitchTrigger},                   
                {'name':'Repeat', 'type':'int', 'limits':(1,255), 'set':self.setNumGlitches, 'get':self.numGlitches},
                {'name':'Manual Trigger', 'type':'action', 'action':self.glitchManual},
                {'name':'Output Mode', 'type':'list', 'values':{'Clock XORd':0, 'Clock ORd':1, 'Glitch Only':2, 'Clock Only':3}, 'set':self.setGlitchType, 'get':self.glitchType},
                {'name':'Read Status', 'type':'action', 'action':self.checkLocked},
                {'name':'Reset DCM', 'type':'action', 'action':self.resetDCMs},
                ]
            
        #Load FPGA partial configuration data
        self.glitchPR = pr.PartialReconfigDataMulti()
        self.prCon = pr.PartialReconfigConnection()
        self.oa = None
        
        try:            
            self.glitchPR.load("scopes/cw-partial-files/s6lx25-glitchwidth.p")
            self.glitchPR.load("scopes/cw-partial-files/s6lx25-glitchoffset.p")
            self.prEnabled = True
        except IOError, e:
            print str(e)
            self.prEnabled = False
        except ValueError, e:
            print str(e)
            self.prEnabled = False
        #self.prEnabled = False
            
        if self.prEnabled:
            #Enable glitch width, check what we've got access to
            paramSS[1]['readonly'] = False
            lim = (self.glitchPR.limitList[0][0] / 2.55, self.glitchPR.limitList[0][1] / 2.55 )
            #if lim[0] < 0:
            #    lim = (0, lim[1])
            paramSS[1]['limits'] = lim
            
            paramSS[3]['readonly'] = False
            lim = (self.glitchPR.limitList[1][0] / 2.55, self.glitchPR.limitList[1][1] / 2.55 )
            #if lim[0] < 0:
            #    lim = (0, lim[1])
            paramSS[3]['limits'] = lim
                
        self.params = Parameter.create(name='Glitch Module', type='group', children=paramSS)
        ExtendedParameter.setupExtended(self.params, self)
        self.showScriptParameter = showScriptParameter
        
    def paramTreeChanged(self, param, changes):
        if self.showScriptParameter is not None:
            self.showScriptParameter(param, changes, self.params)

    def setOpenADC(self, oa):
        if self.prEnabled:
            self.prCon.con(oa)            
            #Reset FPGA back to defaults in case previous bitstreams loaded
            self.updatePartialReconfig()
            
        self.oa = oa
            
        self.params.getAllParameters()
        
    def paramList(self):
        p = []
        p.append(self.params)            
        return p
    
    def updatePartialReconfig(self, anything=None):
        width = self.findParam('width').value()
        offset = self.findParam('offset').value()
        
        widthint = round((width/100) * 256)
        offsetint = round((offset/100) * 256)
                    
        bs = self.glitchPR.getPartialBitstream([widthint, offsetint])
                 
        if self.prEnabled:
            self.prCon.program(bs)
            if self.oa is not None:
                self.resetDCMs()   
            
        print "Partial: %d %d"%(widthint, offsetint)
       
    def setGlitchWidthFine(self, fine):
        '''Set the fine phase adjust, range -255 to 255'''
        current = self.oa.sendMessage(CODE_READ, glitchaddr, Validate=False, maxResp=8)               

        LSB = fine & 0x00FF;
        MSB = (fine & 0x0100) >> 8;
       
        current[0] = LSB #7..0
        current[1] = (current[1] & ~0x01) | MSB #15..8

        #Start adjust
        current[2] = current[2] | 0x04 #23..16    
        #assign clockglitch_settings_read[37] = phase1_done_reg;
        #assign clockglitch_settings_read[38] = phase2_done_reg;
     
        self.oa.sendMessage(CODE_WRITE, glitchaddr, current, Validate=False)
        
    def getGlitchWidthFine(self):
        return self.getDCMStatus()[0]

    def setGlitchOffsetFine(self, fine):
        '''Set the fine phase adjust, range -255 to 255'''
        current = self.oa.sendMessage(CODE_READ, glitchaddr, Validate=False, maxResp=8)               

        LSB = fine & 0x00FF;
        MSB = (fine & 0x0100) >> 8;
       
        current[1] = (current[1] & 0x01) | ((LSB & 0x7F) << 1);
        current[2] = (current[2] & ~0x03) | ((LSB >> 7) | (MSB << 1));

        #Start adjust
        current[2] = current[2] | 0x04 #23..16    
        #assign clockglitch_settings_read[37] = phase1_done_reg;
        #assign clockglitch_settings_read[38] = phase2_done_reg;     
        self.oa.sendMessage(CODE_WRITE, glitchaddr, current, Validate=False)
                
    def getGlitchOffsetFine(self):
        return self.getDCMStatus()[1] 

    def getDCMStatus(self):
        current = self.oa.sendMessage(CODE_READ, glitchaddr, Validate=False, maxResp=8)
        
        phase1 = current[2] >> 3
        phase1 |= (current[3] & 0x0F) << 5        
        phase1 = SIGNEXT(phase1, 9)
        
        phase2 = (current[3] & 0xF0) >> 4
        phase2 |= (current[4] & 0x1F) << 4
        phase2 = SIGNEXT(phase2, 9)
        
        dcm1Lock = False
        dcm2Lock = False
        
        if current[4] & 0x80:
            dcm1Lock = True
            
        if current[5] & 0x01:
            dcm2Lock = True
        
        return (phase1, phase2, dcm1Lock, dcm2Lock)
        
    def resetDCMs(self):
        reset = self.oa.sendMessage(CODE_READ, glitchaddr, Validate=False, maxResp=8) 
        reset[5] |= (1<<1)
        self.oa.sendMessage(CODE_WRITE, glitchaddr, reset, Validate=False)
        reset[5] &= ~(1<<1)
        self.oa.sendMessage(CODE_WRITE, glitchaddr, reset, Validate=False)
        
        self.findParam('widthfine').setValue(0)
        self.findParam('offsetfine').setValue(0)
        
    def checkLocked(self):
        stat = self.getDCMStatus()
        print "DCM1: Phase %d, Locked %r"%(stat[0], stat[2])
        print "DCM2: Phase %d, Locked %r"%(stat[1], stat[3])  
        
    def setNumGlitches(self, num):
        resp = self.oa.sendMessage(CODE_READ, glitchaddr, Validate=False, maxResp=8)
        if num < 1:
            num = 1
        resp[6] = num-1
        self.oa.sendMessage(CODE_WRITE, glitchaddr, resp, Validate=False)
        
    def numGlitches(self):
        resp = self.oa.sendMessage(CODE_READ, glitchaddr, Validate=False, maxResp=8)
        return resp[6]+1
    
    def setGlitchTrigger(self, trigger):
        resp = self.oa.sendMessage(CODE_READ, glitchaddr, Validate=False, maxResp=8)
        resp[5] = (resp[5] & ~(0x0C)) | (trigger << 2)
        self.oa.sendMessage(CODE_WRITE, glitchaddr, resp, Validate=False)        
        
    def glitchTrigger(self):
        resp = self.oa.sendMessage(CODE_READ, glitchaddr, Validate=False, maxResp=8)
        return (resp[5] & 0x0C) >> 2
    
    def setGlitchType(self, t):
        resp = self.oa.sendMessage(CODE_READ, glitchaddr, Validate=False, maxResp=8)
        resp[5] = (resp[5] & ~(0x70)) | (t << 4)
        self.oa.sendMessage(CODE_WRITE, glitchaddr, resp, Validate=False)        
        
    def glitchType(self):
        resp = self.oa.sendMessage(CODE_READ, glitchaddr, Validate=False, maxResp=8)
        return (resp[5] & 0x70) >> 4
        
    def glitchManual(self):
        resp = self.oa.sendMessage(CODE_READ, glitchaddr, Validate=False, maxResp=8)
        resp[5] = resp[5] | (1<<7)
        self.oa.sendMessage(CODE_WRITE, glitchaddr, resp, Validate=False)           
        resp[5] = resp[5] & ~(1<<7)
        self.oa.sendMessage(CODE_WRITE, glitchaddr, resp, Validate=False) 
        
