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

from sqlalchemy.orm import MapperExtension, EXT_CONTINUE
from dawpag import utils as u

log = u.get_logger('dawpag.database_ext')

class EventExtension(MapperExtension):

    def after_delete(self, mapper, connection, instance):
        """
        Receive an object instance after that instance is DELETEed.
        """
        log.debug('AFTER DELETE')

    def after_insert(self, mapper, connection, instance):
        """
        Receive an object instance after that instance is INSERTed.
        """
        log.debug('AFTER INSERT')

    def after_update(self, mapper, connection, instance):
        """
        Receive an object instance after that instance is UPDATEed.
        """
        log.debug('AFTER UPDATE')

    def append_result(self, mapper, selectcontext, row, instance, result,
        **flags):
        """
        Receive an object instance before that instance is appended to a result
        list.

        If this method returns EXT_CONTINUE, result appending will proceed
        normally. if this method returns any other value or None, result
        appending will not proceed for this instance, giving this extension an
        opportunity to do the appending itself, if desired.

        mapper
            The mapper doing the operation.
        selectcontext
            SelectionContext corresponding to the instances() call.
        row
            The result row from the database.
        instance
            The object instance to be appended to the result.
        result
            List to which results are being appended.
        **flags
            extra information about the row, same as criterion in
            create_row_processor() method of MapperProperty
        """
        log.debug('APPEND RESULT')
        return EXT_CONTINUE

    def before_delete(self, mapper, connection, instance):
        """
        Receive an object instance before that instance is DELETEed.

        Note that no changes to the overall flush plan can be made here; this
        means any collection modification, save() or delete() operations which
        occur within this method will not take effect until the next flush call.
        """
        log.debug('BEFORE DELETE')

    def before_insert(self, mapper, connection, instance):
        """
        Receive an object instance before that instance is INSERTed into its
        table.

        This is a good place to set up primary key values and such that aren't
        handled otherwise.

        Column-based attributes can be modified within this method which will
        result in the new value being inserted. However no changes to the
        overall flush plan can be made; this means any collection modification
        or save() operations which occur within this method will not take effect
        until the next flush call.
        """
        log.debug('BEFORE INSERT')

    def before_update(self, mapper, connection, instance):
        """
        Receive an object instance before that instance is UPDATEed.

        Note that this method is called for all instances that are marked as
        "dirty", even those which have no net changes to their column-based
        attributes. An object is marked as dirty when any of its column-based
        attributes have a "set attribute" operation called or when any of its
        collections are modified. If, at update time, no column-based attributes
        have any net changes, no UPDATE statement will be issued. This means
        that an instance being sent to before_update is not a guarantee that an
        UPDATE statement will be issued (although you can affect the outcome
        here).

        To detect if the column-based attributes on the object have net changes,
        and will therefore generate an UPDATE statement, use
        object_session(instance).is_modified(instance,
        include_collections=False).

        Column-based attributes can be modified within this method which will
        result in their being updated. However no changes to the overall flush
        plan can be made; this means any collection modification or save()
        operations which occur within this method will not take effect until the
        next flush call.
        """
        log.debug('BEFORE UPDATE')

    def create_instance(self, mapper, selectcontext, row, class_):
        """
        Receive a row when a new object instance is about to be created from
        that row.

        The method can choose to create the instance itself, or it can return
        EXT_CONTINUE to indicate normal object creation should take place.

        mapper
            The mapper doing the operation
        selectcontext
            SelectionContext corresponding to the instances() call
        row
            The result row from the database
        class_
            The class we are mapping.
        return value
            A new object instance, or EXT_CONTINUE
        """
        log.debug('CREATE INSTANCE')
        return EXT_CONTINUE

    def init_failed(self, mapper, class_, oldinit, instance, args, kwargs):
        log.debug('INIT FAILED')

    def init_instance(self, mapper, class_, oldinit, instance, args, kwargs):
        log.debug('INIT INSTANCE')

    def instrument_class(self, mapper, class_):
        log.debug('INSTRUMENT CLASS')

    def on_reconstitute(self, mapper, instance):
        """
        Receive an object instance after it has been created via __new__(), and
        after initial attribute population has occurred.

        This typicically occurs when the instance is created based on incoming
        result rows, and is only called once for that instance's lifetime.

        Note that during a result-row load, this method is called upon the first
        row received for this instance; therefore, if eager loaders are to
        further populate collections on the instance, those will not have been
        completely loaded as of yet.
        """
        log.debug('ON RECONSTITUTE')

    def populate_instance(self, mapper, selectcontext, row, instance, **flags):
        """
        Receive an instance before that instance has its attributes populated.

        This usually corresponds to a newly loaded instance but may also
        correspond to an already-loaded instance which has unloaded attributes
        to be populated. The method may be called many times for a single
        instance, as multiple result rows are used to populate eagerly loaded
        collections.

        If this method returns EXT_CONTINUE, instance population will proceed
        normally. If any other value or None is returned, instance population
        will not proceed, giving this extension an opportunity to populate the
        instance itself, if desired.

        As of 0.5, most usages of this hook are obsolete. For a generic "object
        has been newly created from a row" hook, use on_reconstitute(), or the
        @attributes.on_reconstitute decorator.
        def translate_row(self, mapper, context, row)

        Perform pre-processing on the given result row and return a new row
        instance.

        This is called when the mapper first receives a row, before the object
        identity or the instance itself has been derived from that row.
        """
        log.debug('POPULATE INSTANCE')
        return EXT_CONTINUE