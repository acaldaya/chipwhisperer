#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2013-2014, NewAE Technology Inc
# All rights reserved.
#
# Author: Colin O'Flynn
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

try:
    from PySide.QtCore import *
    from PySide.QtGui import *
except ImportError:
    print "ERROR: PySide is required for this program"
    sys.exit()

from chipwhisperer.analyzer.preprocessing.PreprocessingBase import PreprocessingBase
from openadc.ExtendedParameter import ExtendedParameter
from pyqtgraph.parametertree import Parameter

# from functools import partial
import scipy as sp
# import numpy as np
        
class Filter(PreprocessingBase):
    """
    Generic filter, pulls in from SciPy for doing the actual filtering of things
    """
     
    def setupParameters(self):
        ssParams = [{'name':'Enabled', 'type':'bool', 'value':True, 'set':self.setEnabled},
                         {'name':'Form', 'key':'form', 'type':'list', 'values':{"Butterworth":sp.signal.butter}, 'set':self.updateFilter},
                         {'name':'Type', 'key':'type', 'type':'list', 'values':["low", "high", "bandpass"], 'value':'low', 'set':self.updateFilter},
                         {'name':'Critical Freq #1 (0-1)', 'key':'freq1', 'type':'float', 'limits':(0, 1), 'step':0.05, 'value':0.1, 'set':self.updateFilter},
                         {'name':'Critical Freq #2 (0-1)', 'key':'freq2', 'type':'float', 'limits':(0, 1), 'step':0.05, 'value':0.8, 'set':self.updateFilter},
                         {'name':'Order', 'key':'order', 'type':'int', 'limits':(1, 32), 'value':5, 'set':self.updateFilter},
                         {'name':'Desc', 'type':'text', 'value':self.descrString}
                      ]
        self.params = Parameter.create(name='Filter', type='group', children=ssParams)
        ExtendedParameter.setupExtended(self.params, self)

        self.updateFilter()

    def updateFilter(self, param1=None):
        filt = self.findParam('form').value()
        N = self.findParam('order').value()
        ftype = self.findParam('type').value()
        freq1 = self.findParam('freq1').value()
        freq2 = self.findParam('freq2').value()
        
        if ftype == "bandpass":
            self.findParam('freq2').show()
            freq = [freq1, freq2]
        else:
            self.findParam('freq2').hide()
            freq = freq1
        
        b, a = filt(N, freq, ftype)
        self.b = b
        self.a = a
   
    def getTrace(self, n):
        if self.enabled:
            trace = self.trace.getTrace(n)
            if trace is None:
                return None
            
            filttrace = sp.signal.lfilter(self.b, self.a, trace)
            
            #print len(trace)
            #print len(filttrace)
            
            return filttrace
            
        else:
            return self.trace.getTrace(n)       

