# -*- coding: utf-8 -*-
# linstaller userhost module install - (C) 2011 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.frontends.glade as glade
import linstaller.core.main as m
import t9n.library
_ = t9n.library.translation_init("linstaller")

from linstaller.core.main import warn,info,verbose

class Progress(glade.Progress):
	def progress(self):
		
		try:
			verbose("Creating user")
			# USER: set.
			self.parent.moduleclass.install.user_set()
			self.parent.progress_set_percentage(1)
			
			# USER: commit.
			self.parent.moduleclass.install.user_commit()
			self.parent.progress_set_percentage(2)
			
			verbose("Setting username")
			# HOSTNAME: commit
			self.parent.moduleclass.install.host_commit()
			self.parent.progress_set_percentage(3)
		finally:
			# Exit
			self.parent.moduleclass.install.close()

class Frontend(cli.Frontend):
	def start(self):
		""" Start the frontend """

		self.progress_set_quota(3)
	
	def process(self):
		""" Called when we should do things! """
		
		prog = Process(self)
		prog.start()

