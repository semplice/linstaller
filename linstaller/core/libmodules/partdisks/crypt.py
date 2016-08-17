# -*- coding: utf-8 -*-
# partdisks crypto library. - (C) 2011-12 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

## Maybe it's better to move everything to python-cryptosetup when it
## lands on Debian... ~g7

import os, commands

import subprocess

import linstaller.core.main as m
import linstaller.core.libmodules.partdisks.library as lib

FillQuality = m.enum("LOW", "HIGH")

class LUKSdrive:
	""" A LUKS-encrypted drive/partition. """
	
	def __init__(self, device=None, string_device=None):
		
		if not device and not string_device:
			raise m.CodeError("At least device or string_device must be specified!")
		elif device and string_device:
			raise m.CodeError("You must specify only device OR string_device!")
		
		if device:
			self.string_device = device.path
		else:
			self.string_device = string_device
		
		self.device = device
		self.crypt_name = os.path.basename(self.string_device) + "_crypt"
		self.mapper_path = os.path.join("/dev/mapper", self.crypt_name)
		#self.path = self.mapper_path

	def random_fill(self, type=FillQuality.LOW):
		""" Fills the device with random data.
		
		type is an object from the FillQuality enum.
		
		It returns the process object to the frontend.
		"""
		
		# Umount
		lib.umount_bulk(self.string_device)
		
		if type == FillQuality.LOW:
			m.sexec("badblocks -c 10240 -s -w -t random -v %s" % self.string_device)
		elif type == FillQuality.HIGH:
			m.sexec("dd if=/dev/urandom of=%s" % self.string_device)

	def format(self, password, cipher="aes-xts-plain64", keysize=512):
		""" Formats the device and sets password as the drive's password. """
		
		# Umount
		lib.umount_bulk(self.string_device)
		
		# Try to close
		try:
			self.close()
		except m.CmdError:
			pass
		
		process = subprocess.Popen(
			[
				"cryptsetup",
				"luksFormat",
				"--cipher",
				cipher,
				"--key-size",
				str(keysize),
				self.string_device
			],
			stdin=subprocess.PIPE
		)
		process.communicate(password)

		process.wait()

	def open(self, password):
		""" Opens the device. """
		
		process = subprocess.Popen(
			[
				"cryptsetup",
				"luksOpen",
				self.string_device,
				self.crypt_name
			],
			stdin=subprocess.PIPE
		)
		process.communicate(password)

		process.wait()

	
	def close(self):
		""" Closes the device. """
		
		# Bugfix
		if not self.path: return
		
		# Ensure we have it unmounted...
		if lib.is_mounted(self.path): lib.umount(path=self.path)
		
		# Then close...
		m.sexec("cryptsetup luksClose %s" % self.path)
	
	def get_partition(self):
		""" Returns a parted.Partition object from the encrypted device. """
		
		return lib.p.Disk(device=lib.p.Device(self.path)).getFirstPartition()
	
	@property
	def path(self):
		""" Returns the path if the device is unlocked. Otherwise, it will return None. """
		
		for line in commands.getoutput("lsblk %s --noheadings --list -o NAME,TYPE" % self.string_device).split("\n"):
			line = line.split(" ")
			
			while line.count(""):
				line.remove("")
			
			if line[-1] == "crypt":
				# Found!
				return os.path.join("/dev/mapper", line[0])
		
		return None

def return_luks():
	""" Returns a dictionary with all the LUKS devices found in the system. """
	
	dct = {}
	
	for line in commands.getoutput("lsblk --noheadings --list -o NAME,FSTYPE").split("\n"):
		line = line.split(" ")
		
		while line.count(""):
			line.remove("")
		
		if len(line) == 2 and line[-1] == "crypto_LUKS":
			# Found one encrypted device!
			dev = os.path.join("/dev", line[0])
			dct[dev] = LUKSdrive(string_device=dev)
	
	return dct

def refresh():
	""" Refreshes. """
	
	global LUKSdevices
	
	LUKSdevices = return_luks()

refresh()

