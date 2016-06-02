# -*- coding: utf-8 -*-
# DAWPaG - Desktop Applications With Python and GTK+
# Copyright © 2008 Alexandre da Silva / Carlos Antonio da Silva
#
# This file is part of DAWPaG.
#
# DAWPaG. is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# DAWPaG. is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with DAWPaG.; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301
# USA

import dawpag.utils as u
from new import instancemethod

log = u.get_logger('dawpag.signal_emissor')

class SignalEmissor(object):
    """
    A class to define a signal emissor object.
    A signal emissor can emit signals and connect callbacks to signals, just
    like gtk and/or Qt does
    """

    def __initialize_meta(self):
        if not hasattr(self, '__signals__dict__'):
            self.__signals__count = 0
            self.__signals__dict__ = {}

    def __signal_exists(self, signal):
        """
        Test if a given signal exists
        """
        self.__initialize_meta()
        if not self.__signals__dict__.has_key(signal):
            raise KeyError('signal %s not defined for %s' % (signal, str(self)))
            return False
        return True

    def signal_define(self, signal):
        """
        Define a signal from given name that can be sent by a object
        """
        self.__initialize_meta()
        if self.__signals__dict__.has_key(signal):
            raise KeyError('Signal %s already exists' % signal)
        self.__signals__dict__[signal] = []

    def signal_connect(self, signal, callback, **kwargs):
        """
        Connect a callback to a signal, acceptiog user arguments
            signal: the name of signal to be connected
            callback: a method or function to be called when the signal is
                sent
            kwargs: any number of keyword argumets to be used by user
            returns: the handler id of this signal or -1 if signal not exists
        """
        if not self.__signal_exists(signal):
            return -1
        self.__signals__count += 1
        self.__signals__dict__[signal].append((self.__signals__count, callback,
            kwargs))
        return self.__signals__count

    def signal_send(self, signal, *args, **kwargs):
        """
        Send/Emit the given signals with  any number of arguments or keyword
        arguments
        """
        if not self.__signal_exists(signal):
            return False
        for c, callback, kwargs_ in self.__signals__dict__[signal]:
            #if kwargs_:
            for k in kwargs_:
                kwargs[k] = kwargs_[k]
            callback(*args, **kwargs)
        return True

    def signal_disconnect(self, handler_id):
        """
        Disconnect the signal callback from the given handler id
        """
        for signal in self.__signals__dict__:
            slist = self.__signals__dict__[signal]
            for ix, val in enumerate(slist):
                log.debug(str(val))
                if val[0] == handler_id:
                    slist.pop(ix)
                    return True
        log.warning('handler "%d" does not exist' % handler_id)
        return False

    def signal_disconnect_all(self, signal):
        """
        Disconnects all callbacks for the given signal
        """
        if not self.__signal_exists(signal):
            return False
        self.__signals__dict__[signal] = []
        return True