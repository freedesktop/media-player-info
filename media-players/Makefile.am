mpidir = $(datadir)/media-player-info
dist_mpi_DATA =  $(shell find $(top_srcdir)/media-players -name "*.mpi" -printf "%P\n")

udevrulesdir = $(UDEV_DIR)/rules.d
dist_udevrules_DATA = 40-usb-media-players.rules
40-usb-media-players.rules: $(dist_mpi_DATA) $(top_srcdir)/tools/mpi2udev.py
if HAVE_HWDB
	$(top_srcdir)/tools/mpi2udev.py hwdb $(dist_mpi_DATA) > 40-usb-media-players.rules
else
	$(top_srcdir)/tools/mpi2udev.py udev $(dist_mpi_DATA) > 40-usb-media-players.rules
endif
	$(top_srcdir)/tools/udev-syntax-check.py 40-usb-media-players.rules

if HAVE_HWDB
udevhwdbdir = $(UDEV_DIR)/hwdb.d
dist_udevhwdb_DATA = 20-usb-media-players.hwdb
20-usb-media-players.hwdb: $(dist_mpi_DATA) $(top_srcdir)/tools/mpi2hwdb.py
	$(top_srcdir)/tools/mpi2hwdb.py $(dist_mpi_DATA) > 20-usb-media-players.hwdb
endif

clean-local:
	rm -f 40-usb-media-players.rules 20-usb-media-players.hwdb
