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

# vi: ts=2 sw=2

