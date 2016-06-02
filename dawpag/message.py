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

M_INFO = gtk.MESSAGE_INFO
M_ERROR = gtk.MESSAGE_ERROR
M_WARNING = gtk.MESSAGE_WARNING
M_QUESTION = gtk.MESSAGE_QUESTION

B_OK = gtk.BUTTONS_OK
B_CANCEL = gtk.BUTTONS_CANCEL
B_YES_NO = gtk.BUTTONS_YES_NO

R_YES = gtk.RESPONSE_YES
R_NO = gtk.RESPONSE_NO
R_OK = gtk.RESPONSE_OK
R_CANCEL = gtk.RESPONSE_CANCEL


def message(text, title, msg_type, msg_buttons, window=None):
    """
    Create a message box with specified type and buttons
    """
    msg = gtk.MessageDialog(window, gtk.DIALOG_MODAL, msg_type, msg_buttons,\
        text)
    msg.set_title(title)
    msg.set_markup(text) # Format Message text with pango
    msg.set_position(gtk.WIN_POS_CENTER)
    #msg.set_modal(True) #should already be a modal window
    #msg.set_keep_above(True)
    response = msg.run()
    msg.destroy()
    return response

def info(text, window=None):
    """
    Display an information message dialog with an OK button
    """
    message(text, u'Informação', M_INFO, B_OK, window)

def warning(text, window=None):
    """
    Display an error message dialog with an OK button
    """
    message(text, u'Atenção', M_WARNING, B_OK, window)

def error(text, window=None):
    """
    Display an error message dialog with an OK button
    """
    message(text, u'Erro', M_ERROR, B_OK, window)

def confirm(text, window=None):
    """
    Display a confirmation message dialog with an YES and a NO button, and
    returns True if user clicked YES and False if user cliked NO
    """
    return message(text, u'Confirma', M_QUESTION, B_YES_NO, window) == R_YES
