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


from datetime import datetime as dt
from dawpag.database import metadata, get_engine
from sqlalchemy import Table, Column, ForeignKey
from sqlalchemy import Integer, String, Boolean, Numeric, DateTime, Text,\
    PickleType


engine = get_engine()


users_table = Table('users', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String(15), unique=True),
    Column('fullname', String(60)),
    Column('salt', String),
    Column('password', String),
    Column('password_pending', Boolean, default=True),
    Column('active', Boolean, default=True)
)


configs_table = Table('configs', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String(30), unique=True),
    Column('group', String(30)),
    Column('description', String(80)),
    Column('value', PickleType),
)


currency_types_table = Table('currency_types', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String(60)),
    Column('active', Boolean, default=True)
)


states_table = Table('states', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String(60)),
    Column('state', String(2)),
    Column('active', Boolean, default=True)
)


cities_table = Table('cities', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String(60)),
    Column('state_id', ForeignKey('states.id'), nullable=False),
    Column('active', Boolean, default=True)
)


people_table = Table('people', metadata,
    Column('id', Integer, primary_key=True),
    #Column('reference', String(15), unique=True),
    Column('name', String(60), nullable=False),
    Column('nickname', String(60)),
    Column('kind', String(10)), # Fisica/Juridica
    Column('identification', String(20)), # CPF/CNPJ
    Column('identification_auxiliar', String(15)), # IE/RG
    Column('born_at', DateTime),
    Column('naturality', String(80)),
    Column('mother_name', String(60)),
    Column('father_name', String(60)),
    Column('civil_state', String(15)),
    Column('gender', String(15)), # Male/Female
    # Contact Information ------------------------------------------------------
    Column('contact', String(30)),
    # Create an Address Entity? I think not
    Column('primary_addr_street', String(60)), # Rua
    Column('primary_addr_compl', String(20)), # Complemento
    Column('primary_addr_number', String(8)), # Numero
    Column('primary_addr_zone', String(30)), # Bairro
    Column('primary_addr_zip', String(10)), # CEP
    Column('primary_city_id', ForeignKey('cities.id'), nullable=False),
    Column('secondary_addr_street', String(60)), # Rua
    Column('secondary_addr_compl', String(20)), # Complemento
    Column('secondary_addr_number', String(8)), # Numero
    Column('secondary_addr_zone', String(30)), # Bairro
    Column('secondary_addr_zip', String(10)), # CEP
    Column('secondary_city_id', ForeignKey('cities.id'), nullable=True),
    # Phone Numbers, Contact
    Column('primary_phone', String(15)),
    Column('secondary_phone', String(15)),
    Column('mobile_phone', String(15)),
    Column('fax', String(15)),
    Column('email', String(250)),
    Column('website', String(250)),
    # Kind Information
    Column('is_customer', Boolean, default=False),
    Column('is_supplier', Boolean, default=False),
    Column('is_employee', Boolean, default=False),
    Column('is_bank', Boolean, default=False),
    Column('is_partner', Boolean, default=False),
    Column('is_carrier', Boolean, default=False),
    Column('is_other', Boolean, default=False),
    # Other Information
    Column('locked', Boolean, default=False),
    Column('credit_limit', Numeric(14,4)),
    Column('comments', Text),
    Column('active', Boolean, default=True),
    Column('updated_at', DateTime, onupdate=dt.now)
)


taxes_table = Table('taxes', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String(30), unique=True),
    Column('value', Numeric(14,4)),
    Column('active', Boolean, default=True)
)


subsidiaries_table = Table('subsidiaries', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String(30), unique=True),
    Column('active', Boolean, default=True)
)


product_groups_table = Table('product_groups', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String(60)),
    Column('active', Boolean, default=True)
)


products_table = Table('products', metadata,
    Column('id', Integer, primary_key=True),
    Column('reference', String(15), unique=True),
    Column('barcode', String(20)),
    Column('group_id', ForeignKey('product_groups.id')),
    Column('name', String(80)),
    Column('name_redux', String(40)),
    Column('measure_unit', String(10)),
    Column('is_service', Boolean, default=False),
    Column('tax_id', ForeignKey('taxes.id')),
    # Melhorar isto aqui? mudar ao inves de por so o codigo, colocar uma combo
    # na tela para o usuario escolher... ? ficaria melhor quems sabe
    Column('cst', String(5)), # Brazilian: Codigo de Situacao Trubutaria
    Column('active', Boolean, default=True),
    Column('updated_at', DateTime, onupdate=dt.now)
)


