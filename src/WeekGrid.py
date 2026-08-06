import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk
import datetime
from . import config
from .DayGrid import DayGrid
from .config import dbglog


class WeekGrid(Gtk.Grid):
    """This view arranges all weekdays in a grid."""
    def __init__(self, date, window):
        Gtk.Grid.__init__(self)

        self.date = date
        self.window = window
        self.widList = []

        # some space between the columns of the grid
        self.set_column_spacing(2)

        # start with moday of the week in which the date lays
        self.mondayDate = date - datetime.timedelta(days=date.weekday())

        self.mon = DayGrid( self.mondayDate, parent=self )
        self.tue = DayGrid( self.mondayDate + datetime.timedelta(days=1), parent=self )
        self.wed = DayGrid( self.mondayDate + datetime.timedelta(days=2), parent=self )
        self.thu = DayGrid( self.mondayDate + datetime.timedelta(days=3), parent=self )
        self.fri = DayGrid( self.mondayDate + datetime.timedelta(days=4), parent=self )
        self.sat = DayGrid( self.mondayDate + datetime.timedelta(days=5), parent=self )

        self.widList = [self.mon, self.tue, self.wed, self.thu, self.fri, self.sat]

        vsep1 = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)
        vsep2 = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)
        hsep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)

        self.attach(self.mon, 0, 0, 1, 1)
        self.attach(self.thu, 0, 2, 1, 1)

        self.attach(vsep1, 1, 0, 1, 3)

        self.attach(self.tue, 2, 0, 1, 1)
        self.attach(self.fri, 2, 2, 1, 1)

        self.attach(vsep2, 3, 0, 1, 3)

        self.attach(self.wed, 4, 0, 1, 1)
        self.attach(self.sat, 4, 2, 1, 1)

        self.attach(hsep, 0, 2, 11, 1)

        # if the weekday is a sunday (or saturday), go to the next week
        self.setToday()


    def update(self):
        """Sets the right date (could have changed) and
        calls update() on all daygrids in the week and displays the
        saturday, if desired.
        """
        for wid in self.widList:
            if wid is self.mon:
                nxdate = self.mondayDate
            elif wid is self.tue:
                nxdate = self.mondayDate + datetime.timedelta(days=1)
            elif wid is self.wed:
                nxdate = self.mondayDate + datetime.timedelta(days=2)
            elif wid is self.thu:
                nxdate = self.mondayDate + datetime.timedelta(days=3)
            elif wid is self.fri:
                nxdate = self.mondayDate + datetime.timedelta(days=4)
            elif wid is self.sat:
                nxdate = self.mondayDate + datetime.timedelta(days=5)
            else:
                nxdate = None

            wid.date = nxdate
            wid.update()

        # should we show the saturday?
        if self.window.environment.setting_show_saturday() == True:
            self.sat.set_visible(True)

    def setToday(self):
        """Adjust the week so it contains today.

        If today is Saturday or Sunday, advance to the next week so the view
        shows the upcoming week instead of the weekend of the current week.
        Then refresh child widgets.
        """
        today = datetime.date.today()
        # If today is Saturday (5) or Sunday (6), show the next week
        if today.weekday() >= 5:
            self.mondayDate = self.mondayDate + datetime.timedelta(days=7)
        # Ensure child widgets reflect the (possibly updated) mondayDate
        self.update()
