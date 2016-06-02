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

from assessor.model import Subsidiary
import dawpag.utils as u
import gtk

log = u.get_logger('assessor.utils')

class SubsidiarySelect(object):
    def __init__(self, combo, default=None, callback=None):
        log.debug('Create a subsidiary selection combo...')
        self.callback = callback
        #self.combo = combo
        item_list = gtk.ListStore(object, str)
        default_id = -1
        for ix, sub in enumerate(Subsidiary.all()):
            item_list.append([sub, getattr(sub, 'name')])
            if default == sub:
                default_id = ix
        cell = gtk.CellRendererText()
        combo.pack_start(cell, True)
        combo.add_attribute(cell, 'text', 1)
        combo.set_model(item_list)
        combo.connect('changed', self.__on_combo_change)
        if default:
            combo.set_active(default_id)

    def __on_combo_change(self, combo, data=None):
        cb_active = combo.get_active()
        cb_model = combo.get_model()
        if cb_active >= 0:
            obj = cb_model[cb_active][0]
            if self.callback:
                self.callback(obj)
