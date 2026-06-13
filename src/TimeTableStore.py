import gi
gi.require_version('Gtk', '4.0')
#from gi.repository import Gtk, Gio
import copy
from . import config
from .config import dbglog
import pickle
import re
import datetime
import operator
import json
import dateutil.tz as dtz


class TimeTableStore():
    """ This class stores the timetable and all classes. """

    def __init__(self, environment):
        """Creates a new timetable. "env" is the Environment() as to find in
        MainWindow.py.
        """
        self.environment = environment

        periodsInd = range(1, self.environment.setting_number_of_periods_create()+1)
        weekdaysInd = range(1, 7)

        # create list of empty listes of the periods
        # the format of the tuple is (date, name)
        # date is the day, from which on the name is valid

        initclass = (config.epoch, "")      # default classname is an emptry string
        l = [ [ initclass ] for i in periodsInd]

        # fill each period with an empty list
        periodDict = dict( zip( periodsInd, l ) )

        # fill each dey with the dict of empty periods
        l = [ copy.deepcopy( periodDict ) for i in weekdaysInd]
        self.__tt = dict(zip(weekdaysInd, l))

        # repeat for the dot-entries
        l = [ copy.deepcopy( periodDict ) for i in weekdaysInd]
        self.__dottt = dict(zip(weekdaysInd, l))

        # create the list with off days
        self.__dayOff = []

        # create the list with of sequences
        self.__sequences = dict()

        # create the list of calendar-entries
        self.__calendarEntries = dict()


    def clear(self, env):
        """Resets the timetable to a new one. "env" is the Environment() as to find
        in MainWindow.py.
        """
        self.__init__(env)

    def getClassName(self, date, period):
        """Returns the valid classname for a "date" and "period"."""
        weekday = date.isoweekday()

        # at first, try, if it is a dot entry. it has to be at
        # the exact date
        classNameList = self.__dottt[weekday][period]
        for ld, ln in classNameList:
            if ld == date:
                return ln

        # at second, try it for the regular timetable
        classNameList = self.__tt[weekday][period]
        # iterate over all ever injected classes from behind
        rClassNameList = reversed(classNameList)

        for ldate, lname in rClassNameList:
            # match
            if date >= ldate:
                return lname



    def dayOff(self, date):
        """Returns True, if the dates is marked as off-school."""
        if date in self.__dayOff:
            return True
        else:
            return False


    def addDayOff(self, date):
        """Add the date to the list of off-school days."""
        self.__dayOff.append(date)

    def removeDayOff(self, date):
        """Removes the date from the list of off-school days."""
        self.__dayOff.remove(date)


    def classNameIsEdited(self, date, period):
        """Returns True, if the classname has been edited at the given date
        and period.
        The class entry is painted coloured by the daygrid, if.
        """
