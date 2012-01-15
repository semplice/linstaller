# -*- coding: utf-8 -*-
# linstaller gtk3 frontend - (C) 2011-12 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a frontend of linstaller, should not be executed as a standalone application.

import os, sys
import getpass

from gi.repository import Gtk, Gdk

import linstaller.core.main as m
from linstaller.core.main import warn,info,verbose

import t9n.library
_ = t9n.library.translation_init("linstaller")

### HEADER TYPES ###
head_col = {"error":"#F07568","info":"#729fcf","ok":"#73d216","hold":"#f57900"}
head_ico = {"info":Gtk.STOCK_INFO,"error":Gtk.STOCK_DIALOG_ERROR,"ok":Gtk.STOCK_OK,"hold":Gtk.STOCK_EXECUTE}

class Frontend:
	class InstallerWindow(Gtk.Window):
		def __init__(self, frontend, header=False):
			""" Initialize the InstallerWindow. """
			
			Gtk.Window.__init__(self, title=header)
			
			self.frontend = frontend
						
			self.main_vbox = Gtk.VBox() # Create the main vbox.
			self.add(self.main_vbox) # Add the main vbox to the window.
			
			self.connect("delete-event",self.on_cancel)
			
			# Create the fixed three buttons at bottom
			self.button_cancel = Gtk.Button(stock=Gtk.STOCK_CANCEL)
			self.button_next = Gtk.Button(stock=Gtk.STOCK_GO_FORWARD)
			self.button_back = Gtk.Button(stock=Gtk.STOCK_GO_BACK)
			
			self.button_cancel.connect("clicked",self.on_cancel)
			self.button_next.connect("clicked",self.on_next)
			self.button_back.connect("clicked",self.on_back)
			
			self.button_box = Gtk.ButtonBox()
			self.button_box.pack_start(self.button_cancel, True, True, 0)
			self.button_box.pack_start(self.button_next, True, True, 0)
			self.button_box.pack_start(self.button_back, True, True, 0)
			
			# Create another vbox, on which put the header.
			self.page_vbox = Gtk.VBox()	
			
			self.main_vbox.pack_start(self.page_vbox, True, True, 0)
			# Add the button_box to the end of the main vbox
			self.main_vbox.pack_end(self.button_box, True, True, 0)
			
			# Create the header.
			self.header_eventbox = Gtk.EventBox()
			self.header = Gtk.HBox()
			self.header_icon = Gtk.Image()
			self.header_message_container = Gtk.VBox()
			self.header_message_title = Gtk.Label()
			self.header_message_subtitle = Gtk.Label()
			
			self.header_message_container.pack_start(self.header_message_title, True, True, 0)
			self.header_message_container.pack_start(self.header_message_subtitle, True, True, 0)
			
			self.header.pack_start(self.header_icon, True, True, 0)
			self.header.pack_start(self.header_message_container, True, True, 0)

			self.header_eventbox.add(self.header)	
			self.page_vbox.pack_start(self.header_eventbox, True, True, 0)
								
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
			self.set_title(title)
			
			# Set color
			self.header_eventbox.override_background_color(0, color)
		
		def text_new(self, string=""):
			""" Adds new text to the page_vbox. """
			
			text = Gtk.Label()
			text.set_markup(string)
			text.show()
			
			self.page_vbox.pack_start(text, True, True, 0)
		
		def entry(self, string, password=False):
			""" Adds a new entry to the page_vbox. """
			
			container = Gtk.HBox()
			label = Gtk.Label()
			text = label.set_markup(string)
			entry = Gtk.Entry()
			if password:
				entry.set_visibility(False)
			
			container.pack_start(label, True, True, 0)
			container.pack_start(entry, True, True, 0)
			container.show_all()
			
			self.page_vbox.pack_start(container, True, True, 0)
			
			return container, entry
		
		def password_entry(self, string):
			""" Adds a new password entry to the page_vbox. """
			
			return self.entry(string, password=True)
		
		def password_entry_with_confirm(self, string):
			""" Adds two password entries to the page_vbox.
			Returns both entry object. """
			
			entry1 = self.password_entry(string)
			entry2 = self.password_entry(string + _(" (again)"))
			
			return entry1, entry2
		
		def switch(self, string, default=False):
			""" Adds a new switch to the page_vbox. """
			
			container = Gtk.HBox()
			label = Gtk.Label()
			text = label.set_markup(string)
			switch = Gtk.Switch()
			if default:
				switch.set_active(True)
			else:
				switch.set_active(False)
			
			container.pack_start(label, True, True, 0)
			container.pack_start(switch, True, True, 0)
			container.show_all()
			
			self.page_vbox.pack_start(container, True, True, 0)
			
			return container, switch
		
		def reset_position(self):
			""" Resets the window position. """
			
			self.set_position(Gtk.WindowPosition.CENTER)

		def on_cancel(self, button, other=None):
			Gtk.main_quit()
			self.frontend.end()
		
		def on_back(self, button):
			Gtk.main_quit()
			return "back"
		
		def on_next(self, button):
			Gtk.main_quit()
			return

	
	def __init__(self, moduleclass):
		
		self.moduleclass = moduleclass
		self.settings = moduleclass.settings
		self.changed = moduleclass.changed
		
		self.window = self.InstallerWindow(self)
		self.window.show_all()
	
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

			
