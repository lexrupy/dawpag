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

from dawpag import utils as u, message as m
from dawpag.database import session
from dawpag.base_window import BaseWindow

log = u.get_logger('application.change_password')

class ChangePasswordWindow(BaseWindow):

    def _initialize(self):
        # Change the "Tab Order"
        self.button_box.set_focus_chain([self.bt_confirm, self.bt_cancel])
        self.__user = None

    def set_user(self, user):
        """
        Set the user object to work with
        if user has a pending password && already have a password, assume that
        an administrator has requested a password change, in this case:
            Show pending label
            ask for old password
            ask for new password
            ask for confirmation
        if user has no current password and have a password pending, assume
        that user is a New user, in this case:
            set new user welcome to pending label
            hide old passowd box
            change label to password definition
        """
        self.__user = user
        if user.password_pending:
            if not user.password:
                self.lb_old_password.hide()
                self.ed_old_password.hide()
                self.window.set_title(_(u'Finalizar criação de conta'))
                self.lb_pending_password.set_markup(_(u'<span size="small">Esta'
                    ' parece ser uma nova conta de usuário. Para começar\n'
                    'a utilizá-la você precisa definir uma senha.</span>'))
                self.lb_user.set_text(_('Criação de senha para:'))
            self.lb_pending_password.show()
        self.lb_username.set_markup('<b>%s</b>' % user.name)

    def do_exit(self):
        self.window.destroy()
        # TODO: Is this stuff necessary for Garbadge Collect?
        self = None

    def on_bt_cancel_clicked(self, button, data=None):
        """
        Close this window
        """
        self.do_exit()

    def on_bt_confirm_clicked(self, button, data=None):
        """
        Check provided information, and decide if user password will or not
        change
        """
        new_user = not self.__user.password
        old = self.ed_old_password.get_text()
        if new_user or self.__user.check_password(old):
            new = self.ed_new_password.get_text()
            new_confirm = self.ed_new_password_confirm.get_text()
            if new == new_confirm:
                self.__user.set_password(new)
                session.commit()
                if new_user:
                    m.info(_(u'Sua nova conta de usuário foi criada com'
                        ' sucesso!\nBem Vindo!'), self.window)
                else:
                    m.info(_(u'A senha foi alterada com sucesso!'), self.window)
                self.do_exit()
            else:
                m.warning(_(u'As confirmação de senha não confere.'),
                    self.window)
        else:
            m.error(_(u'Senha antiga não confere!\nTente novamente'),
                self.window)