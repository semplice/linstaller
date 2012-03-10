# -*- coding: utf-8 -*-
# linstaller echo.bootloader module install - (C) 2012 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.core.module as module
import linstaller.core.main as m

from linstaller.core.main import verbose

import linstaller.core.libmodules.partdisks.library as lib

import os

class Module(module.Module):
	def install(self):
		""" Installs the bootloader on the specified device. """
		
		target = self.settings["target"]
		if not target:
			# No target, we should get one.
			try:
				target = self.modules_settings["partdisks"]["root"]
			except:
				# We can't get a target
				raise m.UserError("Please specify target device.")
		# Get partition
		part = lib.return_partition(target)
		if part == None:
			raise m.UserError("Target device %s not found." % target)
		
		bootloader = self.settings["bootloader"]
		if not bootloader:
			# We should get the bootloader ourselves.
			# What this means? We need to check for the partition type and set the appropiate bootloader.
			
			fs = part.fileSystem.type
			if fs in ("fat32"):
				bootloader = "syslinux"
			elif fs in ("ext2","ext3","ext4"):
				bootloader = "extlinux"
		
		verbose("Selected location: %s" % target)

		directory = "/linstaller/target/syslinux"
			
		m.sexec("%(bootloader)s -i -d '%(dir)s' '%(location)s'" % {"bootloader":bootloader, "dir":directory,"location":target})
		
		# Make partition bootable...
		verbose("Making partition bootable...")
		lib.setFlag(part, "boot")
				
	def seedpre(self):
		""" Cache preseeds. """
		
		self.cache("target")
		self.cache("bootloader")
