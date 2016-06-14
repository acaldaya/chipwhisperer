#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2016, NewAE Technology Inc
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

import os
import os.path
from chipwhisperer.common.utils.parameter import Parameterized

class Settings(Parameterized):
    #Default settings all in one handy location
    _name = "Settings"
    fname = "settings.txt"
    parameters = None

    def __init__(self, fname=None):
        if fname:
            self.fname = fname
        if Settings.parameters is None:
            self.getParams().register()
            self.getParams().addChildren([
                {'name':"Project Folder", 'key':"project-home-dir", 'type':"file", "filter":"dir",
                 "value":os.path.join(os.path.expanduser('~'), 'chipwhisperer_projects')}
            ])
            Settings.parameters = self.params
            if os.path.isfile(self.fname):
                self.params.load(self.fname)
        else:
            self.params = Settings.parameters


    def value(self, name, default=None):
        """Get the value from the settings, if not present return default"""
        try:
            return self.params.getChild(name).getValue(default)
        except KeyError:
            return default

    def setValue(self, name, value):
        """Set the value"""
        try:
            self.params.getChild(name).setValue(value)
        except KeyError:
            self.params.addChildren([{'name':name, 'type':"str", "value":str(value)}])

    def save(self):
        self.params.save(self.fname)
