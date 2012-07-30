# -*- coding: utf-8 -*-
# linstaller command line frontend - (C) 2011-12 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a frontend of linstaller, should not be executed as a standalone application.

import os, sys
import getpass
import progressbar

import linstaller.core.frontend

import linstaller.core.main as m
from linstaller.core.main import warn,info,verbose

import t9n.library
_ = t9n.library.translation_init("linstaller")

class Frontend(linstaller.core.frontend.Frontend):
	class __ProgressBar:
		""" Wrapper to standard progressbar, in order to reduce installer crashes caused by progressbar exceptions. """
		
		def __init__(self, widgets, maxval):
			""" Creates the progressbar. """

			self.widgets = widgets
			self.maxval = maxval
			
			self.create_progressbar()
		
		def create_progressbar(self):
			""" Creates the progressbar. """
			
			self.progressbar = progressbar.ProgressBar(widgets=self.widgets, maxval=self.maxval)
		
		def start(self):
			""" Starts the progressbar. """
			
			self.progressbar.start()
		
		def update(self, num):
			""" Updates the progressbar. """
			
			try:
				self.progressbar.update(num)
			except:
				verbose("Progressbar crashed")
				# Generate a new progressbar, and update to the given value
				self.create_progressbar()
				self.update(num)
		
		def finish(self):
			""" Finishes the progressbar. """
			
			self.progressbar.finish()
	
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
	
	def entry(self, text, password=False, blank=False, onlyint=False):
		""" Displays and entry prompt (normal or password) """
		
		if password == True:
			choice = getpass.getpass(text + ": ")
		else:
			choice = raw_input(text + ": ")

		if onlyint:
			# We should check if it is an integer
			try:
				choice = int(choice)
			except:
				print "E: %s" % (_("You need to insert a number!"))

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
		return self.__ProgressBar(widgets=widgets, maxval=maxval)
	
	def action_list(self, lst, typ="ordered", after=False, selection_text=_("Please insert your action here"), skip_list=False):
		""" Creates a ordered/unordered list.
		
		Paramters:
		lst = dictionary that contains action name and action to be executed.
		type = "ordered" or "unordered". Default is "ordered".
		after = str that will be printed after the list.
		selection_text = text of the selection entry
		
		skip_list = internal
		
		WARNING: UNORDERED LIST WILL *NOT* PROMPT FOR ANYTHING.
		"""
		
		actions = {}
		
		ORDERED_OPERATOR = 0
		UNORDERED_OPERATOR = "*"
		
		if not skip_list:
			if typ == "unordered":
				# unordered uses tuples/lists for actions.
				
				for thing in lst:
					print "  %s %s" % (UNORDERED_OPERATOR, thing)
			else:
				# An example lst: {"Format partition":self.edit_partitions_format, ...}
				
				for name, action in lst.items():
					ORDERED_OPERATOR += 1 # Increase the operator by one
				
					# Print string
					print "  %d) %s" % (ORDERED_OPERATOR, name)
					
					# Link number to action
					actions[ORDERED_OPERATOR] = action
				
			# Print after.
			if after: print "\n" + after
			
		if typ == "unordered": return # If unordered, exit.
		
		print
		
		# Make the question
		result = self.entry(selection_text)
		try:
			result = int(result)
		except:
			return self.list(lst, typ=typ, selection_text=selection_text, skip_list=True)
		if not result in actions:
			return self.list(lst, typ=typ, selection_text=selection_text, skip_list=True)
		
		return actions[result]

			
