# -*- coding: utf-8 -*-
# linstaller bootloader module install - (C) 2011 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.core.module as module
import linstaller.core.main as m

from linstaller.core.main import warn,info,verbose

import os, sys, fileinput
import commands

UEFIplatforms = {
	"i386": "i386-efi",
	"amd64": "x86_64-efi"
}

class Install(module.Install):
	def grub_pkgs_install(self):
		""" Installs the packages previously fetched. """
		
		if not self.moduleclass.cache:
			# Older Semplice release, no repo, returning nicely
			return
		
		# We need to reset the cache rootdir to / because we are into the
		# chroot.
		self.moduleclass.cache.change_rootdir("/")
		
		# Now we can commit.
		self.moduleclass.cache.commit()
	
	def grub_install(self):
		""" Installs grub. """

		# Get target
		target = self.moduleclass.modules_settings["bootloader"]["device"]

		verbose("Selected location: %s" % target)

		if "uefidetect.inst" in self.moduleclass.modules_settings and self.moduleclass.modules_settings["uefidetect.inst"]["uefi"] == True:
			# UEFI (need blank grub-install)
			
			# We need to get the architecture on which we are running.
			# platform.machine() is not reliable as it will give the host system's architecture
			# So we are relying on dpkg-architecture (if Debian system), or fallbacking
			# to amd64 if not a Debian system
			if os.path.exists("/usr/bin/dpkg-architecture"):
				arch = commands.getoutput("/usr/bin/dpkg-architecture -qDEB_BUILD_ARCH")
			else:
				arch = "amd64"
			
			location = ""
			args = "--target=%s" % UEFIplatforms[arch]
		elif target == "root":
			# Root.
			location = self.moduleclass.modules_settings["partdisks"]["root"]
			args = "--no-floppy --force"
		else:
			# MBR
			location = "(hd0)"
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
		
		if "supportrepo.inst" in self.modules_settings:
			self.cache = self.modules_settings["supportrepo.inst"]["cache"]

		self._pkgs_fetch = {"grub":self.grub_pkgs_fetch}
		
		module.Module.start(self)
		
		# Reset rootdir
		self.cache.change_rootdir(self.main_settings["target"])

	def grub_pkgs_fetch(self):
		""" Selects and fetches the bootloader from the supportrepo. """
		
		if not self.cache:
			# Older Semplice release, no repo, returning nicely
			return
		
		if "uefidetect.inst" in self.modules_settings and self.modules_settings["uefidetect.inst"]["uefi"] == True:
			# UEFI
			self.cache["grub-efi"].mark_install()
		else:
			# Normal BIOS or unable to detect
			self.cache["grub-pc"].mark_install()
				
		# FETCH!
		self.cache.local_fetch_changes()
	
	def install_phase(self):
		""" Set-ups self.install and relevant dictionaries.
		To be executed by the frontend AFTER the package installation,
		as we should execute it outside the chroot. """
		
		self.install = Install(self)
		self._pkgs_install = {"grub":self.install.grub_pkgs_install}
		self._install = {"grub":self.install.grub_install}
		self._update = {"grub":self.install.grub_update}

