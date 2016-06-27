#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2013-2016, NewAE Technology Inc
# All rights reserved.
#
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

from .base import ResultsBase
from chipwhisperer.common.ui.GraphWidget import GraphWidget
from chipwhisperer.common.utils import util
from chipwhisperer.common.utils.tracesource import TraceSource, ActiveTraceObserver
from chipwhisperer.common.utils.pluginmanager import Plugin


class WaveFormWidget(GraphWidget, ResultsBase, ActiveTraceObserver, Plugin):
    _name = 'Trace Output Plot'
    _description = 'Plots the waveform for a given trace source'

    def __init__(self, name=None):
        GraphWidget.__init__(self)
        if name is not None:
            self._name = name
        ActiveTraceObserver.__init__(self)

        self.params.addChildren([
            {'name':'Redraw after Each', 'type':'bool', 'value':False},
            {'name':'Trace Range', 'key':'tracerng', 'type':'range', 'limits':(0, 0), 'value':(0, 0)},
            {'name':'Point Range', 'key':'pointrng', 'type':'rangegraph', 'limits':(0, 0), 'value':(0, 0), 'graphwidget':self},
            {'name':'Redraw', 'type':'action', 'action':self.plotInputTrace},
        ])

        self.findParam('input').setValue(TraceSource.getRegisteredObject("Trace Management"))
        TraceSource.sigRegisteredObjectsChanged.connect(self.traceSourcesChanged)

        self.resetTraceLimits()
        self.setDefaultYRange(-0.5, 0.5)
        self.YDefault()

    def resetTraceLimits(self):
        if self._traceSource:
            lastTrace = self._traceSource.numTraces()-1
            lastPoint = self._traceSource.numPoints()-1
        else:
            lastTrace = -1
            lastPoint = -1

        traceRange = self.findParam('tracerng').getValue()
        self.findParam('tracerng').setLimits((0, lastTrace))
        self.findParam('tracerng').setValue((max(0, traceRange[0]), min(lastTrace, traceRange[1] if traceRange[1] >= 0 else 7)))
        self.findParam('pointrng').setLimits((0, lastPoint))
        self.findParam('pointrng').setValue((0, lastPoint))

    def plotInputTrace(self, _=None):
        #print "Plotting %d-%d for points %d-%d"%(params[0].value(), params[1].value(), params[2].value(), params[3].value())
        initialPersist = self.persistant
        if not self.persistant:
            self.clearPushed()

        tstart = self.findParam('tracerng').getValue()[0]
        tend = self.findParam('tracerng').getValue()[1]
        pstart = self.findParam('pointrng').getValue()[0]
        pend = self.findParam('pointrng').getValue()[1]
        ttotal = 0

        if tend - tstart + 1 > 1:
            self.setPersistance(True)

        for tnum in range(tstart, tend+1):
            trace = self._traceSource.getTrace(tnum)
            if trace is not None:
                ttotal += 1
                #TODO - Not sure if should add _traceSource.offset() or not?
                self.passTrace(trace[pstart:pend+1], pstart + self._traceSource.offset(), idString = str(tnum))

                if self.findParam('Redraw after Each').getValue():
                    util.updateUI()

        self.setPersistance(initialPersist)

    def processTraces(self):
        self.resetTraceLimits()
        self.plotInputTrace()

    def getWidget(self):
        return self