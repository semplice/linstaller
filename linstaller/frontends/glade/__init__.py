# -*- coding: utf-8 -*-
# linstaller glade frontend - (C) 2012 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a frontend of linstaller, should not be executed as a standalone application.

from gi.repository import Gtk, Gdk

import linstaller.core.main as m
from linstaller.core.main import warn,info,verbose

import linstaller.core.frontend

import time

import t9n.library
_ = t9n.library.translation_init("linstaller")

class Frontend(linstaller.core.frontend.Frontend):
	def __init__(self, moduleclass):
		
		self.objects = None
		
		linstaller.core.frontend.Frontend.__init__(self, moduleclass)
		
	def start(self):
		""" This function, the one that other frontends normally override, will only wait.
		The glade service, which MUST be awake and alive, will handle everything.
		
		Developers should override the ready() function. """
		
		while self.res == False:
			time.sleep(0.1)
		
		return self.res
	
	def ready(self):
		""" Ovveride this function to manage frontend objects (declared onto the self.objects dictionary). """
		
		pass
