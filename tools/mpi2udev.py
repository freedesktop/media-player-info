#!/usr/bin/python
# Generate udev rules from music player identification (.mpi) files
#
# (C) 2009 Canonical Ltd.
# Author: Martin Pitt <martin.pitt@ubuntu.com>
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

import sys, ConfigParser, os.path

# translation of mpi Device keys to udev attributes
mpi2udev = {
    'vendorid': 'ATTRS{idVendor}=="%s"',
    'productid': 'ATTRS{idProduct}=="%s"',
    'usbvendor': 'ATTRS{vendor}=="%s"',
    'usbmodel': 'ATTRS{model}=="%s"',
    'usbproduct': 'ATTRS{product}=="%s"',
    'usbmanufacturer': 'ATTRS{manufacturer}=="%s"',
}

def parse_mpi(mpi):
    '''Print udev rule for given ConfigParser object.'''

    cp = ConfigParser.RawConfigParser()
    assert cp.read(mpi)

    try:
        m = cp.get('Device', 'product')
        print '#', m
    except ConfigParser.NoOptionError:
        pass
    for name in ['usbvendor', 'usbproduct', 'usbmodel', 'usbmanufacturer']:
        try:
            value = cp.get('Device', name)
            print mpi2udev[name] % value, ',',
        except ConfigParser.NoOptionError:
            continue

    try:
        usbids = {}
        for usbid in cp.get('Device', 'devicematch').split(';'):
            if len(usbid.split(':')) != 3:
                continue
            (subsystem, vid, pid) = usbid.split(':')
            if subsystem != "usb":
                continue
            if usbids.has_key(vid):
                usbids[vid].append(pid)
            else:
                usbids[vid] = [ pid ]

        for vid, pids in usbids.iteritems():
            print 'ATTRS{idVendor}=="%s" , ATTRS{idProduct}=="%s"'% (vid, '|'.join(pids)), ',',
            print 'ENV{ID_MEDIA_PLAYER}="%s"' % os.path.splitext(os.path.basename(mpi))[0],

    except ConfigParser.NoOptionError:
        print 'ENV{ID_MEDIA_PLAYER}="%s"' % os.path.splitext(os.path.basename(mpi))[0],

    # do we have an icon?
    try:
        icon = cp.get('Device', 'icon')
        # breaks media player detection : https://bugs.launchpad.net/ubuntu/+source/gvfs/+bug/657609
        # print ', ENV{UDISKS_PRESENTATION_ICON_NAME}="%s"' % icon,
    except ConfigParser.NoOptionError:
        pass

    # terminate rule line
    print

#
# main
#

# udev rules header
print '''ACTION!="add|change", GOTO="media_player_end"
# catch MTP devices
ENV{DEVTYPE}=="usb_device", GOTO="media_player_start"

# catch UMS devices
SUBSYSTEM!="block", GOTO="media_player_end"
SUBSYSTEMS=="usb", GOTO="media_player_start"
GOTO="media_player_end"

LABEL="media_player_start"
'''

# parse MPI files
for f in sys.argv[1:]:
    parse_mpi(f)

# udev rules footer
print '\nLABEL="media_player_end"'
