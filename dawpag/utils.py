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

import os, re, gtk
from dawpag import configuration as cfg
from dawpag import basedir
from datetime import datetime, timedelta
import decimal as dec
import logging
import re
from xml.sax.saxutils import escape as _escape_markup

_name_message_format = "%(name)s - %(message)s"

zero = dec.Dec_0
um = dec.Dec_p1
cem = dec.Decimal(100)

class ValueUnset:
    """
    A Class to define an unsetted value
    """
    pass

class DawpagLogger(object):
    """
    A customized simpler log emmiter, to simplify the configuration file
    """
    def __init__(self, loggername):
        self.__name = loggername

    def __format(self, message):
        return _name_message_format % {
            "name": self.__name,
            "message": message
            }

    def critical(self, message):
        """
        Log level 50, messages are logged if log level is set to CRITICAL
        """
        logging.critical(self.__format(message))

    def error(self, message):
        """
        Log level 40, messages are logged if log level is set to ERROR
        """
        logging.error(self.__format(message))

    def warning(self, message):
        """
        Log level 30, messages are logged if log level is set to WARNING
        """
        logging.warning(self.__format(message))

    def info(self, message):
        """
        Log level 20, messages are logged if log level is set to INFO
        """
        # TODO: log info messages to a database log table
        logging.info(self.__format(message))

    def debug(self, message):
        """
        Log level 10, messages are logged if log level is set to DEBUG
        """
        logging.debug(self.__format(message))


def get_file(name):
    """
    Return the file name based on path relative to application
    """
    return os.sep.join([basedir, name])


def get_image(name):
    """
    Return the file name inside image folder
    """
    return os.sep.join([basedir, get_package_name(), 'images', name])


def set_image(img, filename=None):
    """
    Set the image of a GtkImage with given image filename
    if not given it will try to load an image based on Widget name, ignoring
    first 2 letters
    Ex: if you have a widget named "im_image", it will try to load an image
        named image.[default_extension]
    """
    if filename is None:
        filename = '.'.join([
            img.name[3:],
            cfg.config.get('main.default_image_extension')
            ])
    img.set_from_file(get_image(filename))


def camel_to_underscore(camel_string):
    """
    Return a string passwed in CamelCase into a string with underscores
    "camel_case"
    """
    return re.sub(r'(.+?)([A-Z])+?', r'\1_\2', camel_string).lower()


def escape_markup(text):
    """
    Return a markup text properly escaped to be used in Pango, or in HTML/XML
    documents.
    """
    return _escape_markup(text)


def get_pango_markup(text, bold=False, italic=False, underline=None,
                   strikethrough=False, size=None, color=None, bgcolor=None,
                   weight=None, font_family=None, style=None, rise=None):
        """
        size : ['xx-small', 'x-small', 'small', 'medium', 'large', 'x-large',
                'xx-large'] or a numeric value in thousandths of a point
        underline: ['single', 'double', 'low', 'none']
        weight: ['ultralight', 'light', 'normal', 'bold', 'ultrabold', 'heavy']
                 or a numeric weight.
        font_family: ["normal", "sans", "serif", "monospace"]
        rise: The vertical displacement from the baseline, in ten thousandths of
        an em. Can be negative for subscript, positive for superscript.

        Note: Pass all fields quoted (String)
        """
        span_attrs = []
        if weight or bold:
            span_attrs.append('weight="%s"' % (weight or 'bold'))
        if style or italic:
            span_attrs.append('style="%s"' % (style or 'italic'))
        if underline:
            if underline==True:
                underline='single'
            span_attrs.append('underline="%s"' % underline)
        if strikethrough:
            span_attrs.append('strikethrough="true"')
        if size:
            span_attrs.append('size="%s"' % size)
        if color:
            span_attrs.append('foreground="%s"' % color)
        if bgcolor:
            span_attrs.append('background="%s"' % bgcolor)
        if weight:
            span_attrs.append('weight="%s"' % weight)
        if font_family:
            span_attrs.append('font_family="%s"' % font_family)
        if rise:
            span_attrs.append('rise="%s"' % rise)
        span = "<span %s>%s</span>" % (' '.join(span_attrs), r'%s')
        text = _escape_markup(text)
        return span % text


def humanize(_str):
    """
    Return a string humainzed
    """
    parts = _str.split('_')
    new_parts = []
    for p in parts:
        new_parts.append(p.capitalize())
    return ' '.join(new_parts)


def isempty(obj):
    """
    Return true if object is an empty object,
    """
    if obj is None:
        return True
    if isinstance(obj, (str, list)):
        return len(obj) == 0
    if isinstance(obj, (int, float, long)):
        return obj == 0
    if isinstance(obj, dec.Decimal):
        return obj.is_zero()
    return False


def str_to_date(value, default=None):
    """
    Given a string value, try to convert to date based on date format on
    config file
    """
    try:
        return datetime.strptime(value, cfg.config.get('format.date'))
    except:
        return default


