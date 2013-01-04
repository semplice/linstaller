# -*- coding: utf-8 -*-
# linstaller mirrorselect module frontend - (C) 2011-12 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import time
import threading
import os

import linstaller.frontends.glade as glade
import t9n.library
_ = t9n.library.translation_init("linstaller")

from linstaller.core.main import warn,info,verbose,root_check		

import linstaller.core.libmodules.partdisks.library as lib

from gi.repository import Gtk, Gdk, GObject

class Apply(glade.Progress):
	def __init__(self, parent, quit=True):
		
		self.parent = parent
		self.quit = quit
		
		threading.Thread.__init__(self)

	def progress(self):
		""" Applies the changes to the devices. """
		
		# Disable next button
		self.parent.on_steps_hold()
		
		# Make window unsensitive
		self.parent.idle_add(self.parent.objects["parent"].main.set_sensitive, False)
		
		lst, dct = lib.device_sort(self.parent.changed)
		for key in lst:
			try:
				obj = dct[key]["obj"]
				cng = dct[key]["changes"]
			except:
				verbose("Unable to get a correct object/changes from %s." % key)
				continue # Skip.
					
			verbose("Committing changes in %s" % key)
			
			# If working in a Virtual freespace partition, pyparted will segfault.
			# The following is a workaround, but should be fixed shortly.
			#                FIXME
			#           FIXME     FIXME
			#      FIXME    ______     FIXME
			# FIXME        |      |         FIXME
			# FIXME        |      |               FIXME
			# FIXME FIXME FIXME FIXME FIXME FIXME FIXME
			# ------------------------------------------
			# Figure 1: A FIXME big like an house.
			if "-1" in key:
				continue
			
			# A below try statement should handle non existent nodes, but in somecases the installer may crash.
			# To avoid this, we need to check for the node to be existent. This should not be an issue as the
			# commit list is properly sorted by the device_sort call above.
			# This is an huge FIXME, btw.
			#if not os.path.exists(key):
			#	continue

			# Commit on the disk.
			self.parent.set_header("hold", _("Committing changes to %s...") % key, _("This may take a while."))
			#try:
			#	lib.commit(obj, self.parent.touched)
			#except:
			#	self.parent.set_header("error", _("Failed committing changes to %s..")  % key, _("See /var/log/linstaller/linstaller_latest.log for more details."))
			#
			#	# Restore sensitivity
			#	self.parent.idle_add(self.parent.apply_window.set_sensitive, True)
			#	self.parent.idle_add(self.parent.objects["parent"].main.set_sensitive, True)
			#
			#	return False
			try:
				res = lib.commit(obj, self.parent.touched)
				if res == False:
					self.parent.set_header("error", _("Failed committing changes to %s..")  % key, _("See /var/log/linstaller/linstaller_latest.log for more details."))
				
					if self.parent.is_automatic:
						self.parent.is_automatic = "fail"
						self.parent.on_steps_ok()
										
					# Restore sensitivity
					self.parent.idle_add(self.parent.apply_window.set_sensitive, True)
					self.parent.idle_add(self.parent.objects["parent"].main.set_sensitive, True)
			except:
				continue
				
				# Why we are continuing? Simple: some device which doesn't exist anymore may have still been on the list.
				# We *can't* check for it exists as it prevents the creation of new partitions.
				# So we use this.

							
			# Should format?
			if "format" in cng:
				progress = lib.format_partition_for_real(obj, cng["format"])
				self.parent.set_header("hold", _("Formatting %s...") % key, _("Let's hope everything goes well! :)"))
				status = progress.wait()
				if status != 0:
					# Failed ...
					self.parent.set_header("error", _("Failed formatting %s.") % key, _("See /var/log/linstaller/linstaller_latest.log for more details."))

					if self.parent.is_automatic:
						self.parent.is_automatic = "fail"
						self.parent.on_steps_ok()
					
					# Restore sensitivity
					self.parent.idle_add(self.parent.apply_window.set_sensitive, True)
					self.parent.idle_add(self.parent.objects["parent"].main.set_sensitive, True)

					return False
							
			# Check if it is root or swap
			if "useas" in cng:
				if cng["useas"] == "/":
					# Preseed
					self.parent.settings["root"] = key
					self.parent.settings["root_noformat"] = True
				elif cng["useas"] == "swap":
					# Preseed
					self.parent.settings["swap"] = key
					self.parent.settings["swap_noformat"] = True

		# Preseed *all* changes
		self.parent.settings["changed"] = self.parent.changed
		
		# Add to self.previously_changed
		for item in self.parent.touched:
			if not item in self.parent.previously_changed: self.parent.previously_changed.append(item)

		if not self.parent.is_automatic: self.parent.refresh_manual(complete=False)
		
		# If we're here, ok!	
		self.parent.set_header("ok", _("Changes applied!"), _("Press the Forward button to continue!"))		

		# Enable Next button
		self.parent.on_steps_ok()

		# Restore sensitivity
		self.parent.idle_add(self.parent.apply_window.set_sensitive, True)
		self.parent.idle_add(self.parent.objects["parent"].main.set_sensitive, True)
		
		if self.parent.is_automatic: self.parent.is_automatic = "done"

