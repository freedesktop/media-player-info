mpidir = $(datadir)/media-player-info
dist_mpi_DATA =  $(shell find $(top_srcdir)/media-players -name "*.mpi" -printf "%P\n")

udevrulesdir = $(UDEV_DIR)/rules.d
dist_udevrules_DATA = 40-usb-media-players.rules
40-usb-media-players.rules: $(dist_mpi_DATA) $(top_srcdir)/tools/mpi2udev.py
	$(top_srcdir)/tools/mpi2udev.py $(dist_mpi_DATA) > 40-usb-media-players.rules

clean-local:
	-rm -f 40-usb-media-players.rules
EXTRA_DIST = 40-usb-media-players.rules
