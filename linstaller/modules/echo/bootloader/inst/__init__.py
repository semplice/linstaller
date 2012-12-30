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
		
		directory = os.path.join(self.main_settings["target"], "syslinux")
		
		bootloader = self.settings["bootloader"]
		if not bootloader:
			# We should get the bootloader ourselves.
			# What this means? We need to check for the partition type and set the appropiate bootloader.
			
			fs = part.fileSystem.type
			if fs in ("fat32"):
				bootloader = "syslinux"
			elif fs in ("ext2","ext3","ext4"):
				args = "-i '%(location)s'" % {"location":target}
				bootloader = "extlinux"
		
		if bootloader == "syslinux":
			args = "-i -d '%(dir)s' '%(location)s'" % {"dir":directory,"location":target}
		elif bootloader == "extlinux":
			# Generate extlinux configuration file (FIXME)
			with open(os.path.join(directory, "extlinux.cfg"), "w") as f:
				f.write("include syslinux.cfg\n")
			
			# Install MBR (warning: we do not make backups! Are they needed on USB drives MBR?)
			# FIXME: maybe find a cooler way to do this?
			m.sexec("dd if=/usr/lib/extlinux/mbr.bin of='%s' bs=440 count=1" % lib.return_device(target))
			
			args = "-i '%(dir)s'" % {"dir":directory}
		
		verbose("Selected location: %s" % target)
					
		m.sexec("%(bootloader)s %(args)s" % {"bootloader":bootloader, "args":args})
		
		# Make partition bootable...
		verbose("Making partition bootable...")
		lib.setFlag(part, "boot")
		lib.commit(part, (target)) # Commit
				
	def seedpre(self):
		""" Cache preseeds. """
		
		self.cache("target")
		self.cache("bootloader")
