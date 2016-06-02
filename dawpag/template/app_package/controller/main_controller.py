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
import os
from dawpag.configuration import config
from dawpag.base_window import BaseWindow
import dawpag.utils as u
from dawpag.menu_manager import TreeMainMenu
from user_controller import UserWindow
from currency_type_controller import CurrencyTypeWindow
from state_controller import StateWindow
from city_controller import CityWindow
from person_controller import PersonWindow
from product_controller import ProductWindow
from stock_transaction_controller import StockTransactionWindow

class MainWindow(BaseWindow):
    """
    Main Application Window
    """
    def _initialize(self):
        self.window.set_title(
            config.get('main.app_name') + ' - ' + \
            config.get('main.app_version')
        )
        u.set_image(self.im_menu_header)
        self.evt_center.modify_bg(gtk.STATE_NORMAL, \
            gtk.gdk.color_parse("white"))
        u.set_image(self.im_center_background)
        self.menu = TreeMainMenu(self.tv_main_menu)
        self.create_main_menu()

    def create_main_menu(self):
        """
        Create the main menu tree view
        """
        forms = self.menu.add_group(_(u'CADASTROS'))
        self.menu.add_item(forms, PersonWindow)
        self.menu.add_item(forms, ProductWindow)
        self.menu.add_item(forms, CurrencyTypeWindow)
        self.menu.add_item(forms, StateWindow)
        self.menu.add_item(forms, CityWindow)
        transactions = self.menu.add_group(_(u'LANÇAMENTOS'))
        self.menu.add_item(transactions, StockTransactionWindow)
        security = self.menu.add_group(_(u'SEGURANCA'))
        self.menu.add_item(security, UserWindow)

