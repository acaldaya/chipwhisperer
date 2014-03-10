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

__author__ = "Colin O'Flynn"

import sys
from PySide.QtCore import *
from PySide.QtGui import *
import os.path
sys.path.append('../common')

#import TraceContainer
import TraceContainerConfig
import TraceContainerNative
from TraceContainerDPAv3 import ImportDPAv3Dialog

from TraceManagerImport import TraceManagerImport

import re

#For copying files when adding existing traces
import shutil
import glob

#For profiling support (not 100% needed)
import pstats, cProfile

#Reading trace config files
import ConfigParser

class TraceManager():
    """
    When using traces in ChipWhisperer, you may have remapped a bunch of trace files into one
    block of traces. This class is used to handle the remapping.
    """
    
    def __init__(self, parent):
        self.dlg = parent
        self.NumTrace = 0
        self.NumPoint = 0
        self.knownkey = None

    def findMappedTrace(self, n):
        for t in self.dlg.traceList:
            if t.mappedRange:
                if n >= t.mappedRange[0] and n <= t.mappedRange[1]:
                    return t
        raise ValueError("n = %d not in mapped range"%n)

    def getTrace(self, n):
        t = self.findMappedTrace(n)
        return t.getTrace(n - t.mappedRange[0])
    
    def getTextin(self, n):
        t = self.findMappedTrace(n)
        return t.getTextin(n - t.mappedRange[0])

    def getTextout(self, n):
        t = self.findMappedTrace(n)
        return t.getTextout(n - t.mappedRange[0])

    def getKnownKey(self):
        #For now all traces need to have same key
        return self.knownkey

    def UpdateTraces(self):
        #Find total (last mapped range)
        num = []
        pts = []

        for t in self.dlg.traceList:
            if t.mappedRange is not None:
                num.append(t.mappedRange[1])
                pts.append(int(t.config.attr("numPoints")))

                if self.knownkey == None:
                    self.knownkey = t.getKnownKey()

        if not num:
            self.NumTrace = 0
        else:
            self.NumTrace = max(num)
            
        if not pts:
            self.NumPoint = 0
        else:
            self.NumPoint = max(pts)
        
