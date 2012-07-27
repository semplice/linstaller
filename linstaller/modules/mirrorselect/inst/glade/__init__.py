# -*- coding: utf-8 -*-
# linstaller mirrorselect module install - (C) 2012 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.frontends.glade as glade
import linstaller.core.main as m
import t9n.library
_ = t9n.library.translation_init("linstaller")

from linstaller.core.main import warn,info,verbose

import time

class Select(glade.Progress):
	def progress(self):
		
		self.parent.progress_wait_for_quota()
		
		check = self.parent.moduleclass.modules_settings["mirrorselect"]["check"]
		
		try:
			if check == None:
				return # Should not check

			if not self.parent.moduleclass.install.prechecks():
				return # We can't continue.

			num = 0
			for set in self.parent.sets:
				num += 1
				if num == len(self.parent.sets):
					# We are on the last set!
					isLast = True
				else:
					isLast = False
				self.parent.progress_set_text(_("Searching for the best %s mirror...") % set)
				self.parent.moduleclass.install.select(set, isLast=isLast)
				self.parent.progress_set_percentage(num)
		except:
			self.parent.set_header("error", _("Mirrorselect crashed."), _("Please check sources.list(.d) later."))
			# Wait, hoping the user see in this time the error message
			time.sleep(5)
		finally:
			# Exit from chroot
			self.parent.moduleclass.install.close()	
		

class Frontend(cli.Frontend):
	def start(self):
		""" Start the frontend """
	
		self.sets = self.moduleclass.modules_settings["mirrorselect"]["sets"].split(" ")
	
		self.set_header("hold", _("Selecting the fastest mirrors..."), _("The installer is checking for the fastest mirror for your zone."))
		
		self.progress_set_quota(len(self.sets))
	
	def process(self):
		
		clss = Select(self)
		clss.start()
	
