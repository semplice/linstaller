# -*- coding: utf-8 -*-
# linstaller bricks module frontend - (C) 2013 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.frontends.glade as glade
from gi.repository import GObject, Gtk
import t9n.library
_ = t9n.library.translation_init("linstaller")

from linstaller.core.main import warn,info,verbose,root_check		

from libbricks.features import features, features_order

class Frontend(glade.Frontend):
	def build_feature_objects(self):
		""" Builds GTK+ elements to list the features onto the GUI. """
		
		for feature in features_order:
			dic = features[feature]
			self._objects[feature] = {}
			
			# Generate high level HBox
			self._objects[feature]["container"] = Gtk.HBox()
			
			# Generate icon & text HBox
			self._objects[feature]["icontextcontainer"] = Gtk.HBox()
			self._objects[feature]["icontextcontainer"].set_spacing(5)
			
			# Generate text VBox
			self._objects[feature]["textcontainer"] = Gtk.VBox()
			self._objects[feature]["textcontainer"].set_spacing(3)
			
			# Generate switch
			self._objects[feature]["switch"] = Gtk.Switch()
			self._objects[feature]["switch"].set_halign(Gtk.Align.END)
			self._objects[feature]["switch"].set_valign(Gtk.Align.CENTER)

			self._objects[feature]["switch"].set_active(False)
			self._objects[feature]["switch"].set_active(True)

			# Generate icon
			self._objects[feature]["icon"] = Gtk.Image()
			self._objects[feature]["icon"].set_from_icon_name(
				dic["icon"],
				Gtk.IconSize.DIALOG)
			
			# Generate title
			self._objects[feature]["title"] = Gtk.Label()
			self._objects[feature]["title"].set_alignment(0.0,0.0)
			self._objects[feature]["title"].set_markup(
				"<b>%s</b>" % dic["title"])
			
			# Generate subtext
			if "subtext" in dic:
				self._objects[feature]["subtext"] = Gtk.Label()
				self._objects[feature]["subtext"].set_alignment(0.0,0.0)
				self._objects[feature]["subtext"].set_markup(
					dic["subtext"])
				self._objects[feature]["subtext"].set_line_wrap(True)
			
			# Pack title and subtext
			self._objects[feature]["textcontainer"].pack_start(
				self._objects[feature]["title"],
				False,
				False,
				0)
			if "subtext" in dic:
				self._objects[feature]["textcontainer"].pack_start(
					self._objects[feature]["subtext"],
					False,
					False,
					0)
			
			# Pack icon and textcontainer
			self._objects[feature]["icontextcontainer"].pack_start(
				self._objects[feature]["icon"],
				False,
				False,
				0)
			self._objects[feature]["icontextcontainer"].pack_start(
				self._objects[feature]["textcontainer"],
				True,
				True,
				0)
			
			# Pack icontextcontainer and switch
			self._objects[feature]["container"].pack_start(
				self._objects[feature]["icontextcontainer"],
				True,
				True,
				0)
			self._objects[feature]["container"].pack_start(
				self._objects[feature]["switch"],
				False,
				False,
				0)
			
			
			# Pack container into the main container
			self.container.pack_start(
				self._objects[feature]["container"],
				False,
				False,
				0)
			
	
	def ready(self):
		""" Initialize the GUI. """

		if self.is_module_virgin:
			self.set_header("info", _("Feature selection"), _("Select features."), appicon="preferences-desktop-default-applications")

			self._objects = {}
			
			self.container = self.objects["builder"].get_object("features_container")
			
			self.build_feature_objects()
			
			self.container.show_all()

		else:
			self.set_header("ok", _("You can continue!"), _("Press forward to continue."))
			self.has_keyboard_header_shown = True
			self.is_rerun = True
		
	
	def on_module_change(self):
		""" Seeds items when we change module. """
						
		# Preseed changes
		self.settings["features"] = {}
		for feature, objs in self._objects.items():
			self.settings["features"][feature] = objs["switch"].get_active()
