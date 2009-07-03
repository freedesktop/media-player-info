#!/bin/sh

autoreconf --install --symlink
./configure $@
