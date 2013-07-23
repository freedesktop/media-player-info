#!/usr/bin/env python3
# Generate hwdb file from music player identification (.mpi) files
#
# (C) 2009 Canonical Ltd.
# (C) 2013 Tom Gundersen <teg@jklm.no>
# Author: Tom Gundersen <teg@jklm.no>
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA.

import sys, configparser, os.path

def parse_mpi(mpi):
    '''Print hwdb file for given ConfigParser object.'''

    cp = configparser.RawConfigParser()
    assert cp.read(mpi)

    # if we have more info than just idVendor+idProduct we need to use an udev rule,
    # so don't write an hwdb entry
    for name in ['usbvendor', 'usbproduct', 'usbmodel', 'usbmanufacturer']:
        try:
            cp.get('Device', name)
            return
        except configparser.NoOptionError:
            continue

    try:
        m = cp.get('Device', 'product')
        print('#', m)
    except configparser.NoOptionError:
        pass

    try:
        usbids = {}
        for usbid in cp.get('Device', 'devicematch').split(';'):
            if len(usbid.split(':')) != 3:
                continue
            (subsystem, vid, pid) = usbid.split(':')
            if subsystem != "usb":
                continue
            if vid in usbids:
                usbids[vid].append(pid)
            else:
                usbids[vid] = [ pid ]

        for vid, pids in usbids.items():
                for pid in pids:
                    print('usb:v%sp%s*'% (vid.upper(), pid.upper()))
                    print(' ID_MEDIA_PLAYER=%s' % os.path.splitext(os.path.basename(mpi))[0])

                    # do we have an icon?
                    try:
                        icon = cp.get('Device', 'icon')
                        # breaks media player detection : https://bugs.launchpad.net/ubuntu/+source/gvfs/+bug/657609
                        #print ' UDISKS_PRESENTATION_ICON_NAME=%s\n' % icon,
                    except configparser.NoOptionError:
                        pass

                    # terminate line
                    print()

    except configparser.NoOptionError:
        pass

#
# main
#

# parse MPI files
for f in sys.argv[1:]:
    parse_mpi(f)
