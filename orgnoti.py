#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Organizer for memory

based of http://en.wikipedia.org/wiki/Forgetting_curve

after first repeat:
1. +20m
2. +8h
3. +24h (one day)
4. +168h (one week)
5. +1344h (two mounth)

Depends: UNIX with libnotify

EXAMPLE WITH CRON:

    add this script to cron
        0-59 * *   *   *     /path/to/orgnoti_show.sh

create 'orgnoti_show.sh':

    DISPLAY=`/path/to/get_display.sh`
    export DISPLAY

    python /path/to/orgnoti.py

create 'get_display.sh':

    #!/bin/sh
    #

    # get_display [USER] — Returns $DISPLAY of USER.
    # If first param is omitted, then $LOGNAME will be used.
    get_display () {
          who \
          | grep ${1:-$LOGNAME} \
              | perl -ne 'if ( m!\(\:(\d+)\)$! ) {print ":$1.0\n"; $ok = 1; last} END {exit !$ok}'
    }
    get_display
"""

import os
# CONFIG HERE
noti_class = 'Memory Organizer'
stand_summary = '<b>Need remember</b>'
bdname = '.memorg.db'
bdpath = '{dir}/{name}'.format(name = bdname, dir = os.path.expanduser('~'))

import pynotify
import sqlite3
import datetime
import time
import sys
import re

# Initialization of pynotify, and add type of notify
pynotify.init(noti_class)

def datenow(inc = 0):
    """inc - increment in minutes"""
    inc *= 60
    now = datetime.datetime.now()
    now = datetime.datetime(now.year,
                             now.month,
                             now.day,
                             now.hour,
                             now.minute,
                             0,
                             0
            ) + datetime.timedelta(0, inc)
    return time.mktime(now.timetuple())

def getinc(repeat):
    """return inc in minutes from repeat"""
    if repeat == 1:
        return 20
    if repeat == 2:
        return 8 * 60
    if repeat == 3:
        return 24 * 60
    if repeat == 4:
        return 168 * 60
    if repeat == 5:
        return 1344 * 60

    return 0

class SimpleNoti():
    """Class for pynotify.Notification
    """

    def __init__(self, summary='<b>Summary</b>', text = ''):
        self.summary = summary
        self.text = text

    def show(self, text = ''):
        """change of the text for notify and show"""
        self.text = text
        pynotify.Notification(self.summary, self.text).show()

class Organizer(SimpleNoti):
    def __init__(self, bdpath = 'memorg.bd'):
        self.bdpath = bdpath
        self.conn = sqlite3.connect(self.bdpath)
        SimpleNoti.__init__(self, stand_summary)
        cur = self.conn.cursor()
        try:
            cur.execute("CREATE TABLE Mems(Id INTEGER PRIMARY KEY, "\
                        "Text TEXT, Date INT, Repeat INT)")
            self.conn.commit()
        except sqlite3.OperationalError:
            pass

    def add(self, text, repeat = 1):
        cur = self.conn.cursor()

        for url in re.findall(r'(?<!\])\bhttp://[^\s\[<]+', text):
            text = text.replace(url, '<a href="{url}">{url}</a>'.format(url = url))

        cur.execute("INSERT INTO Mems(Text, Date, Repeat) "\
                    "VALUES('{text}', '{now}', {repeat})"\
                    .format(now = datenow(getinc(repeat)), text = text,
                            repeat = repeat))
        self.conn.commit()

    def update(self, id, repeat):
        repeat += 1
        cur = self.conn.cursor()
        if repeat > 5:
            cur.execute("DELETE FROM Mems WHERE Id=?", (id))
        else:
            cur.execute("UPDATE Mems SET Repeat=?, Date=? WHERE Id=?", \
                        (repeat, datenow(getinc(repeat)), id))
        self.conn.commit()

    def show(self):
        cur = self.conn.cursor()
        noti_list = cur.execute("SELECT Id, Text, Repeat FROM Mems "\
                                "WHERE Date <= '{now}'"\
                                .format(now = datenow())).fetchall()
        for id, text, repeat in noti_list:
            SimpleNoti.show(self, '<i>{date}</i> → {text}'.format(text = text,
                                date = datetime.datetime.now().ctime()))
            self.update(id, repeat)

    def close(self):
        self.conn.close()


if __name__ == "__main__":
    if '--show' not in sys.argv:
        text = ' '.join(sys.argv[1:])
        if text != '':
            Organizer(bdpath).add(text)
        else:
            Organizer(bdpath).show()
    else:
        Organizer(bdpath).show()

# vi: ft=python:tw=0:ts=4

