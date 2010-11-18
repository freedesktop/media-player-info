AC_INIT(media-player-info, 11, devkit-devel@lists.freedesktop.org)
AM_INIT_AUTOMAKE
AC_CONFIG_SRCDIR([media-players/])

PKG_CHECK_MODULES(UDEV, udev)
AC_ARG_WITH(udevdir,
	    AS_HELP_STRING([--with-udevdir=DIR],[Installation path for udev rules @<:@auto@:>@]),
	    [ac_with_udevdir=$withval],
	    [ac_with_udevdir=""])
if test "${ac_with_udevdir}" = ""; then
	ac_with_udevdir=`$PKG_CONFIG --variable=udevdir udev`
fi

AC_MSG_NOTICE([installing udev rules in ${ac_with_udevdir}/rules.d])
AC_SUBST([UDEV_DIR],[${ac_with_udevdir}])

AC_OUTPUT([
Makefile
tools/Makefile
media-players/Makefile
])

