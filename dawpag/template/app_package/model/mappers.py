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

from sqlalchemy.orm import mapper, relation
from classes import User, CurrencyType, State, City, Person, Subsidiary,\
    ProductGroup, Product, Stock, Tax, Config, Document, StockTransaction,
    Account, Bill, AccountTransaction
from tables import users_table, currency_types_table, states_table,\
    cities_table, people_table, subsidiaries_table, product_groups_table,\
    products_table, stocks_table, taxes_table, configs_table, documents_table,\
    stock_transactions_table, accounts_table, bills_table,\
    account_transactions_table


users_mapper = mapper(User, users_table)

configs_mapper = mapper(Config, configs_table)

currency_type_mapper = mapper(CurrencyType, currency_types_table)

states_mapper = mapper(State, states_table)

cities_mapper = mapper(City, cities_table, properties={
    'state' : relation(State)}
)

people_mapper = mapper(Person, people_table, properties={
    'primary_city' : relation(City, primaryjoin=
        people_table.c.primary_city_id==cities_table.c.id
        ),
    'secondary_city' : relation(City, primaryjoin=
        people_table.c.secondary_city_id==cities_table.c.id
        )
    }
)

subsidiaries_mapper = mapper(Subsidiary, subsidiaries_table)

taxes_mapper = mapper(Tax, taxes_table)

product_groups_mapper = mapper(ProductGroup, product_groups_table)

stocks_mapper = mapper(Stock, stocks_table, properties={
    'product' : relation(Product, backref='stocks',
        cascade='all, delete, delete-orphan'),
    'subsidiary': relation(Subsidiary, backref='stocks',
        cascade='all, delete, delete-orphan')
    }
)

products_mapper = mapper(Product, products_table, properties={
    'group' : relation(ProductGroup),
    'tax'   : relation(Tax)
    }
)

documents_mapper = mapper(Document, documents_table, properties={
    'subsidiary' : relation(Subsidiary)
    }
)

stock_transactions_mapper = mapper(StockTransaction, stock_transactions_table,
    inherits=Document, properties={
        'product'  : relation(Product)
    }
)

accounts_mapper = mapper(Account, accounts_table)

bills_mapper = mapper(Bill, bills_table,
    properties={
        'document' : relation(Document),
        'account'  : relation(Account),
        'bill'     : relation(Bill),
    }
)

stock_transactions_mapper = mapper(AccountTransaction,
    account_transactions_table, inherits=Document, properties={
        #'document' : relation(Document),
        'bill'                : relation(Bill),
        'account'             : relation(Account),
        'account_transaction' : relation(AccountTransaction),
    }
)