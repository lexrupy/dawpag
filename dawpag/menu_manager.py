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

import gtk
from dawpag.base_controller import BaseController

class TreeMainMenu(object):
    def __init__(self, tree_view):
        self.tree_view = tree_view
        self.tree_model = gtk.TreeStore(str, str, object, str)
        self.menu_column = gtk.TreeViewColumn('Main Menu')
        self.menu_cell_pb = gtk.CellRendererPixbuf()
        self.menu_cell = gtk.CellRendererText()
        tree_view.set_model(self.tree_model)
        tree_view.append_column(self.menu_column)
        tree_view.set_tooltip_column(3)
        self.menu_column.pack_start(self.menu_cell_pb, False)
        self.menu_column.pack_start(self.menu_cell, True)
        self.menu_column.set_attributes(self.menu_cell_pb, stock_id=1)
        self.menu_column.set_attributes(self.menu_cell, text=0)
        # Connect the row-activated event (onClick) to open related controller
        tree_view.connect('row-activated', self.row_activated)

    def add_group(self, name, tooltip=None):
        """
        Create a Group Node for menu TreeView
        """
        return self.tree_model.append(None,
            [name, gtk.STOCK_DIRECTORY, None, None])

    def add_item(self, group, ctrl, name=None, tooltip=None):
        """
        Create a Menu Item
        """                                           #STOCK_GO_FORWARD
        return self.tree_model.append(group,
            [ctrl.name, gtk.STOCK_CONVERT, ctrl, ctrl.description])

    def row_activated(self, treeview, path, column, data=None):
        """
        Test if Clicked item is a subclass of BaseController class, if yes
        instanciate the controller and show it
        """
        model = treeview.get_model()
        iter = model.get_iter(path)
        controller = model.get_value(iter, 2)
        if controller and issubclass(controller, BaseController):
            c = controller()
            c.show()