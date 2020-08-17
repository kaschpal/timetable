import gi
import gettext
from gettext import gettext as _

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, Gio
import datetime
from . import config
from .config import dbglog


class DayGrid(Gtk.Grid):
    """This widget represents one day. It consists of the date, a checkbox,
    where the date can be set off-school and a button for a memo.
    Then the lines of the lessons are displayed: Numbering, period, topic of lesson.
    """

    def __init__(self, date, parent):
        Gtk.Grid.__init__(self)
        self.date = date
        self.weekday = date.isoweekday()
        self.__updateList = []
        self.parent = parent
        # gtk.grid does not store this, it is used to remove/add the last line
        self.__number_of_rows = 1   # starts at one, the first has no entries

        # some space between the columns of the grid
        self.set_column_spacing(5)

        # show date and weekday
        dateLab = DateLabel( self )

        # behind the label of the day comes a checkbutton, if the day
        # is off school
        offBox = Gtk.Box(spacing=1)
        offBox.pack_start(dateLab, True, True, 0)

        self.offToggle = Gtk.CheckButton()
        self.__offDayHandler = self.offToggle.connect("toggled", self.__offButtonToggled)
        offBox.pack_start(self.offToggle, True, True, 0)

        # calendar-button
        button = CalendarButton(parent=self)
        offBox.pack_start(button, False, True, 0)
        self.__updateList.append(button)

        self.attach(offBox, 3, 0, 1, 1)
        self.__updateList.append(dateLab)

        # the period-matrix
        for period in range(1,self.parent.window.environment.setting_number_of_periods_show()+1):
            self.__add_line(period)

        # update to see if the day is off school
        self.update()

    def __add_line(self, period):
        """Adds one line to the daygrid at "period".
        This method is called by add_last_line() with the current
        number of periods.
        """
        # three labels
        periodLab = Gtk.Label()
        classEnt = ClassEntry(weekday=self.weekday , period=period, parent=self)
        topicEnt = TopicEntry(weekday=self.weekday , period=period, parent=self)

        # add widgets, which have to be updated automatically
        self.__updateList.append(classEnt)
        self.__updateList.append(topicEnt)

        topicEnt.set_width_chars(config.topicLen)

        periodLab.set_text(str(period))
        classEnt.set_width_chars(6)


        # in the grid:
        self.attach(periodLab, 1, period+1, 1, 1)
        self.attach(classEnt, 2, period+1, 1, 1)
        self.attach(topicEnt, 3, period+1, 1, 1)

        # activate all items. this is necessary, if the lines are added via the settings menu
        periodLab.show()
        classEnt.show()
        topicEnt.show()

        # darken, if off
        if not self.offToggle.get_active():
            classEnt.set_sensitive(False)
            topicEnt.set_sensitive(False)

        # keep track
        self.__number_of_rows = self.__number_of_rows + 1


    def remove_last_line(self):
        """Removes the last line from the grid."""
        self.remove_row(self.__number_of_rows)
        # keep track
        self.__number_of_rows = self.__number_of_rows - 1
        # remove the class- and topic entries from the updatelist
        # otherwise they are not garbage collected AND always updated
        del self.__updateList[-2:]

    def add_last_line(self):
        """Adds one line to the grid."""
        self.__add_line(self.__number_of_rows)

    def set_to_line(self, number):
        """Set number of lines to value "number"."""
        number = number + 1 # the fist row is only counted in the daygrid, not in sense of the method
        if number > self.__number_of_rows: # add lines
            lines_to_add = number - self.__number_of_rows
            for _ in range(0, lines_to_add):
                self.add_last_line()

        elif number < self.__number_of_rows: # remove lines
            lines_to_del = self.__number_of_rows - number
            for _ in range(0, lines_to_del):
                self.remove_last_line()
        else:                               # no change
            pass

    def __offButtonToggled(self, wid):
        """This is the handler for the off-school-button.
        it darkens/brightens the day and sets it inactive/active in the timetable.
        """
        if self.offToggle.get_active() == False:
            self.parent.window.environment.timeTab.addDayOff(self.date)
        else:
            self.parent.window.environment.timeTab.removeDayOff(self.date)

        self.parent.update()




    def update(self):
        """Rereads all information.
        Updates also all widgets, which are registerd in the __updateList,
        means: calls their .update() method.
        """
        # at first, update all widgets
        for wid in self.__updateList:
            wid.update()

        # update the checkbox
        # block because only marking by hand should call the handler
        with self.offToggle.handler_block(self.__offDayHandler):
            if self.parent.window.environment.timeTab.dayOff(self.date):
                self.offToggle.set_active(False)
                for wid in self.__updateList:
                    if type(wid) is not CalendarButton: # dont deactivate the memos
                        wid.set_sensitive(False)
            else:
                self.offToggle.set_active(True)
                for wid in self.__updateList:
                    wid.set_sensitive(True)

        self.offToggle.handler_unblock(self.__offDayHandler)

        # run updates
        for wid in self.__updateList:
            if type(wid) is ClassEntry or type(wid) is TopicEntry:
                # block change signal. this triggers a whole week-update
                with wid.handler_block(wid.changeHandler):
                    wid.update()
                wid.handler_unblock(wid.changeHandler)
            else:
                wid.update()



