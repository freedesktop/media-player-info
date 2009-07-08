#!/usr/bin/python
# Convert hal's USB music player FDIs into media player information (.mpi)
# property files.
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

import sys, os.path, xml.dom.minidom

# translation of hal match keys to mpi attribute names
_hal_match2mpi = {
    '@storage.originating_device:usb.vendor_id': 'VendorID',
    '@storage.physical_device:usb.vendor_id': 'VendorID',
    '@storage.originating_device:usb.product_id': 'ProductID',
    '@storage.physical_device:usb.product_id': 'ProductID',
    '@storage.originating_device:@info.parent:usb_device.product': 'USBModel',
    'storage.vendor': 'USBVendor',
    'storage.model': 'USBModel',

    # if we actually want/need to check for subdevices, we can do:
    #'storage.lun': 'KERNELS=="*:*:*:%s"', # host:bus:target:lun
    # ... but let's ignore it for now:
    'storage.lun': None,

    # the following are globally checked by rule header, ignore them 
    '@storage.originating_device:info.subsystem': None,
    'info.category': None,
}

_hal_prop2mpi = {
    'portable_audio_player.access_method.protocols': ('Device', 'AccessProtocol'),
    'portable_audio_player.access_method': ('Device', 'AccessProtocol'),
    'portable_audio_player.output_formats': ('Media', 'OutputFormats'),
    'portable_audio_player.input_formats': ('Media', 'InputFormats'),
    'portable_audio_player.audio_folders': ('storage', 'AudioFolders'),
    'portable_audio_player.folder_depth': ('storage', 'FolderDepth'),
    'portable_audio_player.playlist_path': ('storage', 'PlaylistPath'),
    'portable_audio_player.playlist_format': ('Playlist', 'Formats'),
    'portable_audio_player.playlist_formats': ('Playlist', 'Formats'),
    'storage.requires_eject': ('storage', 'RequiresEject'),
    'storage.model': ('Device', 'Model'),
    'storage.vendor': ('Device', 'Vendor'),
    'storage.drive_type': ('storage', 'DriveType'),

    # all of those are "portable audio player"
    'info.capabilities': (None, None),

    # not useful; if we need the device, we should set up a general rule to
    # slam it into the udev db
    'portable_audio_player.storage_device': (None, None),
}

def match_op2glob(node):
    '''Convert FDI match operator to a glob.
    
    Return glob
    '''
    if node.attributes.has_key('string'):
        return node.attributes['string'].nodeValue

    if node.attributes.has_key('contains'):
        return '*' + node.attributes['contains'].nodeValue + '*'

    if node.attributes.has_key('int'):
        v = node.attributes['int'].nodeValue
        if v != '1':
            v = '%04x' % int(v, 0)
	return v

    if node.attributes.has_key('int_outof'):
        alternatives = node.attributes['int_outof'].nodeValue.split(';')
        hex_alternatives = []
        for a in alternatives:
            hex_alternatives.append('%04x' % int(a, 0))
	return hex_alternatives

    if node.attributes.has_key('contains_ncase'):
        v = node.attributes['contains_ncase'].nodeValue 
        nocase_glob = ''.join(['[%s%s]' % (c.lower(), c.upper()) for c in v])
	return '*' + nocase_glob + '*'

    if node.attributes.has_key('prefix_ncase'):
        v = node.attributes['prefix_ncase'].nodeValue 
        nocase_glob = ''.join(['[%s%s]' % (c.lower(), c.upper()) for c in v])
	return nocase_glob + '*'

    raise NotImplementedError, 'unknown string operator ' + str(node.attributes.keys())

def get_node_comment(node):
    '''Return comment before a node.'''

    while True:
        node = node.previousSibling
        if not node:
            break
        if node.nodeType == xml.dom.Node.COMMENT_NODE:
            lines = [l.strip() for l in node.nodeValue.splitlines()]
            return ' '.join(lines)
        if node.nodeType != xml.dom.Node.TEXT_NODE:
            break
    return None

def collect_attributes(node, attrs):
    '''Add media player attributes to attrs.'''

    for n in node.childNodes:
        if n.nodeType != xml.dom.minidom.Node.ELEMENT_NODE:
            continue
        if n.tagName == 'match':
            continue
        assert n.tagName in ('addset', 'merge', 'append')

        (cat, prop) = _hal_prop2mpi[n.attributes['key'].nodeValue]
        if cat is None:
            continue
        content_node = n.childNodes[0]
        assert content_node.nodeType == xml.dom.Node.TEXT_NODE

        attrs.setdefault(cat, {}).setdefault(prop, []).append(content_node.nodeValue.strip())

