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
        weekday = date.isoweekday()
        classNameList = self.__dottt[weekday][period]

        # search for dot-entries (theese are always edited)
        for ld, ln in classNameList:
            if ld == date and ln != "":
                return True

        # at second, try it for the regular timetable
        classNameList = self.__tt[weekday][period]
        # only check the last entry
        if len(classNameList) >= 2:
            ldate, lname = classNameList[-1]
            if ldate == date and lname != "":
                return True

        return False



    def classNameIsDotEntry(self, date, period):
        """Returns True, if the given classname is a dot-entry."""
        weekday = date.isoweekday()
        classNameList = self.__dottt[weekday][period]
        for ld, ln in classNameList:
            if ld == date:
                return ln
        return False

    def injectClassName(self, date, period, name):
        """Inject a classname for a given date and period.
        If it starts with a dot, it is a dot-entry, which overwrites the regular entry for this specific date.
        """
        weekday = date.isoweekday()
        if name.startswith("."):
            # it is a dot-entry
            name = name[1:]
            # remove all previous entries of this date
            for item in self.__dottt[weekday][period]:
                edate, ename = item
                if edate == date:
                    self.__dottt[weekday][period].remove(item)

            self.__dottt[weekday][period].append((date, name))
            self.__sortListByDate(self.__dottt[weekday][period])
        else:
            # it is a regular entry
            # remove all dot-entries from this date
            for item in self.__dottt[date.isoweekday()][period]:
                edate, ename = item
                if edate == date:
                    self.__dottt[date.isoweekday()][period].remove(item)

            self.__tt[date.isoweekday()][period].append((date, name))
            self.__sortListByDate(self.__tt[date.isoweekday()][period])
            self.__sortListByDate(self.__dottt[date.isoweekday()][period])

        #dbglog(self.__tt[date.isoweekday()][period] )
        #dbglog(self.__dottt[date.isoweekday()][period] )
        dbglog("*** inject" + str(self.getClassName(date, period)))


    def __sortListByDate(self, list):
        """Sorts "list" (__tt or __dottt) by date."""
        list.sort(key=lambda x: x[0])


    def saveToFile(self, filename):
        """Saves the all relevant information of the TimeTableStore as pickle to a file
        named "filename".
        """
        # first, create a dictionary with all tables
        names = ["tt", "dottt", "dayOff", "sequences", "calendarEntries"]
        l = [ self.__tt, self.__dottt, self.__dayOff, self.__sequences, self.__calendarEntries ]

        d = dict( zip( names, l ) )

        pickle.dump(d, open(filename, "wb"))


    def loadFromFile(self, filename):
        """Loads all relevant information of the TimeTableStore as pickle from a file
        named "filename".
        """
        try:
            f = open(filename, "rb")
        except FileNotFoundError:
            dbglog("File not found, leave everything as it is")
            return False

        d = pickle.load(f)

        self.__tt = d["tt"]
        self.__dottt = d["dottt"]
        self.__dayOff = d["dayOff"]
        self.__sequences = d["sequences"]
        self.__calendarEntries = d["calendarEntries"]
        return True


    def getClassList(self):
        """Returns a list of all classnames, which are in the timetable.
        The list is the sorted human-readable.
        """
        l = []

        for day, periods in self.__tt.items():
            for per, dates in periods.items():
                l.extend(dates)

        l = [cl for date, cl in l]  # extract the classnames
        l = list(set(l)) # remove duplicates
        if "" in l:
            l.remove("")    # remove ""-entry
        return self.__sortListHuman(l)


    def __sortListHuman(self, l):
        """Sorts the given iterable "l" in the way that humans expect."""
        convert = lambda text: int(text) if text.isdigit() else text
        alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]
        return sorted(l, key = alphanum_key)

    def __sortListDateAndPeriod(self, l):
        """Sort the given list "l" by the first *and* second element.
        This is used to sort by date and then period.
        """
        l.sort(key = operator.itemgetter(0, 1))

    def getDatesOfClass(self, name, MAXDATES=config.MAXDATES, GRAB_DOTS=True):
        """Returns a list of all dates, on which the class with "name" occours. This is used
        to generate the sequence of the lessons.
        """
        dates = []

        # search in the regular timetable
        for weekday, periods in self.__tt.items():
            for period, dateList in periods.items():
                for date, classname in dateList:
                    if classname == name:
                        dates.append((date, period))

        # search in the dotentries
        if GRAB_DOTS:
            for weekday, periods in self.__dottt.items():
                for period, dateList in periods.items():
                    for date, classname in dateList:
                        if classname == name:
                            dates.append((date, period))

        # sort by date and period
        self.__sortListDateAndPeriod(dates)

        if len(dates) > MAXDATES:
            return dates[-MAXDATES:]
        else:
            return dates


    def getTopic(self, date, period):
        """Returns the topic for the given date and period"""
        try:
            return self.__sequences[date][period]
        except KeyError:
            return ""

    def changeTopic(self, date, period, text):
        """Saves the topic for the given date and period."""
        if date not in self.__sequences:
            self.__sequences[date] = dict()

        self.__sequences[date][period] = text

    def getDatesByTopic(self, name):
        """Returns all dates, on which the given topic appears."""
        result = []
        for date in self.__sequences.keys():
            for period in self.__sequences[date].keys():
                topic = self.__sequences[date][period]
                if name in topic:
                    result.append((date, period, topic))
        return result

    def get_position_in_sequence(self, date, period):
        """Returns the position of the given date and period in the sequence of the classname."""
        classname = self.getClassName(date, period)
        dates_of_class = self.getDatesOfClass(classname)
        try:
            return dates_of_class.index((date, period))
        except ValueError:
            return 0

    def getSequence(self, name):
        """Returns the sequence for the given classname"""
        try:
            return self.__sequences[name]
        except KeyError:
            return []

    def putSequence(self, name, sequence):
        """Saves the sequence for the given classname."""
        self.__sequences[name] = sequence

    def getCalendarEntry(self, date):
        """Returns the memo for the given date."""
        try:
            return self.__calendarEntries[date]
        except KeyError:
            return ""

    def putCalendarEntry(self, date, text):
        """Saves the memo for the given date."""
        self.__calendarEntries[date] = text
