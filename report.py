#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2014 Benoît Canet <benoit@irqsave.net>
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301  USA
""" This script generate work report for hourly work and compute total time """

import datetime
import optparse
import sys
import time

USAGE = '''
report.py --input hours.txt
report.py --summary
'''

def hours_to_datetime(string):
    """ Convert a HH:MM to datetime """
    struct = time.strptime(string, "%Hh%M")
    return datetime.datetime.fromtimestamp(time.mktime(struct))

class Formater(object):
    """ This class parse an hour file and output content, date and hours """

    INIT    = 0
    DATE    = 1
    START   = 2
    CONTENT = 3

    def __init__(self, lines, start_line):
        self._report = ""
        self._start_line = start_line
        self._index = 0
        self._lines = lines
        self._state = self.INIT
        self._states = { self.INIT    : 'init',
                         self.DATE    : 'date',
                         self.START   : 'start',
                         self.CONTENT : 'content'
                       }
        self._transitions = { 'date': self._date,
                              'start': self._start,
                              'stop': self._stop,
                            }
        self._start_datetime = None
        self._daily_duration = datetime.timedelta(seconds=0)
        self._total_duration = datetime.timedelta(seconds=0)
        self._consume()

    def is_valid(self):
        return self._start_datetime != None

    def _parse_error(self, line, state):
        """ Called in case of parse error """
        print("Error while parsing %s while state is %s." %\
              (state, self._states[self._state]))
        print("\nThe line number %i is:" % (self._start_line + self._index))
        print(line)
        sys.exit(1)

    def _report_elapsed(self):
        """ Report elapsed time """
        print("\nTime worked: %s\n" % str(self._daily_duration))

    def print_total(self):
        """ Report total elapsed time of all days parsed """
        print("\nTotal time worked: %s\n" % str(self._total_duration))

    def get_line_prefix_and_suffix(self):
        """ Read a line from the list and split it """
        line = self._lines.pop(0).strip()
        components = line.split(':')
        prefix = components[0].strip()
        suffix = None
        if len(components) > 1:
            suffix = components[1].strip()

        self._index += 1
        return line, prefix, suffix

    def _consume(self, must_print=False):
        """ Consume a line a make the state machine work """
        if len(self._lines) == 0:
            self._report_elapsed()
            return

        line, prefix, suffix = self.get_line_prefix_and_suffix()
        while prefix not in self._transitions.keys():

            if must_print:
                print(' ' * 8 + line)

            if len(self._lines) == 0:
                self._report_elapsed()
                return
            line, prefix, suffix = self.get_line_prefix_and_suffix()

        self._transitions[prefix](line, prefix, suffix)

    def _date(self, line, _, __):
        """ transition for "date:" """
        if self._state != self.INIT and self._state != self.CONTENT:
            self._parse_error(line, "date")
        if self._state == self.CONTENT:
            self._report_elapsed()
        print(line)
        self._daily_duration = datetime.timedelta(seconds=0)
        self._state = self.DATE
        self._consume()

    def _start(self, line, _, suffix):
        """ transition for "start:" """
        if self._state != self.DATE and self._state != self.CONTENT:
            self._parse_error(line, "start")
        self._start_datetime = hours_to_datetime(suffix)
        self._state = self.START
        self._consume(True)

    def _stop(self, line, _, suffix):
        """ transition for "stop:" """
        if self._state != self.START:
            self._parse_error(line, "stop")

        end = hours_to_datetime(suffix)
        duration = end - self._start_datetime
        if duration.total_seconds() < 0:
            pre_midnight = hours_to_datetime("23h59")
            midnight = hours_to_datetime("00h00")
            duration = (pre_midnight - self._start_datetime) + (end - midnight)
            duration += datetime.timedelta(minutes=1)

        self._daily_duration += duration
        self._total_duration += duration

        self._state = self.CONTENT
        self._consume(True)

def get_last(lines): 
    """ Eliminate all the lines already processed by a previous call """
    # locate non reported lines walking backward
    lines.reverse()
    length = len(lines)
    for i in range(length):
        line = lines[i]
        if line.strip() == "last:":
            break
    lines = lines[:i]
    lines.reverse()
    return lines, length - i

def store_last(input_file):
    """ Write a tag to remember the last reported hours """
    print("Confirm that these report must not be displayed anymore ? (Y/N)")
    line = sys.stdin.readline()
    if line.strip() != "Y":
        print("Canceling state backup.")
        return
    with open(input_file, 'a') as input_file:
        input_file.write("\nlast:\n")


def format_input(filename, summarize):
    """ compute the time elasped on each day of work format and format report"""
    # read the input file
    index = 0
    with open(filename, 'r') as input_file:
        lines = input_file.readlines()

    if not summarize:
        lines, index = get_last(lines)

    if not len(lines):
        print("Nothing to report.")
        return

    formater = Formater(lines, index)

    if not formater.is_valid():
        print("Invalid file format.")
        return

    if summarize:
        formater.print_total()
    else:
        store_last(filename)

def main():
    """ Main function """
    parser = optparse.OptionParser(usage=USAGE)
    parser.add_option('-f', '--filename', help="File containing the work hours")
    parser.add_option('-s', '--summarize', action="store_true")
    opt, _ = parser.parse_args()

    if opt.filename:
        format_input(opt.filename, opt.summarize)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
