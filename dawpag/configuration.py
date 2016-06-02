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

from configobj import ConfigObj
import logging, logging.config
import os
import dawpag


class ConfigError(Exception):
    pass

class AppConfig(object):
    """
    Application configuration module
    """
    def __init__(self, cfg_file):
        print "Loading configuration file : %s" % cfg_file
        self.conf = ConfigObj(cfg_file)
        self.CONFIG_FILE = cfg_file

    def get(self, key, default=None, return_section=None):
        """
        Return the value of a configuration key, based on current environment
        section. if the key was not found in config, return the default value.
        if return_section is provided find the key in that section, else find
        in default sections global and environment.
        Example main.app_version to get value from conf['main']['app_version']
        """
        # if section is provided
        try:
            if return_section:
                if self.conf[return_section].has_key(key):
                    return self.conf[return_section][key]
                else:
                    return default
            # Look for key in global section
            if self.conf['global'].has_key(key):
                return self.conf['global'][key]
            # look for key in environment section
            if self.conf[self.ENVIRONMENT].has_key(key):
                return self.conf[self.ENVIRONMENT][key]
            else:
                return default
        except:
            raise ConfigError()

    def load_config(self):
        """
        Load the configuration file into config constants
        """
        print "Loading configuration......"
        try: # First of all, load the configured environment
            self.ENVIRONMENT=self.conf['global']['main.environment']
        except:
            raise ConfigError(_(u"Configuration invalid on environment "
                 "definition"))
        # load other default config variables
        self.LOG_LEVEL=self.get('log.level')
        self.DATABASE_LOG_LEVEL=self.get('database.log.level')

    def reload_config(self):
        """
        Reload the configuration file and load the configuration variables again
        """
        self.conf.reload()
        self.load_config()

# Configuration object placeholder
config=None

def set_config(cfg):
    """
    Defines the configuration object
    """
    global config
    config=cfg
    config.load_config()
    # Defines the log configuration
    logging.config.fileConfig(os.sep.join(
        [os.path.dirname(config.CONFIG_FILE),'log.cfg']))
    # Set the log level for sqlalchemy orm
    logging.getLogger('sqlalchemy').setLevel(
            eval('logging.'+config.get('database.log.level'))
        )