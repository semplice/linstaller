# -*- coding: utf-8 -*-
# linstaller widget_test module frontend - (C) 2011 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.core.cli_frontend as cli
import linstaller.core.module as module
import t9n.library
_ = t9n.library.translation_init("linstaller")

import time

from linstaller.core.main import warn,info,verbose,root_check

class CLIFrontend(cli.CLIFrontend):
	def start(self):
		""" Start the frontend """

		self.header("HEADER: linstaller widget test") # Header
		
		res = self.entry("ENTRY #1: Please enter a string:")
		print("String was %s" % res)
		
		res = self.entry("ENTRY #2: Please enter a string (blank accepted)", blank=True)
		print("String was %s" % res)
		
		res = self.entry("PASSWORDENTRY: Please enter a password", password=True)
		print("String length was %d" % len(res))
		
		res = self.question("QUESTION #1: Nothing default")
		print("Answer was %s") % res
		
		res = self.question("QUESTION #2: Yes is default", default=True)
		print("Answer was %s") % res
		
		res = self.question("QUESTION #3: No is default", default=False)
		print("Answer was %s") % res
		
		progressbar = self.progressbar("PROGRESSBAR", 100)
		progressbar.start()
		
		counter = 1
		while counter != 100:
			progressbar.update(counter)
			counter += 1
			time.sleep(0.01)
		
		progressbar.finish()
		
		print("UNORDERED LIST")
		
		self.action_list(lst=("This","These","That","Those"), typ="unordered", after="End unordered list")
		
		print("ORDERED LIST")
		
		res = self.action_list(lst={"This":self.__list_one, "These":self.__list_two, "That":self.__list_three, "Those":self.__list_four}, after="Uh. Lol.", selection_text="SELECTION: Please insert the number")
		
		print res
		
		res()
	
	def __list_one(self):
		print "LOL"
	def __list_two(self):
		print "ASD"
	def __list_three(self):
		print "LMAO"
	def __list_four(self):
		print "ROTFL"

class Module(module.Module):
	def _associate_(self):
		""" Associate frontends. """
		
		self._frontends = {"cli":CLIFrontend}
