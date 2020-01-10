# -*- coding: utf-8 -*-
import datetime
import os
import locale
from gi.repository import Gio
from gettext import gettext as _

DEBUG = True

# stuff, which will likely never change
# Every list in the timetable has an initial entry with this date and classname ""
epoch = datetime.date(year=1970, month=1, day=1)
# how long the textfield should be
topicLen = 30
# how many entries should be fetched max for one class when generating the sequence
MAXDATES = 400
# how often should a date be repeated each week
maxdates_repeat = 100

# configuration code
programDirectory = os.path.dirname( os.path.abspath(__file__) ) + os.sep
#stateFile = programDirectory + "state.p"
dconfPath = "/apps/timetable/"

# language
if os.name == "posix":      # UNIX
    language = locale.getdefaultlocale()[0].split("_")[0]
elif os.name == "nt":       # Windows
    import ctypes
    windll = ctypes.windll.kernel32
    language = locale.windows_locale[windll.GetUserDefaultUILanguage()].split("_")[0]
else:                       # at least try ...
    language = locale.getdefaultlocale()[0].split("_")[0]


# How the days are called

weekdays = {1: _("Monday"),
            2: _("Tuesday"),
            3: _("Wednesday"),
            4: _("Thursday"),
            5: _("Friday"),
            6: _("Saturday"),
            7: _("Sunday")}
weekdaysShort = {1: _("Mon"),
                 2: _("Tue"),
                 3: _("Wed"),
                 4: _("Thu"),
                 5: _("Fri"),
                 6: _("Sat"),
                 7: _("Sun")}


""" Debug messages should only be displayed in debug-mode """
def dbglog(message):
    if DEBUG == True:
        print(message)
