# -*- coding: utf-8 -*-
# linstaller fstab module install - (C) 2011 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.core.module as module
import linstaller.core.main as m
import os
import commands
import shutil

import linstaller.core.libmodules.partdisks.library as lib
import linstaller.core.libmodules.partdisks.crypt as crypt
import linstaller.core.libmodules.partdisks.lvm as lvm

ZRAM_LIMIT = 4096 # If user's ram <= this value, zram will be configured.

class Install(module.Install):
	def generate(self):
		""" Generates /etc/fstab. """
		
		with open("/etc/fstab","w") as fstab:
			
			fstab.write("""# /etc/fstab: static file system information.
#
# <file system> <mount point>   <type>  <options>       <dump>  <pass>

proc   /proc   proc   defaults   0   0
""")

			# Get changed.
			changed = self.moduleclass.modules_settings["partdisks"]["changed"]

			mountpo = []
			changeslist = {}
			
			# Regenerate changed to sort it sanely
			for key, value in changed.items():
				if not "useas" in value["changes"]:
					# There isn't "useas" in changes; skipping this item
					continue

				mountpo.append(value["changes"]["useas"])
				changeslist[value["changes"]["useas"]] = key
			
			mountpo.sort()

			for point in mountpo:
				# Get correct partition
				key = changeslist[point]
				# Get value
				value = changed[key]
				
				# Get UUID
				UUID = commands.getoutput("blkid -s UUID %s | awk '{ print $2 }' | cut -d \"=\" -f2 | sed -e 's/\"//g'" % (key))

				# Write to fstab
				mountpoint = value["changes"]["useas"]
				if not value["obj"].fileSystem: continue # Skip if fileSystem is None.
				filesystem = value["obj"].fileSystem.type
				if filesystem in ("fat32","fat16"): filesystem = "vfat"
				if mountpoint == "/":
					# root partition.
					opts = "relatime,errors=remount-ro"
				elif mountpoint == "swap":
					# swap.
					opts = "sw"
					mountpoint = "none"
					filesystem = "swap"
				elif filesystem == "vfat":
					# FAT partition, needs special opts.
					opts = "auto,users,rw,quiet,umask=000,shortname=lower"
				else:
					# Normal partition.
					opts = "defaults"
				
				# We need to properly set-up mountpoints for partitions which are not formatted but the user asked us
				# to mount at boot.
				# The module needs to check if the partition is already mounted (thus handled by partdisks) or, if not,
				# should check the mountpoint (and if exists, backup it and replace with an empty directory).
				
				if not mountpoint in ("/","none","swap"):
					if not os.path.exists(mountpoint):
						# Mountpoint doesn't exist, we can directly create it and be fine
						os.makedirs(mountpoint)
					elif not os.path.ismount(mountpoint):
						# Mountpoint exists and is not mounted (if mounted, it's already handled by partdisks)
						if not os.path.isdir(mountpoint):
							# Is the user unlucky? :) This should never happen in real use.
							raise m.UserError(_("mountpoint %s exists and it isn't a directory. Please change the mountpoint path.") % mountpoint)
						
						# The mountpoint exists and it's a directory. Check if it's empty.
						if len(os.listdir(mountpoint)) != 0:
							# It isn't. We need to backup it and create another mountpoint.
							shutil.move(mountpoint, "%s.linstaller_backup" % mountpoint)
							os.makedirs(mountpoint)
						# If it's empty, we are fine.
				
				fstab.write("# %(drive)s\nUUID=%(uuid)s   %(mpoint)s   %(filesystem)s   %(opts)s   0   0\n" % {"drive":key, "uuid":UUID, "mpoint":mountpoint, "filesystem":filesystem, "opts":opts})
			
			#CDROMDRIVE = commands.getoutput("cat /proc/mounts | grep \"/live/image\" | awk '{print $1}'")
			#fstab.write("# cdrom drive (%s)\n%s   /media/cdrom   udf,iso9660   user,noauto,exec,utf8   0   0\n" % (CDROMDRIVE,CDROMDRIVE))

	def crypttab(self):
		""" Generates /etc/crypttab. """
		
		if len(crypt.LUKSdevices) == 0:
			return
		
		with open("/etc/crypttab", "w") as f:
			for device, obj in crypt.LUKSdevices.items():
				# See if the device is a physical volume, otherwise
				# we will not touch it...
				if not obj.mapper_path in lvm.PhysicalVolumes:
					continue
				
				UUID = lib.get_UUID(device)
				
				f.write("%(name)s UUID=%(UUID)s none luks\n" % {"name":obj.crypt_name, "UUID":UUID})
		
		# Set proper owner and permissions on the file
		os.chown("/etc/crypttab", 0, 0)
		os.chmod("/etc/crypttab", 0744)
	
	def zramcfg(self):
		""" Configures zram via zramcfg. """
		
		# Get TotalMem size
		with open("/proc/meminfo") as mem:
			MemTotal = int(mem.readline().rstrip("\n").split(" ")[-2])/1024
		
		if not os.path.exists("/usr/bin/zramcfg") or not self.moduleclass.settings["zram"] or not MemTotal <= ZRAM_LIMIT:
			return
		
		m.sexec("/usr/bin/zramcfg")


class Module(module.Module):
	def _associate_(self):
		""" Shut up associate as we do not have any frontend. """
		
		pass

	def start(self):
		""" Start module """
		
		self.install = Install(self)
		
		m.verbose("Configuring fstab...")
		
		try:
			# FSTAB: set.
			self.install.generate()
			# Also set-up crypttab...
			self.install.crypttab()
			# Also configure zram...
			self.install.zramcfg()
		finally:
			# Exit
			self.install.close()
	
	def seedpre(self):
		""" Cache settings. """
		
		self.cache("zram",True)
		
