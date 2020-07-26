## Installation

Timetable is available on flathub:

[https://flathub.org/apps/details/io.github.kaschpal.timetable](https://flathub.org/apps/details/io.github.kaschpal.timetable)


## Overview and basics 

Timetable imitates a classic calendar/planner for teachers.

The topic of the lesson is determined by the curricular sequence. If you shift the lesson, e.g. by adding a substitute lesson, the topic is moved
automatically according to the order of the curricular sequence.

In the sequence view, you can edit the topic and the chronological order. Every line is one topic. The list of topics is an ordinary
text field, which means you can copy and paste to or from a textfile.
The classes in the sequence view are created dynamically. You don't have to keep a list of your classes in the settings.

Note that a classname which *only* appears as temperary entry in the timetable view (dot entry) will not show up in the
sequence view.

## Create classes

The classes are written in the small text field of the day matrix.
In the larger field you write the topic of the lesson. The entered classname is repeated every week starting from the date you created it, so
you have to transfer your timetable only in the first week of school. If you change the entry to something different, $em(this changed class)
is repeated from now on. To end repetition, you delete the entry (=string "").

Note that every change in the class entry has to be confirmed either by hitting enter or by leaving the entry (i.e. tab or mouse click into a
different cell). This has technical reasons due to the dynamic design of the application.

The first time a class is entered, the entry is shown in red colour. This is for quickly finding it again.


## Exceptions, substitute lessons, shifting lessons

Temporary class entries are created by a classname, which is preceeded by a dot. No leading spaces are allowed. An example for a temporary class entry is ".9c".
Dot enties are used for shifting and substitute lessons. They are not repeated and do not affect repetition of the original entry.

If a lesson is simply cancelled, use only a dot (".") as class entry.

Dot entries are also shown in red.

## Holidays and days off

If a day is a holiday or you get sick or you attend an advanced training, you can deactivate all lessons for this date.
Simply uncheck the checkbox right of the date (at the top).

This can be undone.

## Memos and the calendar

The star at the top of every day can be used for memos. It turns orange if a memo for this day exists.
If you have to add a lot of appointments at once, the calendar view is useful. Here you can also edit the memos, which
appear in the timetable view.
