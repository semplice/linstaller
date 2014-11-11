# -*- coding: utf-8 -*-
# linstaller bootloader module install - (C) 2011 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.core.module as module
import linstaller.core.main as m

from linstaller.core.main import warn,info,verbose

from linstaller.core.libmodules.partdisks.library import check_distributions

import os, sys, fileinput
import commands

## Why are we using the "manual" install method instead of debconf?
## First, we want to keep some sort of compatibility with non-Debian
## distros.
## But the most important reason is that we are unable to get the first
## hard-drive without using grub's tools.
## We can use /proc/partitions but it's better to not rely on it.
## Another solution is to split package installation and install 
## the packages which requires configuration (grub-pc, grub-efi-*)
## at last, but we really do not want to split things.
## So, at last, we are using OUR method (it's OUR installer after all)
## and even if we love debconf, in this case is a no go.

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
		
		
		# WORKAROUND! This makes supportrepo unusable by other modules,
		# so it needs to be fixed ASAP!
		# FIXME: supportrepo clashes with libbricks's apt.cache object.
		# This workaround fixes that.
		self.moduleclass.cache.change_rootdir("/")		
		self.moduleclass.cache = None
	
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
		elif target == "mbr":
			# MBR
			
			# Latest GRUB fucked up the (hd0) method, we need to get the
			# first drive by ourselves...
			m.sexec("grub-mkdevicemap --no-floppy --device-map=/tmp/.linstaller")
			
			with open("/tmp/.linstaller","r") as f:
				# While previously we have simply read the first line of
				# the devicemap, we discovered that in some cases grub
				# sees as the first drive an eventual SD card, thus
				# fucking up the entire grub install process (and the installation
				# will fail because the first device is a partition)
				#
				# We workaround this by looping through all the lines
				# and break when needed.
				for line in f.readlines():
					line = os.path.realpath(line.replace("\n","").split("	")[-1])
					if "mmcblk" in line:
						# Sd card, skip
						continue
					
					# If we are here, the line we found is correct.
					break
				location = line
					
			args = "--no-floppy"
		else:
			# Forced
			location = self.moduleclass.modules_settings["bootloader"]["device"]
			args = "--no-floppy"

		if not "uefidetect.inst" in self.moduleclass.modules_settings or self.moduleclass.modules_settings["uefidetect.inst"]["uefi"] == False:
			# Also set the location in debconf database, to avoid apt to
			# bug us when an upgrade of grub occours
			# FIXME: this breaks systems without the debconf module,
			# i.e. every non-Debian based distributions.
			import debconf
			db = debconf.DebconfCommunicator("linstaller")
			db.set("grub-pc/install_devices", location)
			db.shutdown() # Exit.
			
			
		m.sexec("grub-install %(args)s '%(location)s'" % {"args":args,"location":location})
		
		should_hide_menu = self.moduleclass.modules_settings["bootloader"]["should_hide_menu"]
		# Let's see if we can hide the GRUB menu...
		if should_hide_menu:
			distribs = check_distributions()
			
			if distribs:
				# Found other system, disable should_hide_menu
				should_hide_menu = False
		
		custom_init = self.moduleclass.modules_settings["bootloader"]["custom_init"]
		if custom_init and not os.path.exists(custom_init) or (
			os.path.islink("/sbin/init") and os.readlink("/sbin/init") == custom_init
		):
			# If we are here, the specified init replacement doesnt' exist
			# or /sbin/init is already symlinked to that (thus removing
			# the need of the custom init= parameter).
			#
			# The readlink workaround is here to avoid breaking installations
			# on stock Semplice 6, while removing the now useless init=
			# parameter on Semplice 7+
			custom_init = None
		
		if "partdisks" in self.moduleclass.modules_settings and "swap" in self.moduleclass.modules_settings["partdisks"]:
			swap = self.moduleclass.modules_settings["partdisks"]["swap"]
		else:
			swap = None
		
		# Adjust config in order to enable hibernate...
		if should_hide_menu or custom_init or swap:
			#UUID = commands.getoutput("blkid -s UUID %s | awk '{ print $2 }' | cut -d \"=\" -f2 | sed -e 's/\"//g'" % (swap))
			
			# Edit grub config
			for line in fileinput.input("/etc/default/grub",inplace=1):
				# WARNING: Ugly-ness excess in this for
				if line[0] != "#":
					splitted = line.split("=")
					if splitted[0] == "GRUB_CMDLINE_LINUX_DEFAULT" and swap:
						sys.stdout.write("GRUB_CMDLINE_LINUX_DEFAULT=\"quiet resume=%s\"\n" % swap)
						# FIXME: The above line overwrites the entire CMDLINE_DEFAULT. Also, 'swap' is used.
						# We should decide if use it or its UUID.
					elif splitted[0] == "GRUB_CMDLINE_LINUX" and custom_init:
						sys.stdout.write("GRUB_CMDLINE_LINUX=\"init=%s\"\n" % custom_init)
						# FIXME: The above line overwrites the entire CMDLINE_LINUX.
					elif splitted[0] == "GRUB_TIMEOUT" and should_hide_menu:
						sys.stdout.write("# As there aren't other systems installed, the menu is disabled by default.\n")
						sys.stdout.write("# Hold SHIFT during boot to open it.\n")
						sys.stdout.write("GRUB_TIMEOUT=0 # Set to a value != 0 to show the menu.\n")
						sys.stdout.write("GRUB_HIDDEN_TIMEOUT=2 # Comment this to show the menu.\n")
						sys.stdout.write("GRUB_HIDDEN_TIMEOUT_QUIET=true # Comment this to show the menu.\n")
					else:
						sys.stdout.write(line)
				else:
					sys.stdout.write(line)
		
		# FIXME: This isn't the best place to but the following here, is it?
		# If /bin/systemd-machine-id-setup exists, generate /etc/machine-id
		if os.path.exists("/bin/systemd-machine-id-setup"):
			m.sexec("/bin/systemd-machine-id-setup")
	
	def grub_update(self):
		""" Updates grub menu list """

		m.sexec("update-grub")

class Module(module.Module):
	def start(self):
		""" Start module """
		
		if "supportrepo.inst" in self.modules_settings:
			self.cache = self.modules_settings["supportrepo.inst"]["cache"]
		else:
			self.cache = None

		self._pkgs_fetch = {"grub":self.grub_pkgs_fetch}
		
		module.Module.start(self)
		
		# Reset rootdir
		if self.cache: self.cache.change_rootdir(self.main_settings["target"])

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