class CalendarButton(Gtk.Button):
    """The button, which displays the the calendar-memo."""
    def __init__(self, parent):
        Gtk.Button.__init__(self)
        self.parent = parent

        # init icons
        icon = Gio.ThemedIcon(name="io.github.kaschpal.star-grey")
        self.__empty_image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        icon = Gio.ThemedIcon(name="io.github.kaschpal.star-orange")
        self.__not_empty_image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        self.__current_image = None

        # calendar textview
        self.__calBuffer = Gtk.TextBuffer()
        self.__calView = Gtk.TextView(buffer=self.__calBuffer)

        # calendar bubble
        self.__popover = Gtk.Popover()
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        vbox.pack_start(self.__calView, True, True, 10)
        self.__popover.add(vbox)
        self.__popover.connect("map", self.__loadBuf)
        self.__popover.connect("closed", self.__saveBuf)


        self.connect("clicked", self.__togglePopup)
        self.connect("map", self.__loadBuf )
        self.__updateIcon()

    def update(self):
        """Reads the content of the popover bubble and writes ist into the textbuffer."""
        self.__loadBuf(self.__popover)

    def __updateIcon(self):
        """Updates the icon, depending if there is a memo or not."""
        # set icon
        if self.__getText() == "":
            self.__setEmpty()
        else:
            self.__setNotEmpty()
        self.__current_image.show()

    def __saveBuf(self, popover):
        """Saves the content of the textfield to the timetab and updates the icon.
        This is called on close of the bubble.
        """
        self.parent.parent.window.environment.timeTab.putCalendarEntry(self.parent.date, self.__getText())
        self.__updateIcon()

    def __loadBuf(self, popover):
        """On open of the popup, gets the entry from the timetable and updates the textbuffer."""
        memo = self.parent.parent.window.environment.timeTab.getCalendarEntry(self.parent.date)
        self.__calBuffer.set_text(memo)
        self.__updateIcon()


    def __getText(self):
        """Returns the text from the textbuffer as a string."""
        start = self.__calBuffer.get_start_iter()
        end = self.__calBuffer.get_end_iter()
        return self.__calBuffer.get_text(start, end, False)

    def __togglePopup(self, button):
        """Activate popup. This is called on click to the button."""
        self.__popover.set_relative_to(button)
        self.__popover.show_all()
        self.__popover.popup()

    def __setEmpty(self):
        """Sets icon to empty entry, no memo."""
        if self.__current_image is not None:
            self.remove(self.__current_image)
        self.add(self.__empty_image)
        self.__current_image = self.__empty_image

    def __setNotEmpty(self):
        """Sets icon to entry with memo."""
        if self.__current_image is not None:
            self.remove(self.__current_image)
        self.add(self.__not_empty_image)
        self.__current_image = self.__not_empty_image


class ClassEntry(Gtk.Entry):
    """Displays the name of the class"""

    def __init__(self, weekday, period, parent):
        Gtk.Entry.__init__(self)
        self.parent = parent

        self.weekday = weekday
        self.period = period

        self.changeHandler = self.connect("activate", self.__onActivate)
        self.focusOutHandler = self.connect("focus-out-event", self.__onFocusOut)
        #self.changeHandler = self.connect("changed", self.__onChange)

        self.update()



    def __onFocusOut(self, *argv):
        self.__onChange(self)

    def __onActivate(self, entry):
        self.__onChange(entry)

    def __onDel(self, *argv):
        print("*** del")
        print(argv)

    def __onIns(self, *argv):
        print("*** ins")
        print(argv)

    def __onChange(self, entry):
        """Fills the classEntry with the right text."""
        # retrieve the content of the widget
        name = self.get_text()
        period = self.period
        #weekday = entry.weekday

        # first: check, if the entry has changed
        if name.startswith("."):   # cut off dot
            tname = name[1:]
        else:
            tname = name
        if tname == self.parent.parent.window.environment.timeTab.getClassName(date=self.date, period=period):
            return

        # inject the class in the period-table
        self.parent.parent.window.environment.timeTab.injectClassName(date=self.date, period=period, name=name)
        self.update()

        # update the weekgrid, lessons may have shifted
        self.parent.parent.update()

    def update(self):
        """Gets all relevant information from
        the timetable and displayes the classname, if there is one.
        If it is a dot-entry, the dot is added here.
        If the classname is edited at this date, it is displayed red.
        When the day is off-school, the entry is deactivated.
        """
        self.date = self.parent.date

        # if it is a day off, display no text at all
        if self.parent.parent.window.environment.timeTab.dayOff(self.date) == True:
            with self.handler_block(self.changeHandler), self.handler_block(self.focusOutHandler):
                self.set_text("")
            self.handler_unblock(self.changeHandler)
            self.handler_unblock(self.focusOutHandler)
            return

        # set to the last entry
        className = self.parent.parent.window.environment.timeTab.getClassName(self.date, self.period)

        # if it is a dot-entry, display the dot
        if  self.parent.parent.window.environment.timeTab.classNameIsDotEntry(self.date, self.period):
            className = "." + className

        # block signal change while updating text
        with self.handler_block(self.changeHandler), self.handler_block(self.focusOutHandler):
            self.set_text( className )

            # if the class has been set on this day, paint red
            # also, if it is a dot-entry
            if self.parent.parent.window.environment.timeTab.classNameIsEdited(self.date, self.period) or self.parent.parent.window.environment.timeTab.classNameIsDotEntry(self.date, self.period):
                RED = Gdk.Color(50000, 0, 0)
                self.modify_fg(Gtk.StateFlags.NORMAL, RED)
            else:
                self.modify_fg(Gtk.StateFlags.NORMAL, None)

        self.handler_unblock(self.changeHandler)
        self.handler_unblock(self.focusOutHandler)