class TraceManagerDialog(QDialog):
    """Manages traces associated with some project"""
    tracesChanged = Signal()
    
    secName = "Trace Management"
    def __init__(self, parent=None):
        super(TraceManagerDialog, self).__init__(parent)
        self.parent = parent

        #This module is interface for others
        self.iface = TraceManager(self)
        
        layout = QVBoxLayout()

        #Get labels in use
        exampleConfig = TraceContainerConfig.TraceContainerConfig()
        attrs = exampleConfig.attrHeaderValues()      
        attrHeaders = [i["header"] for i in attrs]
        attrHeaders.insert(0, "Mapped Range")
        attrHeaders.insert(0, "Enabled")        
        self.table = QTableWidget(0, len(attrHeaders))     
        self.table.setHorizontalHeaderLabels(attrHeaders)
       
        layout.addWidget(self.table)

        #temp = QPushButton("Add Blank")
        #temp.clicked.connect(self.addRow)
        #layout.addWidget(temp)

        #importDPAv3 = QPushButton("Import DPAv3")
        #importDPAv3.clicked.connect(self.importDPAv3)
        #layout.addWidget(importDPAv3)

        #copyExisting = QPushButton("Copy Existing and Add")
        #copyExisting.clicked.connect(self.copyExisting)
        #layout.addWidget(copyExisting)

        importExisting = QPushButton("Add Reference to Existing")
        importExisting.clicked.connect(self.importExisting)
        layout.addWidget(importExisting)

        # Set dialog layout
        self.setLayout(layout)

        self.setWindowTitle("Trace Management")

        self.newProject()

    #def updatePreview(self):
    #    if self.parent is not None:
    #        self.parent.updatePreview()

    def newProject(self):        
        self.traceList = []    
        return

    def checkProject(self, ask=True):
        #Check trace attributes
        for i in range(0, self.table.rowCount()):
            self.traceList[i].checkTrace()

        #Check out config

    def saveProject(self, config, configfilename):
        for indx, t in enumerate(self.traceList):
            config[self.secName]['tracefile%d'%indx] = os.path.relpath(t.config.configFilename(), os.path.split(configfilename)[0])
            config[self.secName]['enabled%d'%indx] = str(t.config.enabled)

    def loadProject(self, configfilename):
        config = ConfigParser.RawConfigParser()
        config.read(configfilename)
        alltraces = config.items(self.secName)

        self.newProject()

        fdir = os.path.split(configfilename)[0] + "/"

        for t in alltraces:
            if t[0].startswith("tracefile"):
                fname = fdir + t[1]
                print "Opening %s"%fname
                ti = TraceContainerNative.TraceContainerNative()
                ti.config.loadTrace(fname)
                self.traceList.append(ti)
                self.addRow(ti)

            if t[0].startswith("enabled"):
                tnum = re.findall(r'[0-9]+', t[0])
                self.table.cellWidget(int(tnum[0]), self.findCol("Enabled")).setChecked(t[1] == "True")

    def findCol(self, name):
        """ Function is a hack/cheat to deal with movable headers if they become enabled """
        cols = self.table.columnCount()

        for i in range(0, cols):
            if self.table.horizontalHeaderItem(i).text() == name:
                return i

        raise ValueError("findCol argument not in table: %s"%name)

        
    def addRow(self, trace=None, location=None):
        if location == None:
            location = self.table.rowCount()
            
        self.table.insertRow(location)
        row = self.table.rowCount()-1
        cb = QCheckBox()
        cb.clicked.connect(self.validateTable)
        self.table.setCellWidget(row, self.findCol("Enabled"), cb)

        if trace:
            for t in trace.config.attrHeaderValues():
                try:
                    col = self.findCol(t["header"])
                    wid = QTableWidgetItem("%s"%trace.config.attr(t["name"]))
                    attrDict = trace.config.attrDict(t["name"])                    
                    try:        
                        isEditable = attrDict["editable"]
                    except KeyError:
                        isEditable = False
                        
                    if isEditable == False:
                        wid.setFlags(wid.flags() & ~Qt.ItemIsEditable)
                        
                    self.table.setItem(row, col, wid)
                                          
                except ValueError:
                    pass

        self.validateTable()

    def enableTraces(self, index):
        self.table.cellWidget(index, self.findCol("Enabled")).setChecked(True)
        self.validateTable()

    def validateTable(self):
        startTrace = 0
        for i in range(0, self.table.rowCount()):
            if self.table.cellWidget(i, self.findCol("Enabled")).isChecked():
                self.traceList[i].enabled = True
                tlen = self.traceList[i].numTraces()
                self.traceList[i].mappedRange = [startTrace, startTrace+tlen-1]
                self.table.setItem(i, self.findCol("Mapped Range"), QTableWidgetItem("%d-%d"%(startTrace, startTrace+tlen-1)))
                startTrace = startTrace + tlen

                if self.traceList[i].traces is None:
                    if self.traceList[i].config.configFilename() is not None:
                        path = os.path.split(self.traceList[i].config.configFilename())[0]
                        pref = self.traceList[i].config.attr("prefix")                        
                    else:
                        path = None
                        pref = None
                    self.traceList[i].loadAllTraces(path, pref)                   
                
            else:
                self.traceList[i].enabled = False
                self.traceList[i].mappedRange = None
                self.table.setItem(i, self.findCol("Mapped Range"), QTableWidgetItem(""))

        self.iface.UpdateTraces()    
        #self.updatePreview()
        self.tracesChanged.emit()
        
    def importDPAv3(self):
        imp = ImportDPAv3Dialog(self)
        imp.exec_()
        self.importExisting(imp.getTraceCfgFile())
        #self.updatePreview()
        
    def append(self, ti):
        self.traceList.append(ti)
        self.addRow(ti)
        #self.updatePreview()

    def importExisting(self, fname=None):
        
        tmi = TraceManagerImport(self)
        tmi.exec_()
        
        if tmi.getTrace() is not None:
            tmi.updateConfigData()
            self.append(tmi.getTrace())

    def copyExisting(self, fname=None):
        if fname == None:
            fname, _ = QFileDialog.getOpenFileName(self, 'Open file',QSettings().value("trace_last_file"),'*.cfg')
            if fname:
                QSettings().setValue("trace_last_file", fname)

        if fname:
            #Get our project directory
            targetdir = self.parent.cwp.traceslocation + "/"
            cfgname = os.path.split(fname)[1]
            srcdir = os.path.split(fname)[0] + "/"            
            newcfgname = targetdir + cfgname

            #Get prefix from config file
            config = ConfigParser.RawConfigParser()
            config.read(fname)
            prefix = config.get("Trace Config", "prefix")
            newprefix = prefix

            #Check if we'll be overwriting things
            newprefix = prefix
            while(os.path.exists(newcfgname)):
                npstripped = newprefix.rstrip("_")
                newprefix = QInputDialog.getText(self, "Enter New Prefix", "Project already contains trace with\nprefix %s. Please enter new prefix:"%npstripped, text=npstripped)
                if newprefix[1] == True:
                    newcfgname = targetdir + cfgname.replace(prefix.rstrip("_"), newprefix[0])
                    newprefix = newprefix[0] + "_"
                else:
                    return
                
            #Change prefix in config file & write new one
            config.set("Trace Config", "prefix", newprefix)
            configfile = open(newcfgname, 'wb')
            config.write(configfile)        
            configfile.close()
            
            #Copy anything with same prefix, changing as 
            for filename in glob.glob(os.path.join(srcdir, '%s*'%prefix)):
                if os.path.isfile(filename):
                    targetfile = os.path.split(filename)[1].replace(prefix, newprefix)
                    shutil.copy(filename, targetdir + targetfile)
            
            #Add new trace to file list
            ti = TraceFormatNative()
            ti.config.loadTrace(newcfgname)
            self.append(ti)
        

