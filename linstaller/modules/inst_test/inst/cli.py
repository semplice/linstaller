# -*- coding: utf-8 -*-
# linstaller inst_test module install - (C) 2012 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.frontends.cli as cli
import linstaller.core.main as m
import t9n.library
_ = t9n.library.translation_init("linstaller")

from linstaller.core.main import warn,info,verbose

import time

class Frontend(cli.Frontend):
	def start(self):
		""" Start the frontend """

		verbose("Testing install...")
		
		target = 50
		
		# Get a progressbar
		progress = self.progressbar(_("Testing:"), target)

		# Start progressbar
		progress.start()

		done = 0
		while done != target:
			time.sleep(0.1)
			progress.update(done)
			done += 1
		
		progress.finish()

