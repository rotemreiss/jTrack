#!/usr/bin/env sh

 ###########################################################################
#                                                                           #
# Launcher for jTrack to allow it to run from anywhere in the system        #
#                                                                           #
# 1. Change `/opt/jtrack` to the path where you cloned jTrack               #
# 2. Change `python` to `python3` if using both versions of Python locally. #
#                                                                           #
 ###########################################################################

(cd /Users/rotemr/tools/jtrack && python3 jtrack.py "$@")