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

import gtk, gtk.glade
import dawpag.utils as u
from dawpag import basedir
#import gtk.keysyms as gtkey


log = u.get_logger('dawpag.base_window')

class BaseWindow(object):
    """
    A simple window based in a glade file
    """
    # Magic Methods
    def __init__(self, glade_file=None, window_name=None):
        """
        Initialize the base window Object, loading the glade file based on
        module name, then call _initialize() to take place of subclasses
        initialization. After it, connect all events starting with "on_"
        with their correspondents at glade file, and also map the gtk_main_quit
        event of glade file to gtk.main_quit event
        """
        # Store a list of widget trees in this Window
        self.__w_trees = []
        self.__accelerators = []

        # List of tuples containing widget name and format
        self.__widget_formats = []

        if glade_file is not None:
            g_file = glade_file
        else:
            g_file = self.__module__
        w_tree = gtk.glade.XML(u.get_glade_file(g_file))
        if window_name is not None:
            w_name = window_name
        else:
            w_name = self.__class__.__name__
        self.window = w_tree.get_widget(w_name)
        self.window.connect('destroy', self.__on_window_destroy)

        # Setup Accelerators
        self._accel_group = gtk.AccelGroup()
        self.window.add_accel_group(self._accel_group)

        self._add_component_tree(w_tree)
        #self._setup_model()
        self._init_child_window()
        self._initialize()
        self._connect_events(w_tree)
        self._update_view()


    def __parse_accelerator(self, accelerator):
        """
        parse the accelerator for easy parsing and internal use.
        Accelerator Format Examples:
            (ctrl - alt -s)
            (s)
            (alt - a)
        """
        if not (accelerator): return None
        accel_list = [accel.strip() for accel in accelerator.split("-")]
        accel = []
        for item in accel_list:
            if item in("Control", "control", "Ctrl", "ctrl"):
                accel.append("ctrl")
            elif item in ("Alt", "alt"):
                accel.append("alt")
            elif item in ("Shift", "shift", "shft"):
                accel.append("shift")
            else:
                accel.append(item)
        # Remove duplicate elements
        accel = set(accel)
        accel = list(accel)
        accel.sort()
        return tuple(accel)


    def __get_accel_mods_key(self, accel):
        mods = 0
        ac_list = ['ctrl', 'shift', 'alt']
        msk_list = [gtk.gdk.CONTROL_MASK, gtk.gdk.SHIFT_MASK, gtk.gdk.MOD1_MASK]
        accels = list(accel)
        for ix, ac in enumerate(ac_list):
            if ac in accels:
                if mods:
                    mods = mods + msk_list[ix]
                else:
                    mods = msk_list[ix]
                accels.pop(ix)
        # Should be remained just the key
        if len(accels) == 1:
            key = gtk.gdk.keyval_from_name(accels[0])
            return (mods, key)
        else:
            raise Exception('Invalid accelerator. must have exatly one '\
                'function or literal key')


    def _remove_accelerator(self, widget, accelerator):
        accel_tuple = self.__parse_accelerator(accelerator)
        accel_mods, accel_key = self.__get_accel_mods_key(accel_tuple)
        if accel_tuple in self.__accelerators:
            widget.remove_accelerator(self._accel_group, accel_key, accel_mods)
            self.__accelerators.pop(self.__accelerators.index(accel_tuple))


    def __getattr__(self, key):
        """
        Allow glade widgets to be accessed as self.[widgetname]
        """
        widget = self.get_widget(key)
        if widget:
            setattr(self, key, widget)
            return widget
        raise AttributeError(key)


    def __on_window_destroy(self, window, data=None):
        """
        Event Connected to window event. if you want do do some finalization
        override, see also _finalize_all method
        """
        self._finalize_all()
        # TODO: Is this stuff necessary for Garbadge Collect?
        self = None


    # Private Methods

    # Protected Methods

    def _set_widget_formats(self, format_list):
        """
        Defines the format list for widgets. this format is used after user type
        data into widget, and when data is got from database to widget
        """
        self.__widget_formats = format_list


    def _get_formated_value(self, widget_name, value):
        format = filter(lambda x: x[0]==widget_name, self.__widget_formats)
        if value is None:
            return ''
        if format:
            type_ = format[0][2]
            format = format[0][1]
            value = format % type_(value)
        return str(value)

    def _add_accelerator(self, widget, accelerator, signal):
        accel_tuple = self.__parse_accelerator(accelerator)
        if accel_tuple in self.__accelerators:
            from dawpag.exceptions import DuplicateAcceleratorError
            raise DuplicateAcceleratorError('Accelerator %s already'\
                ' defined' % str(accel_tuple))
        accel_mods, accel_key = self.__get_accel_mods_key(accel_tuple)
        widget.add_accelerator(signal, self._accel_group, accel_key, accel_mods,
            gtk.ACCEL_MASK)
        self.__accelerators.append(accel_tuple)

    def _add_component_tree(self, tree):
        """
        Add a component tree to list of component trees, after it, all widgets
        inside that tree can be accessed by "self.[widget_name]"
        """
        self.__w_trees.append(tree)


    def _init_child_window(self):
        """
        Override this method to initialize the child window container
        """
        pass


    def _update_view(self):
        """
        Method called at end of window initialization, override this to update
        stuff like window titles and label texts
        """
        pass


    def _finalize_all(self):
        """
        Method called on window is destroyed. override this to add some
        finalization stuff on window destroy
        """
        pass


    def _connect_events(self, tree):
        """
        Connect event signals to handlers
        """
        handlers = {}
        for h in filter(lambda x:x.startswith("on_"), dir(self.__class__)):
            handlers[h] = getattr(self, h)
            #log.debug('connecting event handler: %s' % str(h))
        handlers['gtk_main_quit'] = gtk.main_quit
        tree.signal_autoconnect(handlers)


    def _clear_components(self, *prefixes):
        """
        Clear all components on form prefixed by "ed_" and "_ed_"
        """
        for prefix in prefixes:
            for c in self.get_components(prefix):
                #log.debug('cleaning component: %s' % c.name)
                if isinstance(c, gtk.ComboBox):
                    c.set_active(-1)
                elif isinstance(c, gtk.ToggleButton):
                    c.set_active(False)
                elif isinstance(c, gtk.TextView):
                    buff = c.get_buffer()
                    buff.set_text('')
                else:
                    c.set_text('')


    # Public Methods

    def get_widget(self, widget_name):
        """
        Return the widget from WidgetTree
        """
        for t in self.__w_trees:
            widget = t.get_widget(widget_name)
            if widget:
                return widget
        return None


    def get_components(self, prefix):
        """
        Get all components from view prefixed by prefix
        """
        components = []
        if not isinstance(prefix, list):
            prefix = [prefix]
        for t in self.__w_trees:
            for p in prefix:
                wlist = t.get_widget_prefix(p)
                if wlist:
                    components.extend(wlist)
        return components


    def set_button_text(self, btn, text, underlines=True):
        """
        Given a Button, a text and if need to use underlines, find the
        label for button and set his text to text.
        """
        # TODO: Also handle simple buttons (with no label inside)
        lbl = getattr(self, '%s_label' % btn.name)
        if lbl:
            self.set_label_text(lbl, text, underlines)


    def set_clicked_accel(self, btn, accel, display_ac=True, accel_alias=None):
        self._add_accelerator(btn, accel, 'clicked')
        if display_ac:
            display_name = "%s_label_accel" % btn.name
            display_label = self.get_widget(display_name)
            if display_label is not None:
                if accel_alias is None:
                    accel_alias = accel
                display_label.set_text("(%s)" % accel_alias)


    def set_label_text(self, label, text, underlines=True):
        # Ignore if text is the same already set
        if label.get_text() == text:
            return
        if underlines:
            label.set_markup_with_mnemonic(text)
        else:
            label.set_text(text)


    def options_combo(self, combo, options, default=0):
        """
        Create a Option List with a combobox.
        options need to be a list of tuples containing the real value and
        the option title.
        example:
            options_combo(self.combo, [('male', 'Male'), ('female', 'Female')])
        """
        log.debug('Setting up the option combo')
        item_list = gtk.ListStore(str, str)
        for f, t in options:
            item_list.append([f, t])
        cell = gtk.CellRendererText()
        combo.pack_start(cell, True)
        combo.add_attribute(cell, 'text', 1)
        combo.set_model(item_list)
        combo.set_active(default)
        return combo


    def set_button_image(self, btn, image, stock=True):
        """
        Given a Button, an image and if need to use stock_id, find the
        image for button and set his image to image
        """
        # TODO: Also handle images from pixmaps
        img = getattr(self, '%s_image' % btn.name)
        if stock:
            # Ignore if image is the same already set
            if img.get_stock()[0] == image:
                return
            img.set_from_stock(image, gtk.ICON_SIZE_BUTTON)
        else:
            # TODO: Implement
            raise NotImplementedError


    def set_button_image_and_text(self, btn, img, txt, stk=True, under=True):
        """
        Set button image and text at the same time of the given button
        btn: button to set image
        img: image to set
        txt: text to set
        stk: if True img need to be a stock_id and set image from stock
        under: if True set text with underline accelerators activated
        """
        self.set_button_image(btn, img, stk)
        self.set_button_text(btn, txt, under)


    def show(self, parent=None):
        """
        Show current window object, referenced on GladeFile with name equals
        tho self.__class__.__name__
        """
        # For some reason if two windows are modal, the last not stay on top of
        # previous
        if parent:
            self.window.set_transient_for(parent)
        self.window.show()


    def on_key_press_next_control(self, widget, event, data=None):
        """
        Generic key event to move to next control with the same container on
        Return key is pressed
        """
        if u.get_key(event) == 'Return':
            container = widget.get_parent()
            if container:
                #log.debug('key_press_next_control')
                container.child_focus(gtk.DIR_TAB_FORWARD)