def mkfilename(attrs, current_vendor):
    '''Return an appropriate mpi file name for attributes.'''

    v = None
    if 'VendorID' in attrs.get('Device', {}):
        v = attrs['Device']['VendorID']
    if 'USBVendor' in attrs.get('Device', {}):
        v = attrs['Device']['USBVendor']
    if current_vendor:
        v = current_vendor.split()[0].split('/')[0].replace(',', '').lower().strip()
    assert v

    m = None
    if 'ProductID' in attrs.get('Device', {}):
        m = attrs['Device']['ProductID']
    if 'USBModel' in attrs.get('Device', {}):
        m = attrs['Device']['USBModel']
    # if we only have a single product ID, attempt to get nicer name
    if len(attrs['Device'].get('ProductID', [''])) <= 1 and \
            'Product' in attrs.get('Device', {}) and \
            '/' not in attrs['Device']['Product']:
        m = attrs['Device']['Product']
    if 'Model' in attrs.get('Device', {}):
        m = attrs['Device']['Model'][0]

    if type(m) == type([]):
        m = '_'.join(m)
    m = m.replace(' ', '_').replace(';', '_').replace('*', '').replace('(',
            '').replace(')', '').lower()
    assert m

    assert '*' not in m, m
    assert '[' not in m, m
    assert ';' not in m, m
    assert '(' not in m, m
    assert ')' not in m, m
    assert ' ' not in m, m

    # a lot of product names start with vendor name
    if m.startswith(v):
        m = m[len(v):]
    if m.startswith('_'):
        m = m[1:]

    print attrs['Device'], '->', '"%s-%s"' % (v, m)

    return '%s-%s' % (v, m)

def usb_ids_to_device_match(attrs):
    '''convert the USB IDs we gathered to a DeviceMatch string appropriate
    for mpi files'''

    if not 'VendorID' in attrs['Device'].keys():
	return

    if not 'ProductID' in attrs['Device'].keys():
	attrs['Device']['ProductID'] = [ '*' ]

    device_match = ''
    for id in attrs['Device']['ProductID']:
	device_match += 'usb:'+ attrs['Device']['VendorID'][0] + ':' + id + ';'

    attrs['Device']['DeviceMatch'] = device_match
    del attrs['Device']['VendorID']
    del attrs['Device']['ProductID']


def write_mpi(attrs, filename):
    '''Write mpi file for attrs.'''

    # define order of sections
    sections = ['Device', 'Media', 'Playlist', 'storage']

    # a lot of product names start with vendor name
    if attrs['Device'].has_key('Vendor') and attrs['Device'].has_key('Product'):
	product = attrs['Device']['Product']
	vendor = attrs['Device']['Vendor']
	if product.startswith(vendor):
	    attrs['Device']['Product'] = product[len(vendor):].strip()

    usb_ids_to_device_match(attrs)

    # only keep the most specific model name
    if attrs['Device'].has_key('Model'):
        attrs['Device']['Model'] = attrs['Device']['Model'][0]

    assert set(attrs.keys()) <= set(sections)

    f = open(os.path.join('media-players', filename + '.mpi'), 'w')

    for section in sections:
        if section not in attrs:
            continue
        print >> f, '[%s]' % section
        for k, v in attrs[section].iteritems():
            if type(v) == type([]):
                v = ';'.join(v)
            print >> f, '%s=%s' % (k, v)
        print >> f
        
    f.close()

def parse_leaf_match(node, current_vendor, current_model):
    '''Parse leaf match.

    Construct udev matches from all parent matches and then write property mpi
    file from all attached properties.
    '''
    # this is from the "Set common keys for detected audio player" section,
    # which we want to ignore
    if node.attributes['key'].nodeValue == 'portable_audio_player.access_method.protocols':
        return

    attrs = {'Media': {'OutputFormats': ['audio/mpeg']}}

    n = node
    while n:
        collect_attributes(n, attrs)

        key = n.attributes['key'].nodeValue
        device_attr = _hal_match2mpi[key]
        if device_attr:
            glb = match_op2glob(n)
	    if type(glb) == type([]):
                attrs.setdefault('Device', {}).setdefault(device_attr, []).extend(glb)
	    else:
                attrs.setdefault('Device', {}).setdefault(device_attr, []).append(glb)
        while True:
            n = n.parentNode
            if n is None or (n.nodeType == xml.dom.minidom.Node.ELEMENT_NODE and 
                    n.tagName == 'match'):
                break

    if current_model:
        attrs.setdefault('Device', {})['Product'] = current_model
    if current_vendor:
        attrs.setdefault('Device', {})['Vendor'] = current_vendor

    fname = mkfilename(attrs, current_vendor)
    write_mpi(attrs, fname)

def parse_fdi(fdi):
    '''Parse music player fdi node.'''

    current_vendor = None

    # find all <match> leaf nodes
    for match_node in fdi.getElementsByTagName('match'):
        current_model = None

        c = get_node_comment(match_node)

        # filter out a few weird cases in current hal-info
        if c and ('No-name' in c or 'require' in c or 'media files' in c):
            c = None
	if c and ('TODO' in c):
            c = 'Apple'
        if c and ('MegaScreen' in c):
            c = 'Nexia'
        if c and ('PSP' in c):
            c = 'Sony'

        if c:
            match_key = match_node.attributes['key'].nodeValue
            if 'model' in match_key or 'product' in match_key:
                current_model = c
            elif 'vendor' in match_key:
                current_vendor = c
            else:
                if 'subsystem' in match_key or 'protocols' in match_key or 'category' in match_key:
                    pass
                else:
                    raise NotImplementedError, 'do not know how to interpret comment ' + c

        children = set([n.tagName for n in match_node.childNodes 
                if n.nodeType == xml.dom.minidom.Node.ELEMENT_NODE])

        if u'match' in children:
            continue

        parse_leaf_match(match_node, current_vendor, current_model)

#
# main
#

for f in sys.argv[1:]:
    parse_fdi(xml.dom.minidom.parse(f))
