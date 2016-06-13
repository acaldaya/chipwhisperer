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
from chipwhisperer.common.utils.parameter import Parameter

#If we have QSettings(), use that to get values from registry
try:
    from PySide.QtCore import QSettings
    settings_backend = QSettings()
except ImportError:
    settings_backend = None


class Settings(object):

    #Default settings all in one handy location

    params = Parameter(usePyQtGraph=True, name="Settings", type='group')
    params.addChildren([
        {'name':"Project Folder", 'key':"project-home-dir", 'type':"file", "filter":"dir",
         "value":os.path.join(os.path.expanduser('~'), 'chipwhisperer_projects')}
    ])

    _backend = settings_backend

    @classmethod
    def value(cls, name, default=None):
        """Get the value from the settings, if not present return default"""

        #Try the backend first (if available)
        val = None
        if cls._backend:
            val = cls._backend.value(name, None)

        #Try our local copy next
        if val is None:
            try:
                val = cls.params.getChild(name).getValue(default)
            except KeyError:
                val = default
        return val

    @classmethod
    def setValue(cls, name, value, ignoreBackend=False):
        """Set the value"""

        try:
            cls.params.getChild(name).setValue(value)
        except KeyError:
            cls.params.append(Parameter(cls.params, {'name':name, 'type':"str", "value":str(value)}))

        #Backend as well
        if cls._backend and not ignoreBackend:
            cls._backend.setValue(name, value)

    @classmethod
    def setBackend(cls, settings_backend):
        cls._backend = settings_backend
        # for child in cls.params.childs:
        #     #If backend has value, store locally
        #     backend_value = cls._backend.value(child.getName(), None)
        #     if backend_value:
        #         cls.setValue(child.getName(), backend_value, ignoreBackend=True)
        #
        #     #If value stored locally, store into backend if different
        #     dict_value = self._settings_dict[key]
        #     if dict_value != backend_value:
        #         self._backend.setValue(key, dict_value)