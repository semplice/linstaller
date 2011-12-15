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
	def __header(self):
		self.header("HEADER: linstaller widget test") # Header
	
	def __entry1(self):
		res = self.entry("ENTRY #1: Please enter a string:")
		print("String was %s" % res)
	
	def __entry2(self):
		res = self.entry("ENTRY #2: Please enter a string (blank accepted)", blank=True)
		print("String was %s" % res)
	
	def __passwordentry(self):
		res = self.entry("PASSWORDENTRY: Please enter a password", password=True)
		print("String length was %d" % len(res))
		
	def __question1(self):
		res = self.question("QUESTION #1: Nothing default")
		print("Answer was %s") % res
	
	def __question2(self):
		res = self.question("QUESTION #2: Yes is default", default=True)
		print("Answer was %s") % res
	
	def __question3(self):
		res = self.question("QUESTION #3: No is default", default=False)
		print("Answer was %s") % res
	
	def __progressbar(self):
		progressbar = self.progressbar("PROGRESSBAR", int(self.settings["progressbar_val"]))
		progressbar.start()
		
		counter = 1
		while counter != int(self.settings["progressbar_val"]):
			progressbar.update(counter)
			counter += 1
			time.sleep(float(self.settings["progressbar_sleep"]))
		
		progressbar.finish()
	
	def __unordered(self):
		print("UNORDERED LIST")
		
		self.action_list(lst=("This","These","That","Those"), typ="unordered", after="End unordered list")
	
	def __ordered(self):
		print("ORDERED LIST")
		
		res = self.action_list(lst={"This":self.__list_one, "These":self.__list_two, "That":self.__list_three, "Those":self.__list_four}, after="Uh. Lol.", selection_text="SELECTION: Please insert the number")
		
		print res
		
		res()

	def start(self):
		""" Start the frontend """

		__sequence_list = {"header":self.__header, "entry1":self.__entry1, "entry2":self.__entry2, "passwordentry":self.__passwordentry, "question1":self.__question2, "question2":self.__question2, "question3":self.__question3, "progressbar":self.__progressbar, "unordered":self.__unordered, "ordered":self.__ordered}

		# Split sequence
		sequence = self.settings["sequence"].split(" ")
		
		# Iterate
		for item in sequence:
			if not item in __sequence_list:
				verbose("Unable to execute %s" % item)
				continue # Skip
			
			__sequence_list[item]()

	
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

	def seedpre(self):
		""" Preseeds items """
		
		self.cache("sequence", "header entry1 entry2 passwordentry question1 question2 question3 progressbar unordered ordered")
		self.cache("progressbar_val", "100")
		self.cache("progressbar_sleep", "0.01")
