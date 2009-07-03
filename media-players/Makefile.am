mpidir = $(datadir)/udev/media-players
dist_mpi_DATA =  $(shell find $(top_srcdir)/media-players -name "*.mpi" -printf "%P\n")

udevrulesdir = $(libexecdir)/rules.d
dist_udevrules_DATA = 90-usb-media-players.rules
90-usb-media-players.rules: $(dist_mpi_DATA)
	$(top_srcdir)/tools/mpi2udev.py $(dist_mpi_DATA) >90-usb-media-players.rules

clean-local:
	-rm -f 90-usb-media-players.rules
EXTRA_DIST = 90-usb-media-players.rules
