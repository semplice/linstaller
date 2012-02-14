# -*- coding: utf-8 -*-
# linstaller fstab module install - (C) 2011 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.core.module as module
import commands

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

			for key, value in changed.items():
				
				if not "useas" in value["changes"]:
					# There isn't "useas" in changes; skipping this item
					continue
				
				# Get UUID
				UUID = commands.getoutput("blkid -s UUID %s | awk '{ print $2 }' | cut -d \"=\" -f2 | sed -e 's/\"//g'" % (key))

				# Write to fstab
				mountpoint = value["changes"]["useas"]
				filesystem = value["obj"].fileSystem.type
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
				
				fstab.write("# %(drive)s\nUUID=%(uuid)s   %(mpoint)s   %(filesystem)s   %(opts)s   0   0\n" % {"drive":key, "uuid":UUID, "mpoint":mountpoint, "filesystem":filesystem, "opts":opts})
			
			#CDROMDRIVE = commands.getoutput("cat /proc/mounts | grep \"/live/image\" | awk '{print $1}'")
			#fstab.write("# cdrom drive (%s)\n%s   /media/cdrom   udf,iso9660   user,noauto,exec,utf8   0   0\n" % (CDROMDRIVE,CDROMDRIVE))


class Module(module.Module):
	def start(self):
		""" Start module """
		
		self.install = Install(self)
		
		module.Module.start(self)
