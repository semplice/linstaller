# -*- coding: utf-8 -*-
# linstaller crashy2 module install - (C) 2011 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a test module of linstaller, should not be executed as a standalone application.

import linstaller.core.module as module
import linstaller.core.main as m

class Module(module.Module):
	def _associate_(self):
		""" Shut up associate as we do not have any frontend. """
		
		pass

	def start(self):
		""" Start module """
		
		m.verbose("Crashing2... ;)")
		
		raise m.UserError("Requested to crash2!")

	def revert(self):
		
		m.verbose("Revert2 called!")
