# -*- coding: utf-8 -*-
# linstaller glade service - (C) 2012 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a service of linstaller, should not be executed as a standalone application.

import linstaller.core.service
import linstaller.core.main as m

import os
import time

import threading

import t9n.library
_ = t9n.library.translation_init("linstaller")

from linstaller.core.main import info, warn, verbose

from gi.repository import Gtk, GObject

GObject.threads_init()

# Get linstaller main dir (a bit hacky and ugly)
MAINDIR = os.path.join(os.path.dirname(m.__file__), "..")
MODULESDIR = os.path.join(MAINDIR, "modules/")

uipath = os.path.join(MAINDIR, "services/glade/base_ui.glade")

class Service(linstaller.core.service.Service):
	""" The glade service is the core of the linstaller's glade frontend.
	A GUI is created and maintained by the service, and linstaller will
	trigger modules changes (whose GUIs are preloaded by this service), 
	thus reducing lags and presenting a cleaner environment. """
	
	def on_frontend_change(self):
		""" Focus on the frontend of the current module. """
		
		# Check if the frontend is glade (or a derivative), otherwise it's useless ;-)
		if "glade" in self.main_settings["frontend"]:
			self.current_frontend.objects = self.modules_objects[self.current_module.package.replace("linstaller.modules.","")]
			self.current_frontend.ready()
	
	def build_pages(self):
		""" Searches for support glade files and adds them to the pages object. """
		
		self.modules_objects = {}
		
		# Get modules
		modules = self.main_settings["modules"]
		
		# Following the format introduced with linstaller 3.0 alpha 1, the modules are residing in directories (so welcome.front is welcome/front/ and not welcome/front.py)
		# Some modules may have not been converted to the new format, and we should handle them too.
		
		# GLADE FRONTEND WILL BE SEARCHED IN welcome/front/glade/ AND NOT in welcome/front/glade.py!
		
		for module in modules.split(" "):
			module_new = module.replace(".","/")
			module_new = os.path.join(MODULESDIR, module_new + "/glade/module.glade")
			
			print module_new
			
			if not os.path.exists(module_new):
				warn(_("Module path %s does not exist! Skipping...") % module_new)
				continue
						
			objects_list = {}
			# New builder
			objects_list["builder"] = Gtk.Builder()
			objects_list["builder"].add_from_file(module_new)
			
			# Get main object
			objects_list["main"] = objects_list["builder"].get_object("main")
			objects_list["main"].reparent(self.main)
			objects_list["main"].show_all()
			
			# Add to pages
			self.pages.append_page(objects_list["main"], None)
			#self.pages.next_page()
			#self.pages.get_current_page()
			
			# Add to modules_objects
			self.modules_objects[module] = objects_list
		
	
	def GUI_init(self):
		""" Get objects, show things... """
		
		self.builder = Gtk.Builder()
		self.builder.add_from_file(uipath)
		
		### MAIN WINDOW
		self.main = self.builder.get_object("main_window")
		self.main.connect("destroy", self.please_exit)
		
		self.pages = self.builder.get_object("pages")
		
		self.next_button = self.builder.get_object("next_button")
		self.back_button = self.builder.get_object("back_button")
		self.cancel_button = self.builder.get_object("cancel_button")
		self.next_button.connect("clicked", self.on_next_button_click)
		self.back_button.connect("clicked", self.on_back_button_click)
		self.cancel_button.connect("clicked", self.on_cancel_button_click)
		
		self.build_pages()
		
		self.main.show_all()
	
	def please_exit(self, obj):
		""" Executed when the main window is destroyed. """
		
		self.current_frontend.end()

	def on_cancel_button_click(self, obj):
		""" Executed when the Cancel button is clicked. """
		
		self.main.destroy()

	def on_next_button_click(self, obj):
		""" Executed when the Next button is clicked. """
		
		self.next_module()
		self.pages.next_page()
	
	def on_back_button_click(self, obj):
		""" Executed when the Back button is clicked. """
		
		self.prev_module()
		self.pages.prev_page()

	def ready(self):
		
		# Check if the frontend is glade (or a derivative), otherwise it's useless ;-)
		if "glade" in self.main_settings["frontend"]:
			self.GUI_init()	
	
	def run(self):
		# Check if the frontend is glade (or a derivative), otherwise it's useless ;-)
		
		if "glade" in self.main_settings["frontend"]:
			Gtk.main()
		else:
			verbose("""################################################################################################
Welcome to the next episode of "How wasting CPU cycles and memory"!
This episode is about Services. Oh yes, this service is running on a separate thread but nothing
requires it. The frontend, in fact, is %s and not glade.

Therefore, is advised to disable the "glade" service. The Gtk main loop will not be started and
nothing bad will happen. This message is just for let you know.

If you are a normal user and not a developer, do not worry. You should be happy that you found
this easter egg!
################################################################################################
""" % self.main_settings["frontend"])
		
	def on_close(self):
		""" Triggered when linstaller needs to close shop. """

		# Check if the frontend is glade (or a derivative), otherwise it's useless ;-)
		if "glade" in self.main_settings["frontend"]:
			Gtk.main_quit()
