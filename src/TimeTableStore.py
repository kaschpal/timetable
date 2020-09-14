import gi
gi.require_version('Gtk', '3.0')
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
        classNameList = self.__tt[weekday][period]

        # iterate over all ever injected classes from behind
        rClassNameList = reversed(classNameList)

        for ldate, lname in rClassNameList:
            if date == ldate:
                return True
        return False

    def classNameIsDotEntry(self, date, period):
        """Returns True, if the classname at the date and period is a dot-entry."""
        weekday = date.isoweekday()
        classNameList = self.__dottt[weekday][period]

        # iterate over all ever injected classes from behind
        for ldate, lname in classNameList:
            if date == ldate:
                return True
        return False


    def injectClassName(self, date, period, name):
        """Inject the classname for "date" and "period" in the list __tt or __dottt.
        After appending to the list, the list is refreshed / sorted.
        """
        # at first, decide, if it is a dot-entry or regluar
        if name.startswith("."):
            #puttab = self.__dottt
            #puttabother = self.__tt
            # remove dot
            name = name[1:]
            # if the injected date is at the exact date of an already existing,
            # the existing is replaced
            # without this, the correct classname is displayed and retrieved,
            # but there can be zombie-classnames in the list, which are no more used
            for item in self.__dottt[date.isoweekday()][period]:
                edate, ename = item
                if edate == date:
                    self.__dottt[date.isoweekday()][period].remove(item)

            # the item can also exist in the  not-dotlist
            for item in self.__tt[date.isoweekday()][period]:
                edate, ename = item
                if edate == date and ename != "":
                    self.__tt[date.isoweekday()][period].remove(item)

            self.__dottt[date.isoweekday()][period].append((date, name))

            self.__sortListByDate(self.__dottt[date.isoweekday()][period])
            self.__sortListByDate(self.__tt[date.isoweekday()][period])
        else:
            # if the injected date is at the exact date of an already existing,
            # the existing is replaced
            # without this, the correct classname is displayed and retrieved,
            # but there can be zombie-classnames in the list, which are no more used
            # ONE EXCEPTION: ""-termination-entries are kept
            for item in self.__tt[date.isoweekday()][period]:
                edate, ename = item
                if edate == date and ename != "":
                    self.__tt[date.isoweekday()][period].remove(item)

            # the item can also exist in the dotlist or not-dotlist
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
        "MAXDATES" specifies how many dates should be generated. If the classname at a given
        weekday/period is never terminated, there would be infinate dates.
        "GRAB_DOTS" can be False, if the dot-entries should be omitted.
        """
        # list of dates, where the  classname occurs
        # the format is (date, period)
        occurls = []
        retdates = []

        # cycle through the whole timetable to find all occurences of "name"
        for day in self.__tt:
            for period in self.__tt[day]:
                l = self.__tt[day][period]   # all lists of dates: 6 weekdays, 10 periods

                for curdate, curname in l:
                    if curname == name:     # hit
                        occurls.append( (curdate, period)  )

        # now for every hit, count up one week, two weeks, ...  until there is the next
        for curdate, curperiod in occurls:
            # at first, find position n in list
            # get the list l, where the name occurs and
            l = self.__tt[curdate.isoweekday()][curperiod]
            n = l.index( (curdate, name) )

            # add the fist date now
            retdates.append( (curdate, curperiod) )

            # list of all dates in the list
            datesInl = [ x for x, y in l  ]

            i = 1
            while curdate + datetime.timedelta(weeks=i) not in datesInl:
                retdates.append( (curdate + datetime.timedelta(weeks=i), curperiod)  )
                i = i + 1

                # if too many
                if len(retdates) > MAXDATES or i > config.maxdates_repeat:
                    break

        # if desired, also grab the dot-entries
        # the dot-entries are not tested for MAXDATE, since there is no real
        # danger of infinite entries
        if GRAB_DOTS == True:
            for day in self.__dottt:
                for period in self.__dottt[day]:
                    l = self.__dottt[day][period]   # all lists of dates: 6 weekdays, 10 periods

                    for curdate, curname in l:
                        if curname == name:     # hit
                            retdates.append( (curdate, period)  )
            # remove possible duplicates
            retdates = list( set(retdates) )
            # the additional dot-entries require sorting by date AND period
            self.__sortListDateAndPeriod( retdates )

        # here go all dates, which are to be removed
        removelist = []

        # remove off-days
        for d, p in retdates:
            if d in self.__dayOff:
                removelist.append( (d, p) )

        # now check for each entry, if there is a conflicting dot-entry, which
        # overrides the class, while counted till the next week.
        # therefor simpliy check, if getClassname return the same result
        for d, p in retdates:
            if self.getClassName(d, p) != name:
                removelist.append( (d, p) )

        # throw out
        retdates = [x for x in retdates if x not in removelist]

        # cut off the list for the fist MAXDATE entries
        retdates = retdates[0:MAXDATES]

        return retdates

    def putSequence(self, className, l):
        """Add or overwrite the list of the sequence for the class with name "className"
        "l" is simply a ordered list of strings with the topics of the lessons.
        The list is served by the editor-view of the sequence-window.
        """
        self.__sequences[className] = l


    def getSequence(self, className):
        """Returns the list of a sequence for a given class. If the class does not exist
        yet, returns an empty list.
        The list is simply a ordered list of strings with the topics of the lessons
        and used by the editor-view of the sequence-window.
        """
        try:
            l = self.__sequences[className]
        except KeyError:
            return []
        return l


    def putCalendarEntry(self, date, memo):
        """Add or overwrite the calendar-entry for a "date"
        The "memo" is a simple string.
        """
        self.__calendarEntries[date] = memo
        self.__cleanCalendar()   # remove ""s


    def __cleanCalendar(self):
        """Cleans the calendar from ""-strings. These appear, when
        the entry is deleted from the calendar-view or the bubble.
        """
        dellist = []

        # search for ""-strings
        for date in self.__calendarEntries:
            if self.__calendarEntries[date] == "":
                dellist.append(date)
        # remove
        for date in dellist:
            self.__calendarEntries.pop(date)


    def getCalendarEntry(self, date):
        """Returns the memo-string for a given "date".
        If the date does not exist in the dictionry, returns "".
        """
        try:
            s = self.__calendarEntries[date]
        except KeyError:
            return ""
        return s


    def getTopic(self, date, period):
        """Returns the topic for the lesson at a given "date" and "period".
        This is displayed at the the topic-entry in the daygrid.
        """
        classname = self.getClassName(date, period)

        # get the dates of the class
        dateslist = self.getDatesOfClass(classname, GRAB_DOTS=True)

        # get the sequene of the class
        seqlist = self.getSequence(classname)

        # zip cuts off, when one list is longer
        combi = zip( dateslist, seqlist)

        # search for the date and period
        for entry in combi:
            d, p = entry[0]  # date, period
            topic = entry[1]

            if d == date and p == period:
                return topic

        # else
        return ""

    def get_position_in_sequence(self, date, period):
        """Returns the position of the topic in the sequence.
        This is used to jump from a topic in the timetable view into the sequence view.
        The first topic numbered as 0.
        """
        classname = self.getClassName(date, period)

        # get the dates of the class
        dateslist = self.getDatesOfClass(classname, GRAB_DOTS=True)

        # get the sequene of the class
        seqlist = self.getSequence(classname)

        # zip cuts off, when one list is longer
        combi = zip( dateslist, seqlist)

        i = 0
        # search for the date and period
        for entry in combi:
            d, p = entry[0]  # date, period
            topic = entry[1]

            if d == date and p == period:
                return i
            i = i + 1



    def changeTopic(self, date, period, topic):
        """Set the topic to the string "topic" for a certain "date" and "period".
        This is used by the at the the topic-entry in the daygrid.
        """
        classname = self.getClassName(date, period)

        # get the dates of the class
        dateslist = self.getDatesOfClass(classname, GRAB_DOTS=True)
        # get the sequene of the class
        seqlist = self.getSequence(classname)

        # find the right entry
        i = 0
        for d, p in dateslist:
            if d == date and p == period: # hit, modify entry and exit
                # extend the topic list with empty topics
                seqlist = seqlist + ["" for i in range(len(seqlist), len(dateslist))]

                seqlist[i] = topic
                self.putSequence(classname, seqlist)
            # next try
            i = i +1

        # should not happen, but can happen e.g. the date/period has no class entry
        return


    def __json_to_dt(obj):
        if obj.pop('__type__', None) != "datetime":
            return obj
        zone, offset = obj.pop("tz")
        obj["tzinfo"] = dtz.tzoffset(zone, offset)
        return datetime.datetime(**obj)

    def __dt_to_json(obj):
        if isinstance(obj, datetime.datetime):
            return {
                "__type__": "datetime",
                "year": obj.year,
                "month" : obj.month,
                "day" : obj.day,
                "hour" : obj.hour,
                "minute" : obj.minute,
                "second" : obj.second,
                "microsecond" : obj.microsecond,
                "tz": (obj.tzinfo.tzname(obj), obj.utcoffset().total_seconds())
            }
        else:
            raise TypeError("Cant serialize {}".format(obj))