stocks_table = Table('stocks', metadata,
    Column('product_id', ForeignKey('products.id'), primary_key=True),
    Column('subsidiary_id', ForeignKey('subsidiaries.id'), primary_key=True),
    Column('sale_price', Numeric(14,4), default=0.0),
    Column('sale_price_timed', Numeric(14,4), default=0.0),
    Column('cost_price', Numeric(14,4), default=0.0),
    Column('stock_min', Numeric(14,4), default=0.0),
    Column('stock_max', Numeric(14,4), default=0.0),
    Column('stock', Numeric(14,4), default=0.0)
)


documents_table = Table('documents', metadata,
    Column('id', Integer, primary_key=True),
    Column('subsidiary_id', ForeignKey('subsidiaries.id')),
    Column('number', String(20), nullable=False),
    Column('doc_type', String(3), nullable=False),
    Column('value', Numeric(14,4), default=0.0),
    Column('comments', String),
    Column('status', String(15), default='new'), # new, open, closed, canceled
    Column('is_printed', Boolean, default=False),
    Column('created_at', DateTime, default=dt.now),
    Column('updated_at', DateTime, default=dt.now, onupdate=dt.now)
)

# TODO: Implement relation between documents
related_documents_table = Table('related_documents', metadata,
    Column('document_id', ForeignKey('documents.id')),
    Column('related_document_id', ForeignKey('documents.id'))
)


stock_transactions_table = Table('stock_transactions', metadata,
    Column('id', ForeignKey('documents.id'), primary_key=True),
    Column('product_id', ForeignKey('products.id')), # TODO: Primary Key?
    Column('quantity', Numeric(14,4), default=0.0),
    Column('kind', String(10), default='entrada') # entrada/inbound,
)                                                 # saida/outbound


accounts_table = Table('accounts', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String(80), nullable=False),
    Column('balance', Numeric(14,4)) # Saldo
)


bills_table = Table('bills', metadata,
    Column('id', Integer, primary_key=True),
    Column('document_id', ForeignKey('documents.id'), nullable=False),
    Column('bill_id', ForeignKey('bills.id')), # if this this bill was unfolded
    Column('bill_type', String(20), nullable=False), #
    Column('due_at', DateTime, nullable=False), # Vencimento
    Column('payed_at', DateTime), # Data de Pagamento
    Column('ammount', Numeric(14,4)), # Valor Pago
    Column('kind', String(10)) # pagar/receber
)

# bill_id e uma referencia para uma conta que foi paga parcialmente ou que
# por algum motivo teve que ser desdobrada. Para identificar
# Contas desdobradas, ou mesmo juros de outras contas, e poder filtrar depois.
# Por exemplo. cada vez que uma conta gerar juros, ao inves de jogar um valor
# maior pago, lancar mais uma conta "filha" com o valor dos juros e do tipo
# juros. Pode-se tornar bastante flexivel e interessante, porem pode-se tornar
# dificil de manter tambem. Analizar
# bill_type e o tipo da conta. tipos iniciais devem ser:
#   normal: Conta Normal/Comum
#   (unfold)desdobrada: Conta desdobrada de outra (Reparcelada/Renegociada)
#   (interest)juros: Juros


account_transactions_table = Table('account_transactions', metadata,
    Column('id', ForeignKey('documents.id'), primary_key=True),
    Column('bill_id', ForeignKey('bills.id')), # Can or not have a bill related
    Column('account_id', ForeignKey('accounts.id'), nullable=False),#Dst Account
    Column('account_transaction_id', ForeignKey('account_transactions.id')),
    Column('comments', String, nullable=False),  # Historico.
    Column('kind', String(10), nullable=False), # entrada/saida
)

# account_transaction_id sera utilizado apenas para identificar que esta transa
# cao e um estorno de uma outra transacao, uma vez que nao poderao ser excluidas
# contas.
# Um estorno por sua vez podera recolocar uma conta (bill) que foi quitada por
# um lancamento como aberta novamente. o historico fica apenas nas transacoes.

# Create all database tables
metadata.create_all(engine)