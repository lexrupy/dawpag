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

from dawpag.base_window import BaseWindow
from dawpag import utils as u
from dawpag.database import session
from dawpag.ui.entry import MaskEntry
from dawpag.enums import DataState, ColumnDraw
from dawpag import message as m
from dawpag.configuration import config as cfg
from dawpag.exceptions import RangeError

from sqlalchemy.orm.properties import PropertyLoader, ColumnProperty
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy import and_, DateTime, Numeric#, Boolean, Text, String, Integer,

from datetime import datetime
import decimal
import gtk

log = u.get_logger('dawpag.base_controller')

msk_masked = "__%s__mAsKeD_"

class BaseController(BaseWindow):
    # Magic Methods
    def __init__(self, search=True):
        self.name = _(u'Nome indefinido')
        self.description = _(u"Descrição indefinida")
        # The column to be defined as default on search fields combo
        self.default_search_column = 0
        # Pointer to Model
        self.model = None
        # Prefixes for widgets that holds data
        self.data_prefixes = ['ed_','ck_', 'cb_', 'bx_']
        # Current state of controller
        self.__state = DataState.BROWSING
        # Pointer to current object when editing or inserting
        self.__curr_obj = None
        self.__curr_obj_changed = False
        self.__populated_with = None
        self.__custom_signal_handlers = []
        # Variable to be set when some validation fails
        self.__has_invalid_data = False
        # List of fields to display on search treeview
        self.__search_fields = []
        # Pointer to the first widget on data panel
        self.__first_widget = None
        # Connections between widget on viwew and field on model
        self.__widget_fields = []

        self.__tree_filter = None
        self._expand_tree_after_search = False

        # Call Ancestor constructor
        super(BaseController, self).__init__('controller.base_controller',\
            'BaseWindow')
        # Button confirm starts hidden
        self.base_bt_next_confirm.hide()
        self.__setup_row_list()
        self.__connect_data_widgets()
        self.__setup_search()

        self.set_clicked_accel(self.base_bt_search, 'F5')
        self.set_clicked_accel(self.base_bt_close, 'Escape', True, 'Esc')
        self.set_clicked_accel(self.base_bt_new_cancel, 'F2')
        self.set_clicked_accel(self.base_bt_edit_goback, 'F3')
        self.set_clicked_accel(self.base_bt_next_confirm, 'F4')

        self.base_button_box.set_focus_chain([self.base_bt_next_confirm,
            self.base_bt_edit_goback,
            self.base_bt_new_cancel,
            self.base_bt_close])
        if search:
            self.do_search()


    # Protected Methods
    def __tv_data_compare(self, treemodel, iter1, iter2, field):
        """
        Data compare function used to sort the treeview when a title is clicked
        """
        obj1 = treemodel.get_value(iter1,0)
        obj2 = treemodel.get_value(iter2,0)
        v1 = getattr(obj1, field)
        v2 = getattr(obj2, field)
        if v1 > v2:
            return -1
        elif v2 > v1:
            return 1
        else: return 0


    def __tv_data_column_clicked(self, column, field):
        """
        Manage how to sort the treeview when some column is clicked
        """
        sort_id = column.get_sort_column_id()
        self.__tree_model.set_sort_func(sort_id, self.__tv_data_compare, field)


    def __setup_row_list(self):
        """
        Create the columns on TreeView, and setup the model
        To define a custom column draw for each column of search treeview
        you need to define a property named: _draw_[FIELD]_as for each
        column you want to customize, and set a ColumnDraw value.
        To Define a Totally custom drawer you need to define
        set the drawer to ColumnDraw.CUSTOM, and define a method named:
        _custom_draw_[FIELD], and it need to return a TreeViewColumn instance
        """
        default_data_funcs = ('text','toggle','pixbuf', 'progress')
        default_cell_renderers = (gtk.CellRendererText, gtk.CellRendererToggle,
            gtk.CellRendererPixbuf, gtk.CellRendererProgress)

        for ix, val in enumerate(self.__search_fields):
            field, title = val
            draw_type = ColumnDraw.TEXT
            drawer_name = '_draw_%s_as' % field
            # Check the type of column drawer
            if hasattr(self, drawer_name):
                draw_type = getattr(self, drawer_name)
            if draw_type == ColumnDraw.CUSTOM:
                custom_draw_func = "_custom_draw_%s" % field
                if hasattr(self, custom_draw_func):
                    col = getattr(self, custom_draw_func).__call__(title)
            else:
                cr = default_cell_renderers[int(draw_type)]()
                col = gtk.TreeViewColumn(title, cr)
                #col.pack_start(cr, True)
                col.set_resizable(True)
                #
                if draw_type in [ColumnDraw.TOGGLE, ColumnDraw.PIXBUF]:
                    cr.set_property('xalign', 0.0)

                # Get First the default data func
                data_func = getattr(self, "_draw_data_func_%s" %
                    default_data_funcs[int(draw_type)])

                # Check for a custom data func
                data_func_name = '_draw_data_func_%s' % field
                if hasattr(self, data_func_name):
                    data_func = getattr(self, data_func_name)
                col.set_cell_data_func(cr, data_func, field)
            col.connect('clicked', self.__tv_data_column_clicked, field)
            col.set_sort_column_id(ix)
            self.base_tv_data.append_column(col)
        self.__tree_model = self._get_tree_model()
        #self.__tree_model.set_sort_func(self.__tv_data_compare_method)
        self.base_tv_data.set_model(self.__tree_model)


    def _get_tree_model(self):
        """
        Return the default treemodel. if you want to create a TreeStore,
        override and return a treestore instance
        """
        return gtk.ListStore(object)


    def __setup_search(self):
        """
        Setup the search engine by creating field selections on select field
        combo
        """
        log.debug('Setting up the search engine')
        item_list = gtk.ListStore(str, str)
        for f, t in self.__search_fields:
            item_list.append([f, t])
        cell = gtk.CellRendererText()
        self.base_cb_fields.pack_start(cell, True)
        self.base_cb_fields.add_attribute(cell, 'text', 1)
        self.base_cb_fields.set_model(item_list)
        self.base_cb_fields.set_active(self.default_search_column)


    def __populate_view(self, force=False, **kwargs):
        """
        Populate the view widgets with data from self.__curr_obj, and set the
        object __populated_with to get track if current object has been changed
        Also can be forced by passing True for force parameter
        pass new = True to kwargs to populate with values of current object and
        its default values.
        Non Callable (Plain) defaults can be defined directly on table
        definition, other kind of defaults can be defined on controller by
        creating a method named "_default_[fieldname](self)", that returns the
        default value for field
        """
        if force or (self.__curr_obj != self.__populated_with):
            if not self.__curr_obj:
                self.__get_selected_object()
            self.__populated_with = self.__curr_obj
            for f,w in self.__widget_fields:
                value = None
                if kwargs.get('new'):
                    default_name = '_default_%s' % f
                    if hasattr(self, default_name):
                        value = getattr(self, default_name).__call__()
                    else:
                        attr = getattr(self.model, f)
                        if isinstance(attr.property, ColumnProperty):
                            col = attr.parententity.c[f]
                            if col.default:
                                arg = col.default.arg
                                # TODO: manage some callable values too
                                # For now just plain defaults
                                if not callable(arg):
                                    value = arg
                else:
                    value = getattr(self.__curr_obj, f)
                log.debug('POPULATE VIEW: populating %s with value %s'
                    % (w.name, str(value)))
                self.set_widget_value(w, None, None, value)
            log.debug('view has been populated......')
            self._after_populate_view()


    def __connect_data_widgets(self, components=None):
        """
        Get all widgets with name starting with "ed_" from view, than, crop the
        end of name and try to find a field with the same name on model, if
        found add a tuple in self.__widget_fields with the field name and a
        pointer to widget
        """
        comps = self.get_components(self.data_prefixes)
        for c in comps:
            # get the field name from comp name
            fname = c.name[3:]
            if hasattr(self.model, fname):
                self.__set_widget_required(c, self.model, fname)
                self.__widget_fields.append((fname,c))
                at = getattr(self.model, fname)
                if isinstance(c, gtk.ComboBox):
                    at = getattr(self.model, fname)
                    if isinstance(at.property, PropertyLoader):
                        cls = at.property.mapper.class_
                        log.debug('Auto Setup a ComboBox forfield "%s"' % fname)
                        self.relation_combo(c, cls, cls._display_field)
                else:
                    c.connect('focus-out-event', self.__on_get_new_data, fname)


    def __get_widget_value(self, widget):
        # Test if a masked field exists
        masked_name = msk_masked % widget.name
        if hasattr(self, masked_name):
            m = getattr(self, masked_name)
            if m.is_empty():
                return None
        if isinstance(widget, gtk.ToggleButton):
            return widget.get_active()
        elif isinstance(widget, gtk.TextView):
            buff = widget.get_buffer()
            start, end = buff.get_bounds()
            return buff.get_text(start, end)
        text = widget.get_text()
        if text == '':
            return None
        return text


    def __value_for_field(self, value, field, model=None):
        if not model:
            model = self.model
        col_type = str
        attr = getattr(model, field)
        if isinstance(attr, InstrumentedAttribute):
            col = attr.parententity.c[field]
            col_type = col.type
        # Convert value to a datetime value
        if isinstance(col_type, DateTime):
            # TODO: Identify if Column contain only time, or timestamps
            return u.str_to_date(value)
        elif isinstance(col_type, Numeric):
            return decimal.Decimal(str(value))
        log.debug(str(col_type))
        return value


    def __set_widget_required(self, widget, model, field):
        if not hasattr(model, field):
             return
        attr = getattr(model, field)
        if not isinstance(attr, InstrumentedAttribute):
            # TODO: Verify if model defines a class method [fieldname]_required
            # if yes and returns true, mark as required
            return
        if isinstance(attr.property, PropertyLoader):
            fname = '%s_id' % field
            if hasattr(model, fname):
                attr = getattr(model, fname)
                field = fname
        if isinstance(attr.property, ColumnProperty):
            col = attr.parententity.c[field]
            if not col.nullable:
                cl = "#FFF6BC"
                if isinstance(widget, gtk.Entry):
                    # TODO: Read color from configuration
                    u.widget_base_color(widget, cl)
                else:
                    u.widget_bg_color(widget, cl)
                label = self.get_widget('lb_%s' % widget.name[3:])
                if label:
                    markup = '<span weight="bold" foreground="red">* </span>%s'
                    l = len(markup)
                    old = label.get_label()
                    # Test if Already Set
                    if old[:l-2] != markup[:l-2]:
                        new = markup % old
                        self.set_label_text(label, new, True)


    def __set_field_value(self, field, value, model=None, obj=None):
        """
        Get the value from given widget.
        """
        if not model:
            model = self.model
        if not obj:
            obj = self.__curr_obj
        attr = getattr(model, field)
        col_type = str
        if isinstance(attr, InstrumentedAttribute):
            col = attr.parententity.c[field]
            col_type = col.type
        setter_method = "set_%s" % field
        if hasattr(obj, setter_method):
            log.debug("Setter method %s found for field %s. will set"
                " callling it" % (setter_method, field))
            getattr(obj, setter_method).__call__(value)
        else:
            v = getattr(obj, field)
            log.debug("Setting value new:[%s] old:[%s] for field %s" %\
                (value, v, field))
            #log.debug("Types new:[%s] old:[%s]" % (type(value), type(v)))
            setattr(obj, field, value)
        self.__curr_obj_changed = True
        self._after_set_field_value(field, value, model, obj)


    def __on_get_new_data(self, widget, event, field=None):
        """
        Callback to be assosiated with every data related widget 'focus-out'
        event, than update self.__curr_obj field related to widget if
        field value was changed

        at this time values can be validated before set on model, to
        use validation just define a method "_validate_[field](self, text)" on
        controller to validate the field field. to validate as true just return
        true from this method. to return invalid just return False. If you
        prefer you can return a string containing the error message explaining
        why the validation have failed

        example:
            def _validate_password(self, text):
                if len(text) < 4:
                    return 'password is too short'
                return True
        """
        #field = self.__get_field_from_widget(widget)
        if self.__curr_obj is None:
            return
        old_value = getattr(self.__curr_obj, field)
        new_value = self.__get_widget_value(widget)
        new_value = self.__value_for_field(new_value, field)
        log.debug("old: %s new: %s" % (str(old_value),str(new_value)))
        if u.wasunchanged(new_value, old_value):
            return
        validation_method = "_validate_%s" % field
        is_valid = True
        error = None
        if hasattr(self, validation_method):
            log.debug('will call validation method %s' % validation_method)
            error = getattr(self, validation_method).__call__(new_value)
            if isinstance(error, bool):
                is_valid = error
            else:
                is_valid = not isinstance(error, str)
        if is_valid:
            self.__set_field_value(field, new_value)
            log.debug('ON GET NEW DATA: set widget value')
            self.set_widget_value(widget, self.__curr_obj, field)
        else:
            log.debug('validation error with message: %s' % error)
            # TODO: Make invalid field visible for user, and create a list
            # of invalid fields and the error returned on param "err"
            self.__has_invalid_data = True


    def __on_get_custom_data(self, widget, event, fld=None, mdl=None, obj=None):
        """
        A Custom data getter for widgets, working with a custom field, model
        and object
        """
        if not obj:
            return
        old_value = getattr(obj, fld)
        new_value = self.__get_widget_value(widget)
        new_value = self.__value_for_field(new_value, fld, mdl)
        log.debug("old: %s new: %s" % (str(old_value),str(new_value)))
        if u.wasunchanged(new_value, old_value):
            return
        self.__set_field_value(fld, new_value, mdl, obj)
        log.debug('ON GET CUSTOM DATA: set widget value')
        self.set_widget_value(widget, obj, fld)
        # TODO: Create validation for custom data loader


    def __radio_button_toggled(self, widget, field):
        # The Value is assumed as the last part of widget name
        if widget.get_active():
            offset = 4 + len(field)
            value = widget.name[offset:]
            log.debug(value)
            self.__set_field_value(field, value)
            log.debug('Value changed to %s for field "%s" from radio' %
                (field,value))


    def __get_combo_values(self):
        """
        This method is a
        """
        for c in self.get_components('cb_'):
            fname = c.name[3:]
            if hasattr(self.model, fname):
                val = getattr(self.__curr_obj, fname)
                if val is None:
                    log.debug('workarround for combo default selection called')
                    # Call to combochanged function
                    self.__combo_changed(c, fname)


    def __combo_changed(self, combo, field):
        obj = self._get_combo_selected_object(combo)
        if obj is not None:
            setattr(self.__curr_obj, field, obj)
            self.__curr_obj_changed = True


    def __focus_first_widget(self):
        """
        Grab the focus to the first defined widted
        """
        if (self.base_nb_main.get_current_page() == 1) and self.__first_widget:
            self.__first_widget.grab_focus()


    def __set_state(self, new_state):
        """
        Set the current state of controller data
        """
        if (self._check_state(DataState.INSERTING) and
            new_state == DataState.EDITING):
            return
        if self.__state != new_state:
            self.__state = new_state
            self._update_buttons()
            self.__curr_obj_changed = False
            # LOG IF STATE SWITCHED
            # Change current page within new state
            if self._check_state([DataState.INSERTING, DataState.EDITING]):
                self.__show_data_page()
            else:
                self.__show_search_page()
            log.debug('changed state to: %s' % [
                'INSERTING', 'BROWSING','EDITING'][new_state])


    def __has_pending_data(self):
        """
        Return True if current controller has some posible pending data
        """
        return self._check_state([DataState.INSERTING, DataState.EDITING]) and \
            self.__curr_obj_changed


    def __confirm_delete(self):
        if self.__curr_obj is None:
            return False
        return self.message_confirm(_(u'Exclusão de <b>%s</b>.\nEsta operação'
            ' não poderá ser desfeita.\nDeseja continuar?' %
            u.escape_markup(self.__curr_obj.to_message())))


    def __confirm_data_loss(self):
        """
        Ask user for confirmation if some data can be lost
        """
        if self.__has_pending_data():
            return self.message_confirm(_("Todas as alterações realizadas serão"
                " perdidas.\ncontinuar?"))
        return True

    def __can_close(self):
        """
        Returns true if current window can be closed.
        To ensure that user will not loose data, will ask him to confirm if
        some data can be loss
        """
        return self.__confirm_data_loss()


    def __get_selected_object(self):
        """
        fill self.__curr_obj with object selected on treeview and return
        the cursor from treeview
        """
        cur = self.base_tv_data.get_cursor()
        iter = self.__tree_model.get_iter(cur[0])
        self.__set_state(DataState.BROWSING)
        obj = self.__tree_model.get_value(iter,0)
        cur_obj = self._hack_get_selected_object(obj)
        self.__set_current_object(cur_obj)
        return cur


    def __set_current_object(self, obj=None):
        self._before_set_object()
        self.__curr_obj = obj
        self.__curr_obj_changed = False
        self._after_set_object(obj)


    def __show_data_page(self):
        self._show_data_page()
        self.base_nb_main.set_current_page(1)
        self.__focus_first_widget()


    def __show_search_page(self):
        self._show_search_page()
        self.base_nb_main.set_current_page(0)


    def __on_entry_upper_change(self, entry):
        new_text = entry.get_text().upper()
        entry.set_text(new_text)


    def __date_entry_button_clicked(self, button, entry, callbk):
        # Create and Show Window
        from select_date_controller import SelectDateWindow
        w = SelectDateWindow()
        w.set_date(u.str_to_date(entry.get_text()))
        w.set_callback(callbk)
        w.show_window(entry, self.window)


    def __add_to_tree(self, obj, parent=None):
        """
        Add obj to current treemodel and return the iter.
        If treemodel is a TreeStore use child relation to add childs in correct
        place
        """
        if isinstance(self.__tree_model, gtk.TreeStore):
            return self.__tree_model.append(parent, [obj])
        else:
            return self.__tree_model.append([obj])


    # Private Methods

    def _connect_custom_data_widgets(self, components, model, obj):
        """
        Get all widgets with name starting with "ed_" from view, than, crop the
        end of name and try to find a field with the same name on model, if
        found add a tuple in self.__widget_fields with the field name and a
        pointer to widget
        """
        # Disconnect all first connected signals
        for w, h in self.__custom_signal_handlers:
            w.disconnect(h)
        self.__custom_signal_handlers = []
        comps = self.get_components(components)
        prefix_len = len(components[0])
        for c in comps:
            # get the field name from comp name
            fname = c.name[prefix_len:]
            if hasattr(model, fname):
                self.__set_widget_required(c, model, fname)
                at = getattr(model, fname)
                if isinstance(c, gtk.ComboBox):
                    at = getattr(model, fname)
                    if isinstance(at.property, PropertyLoader):
                        cls = at.property.mapper.class_
                        log.debug('Auto Setup a ComboBox forfield "%s"' % fname)
                        self.relation_combo(c, cls, cls._display_field)
                else:
                    log.debug('connected custom focus-out-event to %s' % c.name)
                    han = c.connect('focus-out-event',
                        self.__on_get_custom_data, fname, model, obj)
                    self.__custom_signal_handlers.append((c,han))


    def _hack_filter(self, new_filter, filter_field, model):
        """
        Override this method on controller to hack the default filter and add
        some more conditions
        """
        return new_filter


    def _hack_get_selected_object(self, obj):
        """
        Override this to hack and set another object different to the main
        object at treeview. in some cases it is necessary to set the edittable
        object really a master of a child object
        """
        return obj


    def _draw_data_func_text(self, column, cell, model, iter, field_name):
        """
        Get value from model field, to display as a text on list
        call a dinamyc method _format_[fieldname](text, obj) on class to
        get value properly formated
        """
        obj = model.get_value(iter, 0)
        value = getattr(obj, field_name)
        formatter_name = '_format_%s' % field_name
        if value is not None:
            if hasattr(self, formatter_name):
                value = getattr(self, formatter_name).__call__(value)
        else:
            value = '-'
        cell.set_property("text", value)


    def _draw_data_func_toggle(self, column, cell, model, iter, field_name):
        """
        Get a valud from model field to display as a CheckButton on list
        """
        obj = model.get_value(iter, 0)
        value = getattr(obj, field_name)
        cell.set_property("active", value)


    def _draw_data_func_pixbuf(self, column, cell, model, iter, field_name):
        """
        Get a valud from model field to display as a PixBuf on list
        it will only work to Boolean values like Toggle. if you want to
        use for other values, you will need to create your own data func
        by declaring the func as:
         _draw_data_func_[FIELD](self, column, cell, model, iter, field_name)
        on your controller
        """
        obj = model.get_value(iter, 0)
        value = getattr(obj, field_name)
        if value is None:
            pb = gtk.STOCK_REMOVE
        elif isinstance(value, bool):
            pb = gtk.STOCK_NO
            if value:
                pb = gtk.STOCK_YES
        else:
            raise ValueError('You can only use default ColumnDraw.PIXBUF '
                'for boolean columns. Column:"%s" is not a boolean column. to '
                'use with column other types you will need to define a method:'
                ' _draw_data_func_%s(self, col, cell, model, iter, field_name) '
                'at your controller' % (field_name,field_name))
        cell.set_property('stock_id', pb)


    def _draw_data_func_progress(self, column, cell, model, iter, field_name):
        """
        Get a valud from model field to display as a ProgressBar on list
        it will only work to numeric values between 0 and 100
        """
        obj = model.get_value(iter, 0)
        value = getattr(obj, field_name)
        if value is None:
            value = 0
        elif not isinstance(value, (int, float, long)):
            raise ValueError('You can only use default ColumnDraw.PROGRESS '
                'for numeric columns. Column:%s is not a numeric column. to '
                'use with column types you will need to define a method:'
                ' _draw_data_func_%s(self, col, cell, model, iter, field_name) '
                'at your controller' % (field_name,field_name))
        if not (value in range(100)):
            raise RangeError('Value is out of range. Value need to be between'
                ' 0 and 100. Provided:%d Field:%s'% (value, field_name))
        cell.set_property('value', value)


    # override
    def _init_child_window(self):
        # Get the glade file for controller data
        w_tree = gtk.glade.XML(u.get_glade_file(self.__module__))
        # Get the toplevel window with name of current controller
        dw = w_tree.get_widget(self.__class__.__name__)
        place = self.dw_placeholder.get_parent()
        place.remove(self.dw_placeholder)
        # Get the child object from toplevel window
        dw_child = dw.get_child()
        # Remove child object from parent window to allow reparent
        dw.remove(dw_child)
        place.add(dw_child) # Reparent
        # Connect the events of current file
        self._add_component_tree(w_tree)
        self._connect_events(w_tree)


    # override
    def _update_view(self):
        """
        Update View Object just before window shown
        """
        self.base_lb_title.set_markup(
            """<span size="xx-large"><b>%s</b></span>""" % self.__class__.name)
        self.window.set_title(self.__class__.name)


    def _check_state(self, state):
        """
        Check if given state(s) matches with current controller data state
        """
        if isinstance(state, list):
            return self.__state in state
        return self.__state == state


    def _switch_new_cancel_button_state(self):
        """
        Switch the state of button New/Cancel.
        Change the button label and image to reflect current state
        """
        if self._check_state([DataState.INSERTING, DataState.EDITING]):
            text = _('C_ancelar')
            img = gtk.STOCK_NO
        else:
            text =  _('_Novo')
            img = gtk.STOCK_NEW
        self.set_button_image_and_text(self.base_bt_new_cancel, img, text)


    def _switch_next_confirm_button_state(self):
        """
        Switch the state of button Next/Confirm according to current data state
        """
        if self._check_state([DataState.INSERTING, DataState.EDITING]):
            self.base_bt_next_confirm.show()
        else:
            self.base_bt_next_confirm.hide()


    def _switch_edit_goback_button_state(self):
        """
        Switch the state of button Edit/GoBack according to current data state
        """
        if self._check_state([DataState.INSERTING, DataState.EDITING]):
            self.base_bt_edit_goback.hide()
        else:
            self.base_bt_edit_goback.show()


    def _get_search_model(self):
        """
        Override this method to define another model to perform the query
        """
        return self.model


    def _get_query_joins(self):
        """
        Override this method to define joins to you queries
        """
        return []


    def _get_combo_active_model(self, combo):
        """
        Return the active index, and the model of given combobox
        """
        return (combo.get_active(), combo.get_model())


    def _get_combo_selected_object(self, combo):
        """
        Return the selected object or None, for the given combo.
        Note: this combo need to be a model with the object at first column
        """
        ix, mdl = self._get_combo_active_model(combo)
        if ix >= 0:
            return mdl[ix][0]
        return None


    def _update_buttons(self):
        """
        Update Buttons by current data edit state
        """
        self._switch_new_cancel_button_state()
        self._switch_next_confirm_button_state()
        self._switch_edit_goback_button_state()


    def _before_set_object(self):
        """
        Override this to acces the moment just before current object is set
        """
        pass


    def _after_set_object(self, obj):
        """
        Override this to acces the moment just after current object is set and
        get the new setted object
        """
        pass


    def _after_populate_view(self):
        """
        Override this to acces the moment just after current object has been
        sent to view widgets
        """
        pass


    def _after_set_field_value(self, field, value, model, obj):
        """
        Override this to access moment just after set a value property on an
        object
        """
        pass


    def _before_new(self):
        """
        Override this method to get access to make some stuff just before the
        new object is created
        """
        log.debug('[callback] %s: _before_new' % self.__class__.__name__)


    def _after_new(self, obj):
        """
        Override this method to get access to current_object after new object
        is created for insert
        """
        log.debug('[callback] %s: _after_new' % self.__class__.__name__)


    def _after_edit(self, obj):
        """
        Override this method to get access to current_object after new object
        is created for insert
        """
        log.debug('[callback] %s: _after_edit' % self.__class__.__name__)


    def _before_cancel(self, obj):
        """
        Override this method to get access to current object before cancel and
        decide if continue canceling or abort cancelig by returning True or
        False
        """
        log.debug('[callback] %s: _before_cancel' % self.__class__.__name__)
        return True


    def _after_cancel(self, obj):
        """
        Override this method to get access to current_object after cancel action
        is performed.
        if last state was an insert, obj will be None, else will contain the
        original object with any modifications canceled
        """
        log.debug('[callback] %s: _after_cancel' % self.__class__.__name__)


    def _before_save(self, obj):
        """
        This method is called before a record is saved to database and takes the
        object. to continue saving you need to return True, to abort saving
        just return False
        """
        log.debug('[callback] %s: _before_save' % self.__class__.__name__)
        return True


    def _after_save(self, obj):
        """
        This method is called after the record is saved to database
        """
        log.debug('[callback] %s: _after_save' % self.__class__.__name__)


    def _show_data_page(self):
        """
        Override this method to take the event occurred on data page is shown
        """
        log.debug('[callback] %s: _show_data_page' % self.__class__.__name__)


    def _show_search_page(self):
        """
        Override this method to take the event occured on search page is shown
        """
        log.debug('[callback] %s: _show_data_page' % self.__class__.__name__)


    def _remove_object(self, obj, expunge_only=True):
        """
        Remove given object from session.
        if expunge_only is False, and object is not a new object, delete from
        database
        """
        if obj in session.new:
            session.expunge(obj)
        elif expunge_only:
            return # Only expunge... return from here
        else: # supposed to be already persisted
            session.delete(obj)


    # Public Methods

    # FIXME: Maybe its not necessary if sqlalchemy provide some adjacency list
    # facility
    def set_tree_relation(self, column, relation):
        """
        Set the column agrupator for a tree representation as the given column
        """
        self.__tree_filter = ('%s IS NULL' % column, relation)


    def message_info(self, message):
        """
        Display an information message belongs to current window
        see also dawpag.message.info method
        """
        m.info(message, self.window)


    def message_warning(self, message):
        """
        Display a warning message belongs to current window
        see also dawpag.message.warning method
        """
        m.warning(message, self.window)


    def message_error(self, message):
        """
        Display an error dialog belongs to current window
        see also dawpag.message.error method
        """
        m.error(message, self.window)


    def message_confirm(self, message):
        """
        Display a confirmation dialog belongs to current window
        see also dawpag.message.confirm method
        """
        return m.confirm(message, self.window)


    def current_object(self):
        return self.__curr_obj


    def do_close(self):
        """
        Close current Window
        """
        # Before Close remove the current object from session if a new object
        self._remove_object(self.__curr_obj)
        self.window.destroy()


    def do_new(self):
        """
        Create a new object to be inserted in database
        """
        log.debug('DO_NEW')
        self._before_new()
        new_obj = self.model()
        session.add(new_obj)
        self.__set_current_object(new_obj)
        self.__populate_view(new=True)
        self.__set_state(DataState.INSERTING)
        self._after_new(self.__curr_obj)


    def do_edit(self):
        """
        Create a new object to be inserted in database
        """
        log.debug('DO_EDIT')
        self.__populate_view()
        self.__set_state(DataState.EDITING)
        self._after_edit(self.__curr_obj)


    def do_cancel(self):
        """
        Cancel the current object insert or editing
        """
        if self.__confirm_data_loss():
            if self._before_cancel(self.__curr_obj):
                if self._check_state(DataState.INSERTING):
                    self._remove_object(self.__curr_obj)
                    self.__set_current_object()
                elif self._check_state(DataState.EDITING):
                    if session.dirty:
                        session.rollback()
                        session.refresh(self.__curr_obj)
                        self.__populate_view(True)
                self.__set_state(DataState.BROWSING)
                self._after_cancel(self.__curr_obj)


    def do_save(self):
        """
        Save current modifications
        """
        log.debug('DO_SAVE')
        if self._before_save(self.__curr_obj):
            #try:
            redo_search = False
            if self._check_state(DataState.INSERTING):
                session.add(self.__curr_obj)
                if isinstance(self.__curr_obj, self._get_search_model()):
                    iter = self.__add_to_tree(self.__curr_obj)
                    path = self.__tree_model.get_path(iter)
                    self.base_tv_data.set_cursor(path)
                else:
                    redo_search = True
            session.commit()
            self.__set_state(DataState.BROWSING)
            if redo_search:
                self.do_search()
            self._after_save(self.__curr_obj)
            self._update_buttons()
            #except:
                # TODO: Raise the correct exception
            #    log.debug('pau ao salvar')


    def do_delete(self, confirm=True):
        """
        Remove the current object from database, and only if not inserting a new
        object
        """
        log.debug('DO_DELETE')
        if not self._check_state(DataState.INSERTING):
            if confirm and (not self.__confirm_delete()):
                return
            path, ot = self.__get_selected_object()
            iter = self.__tree_model.get_iter(path)
            self.__tree_model.remove(iter)
            session.delete(self.__curr_obj)
            self.__set_current_object()
            session.commit()
            # Set position to previous row
            row = path[0]-1
            if row <=0:
                row = 0
            self.base_tv_data.set_cursor((row,))


    def do_search(self):
        """
        Execute a database search based on current search settings
        """
        log.debug('DO_SEARCH')
        new_filter = None
        filter_field = None
        query_model = self._get_search_model()
        search_text = self.base_ed_search_field.get_text()
        if not u.isempty(search_text):
            cb_model = self.base_cb_fields.get_model()
            cb_active = self.base_cb_fields.get_active()
            if cb_active >= 0:
                field = cb_model[cb_active][0]
                fld_func = '_search_field_%s' % field
                if hasattr(query_model, fld_func):
                    filter_field = getattr(query_model, fld_func).__call__()
                else:
                    filter_field = getattr(query_model, field)
                new_filter=filter_field.like('%'+search_text+'%')
                # If user want to hack the current filter on controller
        new_filter = self._hack_filter(new_filter, filter_field,
            query_model)
        self.query_data(filter_data=new_filter)
        self.display_query_data()


    def query_data(self, filter_data=None):
        """
        Query database from data and filter vy filter_data if filter is not none
        """
        query_model = self._get_search_model()
        query = session.query(query_model)
        for j in self._get_query_joins():
            query = query.join(j)
        if filter_data:
            # FIXME: Workarround to get tree representation
            # If has a treefilter add the filter to filter
            if self.__tree_filter:
                filter_data = and_(filter_data, self.__tree_filter[0])
            query = query.filter(filter_data)
        else:
            # FIXME: Improve DRY query = query.filter is declared twice
            if self.__tree_filter:
                query = query.filter(self.__tree_filter[0])

        self.__query_data = query.order_by(
            query_model.id).limit(cfg.get('database.query_limit'))
        return self.__query_data


    def set_widget_value(self, w, obj=None, field=None, value=None):
        # Get the value if not passed
        if obj:
            value = getattr(obj, field)
        # A boolean Value should be set to a togle button
        if isinstance(w, gtk.ToggleButton):
            w.set_active(value or False)
        # A Combobox should select correct object by iteracting
        elif isinstance(w, gtk.ComboBox):
            mdl = w.get_model()
            if mdl:
                it = mdl.get_iter_first()
                while it:
                    obj = mdl.get_value(it,0)
                    if obj == value:
                        w.set_active_iter(it)
                        break
                    it = mdl.iter_next(it)
        elif isinstance(w, gtk.TextView):
            buff = w.get_buffer()
            buff.set_text(str(value or ''))
        elif isinstance(w, (gtk.HBox, gtk.VBox)):
            fname = w.name[3:]
            radio_button = self.get_widget('rb_%s_%s' % (fname, value))
            if radio_button:
                radio_button.set_active(True)
        else:
            # TODO: Move this format to _get_formated_value
            if isinstance(value, datetime):
                value = u.date_to_str(value)
            else:
                log.debug('FORMATED')
                value = self._get_formated_value(w.name, value)
            log.debug('WILL SET TEXT FOR %s %s' % (w.name, value))
            w.set_text(value)


    def display_query_data(self):
        """
        Display on TreeView the data got by query_data method and stored on
        self.__query_data
        """
        ## inner adjacency list generator for trees ----------------------------
        def add_objects(parent, obj, relation):
            rel = getattr(obj, relation)
            parent_iter = self.__add_to_tree(obj, parent)
            for child in rel:
                add_objects(parent_iter, child, relation)
        ##----------------------------------------------------------------------
        # Test if controller defines a tree_group_column, if yes, track parent
        # and child object to get a treeview behavior
        relation = None
        if self.__tree_filter:
            relation = self.__tree_filter[1]
        self.__tree_model.clear()
        if self.__query_data.count() > 0:
            if relation is not None:
                func = lambda o: add_objects(None, o, relation)
            else:
                func = lambda o: self.__add_to_tree(o)
            [func(obj) for obj in self.__query_data]
            # set the first item of treeview
            self.base_tv_data.set_cursor((0,))


    def options_box(self, box, field):
        """
        Setup an option list based in a box with Radio Buttons inside
        """
        for c in box.get_children():
            if isinstance(c, gtk.RadioButton):
                c.connect('toggled', self.__radio_button_toggled, field)
                log.debug('connected group changed callback for %s' % field)


    def gtkEntry(self, name=None, _max=0):
        ret = gtk.Entry(_max)
        ret.set_name(name)
        return ret


    def date_entry(self, entry, resize=False, custom_button=None, callbk=None):
        """
        Create a mask_entry for date values.
        Need a button [entryname]_button to associate
        """
        self.mask_entry(entry, cfg.get('mask.date'))
        if resize:
            entry.set_size_request(90, -1)
        button = custom_button
        if not button:
            if hasattr(self, '%s_button' % entry.name):
                button = getattr(self, '%s_button' % entry.name)
        if button:
            button.connect('clicked', self.__date_entry_button_clicked, entry,
                callbk)


    # Override
    def options_combo(self, combo, options, default=0, autoconnect=True):
        """
        Override to provide automatic change track
        """
        combo = super(BaseController, self).options_combo(combo, options,
            default)
        # If need to connect direct to auto changed with field
        if autoconnect:
            field_name = combo.name[3:]
            combo.connect('changed', self.__combo_changed, field_name)


    def mask_entry(self, entry, mask):
        """
        Create an object wrapper to mask the entry text
        if wrapper has already been created, just change the masked text
        """
        obj_name = msk_masked % entry.name
        me = None
        if hasattr(self, obj_name):
            log.info('object %s already found. reseting mask' % obj_name)
            me = getattr(self, obj_name)
            me.set_mask(mask)
        else:
            me = MaskEntry(entry)
            me.set_mask(mask)
            setattr(self, obj_name, me)
        return me


    def upper_entry(self, entry):
        """
        Make text typed on given entry always uppercase
        """
        entry.connect("changed", self.__on_entry_upper_change)


    def relation_combo(self, combo, model, field, default=None):
        """
        Create a combobox object related to a foreign model
        """
        log.debug('Setting a combobox connected to model "%s" and field "%s"' %
            (model.__name__, field))
        field_name = combo.name[3:]
        item_list = gtk.ListStore(object, str)
        obj_list = session.query(model).all()
        default_id = -1
        for ix, obj in enumerate(obj_list):
            item_list.append([obj, getattr(obj, field)])
            if default == obj:
                default_id = ix
        cell = gtk.CellRendererText()
        combo.pack_start(cell, True)
        combo.add_attribute(cell, 'text', 1)
        combo.set_model(item_list)
        # Default is checked and defined before connect changed event o avoid
        # unwanted event hand
        if default:
            combo.set_active(default_id)
        combo.connect('changed', self.__combo_changed, field_name)


    def set_search_fields(self, field_list):
        """
        Set the list of fields to appear on search results (list)
        field_list can be a list of strings or tuples in format
        (fieldname, fieldtitle), if is a list of string, each item will be
        humanized and inserted in internal field list as a tuples in format
        (fieldname, humanizedfieldname)
        """
        for field in field_list:
            new_field = None
            if isinstance(field, tuple):
                new_field = field
            elif isinstance(field, str):
                new_field = (field, u.humanize(field))
            else:
                raise TypeError('field need to be a string or a tuple')
            self.__search_fields.append(new_field)


    def set_first_widget(self, widget):
        """
        Set the first widget on form to be focused when new button is pressed
        """
        self.__first_widget = widget


    # Event Handlers

    def on_base_tv_data_row_activated(self, treeview, path, column, data=None):
        """
        On double click on treeview row change to data page on notebook
        """
        self.do_edit()


    def on_base_tv_data_cursor_changed(self, data=None):
        """
        The Cursor of TreeView was changed.
        get tue cursor, get the object related and set self.__curr_obj
        """
        self.__get_selected_object()


    def on_base_tv_data_button_press_event(self, treeview, event, data=None):
        """
        Catch the mouse button press event for treeview to popup a context
        menu with some usefull options
        """
        if event.button == 3:
            self.base_mnu_tv_data.popup(None, None, None, event.button,
                event.time)


    def on_base_mnu_tv_data_delete_activate(self, widget, data=None):
        """
        Clicked on delete option on context menu
        """
        self.do_delete()


    def on_base_tv_data_key_press_event(self, widget, event, data=None):
        """
        Manage the key-press-event for treeview to get DELETE signal
        """
        if u.get_key(event) == 'Delete':
            self.do_delete()
            return


    def on_base_ed_search_field_key_press_event(self, widget, event, data=None):
        """
        Key press event of search box
        """
        if u.get_key(event) == 'Return':
            self.do_search()


    def on_base_bt_search_clicked(self, widget, data=None):
        """
        Call when buton search is clicked
        """
        self.do_search()


    def on_base_bt_close_clicked(self, data=None):
        """
        Close the Window
        """
        if self.__can_close():
            self.do_close()


    def on_BaseWindow_delete_event(self, w, e, d=None):
        if self.__can_close():
            log.debug('delete event')
            self.do_close()
            return False # False mean yes, we can close
        return True


    def on_base_bt_edit_goback_clicked(self, data=None):
        """
        On click at Edit/Go-back button
        """
        self.do_edit()


    def on_base_bt_new_cancel_clicked(self, widget, data=None):
        """
        Action performed when user click on New/Cancel button
        """
        if self._check_state(DataState.BROWSING):
            self.do_new()
            #self.__focus_first_widget()
        elif self._check_state([DataState.INSERTING, DataState.EDITING]):
                self.do_cancel()


    def on_base_bt_next_confirm_clicked(self, widget, data=None):
        """
        Call when button next/confirm is clicked
        """
        # FIXME: this is a workarround to get value from combos if field is not
        # yet filled from combo value
        self.__get_combo_values()
        self.do_save()