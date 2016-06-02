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

import pygtk
pygtk.require("2.0")
import gtk
from controller.main_controller import MainWindow
from controller.login_controller import LoginWindow
import dawpag.utils as u
from dawpag.configuration import config

log = u.get_logger('dawpag.startup')

class MainApp(object):
    """
    The Simple Main Application Class
    """
    def __init__(self):
        """
        Initialize the Main Window
        """
        w = MainWindow()
        login = LoginWindow()
        login.authenticate(w)

    def load_default_config(self):
        # Load default Configuration Constants
        from assessor.model import Config
        import assessor
        assessor.DEFAULT_SUBSIDIARY=Config.get('default_subsidiary', 1)
        log.debug('Loaded default subsidiary: %d' % assessor.DEFAULT_SUBSIDIARY)

    def start(self):
        """
        Start the GTK Application
        """
        self.load_default_config()
        gtk.main()

def start():
    log.debug('starting up...')
    log.debug('configuration file is "%s"' % config.CONFIG_FILE)
    app = MainApp()
    app.start()