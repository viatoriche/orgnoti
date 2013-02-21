#!/bin/sh
# qtinput --> https://github.com/viatoriche/QtInput

filename=`mktemp`
qtinput $filename && cat $filename | orgnoti

# vi: ts=2 sw=2

