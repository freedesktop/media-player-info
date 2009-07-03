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
# keymap is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with keymap; if not, write to the Free Software Foundation,
# Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA.

import sys, ConfigParser, os.path

# translation of mpi Device keys to udev attributes
mpi2udev = {
    'vendorid': 'ATTRS{idVendor}=="%s"',
    'productid': 'ATTRS{idProduct}=="%s"',
    'usbvendor': 'ATTRS{vendor}=="%s"',
    'usbmodel': 'ATTRS{model}=="%s"',
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
    for name in ['vendorid', 'usbvendor', 'usbproduct']:
        try:
            value = cp.get('Device', name)
            print mpi2udev[name] % value, ',',
        except ConfigParser.NoOptionError:
            continue

    try:
        productids = cp.get('Device', 'productid').replace(';', '|')
        print mpi2udev['productid'] % productids, ',',
    except ConfigParser.NoOptionError:
        pass

    print 'ENV{ID_MEDIA_PLAYER}="%s"' % os.path.splitext(os.path.basename(mpi))[0]

#
# main
#

# udev rules header
print '''ACTION!="add", GOTO="media_player_end"
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
