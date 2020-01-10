import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
import datetime
from . import config
from .config import dbglog
import calendar

class Calendar(Gtk.Box):
    """Calendar-Wiget for navigation and memos"""

    def __init__(self, parent):
        """Creates a new calendar-widget. It consists of a view for the calendar itself and a textfield, in
        which the memos are written.
        """
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)
        self.parent = parent

        self.textview = MemoView(parent=self)
        self.calendar = MemoCalendar(parent=self)
        self.pack_start(self.calendar, False, True, 0)

        self.pack_start(self.textview, True, True, 0)
        self.connect("map", self.__showHandler)

    def __showHandler(self, wid):
        """calls .update(). May be added more functionality."""
        self.update()

    def update(self):
        """Updates the calendar. Calls "show" on iteself und .update() on the
        textview and the calendar.
        """
        self.show_all()
        self.textview.update()
        self.calendar.update()

class MemoCalendar(Gtk.Calendar):
    """Actual calendar where the days with memo are marked"""

    def __init__(self, parent):
        Gtk.Calendar.__init__(self)
        self.parent = parent
        self.connect("day-selected", self.__selectHandler)
        self.connect("day-selected-double-click", self.__doubleclickHandler)
        self.connect("month-changed", self.update)

        # call selection handler on current (initial) selection
        self.__selectHandler(self)

    def __getSelectedDate(self):
        """Returns date of the selected day as pythondatetime-object."""
        d = self.props.day
        m = self.props.month+1
        y = self.props.year
        return datetime.date(day=d,month=m,year=y)

    def __selectHandler(self, wid):
        """Is called, when the selected day changes.
        Saves changes in the current textbuffer before switching. Then the currentSelectionDate is updated.
        """
        txt = self.parent.textview.getText()
        try:
            self.parent.textview.save()
        except AttributeError:   # on first call (at initialisation) the calendar does not exist yet
            pass
        # needed by the textview
        self.currentSelectionDate = self.__getSelectedDate()
        # set textwid to selected entry
        self.parent.textview.loadEntry(self.currentSelectionDate)
        # if saved, update marks
        #if txt != "":
        self.update()

    def __doubleclickHandler(self, wid):
        """Called on doubleclick at a day. Sets timetable to the dclicked
        week/day and switch to it."""
        # set selected date in timetable
        date = self.__getSelectedDate()
        self.parent.parent.weekWid.setDate(date)
        # switch to timetable
        self.parent.parent.stack.set_visible_child_name("timetable")


    def update(self, wid=None):
        """Marks all days, which have a memo."""
        dbglog("cal update")

        m = self.props.month + 1
        y = self.props.year

        # determine how many days the current month has
        last = calendar.monthrange(y, m)[1]

        self.clear_marks() # remove all previous
        # mark days with entry
        for d in range(1, last+1):
            if self.parent.parent.environment.timeTab.getCalendarEntry(datetime.date(day=d,month=m,year=y)) != "":
                self.mark_day(d)


class MemoView(Gtk.TextView):
    """The textfiled, where the memos are edited."""

    def __init__(self, parent):
        Gtk.TextView.__init__(self)

        self.buffer = Gtk.TextBuffer()
        self.set_buffer(self.buffer)
        self.parent = parent
        # when disappearing, save content
        self.connect("unmap", self.save)

    def loadEntry(self, date):
        """Loads the string, which belongs to "date" into the textbuffer"""
        s = self.parent.parent.environment.timeTab.getCalendarEntry(date)
        self.buffer.set_text(s)

    def update(self):
        """Looks into the calendar, which day is marked and loads this memo-string."""
        date = self.parent.calendar.currentSelectionDate
        self.loadEntry(date)

    def save(self, wid=None):
        """Saves the current memo-string into the timetablestore."""
        txt = self.getText()
        date = self.parent.calendar.currentSelectionDate
        self.parent.parent.environment.timeTab.putCalendarEntry(date, txt)

    def getText(self):
        """Gets the text from the buffer as a string."""
        start = self.buffer.get_start_iter()
        end = self.buffer.get_end_iter()
        return self.buffer.get_text(start, end, False)











