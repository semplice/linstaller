# -*- coding: utf-8 -*-
# linstaller welcome module frontend - (C) 2011-12 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.frontends.glade as glade
from gi.repository import GObject, Gtk
import t9n.library
_ = t9n.library.translation_init("linstaller")

from linstaller.core.main import warn,info,verbose,root_check		

from keeptalking import TimeZone as timezone

class Frontend(glade.Frontend):
	def ready(self):
		
		if self.is_module_virgin:
			self.set_header("info", _("Timezone selection"), _("Select your timezone here."))
		else:
			self.set_header("ok", _("You can continue!"), _("Press forward to continue."))

		self.notebook = self.objects["builder"].get_object("notebook")

		# Hide things not needed in linstaller ;)
		self.objects["builder"].get_object("live_box").hide()
		self.objects["builder"].get_object("progress_box").hide()
		self.objects["builder"].get_object("dialog-action_area1").hide()
		
		# Remove tabs and notebook border
		self.notebook.set_show_border(False)
		self.notebook.set_show_tabs(False)
		
		self.notebook.set_current_page(2)
		
		##### NOTE: Much of the code below is from the keeptalking project ;) Which as it seems is from the same author :P So we are in fact reusing our own code.
		## We need to make some alias to not change the code too much.
		self.builder = self.objects["builder"]
		self.is_building = False
		global timezone
		timezone = self.moduleclass.tz
		
		## TIMEZONE PAGE
		self.timezone_label = self.builder.get_object("tzonelabel")
		## Create a treeview
		self.timezone_treeview = self.builder.get_object("timezone_treeview")
		self.timezone_model = Gtk.ListStore(str, str)
		
		self.timezone_treeview.set_model(self.timezone_model)
		# Create cell
		if self.is_module_virgin:
			self.timezone_treeview.append_column(Gtk.TreeViewColumn("Timezone", Gtk.CellRendererText(), text=0))
		# Populate
		if self.settings["timezone"]:
			tzone = self.settings["timezone"]
		elif "language" in self.moduleclass.modules_settings and "timezone_auto" in self.moduleclass.modules_settings["language"]:
			tzone = self.moduleclass.modules_settings["language"]["timezone_auto"]
		else:
			tzone = None
		self.populate_timezone_model(tzone=tzone)
		
	def get_selected_timezone(self):
		""" Gets the selected timezone. """
		
		# get selection
		selection = self.timezone_treeview.get_selection()
		if not selection: return None
		model, itr = selection.get_selected()
		
		return self.timezone_model.get_value(itr, 0)


	def populate_timezone_model(self, tzone=None):
		""" Populates self.timezone_model. """

		if self.is_building: return
		self.is_building = True

		# Make the tab label normal.
		self.timezone_label.set_markup(self.timezone_label.get_text().strip("<b>").strip("</b>"))

		print "REBUILDING TIMEZONE MODEL"
		
		default = None
		tzoneitr = None
		
		self.timezone_model.clear()
		
		for item, key in timezone.supported.items():
			for zone in key:
				zone1 = "%s/%s" % (item, zone)
				itr = self.timezone_model.append([zone1, zone])
				if zone1 == timezone.default:
					# save the iter! ;)
					default = itr
				elif zone1 == tzone:
					# save the iter! ;)
					tzoneitr = itr
		self.timezone_model.set_sort_column_id(0, Gtk.SortType.ASCENDING)
		
		# Set default
		if tzoneitr:
			sel = self.timezone_treeview.get_selection()
			sel.select_iter(tzoneitr)
			self.timezone_treeview.scroll_to_cell(sel.get_selected_rows()[1][0])

			# Make the tab label bold.
			self.timezone_label.set_markup("<b>%s</b>" % self.timezone_label.get_text())
		elif default:
			sel = self.timezone_treeview.get_selection()
			sel.select_iter(default)
			self.timezone_treeview.scroll_to_cell(sel.get_selected_rows()[1][0])
			#self.locale_treeview.scroll_to_cell(default)
		
		self.is_building = False

	def on_module_change(self):
		""" Preseed changes """
		
		# Preseed changes
		self.settings["timezone"] = self.get_selected_timezone()
		
		verbose("Selected timezone %s" % self.settings["timezone"])
		
