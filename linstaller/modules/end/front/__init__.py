# -*- coding: utf-8 -*-
# linstaller end module frontend - (C) 2011 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.core.module as module

class Module(module.Module):
	def seedpre(self):
		""" Cache configuration used by this module. """
		
		self.cache("reboot")
