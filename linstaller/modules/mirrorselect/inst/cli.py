# -*- coding: utf-8 -*-
# linstaller mirrorselect module install - (C) 2012 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.frontends.cli as cli
import linstaller.core.main as m
import t9n.library
_ = t9n.library.translation_init("linstaller")

from linstaller.core.main import warn,info,verbose

class Frontend(cli.Frontend):
	def start(self):
		""" Start the frontend """

		# Sets
		sets = self.moduleclass.modules_settings["mirrorselect"]["sets"].split(" ")
		check = self.moduleclass.modules_settings["mirrorselect"]["check"]

		# Get a progressbar
		progress = self.progressbar(_("Selecting mirrors:"), len(sets))

		# Start progressbar
		progress.start()
		
		try:
			if check == None:
				return # Should not check

			if not self.moduleclass.install.prechecks():
				return # We can't continue.

			num = 0
			for set in sets:
				num += 1
				if num == len(sets):
					# We are on the last set!
					isLast = True
				else:
					isLast = False
				self.moduleclass.install.select(set, isLast=isLast)
				progress.update(num)
		except:
			warn(_("Mirrorselect crashed. Please check sources.list(.d) later."))
		finally:
			# Exit from chroot
			self.moduleclass.install.close()	
		
		progress.finish()
