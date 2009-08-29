AC_INIT(media-player-info, 2, devkit-devel@lists.freedesktop.org)
AM_INIT_AUTOMAKE
AC_CONFIG_SRCDIR([media-players/])

PKG_CHECK_MODULES(UDEV, udev)
AC_SUBST([udev_dir], [$($PKG_CONFIG --variable=udevdir udev)])

AC_OUTPUT([
Makefile
media-players/Makefile
])

