import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

def ui_translate(ui):
    """This is a bit annoying: Gtk with python does not
    always translate ui files from glade."""
    wids = ui.get_objects()
    for wid in wids:
        if (type(wid) == Gtk.ShortcutsShortcut) or (type(wid) == Gtk.ShortcutsGroup):
            wid.props.title = _(wid.props.title)

