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

import utils as u
from dawpag.base_window import BaseWindow
import datetime

#log = u.get_logger('dawpag.date_selection')

class SelectDateWindow(BaseWindow):
    __entry = None

    def _initialize(self):
        self.__callback = None
        # Change the "Tab Order"
        self.button_box.set_focus_chain([self.bt_select, self.bt_today,
            self.bt_cancel])

    def show_window(self, entry, parent=None):
        """
        Start the login dialog
            show_window: window to show if login success
        """
        self.__entry = entry
        self.show(parent)

    def on_bt_select_clicked(self, data=None):
        """
        Check user information and accept or reject the login
        """
        # Calendar widget holds month in zero based index 0..11
        y, m, d = self.calendar.get_date()
        date = datetime.date(y, m + 1, d)
        try:
            self.__entry.set_text(u.date_to_str(date))
            if self.__callback:
                self.__callback()
            self.window.destroy()
        except:
            self.message_error(_(u'Selecione a data corretamente'))

    def on_bt_cancel_clicked(self, data=None):
        """
        Check user information and accept or reject the login
        """
        self.window.destroy()

    def on_bt_today_clicked(self, data=None):
        """
        Check user information and accept or reject the login
        """
        #
        self.set_date(None)

    def set_callback(self, callbk):
        self.__callback = callbk

    def set_date(self, date):
        if not date:
            date = datetime.date.today()
        self.calendar.select_month(date.month - 1, date.year)
        self.calendar.select_day(date.day)
        self.calendar.clear_marks()
        self.calendar.mark_day(date.day)