class Frontend(glade.Frontend):	
	def ready(self):
		""" partdisks is a really complex module which needs a fresh start every time.
		Thus, we can't rely on the virgin state, but we need to destroy and recreate the entire interface.
		
		We do so using service's build_pages() function, and then getting the new objects (to avoid restarting
		the module).
		"""
		
		self.on_steps_hold() # Disable now the next button.
		
		self.objects["main"].destroy() # We need to destroy the old container
				
		# Re-initialize builder, a complex module like this needs a virgin state everytime.
		current = self.objects["parent"].pages.get_current_page()
		self.idle_add(self.objects["parent"].build_pages, "partdisks.front", current, self.can_continue)
		
	def can_continue(self, objects):
		""" Called by service's build page during ready call.
		
		This method retrieves the new objects and also unblocks the ready function and thus permits it to continue. """
		
		# Get new objects
		self.objects = self.objects["parent"].get_module_object("partdisks.front")
		
		self.idle_add(self.real_ready)
		
	def real_ready(self):

		self.onlyusb = False
		self.has_manual_touched = False
		self.is_automatic = None
		
		self.set_header("info", _("Disk partitioning"), _("Manage your drives"))

		# Get the notebook
		self.pages_notebook = self.objects["builder"].get_object("pages_notebook")
		# Ensure we are on the first page
		self.pages_notebook.set_current_page(1)

		# Get pages
		self.main_page = self.objects["builder"].get_object("main_page")
				
		### SOME TIME-CONSUMING THINGS
		if True:
			# Cache distribs
			self.distribs = lib.check_distributions()
			#self.distribs = {}

			self.devices, self.disks = lib.devices, lib.disks

			if self.settings["onlyusb"]:
				self.onlyusb = True # Keep track of onlyusb
				# Only usb, we need to rebuild devices.
				lib.restore_devices(onlyusb=True)
		### END
		
		# Get buttons of the first page
		self.automatic_button = self.objects["builder"].get_object("automatic_button")
		self.automatic_button.connect("clicked", self.on_automatic_button_clicked)
		
		#self.automatic_button.set_sensitive(False) # Set insensitive, automatic not ready for Beta1
		
		self.manual_button = self.objects["builder"].get_object("manual_button")
		self.manual_button.connect("clicked", self.on_manual_button_clicked)

		# Disable next button
		self.on_steps_hold()
		
		# If is_echo, we need to deploy the automatic page... automatically.
		if self.settings["is_echo"]:
			self.on_automatic_button_clicked(obj=None)
	
	def refresh(self):
		""" Refreshes the devices and disks list. """
		
		lib.restore_devices(onlyusb=self.onlyusb)
		self.disks, self.devices = lib.disks, lib.devices
	
	def refresh_manual(self, obj=None, complete=True):
		""" Refreshes the manual partitioning page. """

		self.set_header("info", _("Manual partitioning"), _("Powerful tools for powerful pepole."))

		self.has_swap_warning_showed = False

		self.refresh()
		
		# Also remove flags.
		for name, changes in self.changed.items():
			if complete:
				# Clear.
				changes["changes"].clear()
			else:
				# Remove all but useas
				for key, value in changes["changes"].items():
					if not key == "useas":
						del changes["changes"][key]
		
		# Clear touched
		self.touched = []
		
		self.manual_populate()
	
	def apply(self):
		""" Applies the changes to the devices. """
		
		# Apply!
		if self.is_automatic == True:
			quit = True
		else:
			quit = False
		clss = Apply(self, quit=quit)
		clss.start()
		
		return
	
	def automatic_buttons_creator(self, by, info):
		""" Creates the buttons that are showed on the automatic wizard. """
		
		container = {}
		# Create the button
		container["button"] = Gtk.Button()
		container["hbox"] = Gtk.HBox()
		container["hbox"].set_homogeneous(False)
		container["hbox"].set_spacing(8)
		container["vbox"] = Gtk.VBox()
		container["vbox"].set_homogeneous(False)
		
		# Create the button objects
		if by == "freespace":
			container["title"] = Gtk.Label()
			container["title"].set_markup("<big><b>%s</b></big>" % (_("Install %(distro)s to the %(size)s GB of free space in %(drive)s") % {"distro":self.moduleclass.main_settings["distro"], "size":round(info["freesize"] / 1024, 2), "drive":info["drive"]}))
			
			container["text"] = Gtk.Label()
			container["text"].set_markup(_("This installs the distribution on the free space on the drive."))

			container["text2"] = Gtk.Label()
			if info["swapwarning"] == "exist":
				container["text2"].set_markup(_("<b>Note:</b> an existing virtual memory (swap) partition will be used."))
			elif info["swapwarning"]:
				container["text2"].set_markup(_("<b>Note:</b> due to the few space, it's not possible to create a virtual memory (swap) partition."))
			else:
				container["text2"].set_markup(_("<b>Note:</b> a virtual memory (swap) partition will be created."))
						
			container["icon"] = Gtk.Image()
			container["icon"].set_from_stock("gtk-add", 6)
		elif by == "delete":
			container["title"] = Gtk.Label()
			container["title"].set_markup("<big><b>%s</b></big>" % (_("Replace %(system)s with %(distro)s") % {"system":info["system"], "distro":self.moduleclass.main_settings["distro"]}))
			
			container["text"] = Gtk.Label()
			container["text"].set_markup(_("This replaces %(system)s with %(distro)s. <b>All data on %(system)s will be deleted.</b>") % {"system":info["system"], "distro":self.moduleclass.main_settings["distro"]})

			container["text2"] = Gtk.Label()
			if info["swapwarning"] == "exist":
				container["text2"].set_markup(_("<b>Note:</b> an existing virtual memory (swap) partition will be used."))
			elif info["swapwarning"]:
				container["text2"].set_markup(_("<b>Note:</b> due to the few space, it's not possible to create a virtual memory (swap) partition."))
			else:
				container["text2"].set_markup(_("<b>Note:</b> a virtual memory (swap) partition will be created."))

			container["icon"] = Gtk.Image()
			container["icon"].set_from_stock("gtk-remove", 6)
		elif by == "clear":
			container["title"] = Gtk.Label()
			container["title"].set_markup("<big><b>%s</b></big>" % (_("Use the entire %s disk") % (info["model"])))
			
			container["text"] = Gtk.Label()
			container["text"].set_markup(_("This <b>destroys everything</b> on <b>%(dev)s</b> (%(model)s) and installs there %(distro)s.") % {"dev":info["drive"], "model":info["model"], "distro": self.moduleclass.main_settings["distro"]})

			container["text2"] = Gtk.Label()
			if info["swapwarning"] == "exist":
				container["text2"].set_markup(_("<b>Note:</b> an existing virtual memory (swap) partition will be used."))
			elif info["swapwarning"]:
				container["text2"].set_markup(_("<b>Note:</b> due to the few space, it's not possible to create a virtual memory (swap) partition."))
			else:
				container["text2"].set_markup(_("<b>Note:</b> a virtual memory (swap) partition will be created."))

			container["icon"] = Gtk.Image()
			container["icon"].set_from_stock("gtk-delete", 6)
		elif by == "echo":
			container["title"] = Gtk.Label()
			container["title"].set_markup("<big><b>%s</b></big>" % (_("Install %(distro)s to %(path)s (%(model)s)") % {"distro":self.moduleclass.main_settings["distro"], "path":info["path"], "model":info["model"]}))
			
			container["text"] = Gtk.Label()
			if info["shouldformat"]:
				# Disk is empty, a partition will be created, no data is lost (as there aren't), but is nice to tell the user about that...
				container["text"].set_markup(_("As the Disk is currently empty, this partition will be created."))
			else:
				container["text"].set_markup(_("No data will be deleted."))

			container["text2"] = None

			container["icon"] = Gtk.Image()
			container["icon"].set_from_icon_name("drive-removable-media", 6)
		elif by == "notable":
			container["title"] = Gtk.Label()
			container["title"].set_markup("<big><b>%s</b></big>" % (_("Initialize %s") % (info["model"])))
			
			container["text"] = Gtk.Label()
			container["text"].set_markup(_("This initializes the drive (<b>%s</b>) for usage by creating a partition table.") % info["drive"])
			
			container["text2"] = None
			
			container["icon"] = Gtk.Image()
			container["icon"].set_from_stock("gtk-new", 6)
			
			
		# Add to the box
		container["title"].set_alignment(0.0,0.50)
		container["text"].set_alignment(0.0,0.50)
		if container["text2"]: container["text2"].set_alignment(0.0,0.50)
		
		container["hbox"].pack_start(container["icon"], False, False, True)
		container["hbox"].pack_end(container["vbox"], True, True, True)
		container["vbox"].pack_start(container["title"], True, True, True)
		container["vbox"].pack_start(container["text"], True, True, True)
		if container["text2"]:
			container["vbox"].pack_start(container["text2"], True, True, True)
		
		container["button"].add(container["hbox"])
		container["button"].connect("clicked", self.automatic_calc)
		container["button"].show_all()
		return container

	def automatic_calc(self, obj):
		""" Adds/Removes/etc partitions. """
		
		# Get item
		item = self.automatic_buttons_reverse[obj]
		
		res = self.automatic_res[item]
		
		# Everything has been already done virtually (we <3 pyparted).
		# Just replace the old disk and devices objects with the new ones.
		
		dev = res["device"]
		dis = res["disk"]
				
		# Special case for notable: create the partition table and return.
		if dis == "notable":
			# Go ahead and create the table: is harmless.
			
			if "uefidetect.inst" in self.moduleclass.modules_settings and self.moduleclass.modules_settings["uefidetect.inst"]["uefi"] == True:
				progress = lib.new_table(dev, "gpt")
			else:
				progress = lib.new_table(dev, "mbr")
			status = progress.wait()
			
			self.refresh()
			
			if status != 0:
				# Failed ...
				self.set_header("error", _("Unable to create a new partition table."), _("See /var/log/linstaller/linstaller_latest.log for details."))
			else:
				# Ok! Regenerate solutions...
				self.on_automatic_button_clicked(obj=None)
			
			return

		lib.devices[dev.path.replace("/dev/","")] = dev
		lib.disks[dev.path.replace("/dev/","")] = dis

		
		# Prepare for entering in manual page...
		self.changed = {}
		self.touched = []
		self.previously_changed = []
		self.mountpoints_added = {}
		
		partpath = res["result"]["part"].path
		self.changed[partpath] = {"changes": {}, "obj":res["result"]["part"]}
		self.change_mountpoint(partpath, "/")
		if self.settings["is_echo"]:
			# by_echo() as an handy item into the return dict, which says if we need to format the partition.
			if res["result"]["format"]:
				self.queue_for_format(partpath, res["result"]["format"])
		else:
			# if not is_echo, we do not want to format partition.
			self.queue_for_format(partpath, "ext4")
		self.touched.append(partpath)
		self.previously_changed.append(partpath)
		
		if res["result"]["swap"]:
			swappath = res["result"]["swap"].path
			self.changed[swappath] = {"changes": {}, "obj":res["result"]["swap"]}
			self.change_mountpoint(swappath, "swap")
			self.queue_for_format(swappath, "linux-swap(v1)")
			self.touched.append(swappath)
			self.previously_changed.append(swappath)
		elif res["result"]["swap"] == None:
			# We should pick the right one
			righto = lib.swap_available()
			if righto:
				right = righto.path
				self.changed[right] = {"changes": {}, "obj":righto}
				self.change_mountpoint(right, "swap")
				self.touched.append(right)
				self.previously_changed.append(right)
		
		if res["result"]["efi"]:
			efipath = res["result"]["efi"].path
			self.changed[efipath] = {"changes": {}, "obj":res["result"]["efi"]}
			self.change_mountpoint(efipath, "/boot/efi")
			self.queue_for_format(efipath, "fat32")
			self.touched.append(efipath)
			self.previously_changed.append(efipath)
		
		#self.changed[part.path]["changes"]["useas"]
		
		# Enter on manual page
		self.pages_notebook.set_current_page(3)
		self.manual_ready(clean=False)
		
		# Hide the toolbar
		#self.idle_add(self.manual_toolbar.hide)
		
		# Hide the apply and the refresh buttons
		self.idle_add(self.apply_button.hide)
		self.idle_add(self.refresh_button.hide)
		
		# Set proper header...
		self.set_header("ok", _("Please review your changes."), _("When done this, press the Next button to permanently write them to the disk."))
		
		# Enable next button
		self.on_steps_ok()
		
		# If is_echo, trigger next button.
		if self.settings["is_echo"]:
			self.on_next_button_click()
		

	def automatic_ready(self):
		""" Called when the automatic window is ready. """
		
		# Refresh, some automatic solutions may be in place even after restarting the module
		self.refresh()
		
		self.automatic_buttons = {}
		self.automatic_buttons_reverse = {}
		self.is_automatic = True
		
		if self.settings["is_echo"]:
			self.set_header("info", _("Select the partition where install %s") % self.moduleclass.main_settings["distro"], _("No data will be touched."))
		else:
			self.set_header("info", _("Automatic partitioning"), _("Let the magic manage your drives!"))
		
		# get objects
		self.automatic_container = self.objects["builder"].get_object("automatic_container")
		for child in self.automatic_container.get_children():
			child.destroy()
		self.automatic_container.show()

		### COSMETIC HIDES
		self.automatic_scroller = self.objects["builder"].get_object("automatic_scroller")
		self.automatic_nosolutions = self.objects["builder"].get_object("automatic_nosolutions")
		self.automatic_scroller.show()
		self.automatic_nosolutions.show()
		
		# Create automatic_check_ng object
		if "uefidetect.inst" in self.moduleclass.modules_settings and self.moduleclass.modules_settings["uefidetect.inst"]["uefi"] == True:
			efi = True
		else:
			efi = False
		automatic = lib.automatic_check_ng(distribs=self.distribs, efi=efi, onlyusb=self.onlyusb, is_echo=self.settings["is_echo"])
		
		# Check by freespace
		self.automatic_res, self.automatic_order = automatic.main()
		if not self.automatic_order == []:
			for item in self.automatic_order:
				if item.startswith("freespace"):
					cont = self.automatic_buttons_creator(by="freespace", info={"drive":self.automatic_res[item]["device"].path, "swapwarning":self.automatic_res[item]["swapwarning"], "freesize":self.automatic_res[item]["freesize"]})
					self.automatic_buttons[item] = cont
					self.automatic_buttons_reverse[cont["button"]] = item
				elif item.startswith("delete"):
					cont = self.automatic_buttons_creator(by="delete", info={"drive":self.automatic_res[item]["device"].path, "swapwarning":self.automatic_res[item]["swapwarning"], "system":self.automatic_res[item]["system"]})
					self.automatic_buttons[item] = cont
					self.automatic_buttons_reverse[cont["button"]] = item
				elif item.startswith("clear"):
					cont = self.automatic_buttons_creator(by="clear", info={"drive":self.automatic_res[item]["device"].path, "swapwarning":self.automatic_res[item]["swapwarning"], "model":self.automatic_res[item]["model"]})
					self.automatic_buttons[item] = cont
					self.automatic_buttons_reverse[cont["button"]] = item
				elif item.startswith("echo"):
					cont = self.automatic_buttons_creator(by="echo", info={"drive":self.automatic_res[item]["device"].path, "path":self.automatic_res[item]["result"]["part"].path, "model":self.automatic_res[item]["model"], "shouldformat":self.automatic_res[item]["result"]["format"]})
					self.automatic_buttons[item] = cont
					self.automatic_buttons_reverse[cont["button"]] = item
				elif item.startswith("notable"):
					cont = self.automatic_buttons_creator(by="notable",info={"drive":self.automatic_res[item]["device"].path, "model":self.automatic_res[item]["model"]})
					self.automatic_buttons[item] = cont
					self.automatic_buttons_reverse[cont["button"]] = item
							
			# Ensure we hide nosolutions as we have indeeed some solution
			self.automatic_nosolutions.hide()
		else:
			# Hide the solution scroller
			self.automatic_scroller.hide()
		
		#part, swap = lib.automatic_precheck(by="freespace")
		#if part:
		#	cont = self.automatic_buttons_creator(by="freespace", info={"drive":part.disk.device.path})
		#	self.automatic_buttons[part.path] = cont
		#	self.automatic_buttons_reverse[cont] = (part, swap, "freespace")


		# Check by delete
		#delete, swap = lib.automatic_precheck(by="delete", distribs=self.distribs)
		#if delete:
		#	for part, _name in delete:
		#		if part:
		#			name = _name.split(" ")
		#			for word in _name.split(" "):
		#				if "(" in word or ")" in word:
		#					name.remove(word)
		#			name = " ".join(name)
		#			cont = self.automatic_buttons_creator(by="delete", info={"drive":part.path, "system":name})
		#			self.automatic_buttons[part.path] = cont
		#			self.automatic_buttons_reverse[cont] = (part, swap, "delete")
		
		for button in self.automatic_order:
			obj = self.automatic_buttons[button]
			self.automatic_container.pack_start(obj["button"], True, True, True)
	
	def on_manual_treeview_changed(self, obj):
		""" Called when a treeview on the manual page is changed. """
		
		### UNSELECTION
		treeviews = []
		
		# Obtain the list of the treeviews to unselect...
		for name, container in self.manual_devices.items():
			if container["treeview"] != obj:
				treeviews.append(container["treeview"])
		
		for view in treeviews:
			sel = view.get_selection()
			if sel:
				sel.unselect_all()
		### END UNSELECTION
		
		### Toolbar: we need to make unsensitive buttons 
		# Get selection
		selection = obj.get_selection()
		
		# Get selected item
		if selection: model, _iter = selection.get_selected()
		
		# Get the description
		description = self.treeview_description[obj]
		
		if description == "notable":
			# notable, we need to make unsensitive everything but the "Add partition table button"
			self.add_button.set_sensitive(False)
			self.remove_button.set_sensitive(False)
			self.edit_button.set_sensitive(False)
			self.newtable_button.set_sensitive(True)
			self.delete_button.set_sensitive(False)
		elif description == "empty":
			# empty, we need to make unsensitive everything but the "Add partition button"
			self.add_button.set_sensitive(True)
			self.remove_button.set_sensitive(False)
			self.edit_button.set_sensitive(False)
			self.newtable_button.set_sensitive(False)
			self.delete_button.set_sensitive(False)
		elif description == "full":
			# full, we need to make sensitive everything but the "New table button" and the "Add button"
			self.add_button.set_sensitive(False)
			self.remove_button.set_sensitive(True)
			self.edit_button.set_sensitive(True)
			self.newtable_button.set_sensitive(False)
			self.delete_button.set_sensitive(True)
		elif description == None:
			# None, we need to make sensitive everything but the "New table button"
			self.add_button.set_sensitive(True)
			self.remove_button.set_sensitive(True)
			self.edit_button.set_sensitive(True)
			self.newtable_button.set_sensitive(False)
			self.delete_button.set_sensitive(True)
		## END TOOLBAR
		
		## current_selected:
		if selection:
			self.current_selected = {"value": model.get_value(_iter, 0), "model": model, "iter":_iter}
			if description != "notable":
				part = self.get_partition_from_selected()
				if part.type == 2:
					is_extended = True
				else:
					is_extended = False
			else:
				is_extended = False
			# We need to see if the selected partition is a freespace partition (can add, can't remove). Enable/Disable buttons accordingly
			if not description == "notable":
				if "-" in self.current_selected["value"]:
					self.add_button.set_sensitive(True)
					self.remove_button.set_sensitive(False)
					self.edit_button.set_sensitive(False)
				else:
					self.add_button.set_sensitive(False)
					self.remove_button.set_sensitive(True)
					self.edit_button.set_sensitive(True)
				if is_extended:
					self.remove_button.set_sensitive(False)
					self.edit_button.set_sensitive(False)
	
	def get_device_from_selected(self):
		""" Returns a device object from self.current_selected. """
		
		return self.devices[lib.return_device(self.current_selected["value"]).replace("/dev/","")]

	def get_disk_from_selected(self):
		""" Returns a device object from self.current_selected. """
		
		return self.disks[lib.return_device(self.current_selected["value"]).replace("/dev/","")]
	
	def get_partition_from_selected(self):
		""" Returns a partition object from self.current_selected. """
				
		disk = self.disks[lib.return_device(self.current_selected["value"]).replace("/dev/","")]
		result = disk.getPartitionByPath(self.current_selected["value"])
		if result == None:
			# This may be a freespace partition?
			for part in disk.getFreeSpacePartitions():
				if self.current_selected["value"] == part.path:
					result = part
					break
		
		return result

	def change_button_bg(self, button, color=None):
		""" Changes the background of the specified button. """
		
		# Get color
		color1 = Gdk.RGBA()
		color1.parse(color)
		print color1
		
		self.idle_add(button.override_background_color, Gtk.StateFlags.NORMAL, color1)
	
	def on_newtable_button_clicked(self, obj):
		""" Called when the newtable button has been clicked. """
		
		self.idle_add(self.objects["parent"].main.set_sensitive, False)
		self.idle_add(self.newtable_window.show)

	def on_remove_button_clicked(self, obj):
		""" Called when the remove button has been clicked. """
		
		self.remove_window.set_markup("<big><b>" + _("Do you really want to remove %s?") % self.get_partition_from_selected().path + "</b></big>")
		
		self.idle_add(self.objects["parent"].main.set_sensitive, False)
		self.idle_add(self.remove_window.show)

	def on_delete_button_clicked(self, obj):
		""" Called when the delete button has been clicked. """

		self.delete_window.set_markup("<big><b>" + _("Do you really want to delete all partitions on %s?") % self.get_device_from_selected().path + "</b></big>")

		self.idle_add(self.objects["parent"].main.set_sensitive, False)
		self.idle_add(self.delete_window.show)

	def on_apply_button_clicked(self, obj):
		""" Called when the apply button has been clicked. """

		self.idle_add(self.objects["parent"].main.set_sensitive, False)
		self.idle_add(self.objects["parent"].header_eventbox.set_sensitive, True)
		self.idle_add(self.apply_window.show)

	def on_add_button_clicked(self, obj):
		""" Called when the add button has been clicked. """
		
		self.idle_add(self.objects["parent"].main.set_sensitive, False)
		
		self.prepare_partition_window_for_add()
		self.on_manual_radio_changed()
		
		self.idle_add(self.partition_window.show)
	
	def prepare_partition_window_for_add(self):
		""" Prepares the partition window for add partition action. """
		
		# Get the device
		device = self.get_partition_from_selected()
				
		# Adjust the adjustment
		self.size_adjustment.set_lower(0.01)
		self.size_adjustment.set_upper(round(device.getSize("MB"), 3))

		# Populate the size
		self.size_manual_entry.set_value(round(device.getSize("MB"), 3))
		
		# Ensure the format checkbox is set to True and unsensitive...
		self.format_box.set_active(True)
		self.format_box.set_sensitive(False)

		# Ensure we make sensitive/unsensitive the fs combobox
		self.on_formatbox_change(self.format_box)
		
		# Set ext4 as default...
		self.filesystem_combo.set_active(self.fs_table["ext4"])
		
		# Clear mountpoint
		self.mountpoint_entry.set_text("")
		self.mountpoint_combo.set_active(-1)
		
		self.partition_ok.set_sensitive(True)
		
		# Connect buttons
		if self.partition_ok_id: self.partition_ok.disconnect(self.partition_ok_id)
		if self.partition_cancel_id: self.partition_cancel.disconnect(self.partition_cancel_id)
		self.partition_ok_id = self.partition_ok.connect("clicked", self.on_add_window_button_clicked)
		self.partition_cancel_id = self.partition_cancel.connect("clicked", self.on_add_window_button_clicked)

	def on_edit_button_clicked(self, obj):
		""" Called when the edit button has been clicked. """
		
		self.idle_add(self.objects["parent"].main.set_sensitive, False)
		
		self.prepare_partition_window_for_edit()
		self.on_manual_radio_changed()
		
		self.idle_add(self.partition_window.show)
	
	def prepare_partition_window_for_edit(self):
		""" Prepares the partition window for edit partition action. """
				
		# Get the device
		device = self.get_partition_from_selected()
		
		self.current_length = round(device.getSize("MB"), 3)
		
		# Adjust the adjustment
		self.size_adjustment.set_lower(0.01)
		#self.size_adjustment.set_upper(round(device.getSize("MB"), 3))
		self.size_adjustment.set_upper(lib.maxGrow(device)) #round(device.getMaxAvailableSize("MB"), 3))

		# Populate the size
		self.size_manual_entry.set_value(round(device.getSize("MB"), 3))
		
		# Unset the format checkbox if we should.
		self.format_box.set_sensitive(True) # Ensure is sensitive
		if device.path in self.changed and "format" in self.changed[device.path]["changes"]:
			# To format; set the box to True
			self.format_box.set_active(True)
			# Set too the filesystem, as it is specified in "format".
			self.current_fs = self.changed[device.path]["changes"]["format"]
			self.current_toformat = True
		else:
			# Unset the format box
			self.format_box.set_active(False)
			# Set the filesystem
			if device.fileSystem != None:
				self.current_fs = device.fileSystem.type
			else:
				self.current_fs = None
			self.current_toformat = False
		
		if self.current_fs:
			self.filesystem_combo.set_active(self.fs_table[self.current_fs])
		else:
			self.filesystem_combo.set_active(-1)

		# Clear mountpoint
		self.mountpoint_entry.set_text("")
		self.mountpoint_combo.set_active(-1)

		# Get current mountpoint (if any)...
		if "useas" in self.changed[device.path]["changes"]:
			self.current_mountpoint = self.changed[device.path]["changes"]["useas"]
			if self.current_mountpoint in self.mountp_table:
				self.mountpoint_combo.set_active(self.mountp_table[self.current_mountpoint])
			else:
				self.mountpoint_combo.set_active(-1)
				self.mountpoint_entry.set_text(self.current_mountpoint)
		else:
			self.current_mountpoint = None
		
		# Ensure we make sensitive/unsensitive the fs combobox
		self.on_formatbox_change(self.format_box)
		
		self.partition_ok.set_sensitive(True)
		
		# Connect buttons
		if self.partition_ok_id: self.partition_ok.disconnect(self.partition_ok_id)
		if self.partition_cancel_id: self.partition_cancel.disconnect(self.partition_cancel_id)
		self.partition_ok_id = self.partition_ok.connect("clicked", self.on_edit_window_button_clicked)
		self.partition_cancel_id = self.partition_cancel.connect("clicked", self.on_edit_window_button_clicked)

	def queue_for_format(self, path, fs):
		""" Queues for format. """
		
		self.changed[path]["changes"]["format"] = fs
	
	def change_mountpoint(self, path, mpoint):
		""" Changes the mountpoint in self.changed. """
		
		self.changed[path]["changes"]["useas"] = mpoint
		
		# Add to mountpoints_added if there is a mpoint
		if mpoint:
			self.mountpoints_added[mpoint] = path
		
	def get_mountpoint(self):
		""" Gets the mountpoint from the ComboboxTextEntry which asks for mountpoint. """
		
		# Get active
		active = self.mountpoint_combo.get_active()
		if active == -1:
			# See if there is text...
			txt = self.mountpoint_entry.get_text()
			if txt:
				result = txt
			else:
				result = None
		else:
			# The user has select one on our list. Get it.
			result = self.mountp_table_inverse[active]
		
		return result
	
	def on_mountpoint_change(self, obj):
		""" Called when a mountpoint on the partition window has been changed. """
		
		# Get mpoint
		mpoint = self.get_mountpoint()
		
		if mpoint in self.mountpoints_added and self.mountpoints_added[mpoint] != self.get_partition_from_selected().path:
			# No way! :)
			self.change_entry_status(self.mountpoint_entry, "error", _("Mountpoint already used!"))
			self.partition_ok.set_sensitive(False)
		else:
			# Not used! yay!
			self.change_entry_status(self.mountpoint_entry, "ok")
			self.partition_ok.set_sensitive(True)
	
	def on_add_window_button_clicked(self, obj):
		""" Called when a button on the add partition window has been clicked. """
		
		self.idle_add(self.partition_window.hide)
		
		if obj == self.partition_ok:
			# Yes.
			# Create the new partition

			self.set_header("hold", _("Creating the partition..."), _("Please wait."))
			
			part = self.get_partition_from_selected()
			targetfs = self.fs_table_inverse[self.filesystem_combo.get_active()]
			
			try:
				res = lib.add_partition(part.disk, start=part.geometry.start, size=lib.MbToSector(float(self.size_adjustment.get_value())), type=lib.p.PARTITION_NORMAL, filesystem=targetfs)
			except:
				# Failed! Ouch!
				self.set_header("error", _("Unable to add partition."), _("You shouldn't get here."))
				return
			
			# Add the new partition to changed
			self.changed[res.path] = {"obj":res, "changes":{}}
			
			self.queue_for_format(res.path, targetfs)
			self.change_mountpoint(res.path, self.get_mountpoint())
			
			self.set_header("hold", _("You have some unsaved changes!"), _("Use the Apply button to save them."))
			self.change_button_bg(self.apply_button, self.objects["parent"].return_color("ok"))
			
			if not res.path in self.touched: self.touched.append(res.path)
			
			self.manual_populate()
		
		# Restore sensitivity
		self.objects["parent"].main.set_sensitive(True)

	def on_edit_window_button_clicked(self, obj):
		""" Called when a button on the edit partition window has been clicked. """
		
		self.idle_add(self.partition_window.hide)
		
		if obj == self.partition_ok:
			# Yes.
			# Edit the partition
			
			part = self.get_partition_from_selected()
			
			# What we should do?
			# Check if the size has been changed...
			newsize = self.size_manual_entry.get_value()
			if newsize != self.current_length:
				# Yes! We need to resize!
				res = lib.resize_partition(part, lib.MbToSector(float(newsize)))
				if not res:
					# Failed! Ouch!
					self.set_header("error", _("Failed to resize partition."), _("Please double-check the inserted values."))
					
					self.objects["parent"].main.set_sensitive(True)
					return
			
			# We should format?
			newtoformat = self.format_box.get_active()
			if newtoformat != self.current_toformat:
				if not newtoformat:
					if part.path in self.changed and "format" in self.changed[part.path]["changes"]:
						del self.changed[part.path]["changes"]["format"]
			
			if newtoformat:	
				newfs = self.fs_table_inverse[self.filesystem_combo.get_active()]
				lib.format_partition(part, newfs) # Ensure we change part.fileSystem
				self.queue_for_format(part.path, newfs)
							
			# We should change mountpoint?
			newmountpoint = self.get_mountpoint()
			if newmountpoint != self.current_mountpoint:
				# Yes! We need to change mountpoint!
				self.change_mountpoint(part.path, newmountpoint)
				# Remove the old mountpoint from the list
				if self.current_mountpoint:
					del self.mountpoints_added[self.current_mountpoint]

			self.set_header("hold", _("You have some unsaved changes!"), _("Use the Apply button to save them."))

			if part.path in self.previously_changed: self.previously_changed.remove(part.path)
			if not part.path in self.touched: self.touched.append(part.path)
						
			self.manual_populate()
		
		# Restore sensitivity
		self.objects["parent"].main.set_sensitive(True)
			
	def on_formatbox_change(self, obj):
		""" Called when formatbox has been toggled. """
		
		if obj.get_active():
			# Make the combobox sensitive
			self.filesystem_combo.set_sensitive(True)
		else:
			# Make it unsensitive
			self.filesystem_combo.set_sensitive(False)
			# ...and restore the filesystem
			try:
				if self.current_fs:
					self.filesystem_combo.set_active(self.fs_table[self.current_fs])
				else:
					self.filesystem_combo.set_active(-1)
			except:
				self.filesystem_combo.set_active(-1)
		
	def on_newtable_window_button_clicked(self, obj):
		""" Called when a button on the newtable window has been clicked. """
		
		self.idle_add(self.newtable_window.hide)
		
		dev = self.get_device_from_selected()
		
		if obj == self.newtable_yes:
			# Yes.
			# Create the new table
			if "uefidetect.inst" in self.moduleclass.modules_settings and self.moduleclass.modules_settings["uefidetect.inst"]["uefi"] == True:
				progress = lib.new_table(dev, "gpt")
			else:
				progress = lib.new_table(dev, "mbr")
			status = progress.wait()
			if status != 0:
				# Failed ...
				self.set_header("error", _("Unable to create a new partition table."), _("See /var/log/linstaller/linstaller_latest.log for details."))
			else:
				# Ok!
				self.set_header("ok", _("New table created successfully!"), _("The new table has been created."))
			
			self.refresh_manual()
		
		# Restore sensitivity
		self.objects["parent"].main.set_sensitive(True)

	def on_remove_window_button_clicked(self, obj):
		""" Called when a button on the remove window has been clicked. """
		
		self.idle_add(self.remove_window.hide)
		
		part = self.get_partition_from_selected()
		
		if obj == self.remove_yes:
			# Yes.
			# Remove the partition
			res = lib.delete_partition(part)
			if not res:
				# Failed!
				self.set_header("error", _("Unable to remove the partition."), _("Why did it happen?!"))
			else:
				# Ok!
				self.set_header("hold", _("You have some unsaved changes!"), _("Use the Apply button to save them."))
			
			if not self.get_device_from_selected().path in self.touched: self.touched.append(self.get_device_from_selected().path)
			
			self.manual_populate()
		
		# Restore sensitivity
		self.objects["parent"].main.set_sensitive(True)

	def on_delete_window_button_clicked(self, obj):
		""" Called when a button on the delete window has been clicked. """
		
		self.idle_add(self.delete_window.hide)
		
		dev = self.get_disk_from_selected()
		
		if obj == self.delete_yes:
			# Yes.
			# Clear the device
			res = lib.delete_all(dev)
			if not res:
				# Failed!
				self.set_header("error", _("Unable to delete all partitions."), _("Why did it happen?!"))
			else:
				# Ok!
				self.set_header("hold", _("You have some unsaved changes!"), _("Use the Apply button to save them."))

			if not self.get_device_from_selected().path in self.touched: self.touched.append(self.get_device_from_selected().path)

			self.manual_populate()
		
		# Restore sensitivity
		self.objects["parent"].main.set_sensitive(True)

	def manual_apply(self):
		""" Workaround to get the apply window hidden while doing things. """

		dev = self.get_disk_from_selected()
			
		res = self.apply()


	def on_apply_window_button_clicked(self, obj):
		""" Called when a button on the apply window has been clicked. """
				
		if obj == self.apply_yes:
			# Yes.
			# APPLY! :)
			self.apply_window.set_sensitive(False)
			self.idle_add(self.apply)
		else:
			# Restore sensitivity
			self.objects["parent"].main.set_sensitive(True)
		
		#self.apply_window.set_sensitive(True)
		self.idle_add(self.apply_window.hide)
			
	def manual_frame_creator(self, device, disk):
		""" Creates frames etc for the objects passed. """
		
		if not device.path in self.changed: self.changed[device.path] = {"obj":device, "changes":{}}
		
		container = {}
		container["frame_label"] = Gtk.Label()
		container["frame_label"].set_markup("<b>%s - %s (%s GB)</b>" % (device.path, device.model, round(device.getSize(unit="GB"), 2)))
		container["frame"] = Gtk.Frame()
		container["frame"].set_label_widget(container["frame_label"])
		## Create the TreeView 
		# ListStore: /dev/part - system/label - filesystem - format? - size

		#if disk != "notable": partitions = list(disk.partitions) + disk.getFreeSpacePartitions()
		if disk != "notable": partitions = lib.disk_partitions(disk)

		if disk != "notable" and len(partitions) > 0:	
			container["model"] = Gtk.ListStore(str, str, str, str, bool, str, str)
		else:
			container["model"] = Gtk.ListStore(str, str)
		#container["model"].set_sort_column_id(0, Gtk.SortType.ASCENDING)
		container["treeview"] = Gtk.TreeView(container["model"])
		container["treeview"].connect("cursor-changed", self.on_manual_treeview_changed)

		# First column
		#cell = gtk.CellRendererText()
		#col = gtk.TreeViewColumn("text")
		#col.pack_start(cell, True)
		#cell.set_property("background-set", True)
		#col.set_attributes(cell, text=0, background=2)
		#self.automatic_actions.append_column(col)

		## Add columns...
		if disk == "notable":
			container["treeview"].append_column(Gtk.TreeViewColumn(_("Informations"), Gtk.CellRendererText(), text=1, cell_background=2))
			
			# Need to add an item to say: this drive hasn't got a proper table yet!
			container["notable"] = container["model"].append((device.path, _("No partition table yet!")))
			container["description"] = "notable" # description.
		elif len(partitions) > 0:
			container["treeview"].append_column(Gtk.TreeViewColumn(_("Partition"), Gtk.CellRendererText(), text=0, cell_background=6))
			container["treeview"].append_column(Gtk.TreeViewColumn(_("Type"), Gtk.CellRendererText(), text=1, cell_background=6))
			container["treeview"].append_column(Gtk.TreeViewColumn(_("Filesystem"), Gtk.CellRendererText(), text=2, cell_background=6))
			container["treeview"].append_column(Gtk.TreeViewColumn(_("Mountpoint"), Gtk.CellRendererText(), text=3, cell_background=6))
			container["treeview"].append_column(Gtk.TreeViewColumn(_("Format?"), Gtk.CellRendererToggle(), active=4, cell_background=6))
			container["treeview"].append_column(Gtk.TreeViewColumn(_("Size"), Gtk.CellRendererText(), text=5, cell_background=6))

			for part in partitions:
				if not part.path in self.changed: self.changed[part.path] = {"obj":part, "changes":{}}

				name = []
				if part.path in self.distribs:
					name.append(self.distribs[part.path])
				if part.name:
					name.append(part.name)
				elif not part.path in self.distribs:
					name.append("Normal partition")

				if int(part.getSize("GB")) > 0:
					# We can use GigaBytes to represent partition size.
					_size = round(part.getSize("GB"), 2)
					_unit = "GB"
				elif int(part.getSize("MB")) > 0:
					# Partition is too small to be represented with gigabytes. Use megabytes instead.
					_size = round(part.getSize("MB"), 2)
					_unit = "MB"
				else:
					## Last try.. using kilobytes
					#_size = round(part.getSize("kB"), 2)
					#_unit = "kB"
					
					# Partition is too small and can be confusing. Simply do not show it.
					continue

				if part.path in self.changed and "format" in self.changed[part.path]["changes"]:
					# We need to format the partition, so don't use the one that parted returns to us
					_fs = self.changed[part.path]["changes"]["format"]
					_to_format = True
				else:
					# See what parted tells us
					if part.fileSystem == None and not part.number == -1 and not part.type == 2:
						# If filesystem == None, skip.
						_fs = _("not formatted")
					elif part.number == -1:
						_fs = _("free space")
					elif part.type == 2:
						# Extended partition
						_fs = _("extended")
					else:
						_fs = part.fileSystem.type
					
					_to_format = False
				
				if part.path in self.changed and "useas" in self.changed[part.path]["changes"]:
					# Set mountpoint.
					_mpoint = self.changed[part.path]["changes"]["useas"]
					if _mpoint == None:
						_mpoint = ""
				else:
					_mpoint = ""

				if part.path in self.previously_changed and (self.changed[part.path]["changes"] == {} or (len(self.changed[part.path]["changes"]) == 1 and "useas" in self.changed[part.path]["changes"]) or self.is_automatic):
					# This was changed previously, "ok" color.
					_bg = self.objects["parent"].return_color("ok")
				elif self.changed[part.path]["changes"] != {}:
					print "%s was changed" % part.path
					# This was changed now, "hold" color.
					_bg = self.objects["parent"].return_color("hold")
					
					# Also, there are some changes, so disable the next button.
					if not self.is_automatic: self.on_steps_hold()
				else:
					# No change
					_bg = None
				
				
				container[part.path] = container["model"].append((part.path, "/".join(name), _fs, _mpoint, _to_format, "%s %s" % (_size, _unit), _bg))
		elif len(partitions) == 0:
			container["treeview"].append_column(Gtk.TreeViewColumn(_("Informations"), Gtk.CellRendererText(), text=1, cell_background=2))
			
			# Need to add an item to say: this drive is empty!
			container["notable"] = container["model"].append((device.path, _("Disk empty!")))
			container["description"] = "empty" # description.

		container["frame"].add(container["treeview"])

		return container
	
	def manual_populate(self):
		""" Populates the harddisk_container with content. """

		for child in self.harddisk_container.get_children():
			self.idle_add(child.destroy)

		for name, obj in self.devices.items():
			self.manual_devices[obj.path] = self.manual_frame_creator(obj, self.disks[name])
			if "description" in self.manual_devices[obj.path]:
				self.treeview_description[self.manual_devices[obj.path]["treeview"]] = self.manual_devices[obj.path]["description"]
			else:
				self.treeview_description[self.manual_devices[obj.path]["treeview"]] = None
			self.idle_add(self.harddisk_container.pack_start, self.manual_devices[obj.path]["frame"], True, True, True)
		
		self.idle_add(self.harddisk_container.show_all)

		# Make everything unsensitive...
		self.idle_add(self.add_button.set_sensitive, False)
		self.idle_add(self.remove_button.set_sensitive, False)
		self.idle_add(self.edit_button.set_sensitive, False)
		self.idle_add(self.newtable_button.set_sensitive, False)
		self.idle_add(self.delete_button.set_sensitive, False)
	
	def on_manual_radio_changed(self, obj=None):
		""" Called when the radios on the add/edit partition window are changed. """
		
		if self.size_manual_radio.get_active():
			# The entry is selected. Make unsensitive the scale.
			self.size_manual_entry.set_sensitive(True)
			self.size_scale_scale.set_sensitive(False)
		else:
			# The scale is selected. Make unsensitive the entry.
			self.size_manual_entry.set_sensitive(False)
			self.size_scale_scale.set_sensitive(True)
	
	def manual_ready(self, clean=True):
		""" Called when the manual window is ready. """
		
		self.has_swap_warning_showed = False
		
		self.current_selected = None
		
		if clean:			
			self.changed = {}
			self.touched = []
			self.previously_changed = []
			self.is_automatic = False

			self.mountpoints_added = {}
			## FIXME: The following is a workaround to get the root overriden via
			## a seed. This is extremly useful for those who need to install the
			## distribution to a partition not recognized by the installer, such
			## as a crypted partition.
			##
			## USAGE:
			##  - "root" seed to the path of the device
			##  - "root_override" seed to True
			##
			## This *may* break some partdisks functions, so we are currently
			## using the "root_override" seed to see if this is something wanted
			## by the user or not.
			## Usage of the CLI frontend of partdisks should not be affected.
			##
			## NOTE: The target root SHOULD BE ALREADY FORMATTED, and no other
			## root should be selected. Also, doing a refresh *may* break out
			## things, so the module may need a restart.
			if self.settings["root_override"] and self.settings["root"]:
				self.mountpoints_added["/"] = self.settings["root"]

			self.refresh()
					
		self.manual_devices = {}
		self.treeview_description = {}

		# Presed changed if this is not the first time...
		if not self.is_module_virgin:
			if not self.is_automatic == True and ("changed" in self.settings and self.settings["changed"]):
				self.changed = self.settings["changed"]
				# Also every changed partition should be on previously_changed...
				for part, value in self.changed.items():
					if value["changes"] != {}:
						self.previously_changed.append(part)
						if "useas" in value["changes"]:
							self.mountpoints_added[value["changes"]["useas"]] = part

		self.partition_ok_id = None
		self.partition_cancel_id = None

		if self.is_module_virgin or not ("changed" in self.settings and self.settings["changed"]):
			self.set_header("info", _("Manual partitioning"), _("Powerful tools for powerful pepole."))
		else:
			self.set_header("ok", _("You can continue!"), _("Press the Apply button and then Forward to continue."))
		
		# Get windows
		self.partition_window = self.objects["builder"].get_object("partition_window")
		self.newtable_window = self.objects["builder"].get_object("newtable_window")
		self.remove_window = self.objects["builder"].get_object("remove_window")
		self.delete_window = self.objects["builder"].get_object("delete_window")
		self.apply_window = self.objects["builder"].get_object("apply_window")
		
		## Partition window:
		self.size_manual_radio = self.objects["builder"].get_object("size_manual_radio")
		self.size_adjustment = self.objects["builder"].get_object("size_adjustment")
		self.size_manual_entry = self.objects["builder"].get_object("size_manual_entry")
		self.size_scale_radio = self.objects["builder"].get_object("size_scale_radio")
		self.size_scale_scale = self.objects["builder"].get_object("size_scale_scale")
		self.format_box = self.objects["builder"].get_object("format_box")
		self.filesystem_combo = self.objects["builder"].get_object("filesystem_combo")
		self.mountpoint_combo = self.objects["builder"].get_object("mountpoint_combo")
		self.mountpoint_entry = self.objects["builder"].get_object("mountpoint_entry")
		self.partition_cancel = self.objects["builder"].get_object("partition_cancel")
		self.partition_ok = self.objects["builder"].get_object("partition_ok")
		
		# Connect the radios...
		self.size_manual_radio.connect("toggled", self.on_manual_radio_changed)
		self.size_scale_radio.connect("toggled", self.on_manual_radio_changed)
		
		# Connect format box
		self.format_box.connect("toggled", self.on_formatbox_change)
		
		# Connect mountpoint entry and combobox...
		self.mountpoint_combo.connect("changed", self.on_mountpoint_change)
		self.mountpoint_entry.connect("changed", self.on_mountpoint_change)
		
		# An empty mountpoint is fine...
		self.change_entry_status(self.mountpoint_entry, "ok")
		
		# Build a list of filesystem to append to self.filesystem_combo
		self.fs_table = {None:-1}
		self.fs_table_inverse = {-1:None}
		
		list_store = Gtk.ListStore(GObject.TYPE_STRING)
		fs_num = -1
		for item, cmd in lib.get_supported_filesystems().items():
			fs_num += 1
			self.fs_table[item] = fs_num
			self.fs_table_inverse[fs_num] = item
			list_store.append((item,))
		self.filesystem_combo.set_model(list_store)
		if not self.has_manual_touched:
			cell = Gtk.CellRendererText()
			self.filesystem_combo.pack_start(cell, True)
			self.filesystem_combo.add_attribute(cell, "text", 0)
		
		# Build a list of mountpoints to append to self.mountpoint_combo
		self.mountp_table = {}
		self.mountp_table_inverse = {}
		
		point_store = Gtk.ListStore(GObject.TYPE_STRING, GObject.TYPE_STRING)
		mp_num = -1
		for item, desc in lib.sample_mountpoints.items():
			if item == "/boot/efi" and not ("uefidetect.inst" in self.moduleclass.modules_settings and self.moduleclass.modules_settings["uefidetect.inst"]["uefi"] == True):
				continue
			mp_num += 1
			point_store.append((item, desc))
			self.mountp_table[item] = mp_num
			self.mountp_table_inverse[mp_num] = item
		self.mountpoint_combo.set_model(point_store)
		#cell = Gtk.CellRendererText()
		#self.mountpoint_combo.pack_start(cell, True)
		#self.mountpoint_combo.add_attribute(cell, "text", 1)

				
		## Newtable window:
		self.newtable_no = self.objects["builder"].get_object("newtable_no")
		self.newtable_yes = self.objects["builder"].get_object("newtable_yes")
		self.newtable_no.connect("clicked", self.on_newtable_window_button_clicked)
		self.newtable_yes.connect("clicked", self.on_newtable_window_button_clicked)

		## Remove window:
		self.remove_no = self.objects["builder"].get_object("remove_no")
		self.remove_yes = self.objects["builder"].get_object("remove_yes")
		self.remove_no.connect("clicked", self.on_remove_window_button_clicked)
		self.remove_yes.connect("clicked", self.on_remove_window_button_clicked)

		## Delete window:
		self.delete_no = self.objects["builder"].get_object("delete_no")
		self.delete_yes = self.objects["builder"].get_object("delete_yes")
		self.delete_no.connect("clicked", self.on_delete_window_button_clicked)
		self.delete_yes.connect("clicked", self.on_delete_window_button_clicked)

		## Apply window:
		self.apply_no = self.objects["builder"].get_object("apply_no")
		self.apply_yes = self.objects["builder"].get_object("apply_yes")
		self.apply_no.connect("clicked", self.on_apply_window_button_clicked)
		self.apply_yes.connect("clicked", self.on_apply_window_button_clicked)

		# Get toolbar buttons
		self.manual_toolbar = self.objects["builder"].get_object("manual_toolbar")
		self.add_button = self.objects["builder"].get_object("add_button")
		self.remove_button = self.objects["builder"].get_object("remove_button")
		self.edit_button = self.objects["builder"].get_object("edit_button")
		self.newtable_button = self.objects["builder"].get_object("newtable_button")
		self.delete_button = self.objects["builder"].get_object("delete_button")
		self.refresh_button = self.objects["builder"].get_object("refresh_button")
		self.apply_button = self.objects["builder"].get_object("apply_button")

		# Connect them
		self.add_button.connect("clicked", self.on_add_button_clicked)
		self.edit_button.connect("clicked", self.on_edit_button_clicked)
		self.newtable_button.connect("clicked", self.on_newtable_button_clicked)
		self.remove_button.connect("clicked", self.on_remove_button_clicked)
		self.delete_button.connect("clicked", self.on_delete_button_clicked)
		self.refresh_button.connect("clicked", self.refresh_manual)
		self.apply_button.connect("clicked", self.on_apply_button_clicked)
		
		# Change text of newtable_button
		if "uefidetect.inst" in self.moduleclass.modules_settings and self.moduleclass.modules_settings["uefidetect.inst"]["uefi"] == True:
			self.newtable_button.set_label(_("Add GPT partition table"))
		else:
			self.newtable_button.set_label(_("Add MBR partition table"))

		# Get the harddisk_container and populate it
		self.harddisk_container = self.objects["builder"].get_object("harddisk_container")
		self.manual_populate()
		
		self.has_manual_touched = True

	def on_automatic_button_clicked(self, obj):
		""" Called when automatic_button is clicked. """

		# Ensure we can go back...
		self.idle_add(self.objects["parent"].back_button.set_sensitive, True)
		
		# Switch to page 2
		self.pages_notebook.set_current_page(2)
		
		self.automatic_ready()
	
	def on_manual_button_clicked(self, obj):
		""" Called when manual_button is clicked. """

		# Ensure we can go back...
		self.idle_add(self.objects["parent"].back_button.set_sensitive, True)
		
		# Switch to page 3
		self.pages_notebook.set_current_page(3)
		
		self.manual_ready()

	def on_back_button_click(self):
		""" Override on_back_button_click. """
		
		self.set_header("info", _("Disk partitioning"), _("Manage your drives"))
		
		# If is_echo, we need exclusively to go to the module before...
		if self.settings["is_echo"]:
			return None
		
		# Return always to page 1, if we aren't already there
		current = self.pages_notebook.get_current_page()
		if not current == 1:
			
			# Restart
			self.module_restart()
			
			# Hide the automatic_container if we are in automatic:
			#if current == 1:
			#	self.automatic_container.hide()
			#else:
			#	# We are on manual, destroy all items in the harddisk_container:
			#	for child in self.harddisk_container.get_children():
			#		self.idle_add(child.destroy)

			
			# Disable next button
			#self.on_steps_hold()
			
			#self.pages_notebook.set_current_page(0)
			return True
	
	def on_next_button_click(self):
		""" Override on_next_button_click. """
		
		if self.pages_notebook.get_current_page() == 3:
			# We are in manual, and we need to check if the / partition is selected...
			
			if self.is_automatic == "fail":
				self.is_automatic = True
				return True
			
			if not "/" in self.mountpoints_added:
				# Error!
				self.set_header("error", _("You can't continue!"), _("You need to specify the root (/) partition."))
				return True
			else:
				# Set root.
				self.settings["root"] = self.mountpoints_added["/"]
			
			# If in UEFI mode, ensure /boot/efi is selected
			if "uefidetect.inst" in self.moduleclass.modules_settings and self.moduleclass.modules_settings["uefidetect.inst"]["uefi"] == True and not lib.return_partition(self.mountpoints_added["/"]).disk.type == "msdos":
				if not "/boot/efi" in self.mountpoints_added:
					# Error!
					self.set_header("error", _("You can't continue!"), _("You need to specify the EFI System Partition (/boot/efi)."))
					return True
			
			# Check for swap too...
			if not "swap" in self.mountpoints_added:
				# Warning!
				if not self.has_swap_warning_showed and not self.is_automatic:
					# Show it
					self.set_header("hold", _("Are you sure?"), _("It seems you haven't selected a swap partition.\nSelect one now, or press Forward to continue without one."))
					self.has_swap_warning_showed = True
					return True
				else:
					self.has_swap_warning_showed = False
					self.settings["swap"] = None
					warn(_("No swap selected."))
			else:
				self.settings["swap"] = self.mountpoints_added["swap"]
			
			# if self.is_automatic, apply now changes.
			if self.settings["is_echo"] and self.is_automatic == True:
				# Apply and go ahead
				self.idle_add(self.apply)
				
				return True
			elif self.is_automatic == True:
				self.on_apply_button_clicked(obj="automatic")
				#clss = Apply(self, quit=True)
				#clss.start()
				
				return True
			
			# Seed changed
			self.refresh_manual(complete=False)
			self.settings["changed"] = self.changed
		
