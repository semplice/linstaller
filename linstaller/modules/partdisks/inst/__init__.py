# -*- coding: utf-8 -*-
# linstaller partdisks module install - (C) 2011 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.core.module as module

from linstaller.core.main import warn,info,verbose
import linstaller.core.libmodules.partdisks.library as lib

import os

class Module(module.Module):
	def _associate_(self):
		""" Shut up associate as we do not have any frontend. """
		
		pass
		
	def start(self):
		""" Start override to unsquash. """
		
		verbose("Let's fix this shit - Starting")
		
		if "partdisks" in self.modules_settings:
			settings = self.modules_settings["partdisks"]
		else:
			settings = self.settings
		
		# Mount root partition.
		root = settings["root"]

		verbose("Let's fix this shit - Checking if root is mounted")

		# Ensure that is unmounted
		if os.path.ismount(self.main_settings["target"]):
			# Target mounted. Unmount
			lib.umount(path=self.main_settings["target"])
		if lib.is_mounted(root):
			# Partition mounted. Unmount
			lib.umount(path=root)
		
		verbose("Let's fix this shit - Mounting root")
		
		# Then mount at TARGET
		lib.mount_partition(path=root, target=self.main_settings["target"])

		used = []
		
		verbose("Let's fix this shit - Getting changed")
		
		# Mount every partition which has "useas" on it
		# Get changed.
		try:
			changed = self.modules_settings["partdisks"]["changed"]
		except:
			# Pass
			changed = {}
		
		mountpo = []
		changeslist = {}
		
		verbose("Let's fix this shit - Sorting changed")
		
		# Regenerate changed to sort it sanely
		for key, value in changed.items():
			if not "useas" in value["changes"]:
				# There isn't "useas" in changes; skipping this item
				continue

			mountpo.append(value["changes"]["useas"])
			changeslist[value["changes"]["useas"]] = key
		
		mountpo.sort()
		
		verbose("Let's fix this shit - Entering in loop...")
		
		for point in mountpo:
			
			verbose("Let's fix this shit - Processing %s" % mountpo)
			
			# Get correct partition
			key = changeslist[point]
			# Get value
			value = changed[key]
			
			verbose("    Let's fix this shit - Getting useas")
						
			# Get useas
			useas = value["changes"]["useas"]
			
			if useas in ("/","swap"):
				# Root or swap, do not use it
				continue
			
			verbose("    Let's fix this shit - Creating temporary mountpoint")
			
			# Create mountpoint
			mountpoint = self.main_settings["target"] + useas # useas begins with a /, so os.path.join doesn't work
			if not os.path.exists(mountpoint): os.makedirs(mountpoint)
			
			verbose("    Let's fix this shit - Trying to mount...")
			
			# Mount key to mountpoint
			if lib.is_mounted(key):
				# Umount
				verbose("    Let's fix this shit - Should umount!")
				lib.umount(path=key)
			if useas == "/boot/efi":
				# If this is going to be the /boot/efi partition
				# we should make sure that it's going to have the
				# proper partition type set to EFI System Partition
				lib.prepareforEFI(lib.return_partition(key))
			lib.mount_partition(path=key, target=mountpoint)
			
			verbose("    Let's fix this shit - Checking if partition is empty")
						
			# Ok, it is mounted. Now let's see if it is empty
			count = len(os.listdir(mountpoint))
			drop = False
			if count == 1:
				# The only one file may be lost+found
				if not os.listdir(mountpoint)[0] == "lost+found":
					# It isn't.
					drop = True # We cannot use it
			elif count > 1:
				# More than one file detected. We cannot use the partition at this stage.
				drop = True
			
			verbose("    Let's fix this shit - mount_on_install?")
			
			# If we mount_on_install, simply set drop to False, as we should use it anyway
			if ("mount_on_install" in value["changes"] and value["changes"]["mount_on_install"]) or useas in ("/boot","/boot/efi"):
				drop = False
			
			if drop:
				verbose("    Let's fix this shit - Should drop")
				# Umount partition, remove mountpoint
				lib.umount(path=key)
				os.rmdir(mountpoint)
			else:
				# Partition will be used during unsquash, we should remember when linstaller will execute revert
				verbose("    Let's fix this shit - Should keep")
				used.append(key)
		
		verbose("Let's fix this shit - Storing used")
				
		# Store used
		self.settings["used"] = used
			

	def revert(self):
		""" Umounts TARGET. """
		
		# Ensure that is mounted
		if not os.path.ismount(self.main_settings["target"]):
			# Umounted. pass.
			pass
		
		# See if "used" was... used :)
		if "partdisks.inst" in self.modules_settings and "used" in self.modules_settings["partdisks.inst"]:
			_used = self.modules_settings["partdisks.inst"]["used"]
			_used.reverse()
			if _used:
				for part in _used:
					if lib.is_mounted(part):
						try:
							lib.umount(path=part, tries=5)
						except:
							pass
		
		# Umount target, finally.
		try:
			lib.umount(path=self.main_settings["target"], tries=5)
		except:
			pass
	
	def seedpre(self):
		""" Cache settings """
		
		self.cache("used")
