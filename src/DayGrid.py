import gi
import gettext
from gettext import gettext as _

gi.require_version('Gtk', '4.0')
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
        offBox.append(dateLab)

        self.offToggle = Gtk.CheckButton()
        self.__offDayHandler = self.offToggle.connect("toggled", self.__offButtonToggled)
        offBox.append(self.offToggle)

        # calendar-button
        button = CalendarButton(parent=self)
        offBox.append(button)
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

        # darken, if off
        if not self.offToggle.get_active():
            classEnt.set_sensitive(False)
            topicEnt.set_sensitive(False)

        # keep track
        self.__number_of_rows = self.__number_of_rows + 1


    def remove_last_line(self):
