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

from base_controller import BaseController
from dawpag import utils as u
from dawpag.enums import DataState
import gtk

log = u.get_logger('dawpag.wizard_controller')

class WizardController(BaseController):
    # Magic Methods
    def __init__(self):
        # Wizard steeps
        self.__current_step = 0
        self.__step_map = None
        self.__wizard_widget = None
        self.wizard_widget = 'nb_wizard'
        # Call Ancestor constructor
        super(WizardController, self).__init__()
        self.__setup_wizard()
        self._set_clicked_accel(self.base_bt_edit_goback, 'ctrl-Left', False)
        self._set_clicked_accel(self.base_bt_next_confirm, 'ctrl-Right', False)

    def __setup_wizard(self):
        """
        Get the wizard Notebook widget from view
        """
        if hasattr(self, self.wizard_widget):
            self.__wizard_widget = getattr(self, self.wizard_widget)
        else:
            raise Exception(u'The provided wizard widget name "%s" does not'
                ' exist' %self.wizard_widget)
        self.__wizard_widget.set_show_tabs(False)
        self._update_buttons()

    def __is_first(self, step=None):
        """
        Return True if given step is the first step or False otherwise
        """
        if not step:
            step = self.__current_step
        return step == 0

    def __get_step_dict(self, step=None):
        """
        Return a dict containing (step, page) for given step. if not step given
        return the current step. in return dict, step is the index of step and
        page is the index of notebook wizard page associated with that step
        """
        if not step:
            step = self.__current_step
        return filter(lambda x: x[0] == step, self.__step_map)[0]

    def __is_last(self, step=None):
        """
        Return True if given step is the last step or False otherwise
        """
        if not step:
            step = self.__current_step
        if self.__step_map:
            obj = self.__get_step_dict(step)
            return self.__step_map.index(obj) == (len(self.__step_map)-1)
        else:
            return step == (self.__wizard_widget.get_n_pages()-1)

    def __get_wizard_page(self):
        """
        Return the page number to be set on wizard_widget notebook correspondent
        to current_step
        """
        if self.__step_map:
            obj = obj = self.__get_step_dict()
            return obj[1]
        return self.__current_step

    # Protected Methods
    def __next(self):
        """
        Return the next step number
        """
        if self.__step_map:
            return self.__step_map[self._current_step+1][1]
        return self.__wizard_widget.get_current_page()+1

    def __prev(self):
        """
        Return the previous step number
        """
        if self.__step_map:
            return self.__step_map[self._current_step-1][1]
        return self.__wizard_widget.get_current_page()-1

    def __validate_step(self):
        """
        Validate current step based on validation methods on controller
        you can define a Generic validator method with signature:
        _step_validate(self, step)  this method will take the current step and
        you can return True for valid or False for invalid given step
        opcionally you can define one method for each step with signature:
        _step_validate_X(self), where X is the number of step you want to
        validate, than just return True or False to get that step Valid or
        Invalid
        Both can be defined, so validate_step will be called first.
        If both defined both must return True to step be considerated valid
        """
        v1, v2 = True, True
        if hasattr(self, '_step_validate'):
            log.debug("Generic validation found will call for "
                "step %d" % self.__current_step)
            v1 = getattr(self, '_step_validate').__call__(self.__current_step)
        step_validator_method = '_step_validate_%d' % self.__current_step
        if hasattr(self, step_validator_method):
            log.debug("Target validation found for step %d will "
                "call" % self.__current_step)
            v2 = getattr(self, step_validator_method).__call__()
        return v1 and v2

    # Private Methods

    # Override
    def _switch_edit_goback_button_state(self):
        """
        Switch the state of Edit/GoBack Button
        Change the button label and image to reflect current state
        """
        if not self._check_state([DataState.INSERTING, DataState.EDITING]):
            text = _(u'Alt_erar')
            img = gtk.STOCK_EDIT
            self.base_bt_edit_goback.set_sensitive(True)
        else:
            text = _(u'A_nterior')
            img = gtk.STOCK_GO_BACK
            enabled = not self.__is_first()
            self.base_bt_edit_goback.set_sensitive(enabled)
        self.set_button_image_and_text(self.base_bt_edit_goback, img, text)

    # Override
    def _switch_next_confirm_button_state(self):
        """
        Switch the state of button Next/Confirm.
        Change the button label and image to reflect current state
        """
        super(WizardController, self)._switch_next_confirm_button_state()
        if self.__is_last():
            text = _(u'C_onfirma')
            img = gtk.STOCK_YES
        else:
            text = _(u'Pró_ximo')
            img = gtk.STOCK_GO_FORWARD
        self.set_button_image_and_text(self.base_bt_next_confirm, img, text)

    # Public Methods

    def map_steps(self, step_list):
        """
        Set the current step map to given step_list, this is used to determine
        the next step. If steps not mapped, Wizard will use the natural order of
        Noteboook pages.
        Note: steps start from index 0
        Example:
        Given a Wizard with 3 steps, and you need to Go across, step 1, than 2,
        than 3, than back to 1 to confirm some data you will map this way:
            map_steps([0,1,2,0])
        """
        self.__step_map = []
        for ix,step in enumerate(step_list):
            self.__step_map.append((ix,step))
        log.debug('steeps mapped:\n MAP: %s' % str(self.__step_map))

    def current_step(self, step=None):
        """
        Return true if given step is the current step.
        if no step given just return the current step index
        """
        if step:
            return self.__current_step == step
        return self.__current_step

    def next(self):
        """
        If current step is valid, than move to next step, otherwise do nothing
        """
        if self.__validate_step():
            self.__current_step = self.__next()
            self.__wizard_widget.set_current_page(self.__get_wizard_page())
            self._update_buttons()

    def prev(self):
        """
        Go back to prior step and update buttons
        """
        self.__current_step = self.__prev()
        self.__wizard_widget.set_current_page(self.__get_wizard_page())
        self._update_buttons()

    # Event Handlers
    def on_base_bt_edit_goback_clicked(self, widget, data=None):
        """
        Action performed when user clicked at Edit/Goback button. it check if
        some data is currently in EDIT or INSERT mode. if Yes, go to prev()ious
        step otherwise call ansestor method to go to EDIT mode
        """
        if not self._check_state(DataState.INSERTING, DataState.EDITING):
            super(WizardController, self).on_base_bt_edit_goback_clicked(widget)
        else:
            self.prev()

    def on_base_bt_next_confirm_clicked(self, widget, data=None):
        """
        Action performed when user clicked at Next/Confirm button. If current
        step is the last step, try to finalize the Wizard by validating the step and calling ancestor method that will save data on database.
        if is not the last step, go to next() step
        """
        if self.__is_last():
            if self.__validate_step():
                # Call ancestor method
                super(WizardController,
                    self).on_base_bt_next_confirm_clicked(widget)
        else:
            self.next()