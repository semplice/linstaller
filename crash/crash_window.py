#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
# linstaller crash window - (C) 2012 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#

from gi.repository import Gtk, GObject
import threading
import subprocess

import locale, t9n.library

import os

locale.setlocale(locale.LC_ALL, '')
locale.bindtextdomain("linstaller", "/usr/share/locale")
_ = t9n.library.translation_init("linstaller")

GObject.threads_init()

UIPATH = "/usr/share/linstaller/crash/ui.glade"
if not UIPATH:
	UIPATH = "./ui.glade"

###################################
class Paste(threading.Thread):
	
	def __init__(self, parent):
		
		self.parent = parent
		
		threading.Thread.__init__(self)
	
	def run(self):
		""" Pastes. """
		
		try:
			res = subprocess.check_output(("/usr/bin/pastebinit", "/var/log/linstaller/linstaller_latest.log"))
		except:
			# Error!
			GObject.idle_add(self.parent.errorwindow.show)
			GObject.idle_add(self.parent.errorwindow.set_markup, "<big><b>Something went wrong while pastebinning your log file.</b></big>")
			GObject.idle_add(self.parent.errorwindow.format_secondary_markup, "It seems you are very unlucky with Semplice.\nWe apologize. Please manually save <b>/var/log/linstaller/linstaller_latest.log</b>\nand point a developer to it.")
			
			return
		
		# Success
		GObject.idle_add(self.parent.dialogwindow.show)
		GObject.idle_add(self.parent.dialogwindow.set_markup, "<big><b>Yay!</b></big>")
		GObject.idle_add(self.parent.dialogwindow.format_secondary_markup, "The log has now been uploaded to: <b>%s</b>\nPlease link it when asking for help." % res.replace("\n",""))
		

class Window:
	def close(self, obj):
		""" Closes the crash window """
		
		Gtk.main_quit()
	
	def do_paste(self, obj):
		""" Does the paste. """
		
		self.crashwindow.set_sensitive(False)
		past = Paste(self)
		past.start()
	
	def hide_dialog(self, obj):
		""" Hides the paste result dialog. """
		
		self.dialogwindow.hide()
		self.crashwindow.set_sensitive(True)
	
	def hide_error(self, obj):
		""" Hides the error dialog. """
		
		self.errorwindow.hide()
		self.crashwindow.set_sensitive(True)
	
	def __init__(self):
		
		self.builder = Gtk.Builder()
		self.builder.set_translation_domain("linstaller")
		self.builder.add_from_file(UIPATH)
		
		self.crashwindow = self.builder.get_object("crash")
		self.crashclose = self.builder.get_object("close")
		self.crashpaste = self.builder.get_object("paste")
		
		self.dialogwindow = self.builder.get_object("dialog")
		self.dialogclose = self.builder.get_object("close2")

		self.errorwindow = self.builder.get_object("error")
		self.errorclose = self.builder.get_object("close3")
		
		self.crashwindow.connect("destroy", self.close)
		self.crashclose.connect("clicked", self.close)
		self.crashpaste.connect("clicked", self.do_paste)
		self.dialogclose.connect("clicked", self.hide_dialog)
		self.errorclose.connect("clicked", self.hide_error)
		
		if os.path.exists("/etc/semplice-live-mode"):
			# Semplice, we can cheer up! :)
			self.crashwindow.set_markup(
				_("<big><b>Drunk people should not write software.</b></big>")
			)
		
		self.crashwindow.show()

win = Window()
Gtk.main()
