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

from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from dawpag import configuration as cfg

_engine = None

def get_engine():
    global _engine
    if not _engine:
        _engine = create_engine(cfg.config.get('database.dburi'),\
            encoding=cfg.config.get('database.encoding'))
    return _engine

def create_session():
        """Create a session that uses the engine from thread-local metadata."""
        if not metadata.is_bound():
            get_engine()
        return sessionmaker()

# Global Application Metadata
metadata = MetaData()

Session = create_session()
Session.configure(bind=_engine)

# The global session object
session = Session()