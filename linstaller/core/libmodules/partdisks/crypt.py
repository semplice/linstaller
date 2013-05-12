# -*- coding: utf-8 -*-
# partdisks crypto library. - (C) 2011-12 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

## Maybe it's better to move everything to python-cryptosetup when it
## lands on Debian... ~g7

import linstaller.core.main as m
import linstaller.core.libmodules.partdisks.library as lib

class Crypt:
	""" A Crypt object handles a drive that should encrypted with LUKS. """
	
	def __init__(self, device, disk):
		""" Init. """
		
		self.device = device
		self.disk = disk
	
	def random_fill(self, hq=False):
		""" Fills the device with random data.
		
		If hq is True, it will use /dev/urandom (slower but more secure).
		
		
		It returns the process object to the frontend.
		"""
		
		# Umount
		lib.umount_bulk(self.device.path)
		
		if not hq:
			command = m.execute("badblocks -c 10240 -s -w -t random -v %s" % self.device.path)
		else:
			command = m.execute("dd if=/dev/urandom of=%s" % self.device.path)
		command.start()
		
		# Return object to frontend
		return command
	
	
