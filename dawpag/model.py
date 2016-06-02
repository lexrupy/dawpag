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

from dawpag.database import session
from dawpag.configuration import config as conf
from dawpag import utils as u

log = u.get_logger('assessor.model')


class Model(object):
    """
    A class to extend all application models
    """
    _code_field = 'code'
    _display_field = 'name'

    def __init__(self, **kwargs):
        super(Model, self).__init__()
        self.set_values(**kwargs)
        self._initialize()

    def _initialize(self):
        """
        Initialization method to override
        """
        pass

    def set_values(self, **kwargs):
        for field in kwargs:
            value = kwargs[field]
            setter_method = 'set_%s' % field
            if hasattr(self, setter_method):
                getattr(self, setter_method).__call__(value)
                continue
            setattr(self, field, value)

    def to_message(self):
        """
        Override this to define an string representation of this object to be
        displayed on generic messages to user, like confirm deletion, etc
        """
        if hasattr(self, self._display_field):
            return getattr(self, self._display_field)
        else:
            return _(u'Este registro')

    def before_save(self):
        """
        Override to create some operations just before saving object
        """
        pass
    # TODO: Really look at mapper extension :)
    def after_save(self):
        """
        Override to create some operations just after saving object
        """
        pass

    def save(self):
        try:
            self.before_save()
            session.add(self)
            session.commit()
            self.after_save()
        except:
            session.rollback()

    def discard(self):
        try:
            session.remove(self)
        except:
            log.warning('Object cannot be discarded...')

    def delete(self):
        try:
            session.delete(self)
            session.commit()
        except:
            session.rollback()
    # Classmethods

    def first(cls):
        return session.query(cls).first()
    first = classmethod(first)

    def get(cls, *args, **kwargs):
        return session.query(cls).get(*args, **kwargs)
    get = classmethod(get)

    def all(cls):
        return session.query(cls).all()
    all = classmethod(all)

    def filter_by(cls, *args, **kwargs):
        return session.query(cls).filter(*args, **kwargs)
    filter_by = classmethod(filter_by)

    # def get_by(cls, *args, **kwargs):
    #     return session.query(cls).filter(*args, **kwargs).first()
    # get_by = classmethod(get_by)

    # def select(cls, *args, **kwargs):
    #     limit = conf.get('database.query_limit')
    #     return session.query(cls).filter(*args, **kwargs).limit(limit).all()
    # select = classmethod(select)