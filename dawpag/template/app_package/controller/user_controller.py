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

from dawpag.base_controller import BaseController
from assessor.model import User
from password_change_controller import ChangePasswordWindow
from dawpag.enums import DataState, ColumnDraw

class UserWindow(BaseController):
    """
    Controller to manage users
    """
    name = _(u'Cadastro de usuários')
    description = _(u"Adicionar, remover e gerenciar contas de usuáros")

    def _initialize(self):
        self.model = User
        self.set_first_widget(self.ed_name)
        self.set_search_fields([
                    ('id', _(u'Código')),
                    ('name', _(u'Login')),
                    ('fullname', _(u'Nome Completo')),
                    ('active', _(u'Ativo')),
                ])
        self.default_search_column = 1
        self._draw_active_as = ColumnDraw.PIXBUF

    def _show_data_page(self):
        """
        On Show data page, hide button to change password when inserting
        """
        if self._check_state(DataState.INSERTING):
            self.bt_change_password.hide()
            self.lb_change_password.show()
        else:
            self.bt_change_password.show()
            self.lb_change_password.hide()

    def on_bt_change_password_clicked(self, button, data=None):
        """
        When user click on change password button, show the password change
        dialog
        """
        dlg = ChangePasswordWindow()
        dlg.set_user(self.current_object())
        dlg.show(self.window)