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

from gi.repository import Gtk, GObject, Gdk

GObject.threads_init()

# Get linstaller main dir (a bit hacky and ugly)
MAINDIR = os.path.join(os.path.dirname(m.__file__), "..")
MODULESDIR = os.path.join(MAINDIR, "modules/")

uipath = os.path.join(MAINDIR, "services/glade/base_ui.glade")

### HEADER TYPES ###
head_col = {"error":"#F07568","info":"#729fcf","ok":"#73d216","hold":"#f57900"}
head_ico = {"info":Gtk.STOCK_INFO,"error":Gtk.STOCK_DIALOG_ERROR,"ok":Gtk.STOCK_OK,"hold":Gtk.STOCK_EXECUTE}

class Service(linstaller.core.service.Service):
	""" The glade service is the core of the linstaller's glade frontend.
	A GUI is created and maintained by the service, and linstaller will
	trigger modules changes (whose GUIs are preloaded by this service), 
	thus reducing lags and presenting a cleaner environment. """
	
	def on_frontend_change(self):
		""" Focus on the frontend of the current module. """
		
		print("Inizio frontend change")
		
		# Check if the frontend is glade (or a derivative), otherwise it's useless ;-)
		if "glade" in self.main_settings["frontend"]:
			if not self.pages_built:
				# We should wait until the pages are built
				while not self.pages_built:
					time.sleep(0.3)	
			print("Objects...")
			self.current_frontend.objects = self.modules_objects[self.current_module.package.replace("linstaller.modules.","")]
			GObject.idle_add(self.current_frontend.on_objects_ready)
			print("Ready...")
			GObject.idle_add(self.current_frontend.ready)
			
			# Set sensitivity, the frontend is up and running
			self.main.set_sensitive(True)
						
			print("Tutto ok!")
			
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
						
			if not os.path.exists(module_new):
				warn(_("Module path %s does not exist! Skipping...") % module_new)
				continue
						
			objects_list = {"parent":self}
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
		
		self.pages_built = False
		
		self.builder = Gtk.Builder()
		self.builder.add_from_file(uipath)
		
		### MAIN WINDOW
		self.main = self.builder.get_object("main_window")
		self.main.connect("destroy", self.please_exit)
		
		self.box = self.builder.get_object("box")
		
		### HEADER
		self.header_eventbox = Gtk.EventBox()
		
		#self.header = Gtk.HBox()
		#self.header.set_homogeneous(False)
		#self.header_icon = Gtk.Image()
		#self.header_message_container = Gtk.VBox()
		#self.header_message_title = Gtk.Label()
		#self.header_message_subtitle = Gtk.Label()

		#self.header_message_container.pack_start(self.header_message_title, True, True, 0)
		#self.header_message_container.pack_start(self.header_message_subtitle, True, True, 0)
		
		#self.header.pack_start(self.header_icon, True, True, 0)
		#self.header.pack_start(self.header_message_container, True, True, 0)

		self.header_alignment = self.builder.get_object("header_alignment")

		self.header = self.builder.get_object("header")
		self.header_icon = self.builder.get_object("header_icon")
		self.header_message_container = self.builder.get_object("header_message_container")
		self.header_message_title = self.builder.get_object("header_message_title")
		self.header_message_subtitle = self.builder.get_object("header_message_subtitle")
		self.header_alignment.reparent(self.header_eventbox)
		#self.header_eventbox.add(self.header)
		
		self.box.pack_start(self.header_eventbox, True, True, 0)
		self.box.reorder_child(self.header_eventbox, 0)
				
		### PAGES
		
		self.pages = self.builder.get_object("pages")
		
		self.next_button = self.builder.get_object("next_button")
		self.back_button = self.builder.get_object("back_button")
		self.cancel_button = self.builder.get_object("cancel_button")
		self.next_button.connect("clicked", self.on_next_button_click)
		self.back_button.connect("clicked", self.on_back_button_click)
		self.cancel_button.connect("clicked", self.on_cancel_button_click)
		
		
		# Set back button as unsensitive, as we're in the first page
		self.back_button.set_sensitive(False)
		
		self.build_pages()
		self.pages_built = True
		
		self.main.show_all()
		#self.main.set_resizable(True)
		#self.main.fullscreen()
	
	def set_header(self, icon, title, subtitle):
		""" Sets the header with the delcared icon, title and subtitle. """
				
		# Get color
		color_s = head_col[icon]
		color = Gdk.RGBA()
		color.parse(color_s)

		# Get icon
		icon = head_ico[icon]
			
		# Set icon
		self.header_icon.set_from_stock(icon, 6)
		# Set header message and window title
		self.header_message_title.set_markup("<b><big>%s</big></b>" % title)
		self.header_message_subtitle.set_text(subtitle)
		self.main.set_title(title + " - " + _("%s Installer") % self.main_settings["distro"])
		
		# Set color
		self.header_eventbox.override_background_color(0, color)

	def change_entry_status(self, obj, status, tooltip=None):
		""" Changes entry secondary icon for object. """
				
		obj.set_icon_from_stock(Gtk.EntryIconPosition.SECONDARY, head_ico[status])
		obj.set_icon_tooltip_text(Gtk.EntryIconPosition.SECONDARY, tooltip)

	def please_exit(self, obj):
		""" Executed when the main window is destroyed. """
		
		self.current_frontend.end()

	def on_cancel_button_click(self, obj):
		""" Executed when the Cancel button is clicked. """
		
		self.main.destroy()

	def on_next_button_click(self, obj=None):
		""" Executed when the Next button is clicked. """
		
		# Make sure everything is not sensitive until the frontend is up and running
		self.main.set_sensitive(False)
		
		self.next_module()
		self.pages.next_page()
		
		# Ensure the back button is clickable
		self.back_button.set_sensitive(True)
	
	def on_back_button_click(self, obj=None):
		""" Executed when the Back button is clicked. """

		# Make sure everything is not sensitive until the frontend is up and running
		self.main.set_sensitive(False)

		self.prev_module()
		self.pages.prev_page()
		
		# If this is the first page, make unsensitive the button.
		if self.pages.get_current_page() == 0:
			self.back_button.set_sensitive(False)

	def on_caspered(self, status):
		""" Override on_caspered to make sure we handle correctly back/forward jobs when a module has been caspered. """
		
		if status == None:
			# Forward
			self.on_next_button_click() # Trigger on_next_button_click
		elif status == "back":
			# Back
			self.on_back_button_click() # Trigger on_back_button_click

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
