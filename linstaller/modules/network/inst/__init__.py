# -*- coding: utf-8 -*-
# linstaller network module install - (C) 2011 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.core.module as module

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

class Module(module.Module):
	def start(self):
		""" Start module """
		
		self.install = Install(self)
		
		module.Module.start(self)
