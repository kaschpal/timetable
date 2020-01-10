#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi
import sys
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio
from .MainWindow import MainWindow
from .config import dbglog


class Uplan(Gtk.Application):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, application_id="de.uleutner.timetable",
                         #flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE,
                         **kwargs)
        self.window = None

    def do_startup(self):
        Gtk.Application.do_startup(self)

        #action = Gio.SimpleAction.new("about", None)
        #action.connect("activate", self.on_about)
        #self.add_action(action)

        action = Gio.SimpleAction.new("quit", None)
        action.connect("activate", self.on_quit)
        self.add_action(action)

    def do_activate(self):
        if not self.window:
            self.window = MainWindow(application=self)
        self.window.present()
        self.window.show_all()

    def on_quit(self, action, param):
        window.quit()
        self.quit()


def main(version):
    app = Uplan()
    exit_status = app.run(sys.argv)
    sys.exit(exit_status)

    # create window
    #win = MainWindow()
    #win.show_all()

    # load config from the statefile
    #win.loadFile( ttfileName )

    # mainloop
    #Gtk.main()


if __name__ == "__main__":
    main(0)



