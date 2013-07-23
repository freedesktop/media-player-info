#!/usr/bin/env python2
# Simple udev rules syntax checker
#
# (C) 2010 Canonical Ltd.
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
# along with keymap; if not, write to the Free Software Foundation,
# Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA.

import re
import sys

if len(sys.argv) < 2:
    print >> sys.stderr, 'Usage: %s <rules file> [...]' % sys.argv[0]
    sys.exit(2)

no_args_tests = re.compile('(ACTION|DEVPATH|KERNELS?|NAME|SYMLINK|SUBSYSTEMS?|DRIVERS?|TAG|PROGRAM|RESULT)\s*(?:=|!)=\s*"([^"]*)"$')
args_tests = re.compile('(ATTRS?|ENV|TEST){(\w+)}\s*(?:=|!)=\s*"([^"]*)"$')
no_args_assign = re.compile('(NAME|SYMLINK|OWNER|GROUP|MODE|TAG|RUN|LABEL|GOTO|WAIT_FOR|OPTIONS)\s*(?:\+=|:=|=)\s*"([^"]*)"$')
args_assign = re.compile('(ATTR|ENV|IMPORT){([a-zA-Z0-9_.-]+)}\s*=\s*"([^"]*)"$')

result = 0
lineno = 0
for path in sys.argv[1:]:
    for line in open(path):
        lineno += 1

        # filter out comments and empty lines
        line = line.split('#')[0]
        line = line.strip()
        if not line:
            continue

        for clause in line.split(','):
            clause = clause.strip()
            if not (no_args_tests.match(clause) or args_tests.match(clause) or
                    no_args_assign.match(clause) or args_assign.match(clause)):

                print 'Invalid line %s:%i: "%s"' % (path, lineno, line)
                sys.exit(1)
                result = 1
                break

sys.exit(result)
