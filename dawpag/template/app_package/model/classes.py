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

import hashlib
from datetime import datetime
from dawpag.configuration import config
from dawpag.model import Model
from dawpag import utils as u
from sqlalchemy import and_
import assessor
from dawpag.database_ext import EventExtension

log = u.get_logger('assessor.model')

zero = u.zero
um = u.um
cem = u.cem

class User(Model):
    """
    User Model
    """
    # Private methods

    def __encrypt(self, pwd):
        """
        Encrypt given pwd and return the encrypted buffer
        """
        enc_buff = pwd
        m = hashlib.sha256()
        for i in range(int(config.get('security.encrypt_times'))):
            tmp_buff = '-'.join([
                config.get('security.encrypt_times'),
                enc_buff,
                self.salt
            ])
            enc_buff = m.update(tmp_buff)
            enc_buff = m.hexdigest()
        return enc_buff

    # Public Methods

    def set_password(self, value):
        """
        Set the user password.
        Generate a password salt based on current timestamp to make a strong
        password, than encrypt password with generated salt
        """
        # Salt need to be generated before set password
        m = hashlib.sha256()
        m.update('-'.join([
            str(datetime.now()),
            config.get('security.password_salt')
        ]))
        self.salt = m.hexdigest()
        self.password_pending = False
        self.password = self.__encrypt(value)

    def check_password(self, password):
        """
        Check if given password is valid
        """
        if self.password is None:
            return password is None
        return self.__encrypt(password) == self.password

    # Magic
    def __repr__(self):
        return "<#User: '%s', '%s'>" % (self.name, self.fullname)


class Config(Model):
    """
    Model for server side configuration. Accepts get and set methods
    """
    def get(cls, name, default=None):
        c = cls.filter_by(cls.name==name).first()
        if c:
            return c.value
        return default
    get = classmethod(get)

    def set(cls, name, value, group=None, description=None):
        c = cls.filter_by(cls.name==name).first()
        if c:
            c.value = value
            if group:
                c.group = group
            if description:
                c.description = description
        else:
            c = cls(name=name, group=group, value=value,
                description=description)
        c.save()
    set = classmethod(set)

    # Magic
    def __repr__(self):
        return "<#Config: '%s', '%s'>" % (self.name, self.value)


class CurrencyType(Model):
    """
    Currency model
    """
    # Magic
    def __repr__(self):
        return "<#CurrencyType: '%s'>" % self.name


class State(Model):
    """
    State model
    """
    # Magic
    def __repr__(self):
        return "<#State: '%s', '%s'>" % (self.name, self.state)


class City(Model):
    """
    City model
    """
    # Magic
    def __repr__(self):
        return "<#City: '%s', '%s'>" % (self.name, self.state.name)


class Person(Model):
    """
    City model
    """
    # Magic
    def __repr__(self):
        return "<#Person: '%s'>" % (self.name)


class Subsidiary(Model):
    """
    City model
    """
    def _initialize(self):
        """
        Subsidiary Initialization, Create an Stock for this subsidiary for each
        product
        """
        for p in Product.all():
            s = Stock(product=p)
            self.stocks.append(s)
    # Magic
    def __repr__(self):
        return "<#Subsidiary: '%s', '%s'>" % (self.name, str(self.active))


class ProductGroup(Model):
    """
    Product Groups model
    """
    # Magic
    def __repr__(self):
        return "<#ProductGroup: '%s'>" % (self.name)


class Stock(Model):
    """
    Information about a product in a subsidiary
    """
    def margin(self):
        """
        Get the calculated margin value
        """
        sp = self.sale_price or zero
        if u.isempty(sp):
            return zero
        cp = self.cost_price or zero
        return u.decimal((um-(cp/sp))*cem, True)

    def set_margin(self, value):
        """
        Set the current sale price based on given margin
        """
        value = u.decimal(value)
        if u.isempty(value):
            self.sale_price = self.cost_price
        else:
            cp = self.cost_price or zero
            self.sale_price = u.decimal(cp/((cem-value)/cem), True)
    margin = property(margin)

    def margin_timed(self):
        """
        Get the calculated margin value for timed sales
        """
        sp = self.sale_price_timed or zero
        if u.isempty(sp):
            return zero
        cp = self.cost_price or zero
        return u.decimal((um-(cp/sp))*cem, True)

    def set_margin_timed(self, value):
        """
        Set the current timed sale price based on given margin
        """
        value = u.decimal(value)
        if u.isempty(value):
            self.sale_price_timed = self.cost_price
        else:
            cp = self.cost_price or zero
            self.sale_price_timed = u.decimal(cp/((cem-value)/cem), True)
    margin_timed = property(margin_timed)

    def initial(self):
        """
        Always returns o (Zero) for initial Stock
        """
        return zero

    def set_initial(self, value):
        """
        Create an Stock Adjustment with given initial quantity
        """
        # TODO: Make an Initial Stock Adjust here
        pass
    initial = property(initial)

    # Magic
    def __repr__(self):
        return "<#Stock: product: '%s', subsidiary: '%s'>" %\
        ((self.product.name or ''), (self.subsidiary.name or ''))


class Product(Model):
    """
    Product Model
    """
    # Override
    def _initialize(self):
        """
        Product Initialization. Create all stocks needed (for each subsidiary)
        """
        for s in Subsidiary.all():
            self.__create_stock(s)
        self.get_stock()

    def __create_stock(self, subsidiary):
        """
        Create an stock for subsidiary if a stock does not exist
        """
        log.debug('CREATE STOCK....')
        p = Stock(subsidiary=s)
        self.stocks.append(p)

    def get_stock(self, from_subsidiary=None):
        """
        Get the current stock from given subsidiary, or None if not found
        """
        try:
            if not from_subsidiary:
                from_subsidiary = Subsidiary.get(assessor.DEFAULT_SUBSIDIARY)
            self.stock = Stock.filter_by(and_(Stock.product_id==self.id,
                Stock.subsidiary_id==from_subsidiary.id)
                ).first()
            if not self.stock:
                self.stock = self.__create_stock(from_subsidiary)
            return self.stock
        except:
            raise
            self.stock = None
        return None

    # Magic
    def __repr__(self):
        return "<#Product: '%s'>" % (self.name)


class Tax(Model):
    """
    Tax Model
    """
    # Magic
    def __repr__(self):
        return "<#Tax: '%s', '%s'>" % (self.name, str(self.value))


class Document(Model):
    """
    Document Model
    """
    # Magic
    def __repr__(self):
        return "<#%s: '%s', '%s', '%s'>" % (self.__class__.__name__,
            self.doc_type, self.number, str(self.value))


class StockTransaction(Document):
    """
    Stock Movement Model
    """
    def _initialize(self):
        # doc_type = MS # TODO: Read document marks from configuration
        self.doc_type = 'AS' # Ajuste de Estoque / Movimento Estoque
        self.number = 'S/N'


class Account(Model):
    """
    Account Model
    """
    # Magic
    def __repr__(self):
        return "<#Account: '%s', balance: '%s' >" % (self.name,
            str(self.balance))


class Bill(Model):
    """
    Account Model
    """
    # Magic
    def __repr__(self):
        return "<#Bill: '%s/%s', due: %s ammount: '%s' >" %\
        (self.document.doc_type, u.date_to_str(self.due_at),
            self.document.number, str(self.ammount))


class AccountTransaction(Document):
    """
    Stock Movement Model
    """
    def _initialize(self):
        # doc_type = MC # TODO: Read document marks from configuration
        self.doc_type = 'MC' # Movimento de Caixa
        #self.number = 'S/N'

#
