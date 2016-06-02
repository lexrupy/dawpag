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

# Ported from Turbogears

import optparse
import sys
import os
import os.path

import pkg_resources

import dawpag
from dawpag.utils import load_project_config, get_project_config, get_model,\
    get_project_name

sys.path.insert(0, os.getcwd())

no_connection_param = ["help", "list"]
no_model_param = ["help"]

def silent_os_remove(fname):
    """
    Tries to remove file FNAME but mutes any error that may happen.

    Returns True if file was actually removed and false otherwise
    """
    try:
        os.remove(fname)
        return True
    except os.error:
        pass
    return False

class CommandWithDB(object):
    "Base class for commands that need to use the database"
    config = None

    def __init__(self, version):
        pass

    def find_config(self):
        """Chooses the config file, trying to guess whether this is a
        development or installed project."""
        load_project_config(self.config)

class Console(CommandWithDB):
    """Convenient version of the Python interactive shell.
    This shell attempts to locate your configuration file and model module
    so that it can import everything from your model and make it available
    in the Python shell namespace."""

    desc = "Start a Python prompt with your database available"
    need_project = True

    def run(self):
        "Run the shell"
        self.find_config()

        from dawpag import database

        mod = get_model()
        if mod:
            locals = mod.__dict__
        else:
            locals = dict(__name__="dawpag")

        locals.update(dict(session=database.session,
            metadata=database.metadata))

        try:
            # try to use IPython if possible
            import IPython

            class CustomIPShell(IPython.iplib.InteractiveShell):
                def raw_input(self, *args, **kw):
                    try:
                        return IPython.iplib.InteractiveShell.raw_input(self,
                            *args, **kw) # needs decoding (see below)?
                    except EOFError:
                        r = raw_input("Do you wish to commit your "
                                    "database changes? [yes]")
                        if not r.lower().startswith("n"):
                            self.push("session.flush()")
                        raise EOFError

            shell = IPython.Shell.IPShell(user_ns=locals,
                                          shell_class=CustomIPShell)
            shell.mainloop()
        except ImportError:
            import code

            class CustomShell(code.InteractiveConsole):
                def raw_input(self, *args, **kw):
                    try:
                        import readline
                    except ImportError:
                        pass
                    try:
                        r = code.InteractiveConsole.raw_input(self,
                            *args, **kw)
                        for encoding in (getattr(sys.stdin, 'encoding', None),
                                sys.getdefaultencoding(), 'utf-8', 'latin-1'):
                            if encoding:
                                try:
                                    return r.decode(encoding)
                                except UnicodeError:
                                    pass
                        return r
                    except EOFError:
                        r = raw_input("Do you wish to commit your "
                                      "database changes? [yes]")
                        if not r.lower().startswith("n"):
                            self.push("session.flush()")
                        raise EOFError

            shell = CustomShell(locals=locals)
            shell.push('print "Starting console shell for project:\'%s\'"' %
                get_project_name())
            shell.interact()

def main():
    "Main command runner. Manages the primary command line arguments."
    # add commands defined by entrypoints
    commands = {}
    for entrypoint in pkg_resources.iter_entry_points("dawpag.command"):
        command = entrypoint.load()
        commands[entrypoint.name] = (command.desc, entrypoint)

    def _help():
        "Custom help text for dpadmin."

        print """
DAwPaG %s command line interface

Usage: %s [options] <command>

Options:
    -c CONFIG --config=CONFIG    Config file to use
    -e EGG_SPEC --egg=EGG_SPEC   Run command on given Egg

Commands:""" % (dawpag.__version__, sys.argv[0])

        longest = max([len(key) for key in commands.keys()])
        format = "    %" + str(longest) + "s  %s"
        commandlist = commands.keys()
        commandlist.sort()
        for key in commandlist:
            print format % (key, commands[key][0])


    parser = optparse.OptionParser()
    parser.allow_interspersed_args = False
    parser.add_option("-c", "--config", dest="config")
    parser.add_option("-e", "--egg", dest="egg")
    parser.print_help = _help
    (options, args) = parser.parse_args(sys.argv[1:])

    # if not command is found display help
    if not args or not commands.has_key(args[0]):
        _help()
        sys.exit()

    commandname = args[0]
    # strip command and any global options from the sys.argv
    sys.argv = [sys.argv[0],] + args[1:]
    command = commands[commandname][1]
    command = command.load()

    if options.egg:
        egg = pkg_resources.get_distribution(options.egg)
        os.chdir(egg.location)

    if hasattr(command,"need_project"):
        if not dawpag.utils.get_project_name():
            print "This command needs to be run from inside a project directory"
            return
        elif not options.config and not os.path.isfile(get_project_config()):
            print """No default config file was found.
If it has been renamed use:
dpadmin --config=<FILE> %s""" % commandname
            return
    command.config = options.config
    command = command(dawpag.__version__)
    command.run()

__all__ = ["main"]