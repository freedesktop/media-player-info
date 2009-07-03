mpidir = $(datadir)/udev/media-players
dist_mpi_DATA =  $(shell find $(top_srcdir)/media-players -name "*.mpi" -printf "%P\n")

udev-rules: $(dist_mpi_DATA)
	$(top_srcdir)/tools/mpi2udev.py $(dist_mpi_DATA) >90-media-players.rules

