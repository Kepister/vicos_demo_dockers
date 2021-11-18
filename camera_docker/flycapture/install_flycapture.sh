#!/bin/bash

set -o errexit

MY_PROMPT='$ '
MY_YESNO_PROMPT='(y/n)$ '

# version of the software
MAJOR_VERSION=2
MINOR_VERSION=13
# 0 Alpha, 1 Beta, 2 RC, 3 Public release
RELEASE_TYPE=3
RELEASE_BUILD=31
INFORMATIONAL_VERSION=2.13.3.201810150064
RELEASE_TYPE_TEXT=Release

dpkg -i libflycapture-2*
dpkg -i libflycapturegui-2*
dpkg -i libflycapturevideo-2*
dpkg -i libflycapture-c-2*
dpkg -i libflycapturegui-c-2*
dpkg -i libflycapturevideo-c-2*
dpkg -i libmultisync-2*
dpkg -i libmultisync-c-2*
dpkg -i flycap-2*
dpkg -i flycapture-doc-2*
dpkg -i updatorgui*

exit 0
