# -*- coding: utf-8 -*-
# linstaller fstab module install - (C) 2011 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.core.cli_frontend as cli
import linstaller.core.module as module
import linstaller.core.main as m
import os
import commands
import shutil
import t9n.library
_ = t9n.library.translation_init("linstaller")

from linstaller.core.main import warn,info,verbose
import linstaller.core.libmodules.chroot.library as lib

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


class CLIFrontend(cli.CLIFrontend):
	def start(self):
		""" Start the frontend """

		verbose("Configuring fstab...")
		
		# Get a progressbar
		progress = self.progressbar(_("Configuring fstab:"), 1)

		# Start progressbar
		progress.start()

		verbose("Generating fstab")
		try:
			# FSTAB: set.
			self.moduleclass.install.generate()
			progress.update(1)
		finally:
			# Exit
			self.moduleclass.install.close()
		
		progress.finish()

class Module(module.Module):
	def start(self):
		""" Start module """
		
		self.install = Install(self)
		
		module.Module.start(self)
		
	def _associate_(self):
		""" Associate frontends. """
		
		self._frontends = {"cli":CLIFrontend}
