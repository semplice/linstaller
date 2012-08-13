#!/usr/bin/env python
# linstaller setup (using distutils)
# Copyright (C) 2011 Eugenio "g7" Paolantonio. All rights reserved.
# Work released under the GNU GPL license, version 3.

import os
import sys
from distutils.core import setup
from distutils import cmd

## FIXME: Need to properly get the install-lib variable from setup.cfg or command line
install_to = "/usr/share/linstaller"

class what_I_should_do_to_get_an_heck_of_a_configuration_variable(cmd.Command):
	def initialize_options(self):
		pass
		
	def finalize_options(self):
		pass
		
	def run(self):
		return self.get_finalized_command("install").install_lib


def search_for_glade():
	""" Searches for glade files, and creates a properly-syntaxed list object to be added to data_files. """
	
	data_files = []
	symlinks = {}
	
	for directory, dirnames, filenames in os.walk("linstaller/"):
		this_dir = [os.path.join(install_to, directory), []]
		this_dir_changed = False
		for file in filenames:
			if ".glade" in file:
				# We got it!
				if not os.path.islink(os.path.join(directory, file)):
					this_dir[1].append(os.path.join(directory, file))
					this_dir_changed = True
				else:
					symlinks[os.path.join(directory, file)] = os.readlink(os.path.join(directory, file))
		
		if this_dir_changed: data_files.append(tuple(this_dir))
	
	return data_files, symlinks
		

data, symlinks = search_for_glade()
data_files = [
	("/usr/bin", ["linstaller_wrapper.sh", "mount_nolive.sh"]),
	("/etc/linstaller", ["config/semplice", "config/semplice-base", "config/semplice-nolive", "config/ubuntu", "config/ubuntu-nolive", "config/semplice-persistent", "config/semplice-persistent-nolive", "config/semplice-raspberrypi"]),
	("/usr/share/alan/alan/ext", ["alan/linstaller_alan.py"]),
]
data_files += data

distrib = setup(name='linstaller',
      version='2.71.2',
      description='Modular, preseedable, GNU/Linux distribution installer',
      author='Eugenio Paolantonio and the Semplice Team',
      author_email='me@medesimo.eu',
      url='http://launchpad.net/linstaller',
      scripts=['linstaller.py'],
      packages=["linstaller", "linstaller.core", "linstaller.frontends", "linstaller.core.libmodules",
      "linstaller.core.libmodules.chroot",
      "linstaller.core.libmodules.partdisks",
      "linstaller.core.libmodules.unsquash",
      
      "linstaller.services",
      "linstaller.services.glade",
      
      "linstaller.frontends.glade",
      
      "linstaller.modules",
      
      "linstaller.modules.bootloader",
      "linstaller.modules.bootloader.front",
      "linstaller.modules.bootloader.front.glade",
      "linstaller.modules.bootloader.inst",
      "linstaller.modules.bootloader.inst.glade",
      
      "linstaller.modules.debian",
      "linstaller.modules.debian.inst",
      "linstaller.modules.debian.inst.glade",
      
      "linstaller.modules.mirrorselect",
      "linstaller.modules.mirrorselect.front",
      "linstaller.modules.mirrorselect.front.glade",
      "linstaller.modules.mirrorselect.inst",
      "linstaller.modules.mirrorselect.inst.glade",
      
      "linstaller.modules.clean",
      "linstaller.modules.clean.inst",
      
      "linstaller.modules.end",
      "linstaller.modules.end.front",
      "linstaller.modules.end.front.glade",
      
      "linstaller.modules.fstab",
      "linstaller.modules.fstab.inst",
      
      "linstaller.modules.language",
      "linstaller.modules.language.front",
      "linstaller.modules.language.front.glade",
      "linstaller.modules.language.inst",
      "linstaller.modules.language.inst.glade",
      
      "linstaller.modules.network",
      "linstaller.modules.network.inst",
      
      "linstaller.modules.partdisks",
      "linstaller.modules.partdisks.front",
      "linstaller.modules.partdisks.front.glade",
      "linstaller.modules.partdisks.inst",
      
      "linstaller.modules.semplice",
#      "linstaller.modules.semplice.inst",

      "linstaller.modules.ubuntu",
      "linstaller.modules.ubuntu.inst",
      
      "linstaller.modules.summary",
      "linstaller.modules.summary.front",
      "linstaller.modules.summary.front.glade",
      
      "linstaller.modules.timezone",
      "linstaller.modules.timezone.front",
      "linstaller.modules.timezone.front.glade",
      "linstaller.modules.timezone.inst",
      "linstaller.modules.timezone.inst.glade",
      
      "linstaller.modules.unsquash",
      "linstaller.modules.unsquash.inst",
      "linstaller.modules.unsquash.inst.glade",
      
      "linstaller.modules.update",
      "linstaller.modules.update.front",
      "linstaller.modules.update.front.glade",
      
      "linstaller.modules.userhost",
      "linstaller.modules.userhost.inst",
      "linstaller.modules.userhost.inst.glade",
      "linstaller.modules.userhost.front",
      "linstaller.modules.userhost.front.glade",
      
      "linstaller.modules.welcome",
      "linstaller.modules.welcome.front",
      "linstaller.modules.welcome.front.glade",
      
      "linstaller.modules.raspberrypi",
      "linstaller.modules.raspberrypi.inst",
      
      "linstaller.modules.echo",
      "linstaller.modules.echo.bootloader",
      "linstaller.modules.echo.bootloader.inst",
      "linstaller.modules.echo.configure",
      "linstaller.modules.echo.configure.inst",
      "linstaller.modules.echo.copy",
      "linstaller.modules.echo.copy.inst",
      "linstaller.modules.echo.partusb",
      "linstaller.modules.echo.partusb.front",
      "linstaller.modules.echo.partusb.inst",
      ],
      data_files=data_files,
      requires=['gi.repository.Gtk', 'gi.repository.GObject', 'gi.repository.Gdk', 'apt.cache', 'ConfigParser', 'commands', 'copy', 'getpass', 'os', 'progressbar', 'subprocess', 'threading', 'traceback', 'debconf', 'exceptions', 'keeptalking', 'operator', 'parted', 'sys', 't9n.library', 'time'],
     )

clss = what_I_should_do_to_get_an_heck_of_a_configuration_variable(distrib)
install_lib = clss.run()

# Recreate symlinks
if "install" in sys.argv:
	for path, linktarget in symlinks.items():
		path = os.path.join(install_lib, path)
		
		if not os.path.exists(os.path.dirname(path)): os.makedirs(os.path.dirname(path))
		
		print("symlinking %s -> %s..." % (linktarget, path))

		os.symlink(linktarget, path)
	