def date_to_str(value, default=None):
    """
    Given a datetime value, try to convert string based on date format on
    config file
    """
    try:
        return datetime.strftime(value, cfg.config.get('format.date'))
    except:
        return default


def timestamp_to_str(value, default=None):
    """
    Given a datetime value, try to convert string based on timestamp format on
    config file
    """
    try:
        return datetime.strftime(value, cfg.config.get('format.timestamp'))
    except:
        return default


def currency_str(value):
    value = float(value)
    temp = "%.2f" % value
    profile = re.compile(r"(\d)(\d\d\d[.,])")
    while 1:
        temp, count = re.subn(profile,r"\1 \2",temp)
        if not count: break
    return temp


def decimal(value, normalized=False, format='0.0001'):
    """
    Try to convert the given value to a decimal value normalized
    """
    if value is None:
        return zero
    if not isinstance(value, str):
        value = str(value)
    try:
        result = dec.Decimal(value)
    except:
        # Try to change a possible colon to a dot
        value = value.replace(',','.')
        result = dec.Decimal(value)
    if normalized:
        return normalize_decimal(result, format)
    return result


def compare_date(date_a, date_b):
    """
    Compare date A with date B ignoring timestamp
    returning
        -1 if date_a is greater than date_b.
         1 if date_b is greater then date_a.
         0 if are equal.
    """
    tmp = date_a.timetuple()
    y, m, d = tmp[0], tmp[1], tmp[2]
    date_a = datetime(y,m,d)
    tmp = date_b.timetuple()
    y, m, d = tmp[0], tmp[1], tmp[2]
    date_b = datetime(y,m,d)
    if date_a > date_b:
        return -1
    elif date_a == date_b:
        return 0
    return 1


def normalize_decimal(value, format='0.0001'):
    """
    Normalize a decimal value to four digits after float point
    """
    return dec.ExtendedContext.quantize(value, dec.Decimal(format))


def widget_base_color(w, new_color):
    """
    Given an entry and a Color change the background color
    """
    w.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse(new_color))


def widget_bg_color(w, new_color):
    """
    Given an entry and a Color change the border color
    """
    w.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse(new_color))


def widget_text_color(w, new_color):
    """
    Given an entry and a Color change the text color
    """
    w.modify_text(gtk.STATE_NORMAL, gtk.gdk.color_parse(new_color))


def widget_fg_color(w, new_color):
    """
    Given an entry and a Color change the text color
    """
    w.modify_fg(gtk.STATE_NORMAL, gtk.gdk.color_parse(new_color))


def wasunchanged(new, old):
    """
    Return True if old value and new value are equal
    """
    return (new==old) or (old is None and isempty(new))


def get_glade_file(module_):
    """
    Return a glade file for the current module
    """
    mlist = str(module_).split('.')
    mlist.reverse()
    return os.sep.join([basedir, get_package_name(), 'controller','glade',
        '.'.join([mlist[0],'glade'])])


def get_key(event):
    """
    Return the keyval name from a gtk key-press-event
    """
    # TODO: Maybe test if event is a keypress event before try to evaluate
    return gtk.gdk.keyval_name(event.keyval)


def get_package_name():
    """Try to find out the package name of the current directory."""
    package = cfg.config.get("main.package")
    if package:
        return package
    if hasattr(sys, 'argv') and "--egg" in sys.argv:
        projectname = sys.argv[sys.argv.index("--egg")+1]
        egg = pkg_resources.get_distribution(projectname)
        top_level = egg._get_metadata("top_level.txt")
    else:
        fname = get_project_meta('top_level.txt')
        top_level = fname and open(fname) or []
    for package in top_level:
        package = package.rstrip()
        if package and package != 'locales':
            return package


def get_model():
    package_name = get_package_name()
    if not package_name:
        return None
    package = __import__(package_name, {}, {}, ["model"])
    if hasattr(package, "model"):
        return package.model


def get_logger(loggername):
    return DawpagLogger(loggername)


def get_project_config():
    """Try to select appropriate project configuration file."""
    cfg =  os.path.exists('setup.py') and 'config.cfg'
    return os.path.abspath(cfg)


def get_project_meta(name):
    """Get egg-info file with that name in the current project."""
    for dirname in os.listdir("./"):
        if dirname.lower().endswith("egg-info"):
            fname = os.path.join(dirname, name)
            return fname


def get_project_name():
    pkg_info = get_project_meta('PKG-INFO')
    if pkg_info:
        name = list(open(pkg_info))[1][6:-1]
        return name.strip()


def load_project_config(configfile=None):
    """Try to update the project settings from the config file specified.

    If configfile is C{None}, uses L{get_project_config} to locate one.

    """
    if configfile is None:
        configfile = get_project_config()
    if not os.path.isfile(configfile):
        print 'Config file %s not found or is not a file.' % (
            os.path.abspath(configfile),)
        sys.exit()
    print "config file is: %s" % configfile
    cfg.set_config(cfg.AppConfig(configfile))
    #config.update_config(configfile=configfile,
    #    modulename = package + ".config")
