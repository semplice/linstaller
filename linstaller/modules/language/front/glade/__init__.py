# -*- coding: utf-8 -*-
# linstaller welcome module frontend - (C) 2011-12 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.frontends.glade as glade
from gi.repository import GObject, Gtk
import t9n.library
_ = t9n.library.translation_init("linstaller")

import locale as locale_module
import os

from linstaller.core.main import warn,info,verbose,root_check,sexec

from keeptalking import TimeZone as timezone

class Frontend(glade.Frontend):
	
	header_title = _("Language selection")
	header_subtitle = _("Select your language here.")
	header_icon = "preferences-desktop-locale"
	
	def on_objects_ready(self):
		# We use this method to properly see if we need to set header to the keyboard page.
		
		self.notebook = self.objects["builder"].get_object("notebook")
		
		if not self.is_module_virgin and self.notebook.get_current_page() == 1:
			self.header_title = _("Keyboard selection")
			self.header_subtitle = _("Select your keyboard settings here.")
			self.header_icon = "input-keyboard"
	
	def ready(self):

		self.is_building = False
		
		if not self.settings["ask"]:
			# Do not ask; instead using host's language and keyboard layout.
			self.settings["language"] = self.moduleclass.la.default
			self.settings["layout"] = self.moduleclass.ke.default_layout
			self.settings["model"] = self.moduleclass.ke.default_model
			self.settings["variant"] = self.moduleclass.ke.default_variant
			
			self.module_casper()
		
		if self.is_module_virgin:
			self.has_keyboard_header_shown = False
			self.is_rerun = None
		else:
			self.set_header("ok", _("You can continue!"), _("Press forward to continue."))
			self.has_keyboard_header_shown = True
			self.is_rerun = True

		# Hide things not needed in linstaller ;)
		self.objects["builder"].get_object("live_box").hide()
		self.objects["builder"].get_object("progress_box").hide()
		self.objects["builder"].get_object("dialog-action_area1").hide()
		
		# Remove tabs and notebook border
		self.notebook.set_show_border(False)
		self.notebook.set_show_tabs(False)
		
		##### NOTE: Much of the code below is from the keeptalking project ;) Which as it seems is from the same author :P So we are in fact reusing our own code.
		## We need to make some alias to not change the code too much.
		self.builder = self.objects["builder"]
		global locale
		global keyboard
		global tzone_countries
		locale = self.moduleclass.la
		keyboard = self.moduleclass.ke
		tzone_countries = timezone.TimeZone().associate_timezones_to_countries()
		
		self.savespace_dialog = self.builder.get_object("savespace_dialog")
		self.savespace_yes = self.builder.get_object("savespace_yes")
		self.savespace_yes.connect("clicked", self.on_savespace_yes)
		self.savespace_no = self.builder.get_object("savespace_no")
		self.savespace_no.connect("clicked", self.on_savespace_no)
		
		## LOCALE PAGE
		self.locale_frame = self.builder.get_object("locale_frame")
		
		## Create a treeview to attach to locale_frame
		self.locale_treeview = self.builder.get_object("locale_treeview")
		self.locale_treeview.connect("cursor-changed", self.on_locale_changed)
		self.locale_model = Gtk.ListStore(str, str, str)
		
		self.locale_treeview.set_model(self.locale_model)
		# Create cell
		if self.is_module_virgin:
			self.locale_treeview.append_column(Gtk.TreeViewColumn("Locale", Gtk.CellRendererText(), text=1))
			self.locale_treeview.append_column(Gtk.TreeViewColumn("Codepage", Gtk.CellRendererText(), text=2))
		#self.locale_frame.add(self.locale_treeview)
		
		## Get the checkbox.
		self.locale_checkbox = self.builder.get_object("all_locales_checkbutton")

		## Tweaks
		self.tweaks_frame = self.builder.get_object("tweaks_frame")
		self.savespace_checkbox = self.builder.get_object("savespace_checkbox")

		# Populate
		if self.settings["language"]:
			defa = self.settings["language"]
		else:
			defa = locale.default
		if self.is_utf8(defa):
			self.populate_locale_model(all=False, toselect=defa)
			self.locale_checkbox.set_active(False)
		else:
			self.populate_locale_model(all=True, toselect=defa)
			self.locale_checkbox.set_active(True)

		self.locale_checkbox.connect("toggled", self.on_locale_checkbox_toggled)

		if self.settings["savespace"]:
			self.savespace_checkbox.set_active(True)
		self.savespace_checkbox.connect("toggled", self.on_savespace_checkbox_toggled)

		## KEYBOARD PAGE
		self.keyboard_label = self.builder.get_object("keyblabel")
		## Create a treeview to attach to locale_frame
		self.layout_treeview = self.builder.get_object("layout_treeview")
		self.layout_model = Gtk.ListStore(str, str)
		
		self.layout_treeview.set_model(self.layout_model)
		# Create cell
		if self.is_module_virgin:
			self.layout_treeview.append_column(Gtk.TreeViewColumn("Layout", Gtk.CellRendererText(), text=1))
		#self.layout_treeview.append_column(Gtk.TreeViewColumn("Type", Gtk.CellRendererText(), text=1))
				
		# Populate
		if self.settings["layout"]:
			laydef = self.settings["layout"][0]
		else:
			laydef = None
		self.populate_layout_model(lay=laydef)
		
		## Create the variants treeview
		self.variant_treeview = self.builder.get_object("variant_treeview")
		self.layout_treeview.connect("cursor-changed", self.populate_variant_model)
		self.variant_model = Gtk.ListStore(str, str)
		
		self.variant_treeview.set_model(self.variant_model)
		# Create cell
		if self.is_module_virgin:
			self.variant_treeview.append_column(Gtk.TreeViewColumn("Variant", Gtk.CellRendererText(), text=1))
		#self.layout_treeview.append_column(Gtk.TreeViewColumn("Type", Gtk.CellRendererText(), text=1))
				
		# Populate
		self.populate_variant_model(var=self.settings["variant"])
		
		## Create the model combobox
		self.model_combo = self.builder.get_object("model_combo")
		self.model_model = Gtk.ListStore(str, str)
		
		self.model_combo.set_model(self.model_model)
		# Create cell
		if self.is_module_virgin:
			renderer_text = Gtk.CellRendererText()
			self.model_combo.pack_start(renderer_text, True)
			self.model_combo.add_attribute(renderer_text, "text", 1)
        #renderer_text = Gtk.CellRendererText()
        #country_combo.pack_start(renderer_text, True)
        #country_combo.add_attribute(renderer_text, "text", 0)
		
		self.populate_model_combo(toselect=self.settings["model"])
		
		# Clear settings (do not worry, they are reobtained later)
		#self.settings["language"] = False
		#self.settings["layout"] = False
		#self.settings["model"] = False
		#self.settings["variant"] = False
		
		self.is_rerun = None

	def get_selected_layouts(self):
		""" Gets the selected keyboard layouts. """
		
		# get selection
		selection = self.layout_treeview.get_selection()
		if not selection: return []
		model, paths = selection.get_selected_rows()
		
		values = []
		
		for path in paths:
			values.append(self.layout_model.get_value(self.layout_model.get_iter(path), 0))
		
		return values
	
	def get_selected_locale(self):
		""" Gets the selected locale. """
		
		# get selection
		selection = self.locale_treeview.get_selection()
		if not selection: return None
		model, itr = selection.get_selected()
		if not itr: return None
		
		
		return self.locale_model.get_value(itr, 0)

	def get_selected_variant(self):
		""" Gets the selected variant. """
		
		# get selection
		selection = self.variant_treeview.get_selection()
		if not selection: return None
		model, itr = selection.get_selected()
		
		return self.variant_model.get_value(itr, 0)

	def get_selected_model(self):
		""" Gets the selected model. """
		
		# get selection
		itr = self.model_combo.get_active_iter()
		
		return self.model_model.get_value(itr, 0)

	def on_savespace_checkbox_toggled(self, obj):
		""" Triggered when the savespace checkbox has been toggled. """
	
		if obj.get_active():
			# Enabled. Display savespace_dialog
			
			self.settings["savespace"] = True
			
			GObject.idle_add(self.objects["parent"].main.set_sensitive, False)
			GObject.idle_add(self.savespace_dialog.show)
		else:
			# Disabled.
			
			self.settings["savespace"] = False

	def on_savespace_yes(self, obj):
		""" Triggered when the Yes button has been pressed on the savespace dialog. """
		
		self.settings["savespace_purge"] = True

		GObject.idle_add(self.objects["parent"].main.set_sensitive, True)
		GObject.idle_add(self.savespace_dialog.hide)

	def on_savespace_no(self, obj):
		""" Triggered when the No button has been pressed on the savespace dialog. """
		
		self.settings["savespace_purge"] = False

		GObject.idle_add(self.objects["parent"].main.set_sensitive, True)
		GObject.idle_add(self.savespace_dialog.hide)


	def on_locale_checkbox_toggled(self, obj):
		""" Triggered when the locale checkbox has been toggled. """
		
		if obj.get_active():
			# Rebuild locale_model with all=True
			GObject.idle_add(self.populate_locale_model, True)
		else:
			# Rebuild locale_model with all=False
			GObject.idle_add(self.populate_locale_model, False)

	def on_locale_changed(self, obj):
		""" Fired when the locale is changed on the first view. """
		
		try:
			if self.is_building: return
		except:
			return # FIXME
		
		loc = self.get_selected_locale()
		if not loc: return
		
		# We need to set the keyboard layout!
		lay = loc.split(".")[0].split("@")[0].split("_")[1].lower()
		# We will use idle_add otherwise GUI will freeze for a few seconds (it should rebuild all layouts).
		if not self.is_rerun: GObject.idle_add(self.populate_layout_model, lay)
		
		# Set the variant too, if any
		var = loc.split(".")[0].split("@")[0].split("_")[0].lower()
		# We will use idle_add otherwise GUI will freeze for a few seconds (it should rebuild all layouts).
		if not self.is_rerun: GObject.idle_add(self.populate_variant_model, None, var)

		# We need to set the timezone!
		tzone = loc.split(".")[0].split("@")[0].split("_")[1].upper()
		if tzone in tzone_countries:
			# Save for later
			self.settings["timezone_auto"] = tzone_countries[tzone]

	def is_utf8(self, _locale):
		""" Checks if the default locale is utf8. """
		
		if _locale in locale.codepages and locale.codepages[_locale] == "UTF-8":
			return True
		else:
			return False

	def populate_variant_model(self, caller=None, var=None):
		""" Populates self.variants_model. """

		try:
			if self.is_building: return
		except:
			return # FIXME
		self.is_building = True
		
		if caller:
			# If we have a caller, this is called when the user has selected another layout (or changed to the keyboard tab). So:
			# Make the tab label normal.
			self.keyboard_label.set_markup(self.keyboard_label.get_text().strip("<b>").strip("</b>"))

		print "REBUILDING VARIANT MODEL"
		
		default = None
		variantitr = None
		
		self.variant_model.clear()
		
		selected = self.get_selected_layouts()
		if len(selected) != 1:
			self.variant_treeview.set_sensitive(False)
			return
		else:
			self.variant_treeview.set_sensitive(True)
		
		models, layouts = keyboard.supported()
		variants = layouts[selected[0]]["variants"]
		
		for variant in variants:
			for item, key in variant.items():
				itr = self.variant_model.append([item, key])
				if item == keyboard.default_variant:
					# save the iter! ;)
					default = itr
				elif item == var:
					# save the iter! ;)
					variantitr = itr
		self.variant_model.set_sort_column_id(1, Gtk.SortType.ASCENDING)
		reciter = self.variant_model.prepend([None, _("%s") % layouts[selected[0]]["description"]])
		
		# Set default		
		sel = self.variant_treeview.get_selection()
		if variantitr:
			sel.select_iter(variantitr)
		elif default:
			sel.select_iter(default)
		else:
			sel.select_iter(reciter)
		
		self.variant_treeview.scroll_to_cell(sel.get_selected_rows()[1][0])
		
		self.is_building = False
	
	def populate_layout_model(self, lay=None):
		""" Populates self.layout_model. """

		try:
			if self.is_building: return
		except:
			return # FIXME
		self.is_building = True

		# Make the tab label normal.
		self.keyboard_label.set_markup(self.keyboard_label.get_text().strip("<b>").strip("</b>"))

		print "REBUILDING LAYOUT MODEL"
		
		default = None
		layout = None
		
		self.layout_model.clear()
		
		models, layouts = keyboard.supported()
		
		for item, key in layouts.items():
			itr = self.layout_model.append([item, key["description"]])
			if item == keyboard.default_layout:
				# save the iter! ;)
				default = itr
			elif item == lay:
				# save the iter! ;)
				layout = itr
		self.layout_model.set_sort_column_id(1, Gtk.SortType.ASCENDING)
				
		# Set default
		sel = self.layout_treeview.get_selection()
		if layout:
			sel.select_iter(layout)
			self.layout_treeview.scroll_to_cell(sel.get_selected_rows()[1][0])
			
			# Make the tab label bold.
			self.keyboard_label.set_markup("<b>%s</b>" % self.keyboard_label.get_text())
		elif default:
			sel.select_iter(default)
			self.layout_treeview.scroll_to_cell(sel.get_selected_rows()[1][0])
			#self.locale_treeview.scroll_to_cell(default)
		
		sel.set_mode(Gtk.SelectionMode.MULTIPLE)
		
		self.is_building = False
	
	def populate_locale_model(self, all=False, toselect=None):
		""" Populates self.locale_model. """
		
		try:
			if self.is_building: return
		except:
			return # FIXME
		self.is_building = True
				
		print "REBUILDING LOCALE MODEL"
		
		default = None
		toselectitr = None
		
		self.locale_model.clear()
		
		for item, key in locale.human_form(all=all).items():
			if all:
				codepage = locale.codepages[item]
			else:
				codepage = ""
			itr = self.locale_model.append([item, key.split("-")[0], codepage])
			if item == locale.default:
				# save the iter! ;)
				default = itr
			elif item == toselect:
				toselectitr = itr
			self.locale_model.set_sort_column_id(1, Gtk.SortType.ASCENDING)
		
		# Set default
		if toselectitr:
			sel = self.locale_treeview.get_selection()
			sel.select_iter(toselectitr)
			self.locale_treeview.scroll_to_cell(sel.get_selected_rows()[1][0])
		elif default:
			sel = self.locale_treeview.get_selection()
			sel.select_iter(default)
			self.locale_treeview.scroll_to_cell(sel.get_selected_rows()[1][0])
			#self.locale_treeview.scroll_to_cell(default)
		
		self.is_building = False

	def populate_model_combo(self, toselect=None):
		""" Populates self.model_combo """
		
		default = None
		pc105 = None
		toselectitr = None
		
		self.model_model.clear()
		
		models, layouts = keyboard.supported()
		
		for item, key in models.items():
			itr = self.model_model.append([item, key])
			if item == keyboard.default_model:
				# save the iter ;)
				default = itr
			elif item == "pc105":
				# Save, fallback if no default
				pc105 = itr
			elif item == toselect:
				toselectitr = itr
		self.model_model.set_sort_column_id(1, Gtk.SortType.ASCENDING)
		
		if toselectitr:
			self.model_combo.set_active_iter(toselectitr)
		elif default:
			self.model_combo.set_active_iter(default)
		else:
			self.model_combo.set_active_iter(pc105) # Do not check, pc105 MUST be there.
	
	def on_next_button_click(self):
		""" Ensure we show the keyboard page if we should. """

		if self.notebook.get_current_page() == 0:
			# We should
			self.notebook.set_current_page(1)
			
			self.set_header("info", _("Keyboard selection"), _("Select your keyboard settings here."), appicon="input-keyboard")
			if not self.has_keyboard_header_shown:
				self.has_keyboard_header_shown = True
			else:
				self.set_header("ok", _("You can continue!"), _("Press forward to continue."))
			
			return True
	
	def on_module_change(self):
		""" Seeds items when we change module. """
		
		# Preseed changes
		self.settings["language"] = self.get_selected_locale()
		self.settings["layout"] = self.get_selected_layouts()
		self.settings["model"] = self.get_selected_model()
		self.settings["variant"] = self.get_selected_variant()

		# Set language, if we should
		norm = locale_module.normalize(self.settings["language"])
		current = locale_module.getlocale()
		if current == (None, None):
			current = None
		else:
			current = ".".join(current)
		if current != norm:
			try:
				verbose("Setting installer language to %s (normalized: %s, current: %s)" % (self.settings["language"], norm, current))
				
				locale.set(norm, generateonly=True)
				
				locale_module.setlocale(locale_module.LC_ALL, norm)

				os.environ["LANG"] = ".".join(locale_module.getlocale())
			except:
				verbose("Unable to set locale to %s, leaving locale unchanged." % norm)
			
			# Also rebuild pages
			self.objects["parent"].build_pages(replacepage=True)
				
		# Set keyboard layout
		kargs = ["setxkbmap", self.settings["layout"][0]]
		if self.settings["model"]: kargs.append("-model %s" % self.settings["model"])
		if self.settings["variant"]: kargs.append("-variant %s" % self.settings["variant"])

		try:
			# Warning: this will change the keyboard layout *globally*
			sexec(" ".join(kargs), shell=False)
		except:
			verbose("Unable to change the keyboard layout.")
			
			
		verbose("Selected language: %s" % self.settings["language"])
		verbose("Selected keyboard: %s (model %s, variant %s)" % (self.settings["layout"], self.settings["model"], self.settings["variant"]))
		
	
	def on_back_button_click(self):
		""" Ensure we show the locale page if we should. """

		if self.notebook.get_current_page() == 1:
			# We should
			self.set_header("info", _("Language selection"), _("Select your language here."), "preferences-desktop-locale")
			self.notebook.set_current_page(0)
			
			self.set_header("ok", _("You can continue!"), _("Press forward to continue."))
			return True
		
