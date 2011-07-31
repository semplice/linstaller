# -*- coding: utf-8 -*-
# linstaller core cli frontend library - (C) 2011 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import os, sys
import getpass
import progressbar

import linstaller.core.main as m
from linstaller.core.main import warn,info,verbose

import t9n.library
_ = t9n.library.translation_init("linstaller")

class CLIFrontend:
	def __init__(self, moduleclass):
		
		self.moduleclass = moduleclass
		self.settings = moduleclass.settings
		self.changed = moduleclass.changed
	
	def end(self):
		""" close frontend and parents. """
		
		verbose("User requested to end.")
		sys.exit(0)
	
	def header(self, _pass):
		""" Displays the installer's header (new page) """
		
		# First, running "clear"
		os.system("clear")
		
		# Second, write the header
		print(_pass)
		# Now write ------- lines after the pass
		for num in range(0, len(_pass)):
			sys.stdout.write("-")
		sys.stdout.write("\n\n")
	
	def entry(self, text, password=False, blank=False):
		""" Displays and entry prompt (normal or password) """
		
		if password == True:
			choice = getpass.getpass(text + ": ")
		else:
			choice = raw_input(text + ": ")
		
		if not choice and blank == False:
			warn(_("You must insert something!"))
			return self.entry(text, password=password, blank=blank)
		else:
			return choice

	def question(self, text, default=None):
		""" A simple yes/no prompt.
		
		if default == None; the user should insert y or n
		if default == False; the user can press ENTER to say n
		if default == True; the user can press ENTER to say y
		"""
		
		if default != None:
			# We can enable blank on entry.
			blank = True
			if default == True:
				# Modify suffix:
				prompt_suffix = _("[Y/n]")
			else:
				# default = False
				prompt_suffix = _("[y/N]")
		else:
			# Nothing default...
			prompt_suffix = _("[y/n]")
			blank = False
		
		result = self.entry("%s %s" % (text, prompt_suffix), blank=blank)
		if not result:
			# result is "", so blank == True... we should set to "y" or "n" according to default.
			if default:
				# = yes
				result = True
			else:
				# = no
				result = False
		else:
			# result is populated.
			result = result.lower() # Make sure it is all lowered
			if _("y") == result:
				# Set y, untranslated.
				result = True
			elif _("n") == result:
				# Set n, untranslated.
				result = False
			elif _("yes") in result:
				# This should be y.
				result = True
			elif _("no") in result:
				# This should be n.
				result = False
			else:
				# Unknown value...
				warn(_("Unknown value %s. Please re-try." % result))
				result = self.question(text, default=default)
		
		# Finally return value
		return result
	
	def progressbar(self, text, maxval):
		""" Creates a progressbar object. """

		widgets = [text, progressbar.Percentage(), ' ', progressbar.Bar(marker='#',left='[',right=']'),' ', progressbar.ETA()]
		return progressbar.ProgressBar(widgets=widgets, maxval=maxval)
