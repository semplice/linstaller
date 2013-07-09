# -*- coding: utf-8 -*-
# linstaller bootloader module install - (C) 2011 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.core.module as module
import linstaller.core.main as m

from linstaller.core.main import warn,info,verbose

import sys, fileinput

class Install(module.Install):
	def grub_install(self):
		""" Installs grub. """

		# Get target
		target = self.moduleclass.modules_settings["bootloader"]["device"]

		verbose("Selected location: %s" % target)

		if "uefidetect.inst" in self.moduleclass.modules_settings and self.moduleclass.modules_settings["uefidetect.inst"]["uefi"] == True:
			# UEFI (need blank grub-install)
			location = ""
			args = ""
		if target == "root":
			# Root.
			location = self.moduleclass.modules_settings["partdisks"]["root"]
			args = "--no-floppy --force"
		else:
			# MBR
			
			# Latest GRUB fucked up the (hd0) method, we need to get the
			# first drive by ourselves...
			with open("/proc/partitions","r") as f:
				for line in f.readlines():
					# Drop \n, split and grab the last section
					line = line.replace("\n","").split(" ")[-1]
					if not line in ("name",""):
						location = "/dev/%s" % line
						break
					
			args = "--no-floppy"
			
		m.sexec("grub-install %(args)s '%(location)s'" % {"args":args,"location":location})
		
		# Adjust config in order to enable hibernate...
		if "partdisks" in self.moduleclass.modules_settings and "swap" in self.moduleclass.modules_settings["partdisks"]:
			swap = self.moduleclass.modules_settings["partdisks"]["swap"]
			#UUID = commands.getoutput("blkid -s UUID %s | awk '{ print $2 }' | cut -d \"=\" -f2 | sed -e 's/\"//g'" % (swap))
			
			# Edit grub config
			if swap:
				for line in fileinput.input("/etc/default/grub",inplace=1):
					# WARNING: Ugly-ness excess in this for
					if line[0] != "#":
						splitted = line.split("=")
						if splitted[0] == "GRUB_CMDLINE_LINUX_DEFAULT":
							sys.stdout.write("GRUB_CMDLINE_LINUX_DEFAULT=\"quiet resume=%s\"\n" % swap)
							# FIXME: The above line overwrites the entire CMDLINE_DEFAULT. Also, 'swap' is used.
							# We should decide if use it or its UUID.
						else:
							sys.stdout.write(line)
					else:
						sys.stdout.write(line)
	
	def grub_update(self):
		""" Updates grub menu list """

		m.sexec("update-grub")

class Module(module.Module):
	def start(self):
		""" Start module """
		
		self.install = Install(self)
		self._install = {"grub":self.install.grub_install}
		self._update = {"grub":self.install.grub_update}
		
		module.Module.start(self)

