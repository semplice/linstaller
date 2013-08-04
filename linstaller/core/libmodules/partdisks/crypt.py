# -*- coding: utf-8 -*-
# partdisks crypto library. - (C) 2011-12 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

## Maybe it's better to move everything to python-cryptosetup when it
## lands on Debian... ~g7

import os

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

class LUKSdrive:
	""" A LUKS-encrypted drive/partition. """
	
	def __init__(self, device):
		
		self.device = device
	
	def format(self, password):
		""" Formats the device and sets password as the drive's password. """
		
		# Umount
		lib.umount_bulk(self.device.path)
		
		# Try to close
		try:
			self.close()
		except m.CmdError:
			pass
		
		# Ugly as hell
		m.sexec("echo '%(password)s' | cryptsetup luksFormat %(device)s" % {"password":password, "device":self.device.path})

	def open(self, password):
		""" Opens the device. """
		
		# Ugly as hell
		m.sexec("echo '%(password)s' | cryptsetup luksOpen %(device)s %(name)s" % {"password":password, "device":self.device.path, "name":lib.get_UUID(self.device.path)})
	
	def close(self):
		""" Closes the device. """
		
		m.sexec("cryptsetup luksClose %s" % self.mapper_path)
	
	def get_partition(self):
		""" Returns a parted.Partition object from the encrypted device. """
		
		return lib.p.Disk(device=lib.p.Device(self.mapper_path)).getFirstPartition()
	
	@property
	def mapper_path(self):
		""" Returns the path of the device in /dev/mapper.
		Please note that this method will return the path regardless of
		the state of the device (i.e. it does not check if it exists or not)"""
		
		return os.path.join("/dev/mapper", lib.get_UUID(self.device.path))
	
	@property
	def path(self):
		""" Compatibility purposes with parted-only things. """
		
		return self.mapper_path