class TopicEntry(Gtk.Entry):
    """Displays the topic of the lesson."""
    def __init__(self, weekday, period, parent):
        Gtk.Entry.__init__(self)
        self.parent = parent

        self.weekday = weekday
        self.period = period
        self.changeHandler = self.connect("changed", self.__onChange)
        #self.connect("button-press-event", self.__onDoubleClick)
        #self.connect("motion-notify-event", self.__on_move_cursor)
        self.connect("key-press-event",self.__on_jump)

        self.update()

    def __onChange(self, entry):
        """Fills the topicEntry with the right text."""
        topic = self.get_text()
        period = self.period
        date = self.parent.date

        # inject the class in the period-table
        self.parent.parent.window.environment.timeTab.changeTopic(date, period, topic)
        self.update()

    def __on_jump(self, widget, event):
        # check the event modifiers (can also use SHIFTMASK, etc)
        ctrl = (event.state & Gdk.ModifierType.CONTROL_MASK)

        # see if we recognise a keypress
        if ctrl and event.keyval == Gdk.KEY_j:
            nb = self.parent.parent.window.classNoteb
            nb.update_tabs()   # if the sequence view has never been started, the tabs are not created yet

            # class tab to jump to
            class_name = self.parent.parent.window.environment.timeTab.getClassName(self.date, self.period)

            # line number to jump to
            position = self.parent.parent.window.environment.timeTab.get_position_in_sequence(self.date, self.period)

            # prevent jumping to solo-dot-classes
            if class_name not in self.parent.parent.window.environment.timeTab.getClassList():
                return

            # to sequence view to class
            self.parent.parent.window.stack.set_visible_child_name("sequence")
            nb.switch_to_tab(class_name)

            # focus
            tab = nb.get_tab(class_name)
            tv = tab.sequenceTextView
            tv.grab_focus()
            #print("focus = " + str(tv.has_focus()))
            #print("tv = " + str(tv))

            # set postion in textfield
            cursor = tab.sequenceBuf.get_iter_at_line(position)
            res = tv.scroll_to_iter(cursor, 0.0, True, 0.5, 0.5)
            tab.sequenceBuf.place_cursor(cursor)

            # select line
            line_begin = tab.sequenceBuf.get_iter_at_line(position) # again, since forward_to_line does not return a copy
            cursor.forward_to_line_end()
            tab.sequenceBuf.select_range(line_begin, cursor)

            print(res)
            #


    def update(self):
        """Gets all relevant information from
        the timetable and displayes the topic, if there is one.
        When the day is off-school, the entry is deactivated.
        """
        self.date = self.parent.date

        # if it is a day off, the display no text at all
        if self.parent.parent.window.environment.timeTab.dayOff(self.date) == True:
            with self.handler_block(self.changeHandler):
                self.set_text( "" )
            self.handler_unblock(self.changeHandler)
            return

        # block signal change while updating text
        with self.handler_block(self.changeHandler):
            self.set_text( self.parent.parent.window.environment.timeTab.getTopic(self.date, self.period) )
        self.handler_unblock(self.changeHandler)

class DateLabel(Gtk.Label):
    """Displays the date in an fancy format. This class is
    mostly defined to be a bit cleaner and write lesser code to the DayGrid.
    """
    def __init__(self, parent):
        Gtk.Label.__init__(self)
        self.parent = parent
        self.update()

    def update(self):
        """Read the date from the parent (DayGrid) and
        displays it in a string including the Weekday.
        A *today* is added, if it is today.
        """
        self.date = self.parent.date
        weekday = self.date.isoweekday()
        dayName = config.weekdays[weekday]

        # if today, write this behind the date
        if self.date == datetime.date.today():
            todayTag = "(" + _("today") + ")"
        else:
            todayTag = ""

        # text to be displayed over the day
        self.set_text('{}, {}.{}. {}'.format(dayName, self.date.day, self.date.month, todayTag) )

        # and write todays date bold
        if self.date == datetime.date.today():
            self.set_markup("<b>" + self.get_text() +"</b>")
