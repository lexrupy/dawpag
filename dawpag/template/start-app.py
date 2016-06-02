#!/usr/bin/env python
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

import sys, os
import dawpag.configuration as conf
import dawpag


if __name__ == "__main__":
    # Get the base dir of application
    dawpag.basedir = os.path.dirname(os.path.abspath(__file__))
    # Test if an argument was passed, if yes this argument sould be an alternate
    # config file, than load the configuration from config file.
    if len(sys.argv) > 1:
        configfile = sys.argv[1]
    else:
        configfile = os.sep.join([dawpag.basedir,'config.cfg'])
    # Set the application configuration file
    conf.set_config(conf.AppConfig(configfile))
    # Create and start the main APP
    from assessor.main import start
    start()
