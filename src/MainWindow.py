import gi
#from . import language
import gettext
from gettext import gettext as _
import datetime
from . import config
from .config import dbglog
from .WeekGrid import WeekGrid
from .SequenceWindow import ClassNotebook
from .CalendarWindow import  Calendar
from .TimeTableStore import TimeTableStore
from gi.repository import Gtk, Gio, GLib, Gdk
gi.require_version('Gtk', '3.0')


class MainWindow(Gtk.ApplicationWindow):
    """This widget displayes the three views: timetable, sequence, calendar and
    the two menubuttons.
    Plus the buttons for navigation in the timetable.
    """

    def __init__(self, application):
        Gtk.ApplicationWindow.__init__(self, application=application)
        #Gtk.Window.__init__(self, title="UPlan", application=app)
        self.resizeable = False
        self.application = application

        # load the environment / configuration
        self.environment = Environment(self)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=1)
        self.add(vbox)

        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self.stack.set_transition_duration(500)

        # the timetable
        self.weekWid = WeekGrid( datetime.date.today(), window=self )
        self.stack.add_titled(self.weekWid, "timetable", _("timetable"))

        # the sequences
        self.classNoteb = ClassNotebook(parent=self)
        self.stack.add_titled(self.classNoteb, "sequence", _("sequence"))

        # the calendar
        self.calendar = Calendar(parent=self)
        self.stack.add_titled(self.calendar, "calendar", _("calendar"))

        ## the switcher
        stack_switcher = Gtk.StackSwitcher()
        stack_switcher.set_stack(self.stack)
        stack_switcher.props.halign = Gtk.Align.CENTER
        #vbox.set_center_widget(stack_switcher)
        vbox.pack_start(stack_switcher, True, True, 0)
        vbox.pack_end(self.stack, False, False, 0)

        self.__header()

        # dont resize
        self.set_resizable(False)

        # update on change of view
        self.stack.connect("notify::visible-child", self.__stackSwitched )
        self.connect("destroy", self.quit)


    def __stackSwitched(self, wid, gparamstring):
        """Updates the weekwid, if the view is changed"""
        if self.classNoteb.currentPage is not None: # first call
            self.classNoteb.currentPage.save()

        self.weekWid.update()
        dbglog("weekupd")


    def __header(self):
        """Creates the headerbar with the navigation- and menu buttons."""
        self.hb = Gtk.HeaderBar()
        self.hb.set_show_close_button(True)
        self.set_titlebar(self.hb)
        # after loading filename
        self.props.title = _("Timetable") + ": " + str(self.environment.currentFileName)

        # popover for menu
        popover = Gtk.PopoverMenu()

        # create actions
        load_action = Gio.SimpleAction.new("load", None)
        self.add_action(load_action)
        load_action.connect("activate", self.__loadClicked)

        save_action = Gio.SimpleAction.new("save", None)
        self.add_action(save_action)
        save_action.connect("activate", self.__saveClicked)

        new_action = Gio.SimpleAction.new("new", None)
        self.add_action(new_action)
        new_action.connect("activate", self.__newClicked)

        quit_save_action = Gio.SimpleAction.new("quit_save", None)
        self.add_action(quit_save_action)
        quit_save_action.connect("activate", self.__quit_save)

        quit_without_saving_action = Gio.SimpleAction.new("quit_without_saving", None)
        self.add_action(quit_without_saving_action)
        quit_without_saving_action.connect("activate", self.__quit_without_saving)

        about_action = Gio.SimpleAction.new("about", None)
        self.add_action(about_action)
        about_action.connect("activate", self.__about)

        # populate menu
        menu = Gio.Menu()
        menu.insert_item( 0, Gio.MenuItem.new( _("open timetable"), "win.load" ) )
        menu.insert_item( 1, Gio.MenuItem.new( _("save timetable"), "win.save" ) )
        menu.insert_item( 2, Gio.MenuItem.new( _("new timetable"), "win.new" ) )
        menu.insert_item( 3, Gio.MenuItem.new( _("save and quit"), "win.quit_save" ) )
        menu.insert_item( 4, Gio.MenuItem.new( _("quit without saving"), "win.quit_without_saving" ) )
        menu.insert_item( 5, Gio.MenuItem.new( _("About Timetable"), "win.about" ) )


        #menu button
        button = Gtk.MenuButton.new()
        popover = Gtk.Popover.new_from_model(button, menu)
        button.set_popover(popover)
        icon = Gio.ThemedIcon(name="open-menu-symbolic")
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        button.add(image)
        self.hb.pack_end(button)

        # settings button
        button = SettingsButton(window=self)
        self.hb.pack_end(button)

        # help-button
        button = Gtk.Button()
        icon = Gio.ThemedIcon(name="help-browser-symbolic")
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        button.add(image)
        button.connect("clicked", self.__helpClicked)
        self.hb.pack_end(button)

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        Gtk.StyleContext.add_class(box.get_style_context(), "linked")


        # left previous week
        button = Gtk.Button()
        button.add(Gtk.Arrow(Gtk.ArrowType.LEFT, Gtk.ShadowType.NONE))
        box.add(button)
        button.connect("clicked", self.__prevWeekclicked)

        # right: next week
        button = Gtk.Button()
        button.add(Gtk.Arrow(Gtk.ArrowType.RIGHT, Gtk.ShadowType.NONE))
        box.add(button)
        button.connect("clicked", self.__nextWeekclicked)

        # current week
        button = Gtk.Button()
        icon = Gio.ThemedIcon(name="document-open-recent-symbolic")
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        button.add(image)
        box.add(button)
        button.connect("clicked", self.__currentWeekclicked)

        #################
        #################
        ################# test button: only enable, if in debug-mode
        if self.environment.setting_debug() == True:
            button = Gtk.Button()
            icon = Gio.ThemedIcon(name="view-refresh")
            image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
            button.add(image)
            box.add(button)
            button.connect("clicked", self.__testclicked)
            self.test = False
        #################
        #################
        #################

        self.hb.pack_start(box)

    #################
    #################
    ################# test button: only enabled, if in debug-mode
    def __testclicked(self, button):
        self.environment.timeTab.getDatesByTopic("Federkraft")
    #################
    #################
    #################


    def __about(self, wid, action):
        """Creates and displays an about-dialog, when the about-action is
        activated. This is done by the user in the menu.
        """
        #dbglog("about")
        # a  Gtk.AboutDialog
        aboutdialog = Gtk.AboutDialog()
        aboutdialog.set_destroy_with_parent(True)

        authors = ["Ulrich Leutner"]
        documenters = ["Ulrich Leutner"]

        # we fill in the aboutdialog
        aboutdialog.set_program_name(_("Timetable"))
        aboutdialog.set_copyright(
            "Copyright 2020 Ulrich Leutner")
        aboutdialog.set_authors(authors)
        aboutdialog.set_license_type(Gtk.License.GPL_3_0)
        #aboutdialog.set_documenters(documenters)
        aboutdialog.set_website("http://github.com/kaschpal/timetable")
        aboutdialog.set_website_label("GitHub Page")
        aboutdialog.set_title("")
        aboutdialog.set_logo_icon_name("io.github.kaschpal.timetable")

        # to close the aboutdialog when "close" is clicked we connect the
        # "response" signal to on_close
        aboutdialog.connect("response", lambda x, y: x.destroy())

        # show
        aboutdialog.show()

    def __nextWeekclicked(self, button):
        """When clicked on next-week-button, shift for one week in the
        timetable.
        """
        nxdate = self.weekWid.date + datetime.timedelta(weeks=1)
        self.weekWid.setDate(nxdate)

    def __helpClicked(self, button):
        """When clicked on next-week-button, shift for one week in the
        timetable.
        """
        try:
            Gtk.show_uri(None, "help:timetable", Gdk.CURRENT_TIME)
        except GLib.Error:
            dbglog("Help handler not available.")

    def __prevWeekclicked(self, button):
        """When clicked on previous-week-button, shift for one week in the
        timetable.
        """
        nxdate = self.weekWid.date - datetime.timedelta(weeks=1)
        self.weekWid.setDate(nxdate)

    def __currentWeekclicked(self, button):
        """When clicked on current-week-button, jump to today in the
        timetable.
        """
        self.weekWid.setToday()

    def __saveClicked(self, button, action):
        """Saves the whole environment to the current file.
        If no file is opened yet (new calendar), the method
        creates a dialog, which askes for a filename.
        """
        # not yet saved, no filename selected
        if self.environment.currentFileName == None:
            filename = self.__chooseFilename()
            if filename == None:
                return

        self.environment.currentFileName = filename
        self.environment.saveCurrentFile()
        self.environment.saveState()
        self.hb.props.title = (_("Timetable") + ": " + filename)

    def __chooseFilename(self):
        """Creates and displays an diaglog, which ask for a filename."""
        # choose new filename and directory
        dialog = Gtk.FileChooserDialog(_("Please choose file"), self,
                                       Gtk.FileChooserAction.SAVE,
                                       (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                        Gtk.STOCK_SAVE, Gtk.ResponseType.OK))
        dialog.set_current_name(_("New.p"))

        # add filters for pickle-files an all files
        filter_p = Gtk.FileFilter()
        filter_p.set_name(_("timetable"))
        filter_p.add_mime_type("text/x-python")
        filter_p.add_pattern("*.p")
        dialog.add_filter(filter_p)

        filter_all = Gtk.FileFilter()
        filter_all.set_name(_("all files"))
        filter_all.add_pattern("*")
        dialog.add_filter(filter_all)

        # display dialog
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            filename = dialog.get_filename()
        elif response == Gtk.ResponseType.CANCEL:
            filename = None
        else:
            filename = None

        dialog.destroy()
        return filename


    def __newClicked(self, button, action):
        """Creates a new calendar without saving the current.
        Asks for a filename immediatley.
        """
        filename = self.__chooseFilename()

        if filename is None:
            return

        # delete everything
        self.environment.clear()

        # save under new filename
        self.environment.currentFileName = filename
        self.environment.saveCurrentFile()
        self.environment.saveState()
        self.environment.loadFile( self.environment.currentFileName )


    def __loadClicked(self, button, action):
        """Creates and displays an diaglog, which ask for a filename to load.
        The current file is not saved and the new file is loaded into the
        environment."""
        # create open dialog
        dialog = Gtk.FileChooserDialog(_("Please choose file"), self,
                                       Gtk.FileChooserAction.OPEN,
                                       (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

        # add filters for pickle-files an all files
        filter_p = Gtk.FileFilter()
        filter_p.set_name(_("timetable"))
        filter_p.add_mime_type("text/x-python")
        filter_p.add_pattern("*.p")
        dialog.add_filter(filter_p)

        filter_all = Gtk.FileFilter()
        filter_all.set_name(_("all files"))
        filter_all.add_pattern("*")
        dialog.add_filter(filter_all)






        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            filename = dialog.get_filename()
            self.environment.loadFile(filename)
        elif response == Gtk.ResponseType.CANCEL:
            filename = None
            pass
        dialog.destroy()

        #dbglog(str(filename))

    def quit(self, wid):
        """Quits the application. If quit-on-save is activated, saves."""
        if self.environment.setting_save_on_quit() == True:
            self.__quit_save(self, None)
        else:
            self.__quit_without_saving(self, None)

    def __quit_without_saving(self, wid, action):
        """Quits the application without saving."""
        dbglog("quit without saving")
        self.environment.saveState()
        self.application.quit()
        #Gtk.main_quit()

    def __quit_save(self, wid, action):
        """Quits the application with saving."""
        dbglog("quit save")
        # no filename choosen yet
        if self.environment.currentFileName == None:
            filename = self.__chooseFilename()
            if filename == None:
                return
            else:
                self.environment.currentFileName = filename

        self.environment.saveCurrentFile()
        self.environment.saveState()
        self.application.quit()
        #Gtk.main_quit()


class SettingsButton(Gtk.Button):
    """Beeing a bit complex, the settings menu has its own class."""

    def __init__(self, window):
        Gtk.Button.__init__(self)
        self.window = window

        # set icon
        icon = Gio.ThemedIcon(name="preferences-system-symbolic")
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        self.add(image)

        self.__popover = Gtk.Popover()
        grid = Gtk.Grid()
        grid.props.column_spacing = 5

        # spinbutton for number of periods per day
        lab = Gtk.Label(_("periods to show"))
        lab.props.halign = Gtk.Align.START
        grid.attach(lab, 0, 0, 1, 1)
        spin = Gtk.SpinButton()
        # get min / max value
        minval, maxval = self.window.environment.settings.get_range("number-of-periods-show")[1]
        # adjustment
        adjustment = Gtk.Adjustment(0, minval, maxval, 1, 1, 0)
        spin.set_adjustment(adjustment)
        self.window.environment.settings.bind("number-of-periods-show", spin, "value", Gio.SettingsBindFlags.DEFAULT)
        grid.attach(spin, 1, 0, 1, 1)
        # immediately show/hide
        spin.connect("value-changed", self.__show_hide_lines)

        # switch for "show saturday"
        lab = Gtk.Label(_("show saturday"))
        lab.props.halign = Gtk.Align.START
        grid.attach(lab, 0, 1, 1, 1)
        sw = Gtk.Switch()
        self.window.environment.settings.bind("show-saturday", sw, "active", Gio.SettingsBindFlags.DEFAULT)
        grid.attach(sw, 1, 1, 1, 1)
        # immediately show/hide
        sw.connect("state-set", self.__show_hide_sat)

        # switch for "autosave on quit"
        lab = Gtk.Label(_("save when quitting"))
        lab.props.halign = Gtk.Align.START
        grid.attach(lab, 0, 2, 1, 1)
        sw = Gtk.Switch()
        self.window.environment.settings.bind("save-on-quit", sw, "active", Gio.SettingsBindFlags.DEFAULT)
        grid.attach(sw, 1, 2, 1, 1)

        # switch for "debug mode"
        #lab = Gtk.Label(_("debug mode"))
        #lab.props.halign = Gtk.Align.START
        #grid.attach(lab, 0, 3, 1, 1)
        #sw = Gtk.Switch()
        #self.window.environment.settings.bind("debug", sw, "active", Gio.SettingsBindFlags.DEFAULT)
        #grid.attach(sw, 1, 3, 1, 1)

        # signals
        self.__popover.add(grid)
        self.__popover.connect("map", self.__open)
        self.__popover.connect("closed", self.__close)
        self.connect("clicked", self.__togglePopup)

    def __show_hide_sat(self, sw, state):
        """Displays or hides the daygrid for the saturday.
        "stat" is True, if it should be displayed.
        This is called with a signal, when the button changes.
        """
        if state == True:
            self.window.weekWid.sat.show()
        else:
            self.window.weekWid.sat.hide()

    def __show_hide_lines(self, spin):
        """Changes the number of periods to display in the daygrid.
        This is called with a signal, when the spin-button "spin" changes.
        """
        value = int(spin.props.value)
        for day in self.window.weekWid.widList:
            day.set_to_line(value)

    def update(self):
        """Dummy method, when called via the updatelist from the parent"""
        pass

    def __close(self, popover):
        """Dummy method for testing"""
        pass

    def __open(self, popover):
        """Dummy method for testing"""
        pass

    def __togglePopup(self, button):
        """Displays or hides the settings-menu, when the "button" is clicked.
        Called by a signal."""
        self.__popover.set_relative_to(button)
        self.__popover.show_all()
        self.__popover.popup()


class Environment():
    """The environment is the representation of the state of the application.
    The environment loads the settings from the gsettings schema and the timetable database
    from the timetable file.
    """
    def __init__(self, parent):
        """
        schema_source = Gio.SettingsSchemaSource.new_from_directory(config.programDirectory,
                                                                    Gio.SettingsSchemaSource.get_default(), False)
        schema = Gio.SettingsSchemaSource.lookup(schema_source, 'de.gymlan.timetable', False)
        if not schema:
            raise Exception("Cannot get GSettings  schema")
        self.settings = Gio.Settings.new_full(schema, None, config.dconfPath)
        """
        self.settings = Gio.Settings.new('io.github.kaschpal.timetable')
        dbglog(self.settings.list_keys())

        self.parent = parent
        self.timeTab = TimeTableStore(environment=self)
        self.loadState()

    def saveFile(self, filename):
        """Saves timetable to "filename"."""
        self.timeTab.saveToFile( filename )

    def saveCurrentFile(self):
        """Saves timetable to current filename."""
        self.saveFile(self.currentFileName)

    def loadFile(self, filename):
        """Load the timetable from "filename" and sets the title of the window.
        After that, everything is updated."""
        if filename == None or self.timeTab.loadFromFile(filename) == False:
            try:
                self.parent.hb.props.title
            except AttributeError:
                pass
            else:
                self.parent.hb.props.title = (_("Timetable") + ": " + "(neu)")
            self.currentFileName = None
            return

        # update, if widgets are already created (maybe this is the first call)
        try:
            self.parent.weekWid.update()
        except AttributeError:
            pass
        else:
            self.parent.weekWid.update()

        try:
            self.parent.hb.props.title
        except AttributeError:
            pass
        else:
            self.parent.hb.props.title = (_("Timetable") + ": " + filename)

        # set new filename in statefile
        self.currentFileName = filename

    def saveState(self):
        """There has been a statefile, which held the current filname. Now this
        current filename is saved to the settings. Did not rename the method.
        """
        self.settings.set_string("current-filename", self.currentFileName)

    def loadState(self):
        """There has been a statefile, which held the current filname. Now this
        current filename is saved to the settings. Did not rename the method.
        This method loads the timetable from the filename in the settings and
        sets the .currentFilename.
        """
        self.currentFileName = self.setting_current_filename()
        if self.currentFileName == "":
            self.currentFileName = None
        self.loadFile(self.currentFileName)

    def clear(self):
        """Creates an empty Environment und updates."""
        #self.__saveEmptyState()
        self.loadState()
        self.timeTab.clear(self)
        self.parent.weekWid.update()

    def setting_number_of_periods_show(self):
        """Method for retrieving settings."""
        return self.settings.get_int('number-of-periods-show')

    def setting_number_of_periods_create(self):
        """Method for retrieving settings."""
        return self.settings.get_int('number-of-periods-create')

    def setting_show_saturday(self):
        """Method for retrieving settings."""
        return self.settings.get_boolean('show-saturday')

    def setting_debug(self):
        """Method for retrieving settings."""
        return self.settings.get_boolean('debug')

    def setting_save_on_quit(self):
        """Method for retrieving settings."""
        return self.settings.get_boolean('save-on-quit')

    def setting_current_filename(self):
        """Method for retrieving settings."""
        return self.settings.get_string('current-filename')
