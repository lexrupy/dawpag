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

#import dawpag.utils as u
from dawpag import utils as u, message
from dawpag.database import session
from assessor.model import User

from dawpag.base_window import BaseWindow

log = u.get_logger('application.login')

class LoginWindow(BaseWindow):
    __invalid_count = 1
    __show_window = None

    def _initialize(self):
        # Change the "Tab Order"
        self.button_box.set_focus_chain([self.bt_confirm, self.bt_cancel])

    def authenticate(self, show_window):
        """
        Start the login dialog
            show_window: window to show if login success
        """
        self.__show_window = show_window
        self.show()

    def on_bt_confirm_clicked(self, data=None):
        """
        Check user information and accept or reject the login
        """
        #
        # Create the default user on database
        #
        # session.add(
        #     User(
        #         name='admin',
        #         fullname='Administrador',
        #         password='admin'
        #         )
        #     )
        # session.commit()
        # log.debug('created default admin user')
        def invalid_user_password():
            message.warning(_(u'Usuário ou Senha Inválida'), self.window)

        usname = self.ed_user.get_text()
        passwd = self.ed_password.get_text()
        # Query the user object from database
        userobj = session.query(User).filter_by(name=usname).first()
        if userobj:
            # Check if user has pending password change
            if userobj.password_pending:
                from password_change_controller import ChangePasswordWindow
                log.debug('will ask for password reset')
                dlg = ChangePasswordWindow()
                dlg.set_user(userobj)
                dlg.show(self.window)
                log.debug('will leave method')
                return
            # If an user was returned, check the password
            if userobj.check_password(passwd):
                log.info('User "%s" has logged in' % usname)
                self.window.destroy()
                self.__show_window.show()
            else:
                log.info('User "%s" tried to login %d time(s)' % \
                    (usname, self.__invalid_count))
                invalid_user_password()
                if self.__invalid_count >= 3:
                    import gtk
                    gtk.main_quit()
                else:
                   self.__invalid_count += 1
        else:
           invalid_user_password()

    def on_ed_password_key_press_event(self, widget, event, data=None):
        if u.get_key(event) == 'Return':
            self.on_bt_confirm_clicked()