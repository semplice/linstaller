# -*- coding: utf-8 -*-
# linstaller network module install - (C) 2011 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.core.cli_frontend as cli
import linstaller.core.module as module
import linstaller.core.main as m
import commands
import t9n.library
_ = t9n.library.translation_init("linstaller")

from linstaller.core.main import warn,info,verbose
import linstaller.core.libmodules.chroot.library as lib

class Install(module.Install):
	def configure(self):
		""" Configures network. """
		
		# /etc/resolv.conf
		with open("/etc/resolv.conf", "w"):
			pass

		# /etc/network/interfaces (configure loopback)
		with open("/etc/network/interfaces", "w") as interfaces:
			interfaces.write("""# The loopback network interface
auto lo
iface lo inet loopback
""")

class CLIFrontend(cli.CLIFrontend):
	def start(self):
		""" Start the frontend """

		verbose("Configuring networking...")
		
		# Get a progressbar
		progress = self.progressbar(_("Configuring networking:"), 1)

		# Start progressbar
		progress.start()

		verbose("Generating networking")
		# NETWORKING: set.
		self.moduleclass.install.configure()
		progress.update(1)

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
