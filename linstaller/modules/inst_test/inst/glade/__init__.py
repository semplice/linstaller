# -*- coding: utf-8 -*-
# linstaller inst_test module install - (C) 2012 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.frontends.glade as glade
import linstaller.core.main as m
import t9n.library
_ = t9n.library.translation_init("linstaller")

from linstaller.core.main import warn,info,verbose

import time

class DoThings(glade.Progress):
	def progress(self):
		done = 0
		while done != self.parent.target:
			time.sleep(0.1)
			self.parent.progress_set_text("Setting %s" % done)
			self.parent.progress_set_percentage(done)
			done += 1
		
class Frontend(glade.Frontend):
	def ready(self):
		""" Ready! (to wait...) """

		verbose("Testing install...")
		
		self.target = 50
		
		# Get a progressbar
		self.progress_set_quota(self.target)
	
	def process(self):
		""" Actually do things! """

		lol = DoThings(self)
		lol.start()
