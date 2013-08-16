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

from linstaller.core.main import warn,info,verbose,root_check,CmdError

import linstaller.core.libmodules.partdisks.library as lib
import linstaller.core.libmodules.partdisks.lvm as lvm
import linstaller.core.libmodules.partdisks.crypt as crypt

from gi.repository import Gtk, Gdk, GObject

class Apply(glade.Progress):
	def __init__(self, parent, quit=True):
		
		self.parent = parent
		self.quit = quit
		
		threading.Thread.__init__(self)

	def resize(self, lst, dct, action):
		""" Do the resize process. """

		# Mini-loop to process filesystem resizing...
		for key in lst:
			try:
				obj = dct[key]["obj"]
				cng = dct[key]["changes"]
				if "LVMcontainer" in dct[key]:
					LVMcontainer = dct[key]["LVMcontainer"]
				else:
					LVMcontainer = None
			except:
				verbose("Unable to get a correct object/changes from %s." % key)
				continue # Skip.
				
			# Should resize?
			if "resize" in cng:
								
				if LVMcontainer:
					# It is a LVM logical volume, pass it instead of the parted object
					_obj = LVMcontainer
				else:
					_obj = obj

				if (cng["resize"] < _obj.getLength("MB") and not action == lib.ResizeAction.SHRINK) or (
				cng["resize"] > _obj.getLength("MB") and not action == lib.ResizeAction.GROW):
					continue
				try:
					progress = lib.resize_partition_for_real(_obj, cng["resize"], action)
					self.parent.set_header("hold", _("Resizing %s...") % key, _("Let's hope everything goes well! :)"))
					if not progress:
						continue
					status = progress.wait()
				except:
					# Workaround to avoid duplicate code when handling errors
					status = 1
				if status != 0:
					# Failed ...
					self.parent.set_header("error", _("Failed resizing %s.") % key, _("See /var/log/linstaller/linstaller_latest.log for more details.") + "\n" + _("Maybe you shrinked too much the partition."))

					if self.parent.is_automatic:
						self.parent.is_automatic = "fail"
						self.parent.on_steps_ok()
					
					# Restore sensitivity
					self.parent.idle_add(self.parent.apply_window.set_sensitive, True)
					self.parent.idle_add(self.parent.objects["parent"].main.set_sensitive, True)

					return False

	def progress(self):
		""" Applies the changes to the devices. """
		
		# Disable next button
		self.parent.on_steps_hold()
		
		# Make window unsensitive
		self.parent.idle_add(self.parent.objects["parent"].main.set_sensitive, False)
		
		lst, dct = lib.device_sort(self.parent.changed)
		
		# If we should shrink something, do it now
		res = self.resize(lst, dct, lib.ResizeAction.SHRINK)
		if res == False: return res
				
		for key in lst:
			try:
				obj = dct[key]["obj"]
				cng = dct[key]["changes"]
				if "LVMcontainer" in dct[key]:
					LVMcontainer = dct[key]["LVMcontainer"]
				else:
					LVMcontainer = None
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

			
			# Should crypt?
			is_crypt = False
			if "crypt" in cng:
				# Fill?
				if "fill" in cng:
					try:
						self.parent.set_header("hold", _("Filling %s with random data...") % key, _("This may take a while, depending by the quality of random data selected."))
						cryptdev = crypt.LUKSdrive(obj)
						cryptdev.random_fill(type=cng["fill"])
					except CmdError:
						# Failed ...
						self.parent.set_header("error", _("Failed filling %s with random data.") % key, _("See /var/log/linstaller/linstaller_latest.log for more details."))

						if self.parent.is_automatic:
							self.parent.is_automatic = "fail"
							self.parent.on_steps_ok()
						
						# Restore sensitivity
						self.parent.idle_add(self.parent.apply_window.set_sensitive, True)
						self.parent.idle_add(self.parent.objects["parent"].main.set_sensitive, True)

						return False
				
				try:
					self.parent.set_header("hold", _("Encrypting %s...") % key, _("Let's hope everything goes well! :)"))
					cryptdev = crypt.LUKSdrive(obj)
					cryptdev.format(cng["crypt"], cipher=self.parent.settings["cipher"], keysize=int(self.parent.settings["keysize"]))
					# Open crypt partition...
					cryptdev.open(cng["crypt"])
					
					is_crypt = obj
					obj = cryptdev
				except CmdError:
					# Failed ...
					self.parent.set_header("error", _("Failed encrypting %s.") % key, _("See /var/log/linstaller/linstaller_latest.log for more details."))

					if self.parent.is_automatic:
						self.parent.is_automatic = "fail"
						self.parent.on_steps_ok()
					
					# Restore sensitivity
					self.parent.idle_add(self.parent.apply_window.set_sensitive, True)
					self.parent.idle_add(self.parent.objects["parent"].main.set_sensitive, True)

					return False
			
			# Should format?
			if "format" in cng:
				if LVMcontainer:
					# It is a LVM logical volume, pass it instead of the parted object
					_obj = LVMcontainer
				else:
					_obj = obj
				progress = lib.format_partition_for_real(_obj, cng["format"])
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
			
			# Should create a PV?
			if "PVcreate" in cng:
				try:
					lvm.PhysicalVolume(part=obj).create()
				except CmdError:
					# Failed ...
					self.parent.set_header("error", _("Failed creating a LVM Physical Volume in %s.") % key, _("See /var/log/linstaller/linstaller_latest.log for more details."))

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

		# If we should grow something, do it now
		res = self.resize(lst, dct, lib.ResizeAction.GROW)
		if res == False: return res

		# Preseed *all* changes
		self.parent.settings["changed"] = self.parent.changed
		
		# Add to self.previously_changed
		for item in self.parent.touched:
			if not item in self.parent.previously_changed: self.parent.previously_changed.append(item)

		if not self.parent.is_automatic: self.parent.idle_add(self.parent.refresh_manual, None, False)
		
		# If we're here, ok!	
		self.parent.set_header("ok", _("Changes applied!"), _("Press the Forward button to continue!"))		

		# Enable Next button
		self.parent.on_steps_ok()

		# Restore sensitivity
		self.parent.idle_add(self.parent.apply_window.set_sensitive, True)
		self.parent.idle_add(self.parent.objects["parent"].main.set_sensitive, True)
		
		if self.parent.is_automatic: self.parent.is_automatic = "done"

class LVM_apply(glade.Progress):
	def __init__(self, parent, quit=True):
		
		self.parent = parent
		self.quit = quit
		
		threading.Thread.__init__(self)

	def restore(self):
		""" Restores sensitivity to the window specified in parent's
		LVMrestoreto. """
		
		if not self.parent.LVMrestoreto:
			# Main window
			self.parent.idle_add(self.parent.objects["parent"].main.set_sensitive, True)
		else:
			# User specified window
			self.parent.idle_add(self.parent.LVMrestoreto.set_sensitive, True)
			self.parent.LVMrestoreto = None # Reset

	def resize(self, obj, newsize, action):
		""" Do the resize process. """
		
		try:
			progress = lib.resize_partition_for_real(obj.partition, newsize, action, path=obj.path, fs=obj.fileSystem.type)
			self.parent.set_header("hold", _("Resizing LVM logical volume..."), _("Let's hope everything goes well! :)"))
			if not progress:
				return
			status = progress.wait()
		except KeyError:
			# Workaround to avoid duplicate code when handling errors
			status = 1
		if status != 0:
			# Failed ...
			self.parent.set_header("error", _("Failed resizing the LVM logical volume."), _("See /var/log/linstaller/linstaller_latest.log for more details.") + "\n" + _("Maybe you shrinked too much the partition."))

			if self.parent.is_automatic:
				self.parent.is_automatic = "fail"
				self.parent.on_steps_ok()
				
			# Restore sensitivity
			self.parent.idle_add(self.parent.lvm_apply_window.set_sensitive, True)
			self.restore()

			return False

	def progress(self):
		""" Applies the changes to the devices. """
		
		share = self.parent.LVMshare
		
		# Disable next button
		self.parent.on_steps_hold()
		
		# Make window unsensitive
		self.parent.idle_add(self.parent.objects["parent"].main.set_sensitive, False)
		
		verbose("Committing LVM changes to %s..." % share["obj"].path)
		self.parent.set_header("hold", _("Committing changes to %s...") % share["obj"].path, _("This may take a while."))
		
		try:
			# Unlike classic Apply(), we process only one device at time,
			# with all informations available in self.LVMshare. Seems easy.
			if share["type"] == "create":
				# We need to create a new LV
				share["obj"].name = share["name"]
				share["obj"].create(share["size"])
			elif share["type"] == "remove":
				# We need to remove a LV
				share["obj"].remove()
			elif share["type"] == "delete":
				# We need to clear the VG
				share["obj"].clear()
			elif share["type"] == "modify":
				if "size" in share:
					# We need to resize
					
					oldsize = share["obj"].getLength("MB")
					
					if oldsize > share["size"]:
						# Shrink, reduce the filesystem then the LV
						res = self.resize(share["obj"], share["size"], lib.ResizeAction.SHRINK)
						if res == False: return res

						share["obj"].resize(share["size"], type=lib.ResizeAction.SHRINK)
					else:
						# Grow, grow the LV then the filesystem
						share["obj"].resize(share["size"], type=lib.ResizeAction.GROW)
						
						# We do not trust our data, so get the size from the LV object
						share["obj"].reload_infos()
						share["size"] = share["obj"].infos["size"]
						
						res = self.resize(share["obj"], share["size"], lib.ResizeAction.GROW)
						if res == False: return res
			elif share["type"] == "VGcreate":
				share["obj"].create(share["devices"])
			elif share["type"] == "VGmodify":
				# Compare old devices and new, and
				# extend/reduce
				toadd = []
				toremove = []
				_original = lvm.return_vg_with_pvs()[self.parent.VGname]
				# Make _original easier to manage
				original = []
				for pv in _original:
					original.append(pv["volume"].pv)
				
				for pv in share["devices"]:
					if not pv in original:
						# Added
						verbose("%s: going to extend VG with %s" % (self.parent.VGname, pv))
						toadd.append(pv)
				
				for pv in original:
					if not pv in share["devices"]:
						# Removed
						verbose("%s: going to reduce VG by removing %s" % (self.parent.VGname, pv))
						toremove.append(pv)
				
				# Add, remove
				if toadd: share["obj"].extend(toadd)
				if toremove: share["obj"].reduce(toremove)

				# Compare names...
				if self.parent.VGname != share["name"]:
					# Name changed, rename
					share["obj"].rename(share["name"])
			elif share["type"] == "VGremove":
				share["obj"].remove()
				
		except KeyError:
			self.parent.set_header("error", _("Failed committing changes to %s..")  % share["obj"].path, _("See /var/log/linstaller/linstaller_latest.log for more details."))
								
			# Restore sensitivity
			self.parent.idle_add(self.parent.lvm_apply_window.set_sensitive, True)
			self.restore()

			# Clear LVMshare
			self.parent.LVMshare = {}
			
			return False
		
		# Now check if we should format the partition: queue it and format
		# NOW.
		if "format" in share and share["format"]:
			progress = lib.format_partition_for_real(share["obj"], share["filesystem"])
			self.parent.set_header("hold", _("Formatting %s...") % share["obj"].path, _("Let's hope everything goes well! :)"))
			status = progress.wait()
			if status != 0:
				# Failed ...
				self.parent.set_header("error", _("Failed formatting %s.") % share["obj"].path, _("See /var/log/linstaller/linstaller_latest.log for more details."))
				
				# Restore sensitivity
				self.parent.idle_add(self.parent.lvm_apply_window.set_sensitive, True)
				self.restore()

				# Clear LVMshare
				self.parent.LVMshare = {}

				return False
		
		# Add to self.previously_changed
		if not share["obj"].path in self.parent.previously_changed:
			self.parent.previously_changed.append(share["obj"].path)

		if not share["type"] in ("remove","delete","modify","VGcreate","VGmodify","VGremove"):
			# Add the new partition to changed
			self.parent.changed[share["obj"].path] = {"obj":share["obj"], "changes":{}}

			# Seed mount_on_install
			self.parent.changed[share["obj"].path]["changes"]["mount_on_install"] = True
			
			# Set mountpoint
			if "mountpoint" in share and share["mountpoint"]:
				self.parent.change_mountpoint(share["obj"].path, share["mountpoint"])
		elif share["type"] == "remove":
			# Remove from changed
			del self.parent.changed[share["obj"].path]
		elif share["type"] == "delete":
			for item, content in self.parent.changed.items():
				if item.startswith(share["obj"].path):
					del self.parent.changed[item]

		# Clear LVMshare
		self.parent.LVMshare = {}

		# FIXME?
		self.parent.idle_add(lvm.refresh)
		self.parent.idle_add(self.parent.manual_populate)
		#self.parent.idle_add(self.parent.refresh_manual, None, False, True)
		# FIXMEEEEE!
		if self.parent.LVMrestoreto == self.parent.vgmanage_window:
			self.parent.idle_add(self.parent.vgmanage_window_populate)

		# If we're here, ok!	
		self.parent.set_header("ok", _("Changes applied!"), _("Press the Forward button to continue!"))		

		# Enable Next button
		self.parent.on_steps_ok()

		# Restore sensitivity
		self.parent.idle_add(self.parent.lvm_apply_window.set_sensitive, True)
		self.restore()
		
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
		
		self.set_header("info", _("Disk partitioning"), _("Manage your drives"), appicon="drive-harddisk")

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
		
		# Also reload LVM  and LUKS devices...
		lvm.refresh()
		crypt.refresh()
	
	def refresh_manual(self, obj=None, complete=True, noclear=False):
		""" Refreshes the manual partitioning page. """

		self.set_header("info", _("Manual partitioning"), _("Powerful tools for powerful pepole."), appicon="drive-harddisk")

		self.has_swap_warning_showed = False

		self.refresh()
		
		# Also remove flags.
		if not noclear:
			for name, changes in self.changed.items():
				if complete:
					# Clear.
					#changes["changes"].clear()
					del self.changed[name]
				else:
					# Remove all but useas and mount_on_install
					for key, value in changes["changes"].items():
						if not key in ("useas","mount_on_install"):
							del changes["changes"][key]
					
					nm = os.path.basename(name)
					if lib.is_disk(nm):
						if nm in self.devices:
							changes["obj"] = self.devices[nm]
						else:
							changes["obj"] = None
					else:
						changes["obj"] = lib.return_partition(nm)
						
					#changes["obj"] = None					
		
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

	def lvm_apply(self):
		""" Applies the LVM changes to the devices. """
		
		# Apply!
		clss = LVM_apply(self, quit=False)
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
			container["title"].set_markup("<big><b>%s</b></big>" % (_("Install %(distro)s to the %(size)s GB of free space in %(drive)s") % {"distro":self.moduleclass.main_settings["distro"], "size":round(info["freesize"] / 1000, 2), "drive":info["drive"]}))
			
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

	def on_crypting_random_toggled(self, obj):
		""" Called when crypting_random is toggled. """
		
		if obj.get_active():
			# True
			self.idle_add(self.crypting_random_hq.set_sensitive, True) # Make the HQ box sensitive
		else:
			# False
			self.idle_add(self.crypting_random_hq.set_active, False) # Reset the HQ box
			self.idle_add(self.crypting_random_hq.set_sensitive, False) # ...and make it insensitive

	def automatic_ready(self):
		""" Called when the automatic window is ready. """
		
		# Refresh, some automatic solutions may be in place even after restarting the module
		self.refresh()
		
		self.automatic_buttons = {}
		self.automatic_buttons_reverse = {}
		self.is_automatic = True
		
		if self.settings["is_echo"]:
			self.set_header("info", _("Select the partition where install %s") % self.moduleclass.main_settings["distro"], _("No data will be touched."), appicon="drive-harddisk-usb")
		else:
			self.set_header("info", _("Automatic partitioning"), _("Let the magic manage your drives!"), appicon="drive-harddisk")
		
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
			self.lock_button.set_sensitive(False)
			self.newtable_button.set_sensitive(True)
			self.delete_button.set_sensitive(False)
		elif description == "empty":
			# empty, we need to make unsensitive everything but the "Add partition button"
			self.add_button.set_sensitive(True)
			self.remove_button.set_sensitive(False)
			self.edit_button.set_sensitive(False)
			self.lock_button.set_sensitive(False)
			self.newtable_button.set_sensitive(False)
			self.delete_button.set_sensitive(False)
		elif description == "full":
			# full, we need to make sensitive everything but the "New table button" and the "Add button"
			self.add_button.set_sensitive(False)
			self.remove_button.set_sensitive(True)
			self.edit_button.set_sensitive(True)
			self.lock_button.set_sensitive(False)
			self.newtable_button.set_sensitive(False)
			self.delete_button.set_sensitive(True)
		elif description == None:
			# None, we need to make sensitive everything but the "New table button"
			self.add_button.set_sensitive(True)
			self.remove_button.set_sensitive(True)
			self.edit_button.set_sensitive(True)
			self.lock_button.set_sensitive(False)
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
			if self.current_selected["value"] in crypt.LUKSdevices:
				# Encrypted partition
				is_encrypted = True
			else:
				is_encrypted = False
			# We need to see if the selected partition is a freespace partition (can add, can't remove). Enable/Disable buttons accordingly
			if not description == "notable":
				if "-" in self.current_selected["value"]:
					self.add_button.set_sensitive(True)
					self.remove_button.set_sensitive(False)
					self.edit_button.set_sensitive(False)
					self.lock_button.set_sensitive(False)
				else:
					self.add_button.set_sensitive(False)
					self.remove_button.set_sensitive(True)
					self.edit_button.set_sensitive(True)
					self.lock_button.set_sensitive(False)
				if is_extended:
					self.remove_button.set_sensitive(False)
					self.edit_button.set_sensitive(False)
				if is_encrypted:
					self.lock_button.set_sensitive(True)
	
	def get_device_from_selected(self):
		""" Returns a device object from self.current_selected. """

		# This may be a LVM Logical Volume, we should check the path
		path = self.current_selected["value"].replace("/dev/","").split("/")[0]
		if path in lvm.VolumeGroups:
			return lvm.VolumeGroups[path]

		# If there is an existing object in changed, we want to return that
		# instead of getting a new one
		if self.current_selected["value"].replace("/dev/","") in self.changed and self.changed[self.current_selected["value"].replace("/dev/","")]["obj"]:
			return self.changed[self.current_selected["value"].replace("/dev/","")]["obj"]

		return self.devices[lib.return_device(self.current_selected["value"]).replace("/dev/","")]

	def get_disk_from_selected(self):
		""" Returns a device object from self.current_selected. """

		# This may be a LVM Logical Volume, we should check the path
		path = self.current_selected["value"].replace("/dev/","").split("/")[0]
		if path in lvm.VolumeGroups:
			return lvm.VolumeGroups[path]

		return self.disks[lib.return_device(self.current_selected["value"]).replace("/dev/","")]
	
	def get_partition_from_selected(self):
		""" Returns a partition object from self.current_selected. """
		
		# This may be a LVM Logical Volume, we should check the path
		path = self.current_selected["value"].replace("/dev/","").split("/")
		if len(path) > 1:
			# We are sure it is not a normal partition...
			# path[0] = volumegroup, path[1] = logicalvolume
			try:
				result = lvm.LogicalVolumes[path[0]][path[1]]
			except KeyError:
				result = None
			
			return result
		
		# If there is an existing object in changed, we want to return that
		# instead of getting a new one
		if not "-1" in self.current_selected["value"] and self.current_selected["value"] in self.changed and self.changed[self.current_selected["value"]]["obj"]:
			return self.changed[self.current_selected["value"]]["obj"]
		
		# Get the object from the iter
		result = self.current_selected["model"].get_value(self.current_selected["iter"], 7)
		if result: return result
		
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
		
		self.idle_add(button.override_background_color, Gtk.StateFlags.NORMAL, color1)

	def on_mount_on_install_changed(self, obj):
		""" Called when mount_on_install is changed. """
		
		if self.mount_on_install_prepare: return
		
		if obj.get_active() == True:
			self.idle_add(self.partition_window.set_sensitive, False)
			self.idle_add(self.mount_on_install_window.show)

	def on_lv_name_change(self, obj):
		""" Called when lv_name is changed. """
		
		if self.LVname == False:
			self.idle_add(self.partition_ok.set_sensitive, True)
			return
		
		txt = obj.get_text()
		
		if txt == "":
			# No text, no sensitiveness...
			self.idle_add(self.partition_ok.set_sensitive, False)
			
			self.change_entry_status(obj, "hold")
		else:
			# There is text, check if we can use the name...
			
			# FIXME? Should we allow two LV of the same name if they
			# are in different groups?
			used = False
			for group, items in lvm.LogicalVolumes.items():
				if txt in items and not txt == self.LVname:
					used = True
			
			if not used:
				self.idle_add(self.partition_ok.set_sensitive, True)
				
				self.change_entry_status(obj, "ok")
			else:
				self.idle_add(self.partition_ok.set_sensitive, False)
				
				self.change_entry_status(obj, "error", "Logical volume name already used!")

	def on_vgmanage_button_clicked(self, obj):
		""" Called when the vgmanage button has been clicked. """
		
		self.idle_add(self.objects["parent"].main.set_sensitive, False)
		self.idle_add(self.vgmanage_window.set_sensitive, False)
		self.idle_add(self.vgmanage_window.show)
		
		self.idle_add(self.vgmanage_window_populate)

	def on_newtable_button_clicked(self, obj):
		""" Called when the newtable button has been clicked. """
		
		self.idle_add(self.objects["parent"].main.set_sensitive, False)
		self.idle_add(self.newtable_window.show)

	def on_remove_button_clicked(self, obj):
		""" Called when the remove button has been clicked. """
		
		part = self.get_partition_from_selected()
		
		self.remove_window.set_markup("<big><b>" + _("Do you really want to remove %s?") % part.path + "</b></big>")
		
		if hasattr(part, "isLVM") and part.isLVM:
			# properly set the secondary text
			self.remove_window.format_secondary_markup(_('You cannot <b>go back!</b>'))
			self.remove_window.set_property("message_type", Gtk.MessageType.WARNING)
		else:
			self.remove_window.format_secondary_markup(_('Use the "Refresh" button to undo this change.'))
			self.remove_window.set_property("message_type", Gtk.MessageType.QUESTION)
		
		self.idle_add(self.objects["parent"].main.set_sensitive, False)
		self.idle_add(self.remove_window.show)

	def on_delete_button_clicked(self, obj):
		""" Called when the delete button has been clicked. """

		dev = self.get_device_from_selected()

		self.delete_window.set_markup("<big><b>" + _("Do you really want to delete all partitions on %s?") % dev.path + "</b></big>")

		if hasattr(dev, "isLVM") and dev.isLVM:
			# properly set the secondary text
			self.delete_window.format_secondary_markup(_('You cannot <b>go back!</b>'))
			self.delete_window.set_property("message_type", Gtk.MessageType.WARNING)
		else:
			self.delete_window.format_secondary_markup(_('Use the "Refresh" button to undo this change.'))
			self.delete_window.set_property("message_type", Gtk.MessageType.QUESTION)

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
		
		self.is_add = True
		
		# Get the device
		device = self.get_partition_from_selected()
		LVMcontainer = None
		if hasattr(device, "isLVM") and device.isLVM:
			LVMcontainer = device
			device = device.partition
			
			path = LVMcontainer.path

			# Show the lv_frame
			self.lv_frame.show()
			
			# Set the LV name
			self.lv_name.set_text("")
			self.change_entry_status(self.lv_name, "hold")
			self.size_manual_entry.grab_focus()
			
			self.LVname = ""				
		else:
			path = device.path
			
			# Hide the lv_frame
			self.lv_frame.hide()
			
			self.LVname = False
				
		# Adjust the adjustment
		self.size_adjustment.set_lower(0.01)
		self.size_adjustment.set_upper(round(device.getLength("MB"), 3))

		# Populate the size
		self.size_manual_entry.set_value(round(device.getLength("MB"), 3))
		
		# Ensure the size frame is sensitive
		self.size_frame.set_sensitive(True)
		
		# Ensure the format checkbox is set to True and the "Do not format" unsensitive...
		self.format_box.set_active(True)
		self.idle_add(self.do_not_format_box.set_sensitive, False)

		# Set crypting_box to false
		self.idle_add(self.crypting_box.set_sensitive, True)

		# Also if we are in a LV, we need to disable "Use for LVM"
		if LVMcontainer:
			self.idle_add(self.lvm_box.set_sensitive, False)
			self.idle_add(self.crypting_box.set_sensitive, False)
		else:
			self.idle_add(self.lvm_box.set_sensitive, True)
			self.idle_add(self.crypting_box.set_sensitive, True)

		# Ensure we make sensitive/unsensitive the fs combobox
		self.on_formatbox_change(self.format_box)
		
		# Set ext4 as default...
		self.filesystem_combo.set_active(self.fs_table["ext4"])
		
		# Ensure the "Fill the device with random data" box is false...
		self.idle_add(self.crypting_random.set_active, False)
		self.on_crypting_random_toggled(self.crypting_random)
		
		# Hide the PVwarning
		self.idle_add(self.PVwarning.hide)
		
		# mount_on_install unsensitive
		self.idle_add(self.mount_on_install.set_sensitive, False)
		self.idle_add(self.crypting_password_alignment.hide)
		
		# Clear mountpoint
		self.mountpoint_entry.set_text("")
		self.mountpoint_combo.set_active(-1)
		
		if not LVMcontainer:
			self.partition_ok.set_sensitive(True)
		else:
			self.partition_ok.set_sensitive(False)
		
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
		
		self.is_add = False
		
		# Get the device
		device = self.get_partition_from_selected()
		LVMcontainer = None
		if hasattr(device, "isLVM") and device.isLVM:
			LVMcontainer = device
			#device = device.partition
			
			path = LVMcontainer.path
			
			# Show the lv_frame
			self.lv_frame.show()

			# Save the LV name
			self.LVname = LVMcontainer.name

			# Set the LV name
			self.lv_name.set_text(LVMcontainer.name)
			self.size_manual_entry.grab_focus()

			self.size_adjustment.set_upper(round(device.getLength("MB"), 3) + round(device.vgroup.infos["free"],3))
		else:
			path = device.path
			
			# Hide the lv_frame
			self.lv_frame.hide()
			
			self.LVname = False
			
			self.size_adjustment.set_upper(lib.maxGrow(device))
		
		self.current_length = round(device.getLength("MB"), 3)
		
		# Adjust the adjustment
		self.size_adjustment.set_lower(0.01)
		#self.size_adjustment.set_upper(round(device.getLength("MB"), 3))
		 #round(device.getMaxAvailableSize("MB"), 3))

		# Populate the size
		self.size_manual_entry.set_value(round(device.getLength("MB"), 3))
		
		# If LVM and fat32, we can't resize
		if LVMcontainer and device.fileSystem.type == "fat32":
			self.size_frame.set_sensitive(False)
		else:
			self.size_frame.set_sensitive(True)

		# Unset the format checkbox if we should.
		self.format_box.set_sensitive(True) # Ensure is sensitive
		if device.path in self.changed and "format" in self.changed[device.path]["changes"]:
			# To format; set the box to True
			self.idle_add(self.format_box.set_active, True)
			# Set too the filesystem, as it is specified in "format".
			self.current_fs = self.changed[device.path]["changes"]["format"]
			self.current_toformat = True
		elif path in lvm.PhysicalVolumes or "PVcreate" in self.changed[device.path]["changes"] or (
			path in crypt.LUKSdevices and crypt.LUKSdevices[path].path in lvm.PhysicalVolumes):
			# LVM Physical Volume, select "Use as LVM physical volume" radiobutton
			self.idle_add(self.lvm_box.set_active, True)
			# No filesystem is here...
			self.current_fs = "ext4"
			self.current_toformat = False
		else:
			# Unset the format box
			self.idle_add(self.do_not_format_box.set_active, True)
			# Set the filesystem
			if device.fileSystem != None:
				self.current_fs = device.fileSystem.type
			else:
				self.current_fs = "ext4"
			self.current_toformat = False
		
		if self.current_fs:
			self.filesystem_combo.set_active(self.fs_table[self.current_fs])
		else:
			self.filesystem_combo.set_active(-1)

		# Ensure we make sensitive/unsensitive the fs combobox
		self.on_formatbox_change(self.format_box)
		self.idle_add(self.do_not_format_box.set_sensitive, True)

		if device.path in crypt.LUKSdevices or "crypt" in self.changed[device.path]["changes"]:
			# The partition is/should be encrypted.
			# Ensure the encryption part is shown, but set sensitiveness to False
			self.idle_add(self.crypting_box.set_active, True)
			self.idle_add(self.crypting_box.set_sensitive, False)
			self.idle_add(self.crypting_password_alignment.set_sensitive, False)
			self.idle_add(self.crypting_password.set_text, "DUMMYPASSWORD") # Dummy password
			self.idle_add(self.crypting_password_confirm.set_text, "DUMMYPASSWORD") # Dummy password
		else:
			self.idle_add(self.crypting_box.set_sensitive, True)
			self.idle_add(self.crypting_password_alignment.set_sensitive, True)
		self.on_formatbox_change(self.crypting_box)
		# Ensure the "Fill the device with random data" box is false...
		self.idle_add(self.crypting_random.set_active, False)
		self.on_crypting_random_toggled(self.crypting_random)

		# Also if we are in a LV, we need to disable "Use for LVM"
		if LVMcontainer:
			self.idle_add(self.lvm_box.set_sensitive, False)
			self.idle_add(self.crypting_box.set_sensitive, False)
		else:
			self.idle_add(self.lvm_box.set_sensitive, True)
			self.idle_add(self.crypting_box.set_sensitive, True)

		# Clear mountpoint
		self.mountpoint_entry.set_text("")
		self.mountpoint_combo.set_active(-1)

		# Get current mountpoint (if any)...
		if "useas" in self.changed[path]["changes"]:
			self.current_mountpoint = self.changed[path]["changes"]["useas"]
			if self.current_mountpoint in self.mountp_table:
				self.mountpoint_combo.set_active(self.mountp_table[self.current_mountpoint])
			else:
				self.mountpoint_combo.set_active(-1)
				self.mountpoint_entry.set_text(self.current_mountpoint)
		else:
			self.current_mountpoint = None

		# Show PVwarning if we need to
		if path in lvm.PhysicalVolumes or path in crypt.LUKSdevices or "PVcreate" in self.changed[device.path]["changes"]:
			self.idle_add(self.PVwarning.show)
		else:
			self.idle_add(self.PVwarning.hide)
		
		# Make mount_on_install sensitive and set it if it is needed
		self.idle_add(self.mount_on_install.set_sensitive, True)
		self.mount_on_install_prepare = True
		if "mount_on_install" in self.changed[path]["changes"]:
			self.mount_on_install.set_active(self.changed[path]["changes"]["mount_on_install"])
		else:
			self.mount_on_install.set_active(False)
		self.mount_on_install_prepare = False
		
		self.idle_add(self.partition_ok.set_sensitive, True)
		
		# Connect buttons
		if self.partition_ok_id: self.partition_ok.disconnect(self.partition_ok_id)
		if self.partition_cancel_id: self.partition_cancel.disconnect(self.partition_cancel_id)
		self.partition_ok_id = self.partition_ok.connect("clicked", self.on_edit_window_button_clicked)
		self.partition_cancel_id = self.partition_cancel.connect("clicked", self.on_edit_window_button_clicked)

	def queue_for_format(self, path, fs):
		""" Queues for format. """
		
		self.changed[path]["changes"]["format"] = fs
	
	def queue_for_resize(self, path, newsize):
		""" Queues for resize. """
		
		self.changed[path]["changes"]["resize"] = newsize
	
	def change_mountpoint(self, path, mpoint):
		""" Changes the mountpoint in self.changed. """
		
		if mpoint:
			self.changed[path]["changes"]["useas"] = mpoint
			self.mountpoints_added[mpoint] = path
		elif "useas" in self.changed[path]["changes"]:
			del self.changed[path]["changes"]["useas"]

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
		
		# Also check the lv_name
		self.on_lv_name_change(self.lv_name)
	
	def child_window_delete(self, obj, event, restoreto=False):
		""" Called when the Close button on the child window has been clicked. """
				
		if restoreto == False:
			restoreto = self.objects["parent"].main
		
		self.idle_add(obj.hide)

		# Restore sensitivity
		if restoreto: restoreto.set_sensitive(True)
		
		return True
	
	def on_add_window_button_clicked(self, obj):
		""" Called when a button on the add partition window has been clicked. """
		
		self.idle_add(self.partition_window.hide)
		
		if obj == self.partition_ok:
			# Yes.
			# Create the new partition
			
			part = self.get_partition_from_selected()
			targetfs = self.fs_table_inverse[self.filesystem_combo.get_active()]
			if targetfs == "fat32" and float(self.size_adjustment.get_value()) < 512.0:
				# fat32 fs must be at least on a 512 mb partition, reverting to fat16
				targetfs = "fat16"
			
			# is LVM?
			isLVM = False
			if hasattr(part, "isLVM") and part.isLVM: isLVM = True
			
			if isLVM:
				# It is LVM, we need to display a confirmation dialog and
				# wait for the user input
				
				# lvcreate does not like decimal numbers, so we need
				# first to convert everything to kilobytes and then
				# drop any decimal number that may be still there...
				# SAFETY ALERT: IT'S UGLY.
				size = float((self.size_adjustment.get_value())-1.0)*1000
				if "." in str(size):
					size = str(size).split(".")[0]
				size = str(size) + "K"
				# Woah. It was really awful.
				
				# Populate LVMshare with direction on what we should do...
				self.LVMshare = {
					"type":"create",
					"obj":part,
					"name":self.lv_name.get_text(),
					"size":float(self.size_adjustment.get_value()),
					"filesystem":targetfs,
					"format":True,
					"mountpoint":self.get_mountpoint()
				}
				
				# Show the window, the Apply process will be started by
				# the window
				self.idle_add(self.lvm_apply_window.set_sensitive, True)
				self.idle_add(self.lvm_apply_window.show)
			else:
				self.set_header("hold", _("Creating the partition..."), _("Please wait."))

				if self.lvm_box.get_active():
					# Ensure the filesystem is None if we are going to make
					# the partition a LVM physical volume
					targetfs = None

				try:
					res = lib.add_partition(part.disk, start=part.geometry.start, size=lib.MbToSector(float(self.size_adjustment.get_value())), type=lib.p.PARTITION_NORMAL, filesystem=targetfs)
				except:
					# Failed! Ouch!
					self.set_header("error", _("Unable to add partition."), _("You shouldn't get here."))
					return
				
				# Add the new partition to changed
				self.changed[res.path] = {"obj":res, "changes":{}}
				

				# Should we make this partition a LVM Physical Volume?
				if self.lvm_box.get_active() or self.crypting_box.get_active():
					# YES!
					self.changed[res.path]["changes"]["PVcreate"] = True

					# Should we encrypt this partition?
					if self.crypting_box.get_active():
						# YES!
						self.changed[res.path]["changes"]["crypt"] = self.crypting_password.get_text()
						
						# Fill?
						if self.crypting_random.get_active() and not self.crypting_random_hq.get_active():
							# "low"-quality data
							self.changed[res.path]["changes"]["fill"] = crypt.FillQuality.LOW
						elif self.crypting_random_hq.get_active():
							# high-quality data
							self.changed[res.path]["changes"]["fill"] = crypt.FillQuality.HIGH
				else:
					self.queue_for_format(res.path, targetfs)
					self.change_mountpoint(res.path, self.get_mountpoint())

					# Seed mount_on_install
					self.changed[res.path]["changes"]["mount_on_install"] = True

				if not "PVcreate" in self.changed[res.path]["changes"]:
					subtext = _("Use the Apply button to save them.")
				else:
					# If we should create a physical volume, urge the
					# user to apply ASAP in order to make it usable for
					# the VGmanage dialog...
					subtext = _("You need to apply your changes in order to use the new LVM physical volume.")
				self.set_header("hold", _("You have some unsaved changes!"), subtext)
				self.change_button_bg(self.apply_button, self.objects["parent"].return_color("ok"))
				
				if not res.path in self.touched: self.touched.append(res.path)
				
				self.manual_populate()
		
		# Restore sensitivity
		if obj == self.partition_cancel or not isLVM:
			self.objects["parent"].main.set_sensitive(True)

	def on_edit_window_button_clicked(self, obj):
		""" Called when a button on the edit partition window has been clicked. """
		
		self.idle_add(self.partition_window.hide)
		
		if obj == self.partition_ok:
			# Yes.
			# Edit the partition
			
			part = self.get_partition_from_selected()
			LVMcontainer = None
			isLVM = False # we could use LVMcontainer, but to ensure consistency with add we use this
			if hasattr(part, "isLVM") and part.isLVM:
				LVMcontainer = part

				#part = part.partition
				isLVM = True

				path = LVMcontainer.path

				# It is LVM, we need to display a confirmation dialog and
				# wait for the user input

				self.LVMshare = {
					"type":"modify",
					"obj":LVMcontainer,
				}
			else:
				path = part.path
			
			# What we should do?
			# Check if the size has been changed...
			newsize = self.size_manual_entry.get_value()
			if newsize != self.current_length and not isLVM:
				# Yes! We need to resize!
				res = lib.resize_partition(part, lib.KbToSector(int(float(newsize)*1000))-1)
				if not res:
					# Failed! Ouch!
					self.set_header("error", _("Failed to resize partition."), _("Please double-check the inserted values."))
					
					self.objects["parent"].main.set_sensitive(True)
					return
				
				self.queue_for_resize(path, float(newsize))
			elif newsize != self.current_length and isLVM:
				self.LVMshare["size"] = float(newsize)
			else:
				if path in self.changed and "resize" in self.changed[path]["changes"]:
					del self.changed[path]["changes"]["resize"]
			
			# We should format?
			newtoformat = self.format_box.get_active()
			if newtoformat != self.current_toformat:
				if not newtoformat and not isLVM:
					if path in self.changed and "format" in self.changed[path]["changes"]:
						del self.changed[path]["changes"]["format"]
			
			if newtoformat:	
				newfs = self.fs_table_inverse[self.filesystem_combo.get_active()]
				if newfs == "fat32" and float(self.size_adjustment.get_value()) < 512.0:
					# fat32 fs must be at least on a 512 mb partition, reverting to fat16
					newfs = "fat16"
				if not isLVM:
					lib.format_partition(part, newfs) # Ensure we change part.fileSystem
					self.queue_for_format(path, newfs)
				else:
					self.LVMshare["filesystem"] = newfs
					self.LVMshare["format"] = True
			
			# Should we make this partition a LVM Physical Volume?
			if self.lvm_box.get_active() and not path in lvm.PhysicalVolumes and not (
				path in crypt.LUKSdevices and crypt.LUKSdevices[path].path in lvm.PhysicalVolumes):
				# YES!
				self.changed[path]["changes"]["PVcreate"] = True
			else:
				# NO :(
				if "PVcreate" in self.changed[path]["changes"]:
					del self.changed[path]["changes"]["PVcreate"]

			# Should we encrypt this partition?
			if self.crypting_box.get_active() and not path in crypt.LUKSdevices:
				# YES!
				self.changed[path]["changes"]["crypt"] = self.crypting_password.get_text()
				# Also ensure we will recreate the LVM PV...
				self.changed[path]["changes"]["PVcreate"] = True

				# Fill?
				if self.crypting_random.get_active() and not self.crypting_random_hq.get_active():
					# "low"-quality data
					self.changed[path]["changes"]["fill"] = crypt.FillQuality.LOW
				elif self.crypting_random_hq.get_active():
					# high-quality data
					self.changed[path]["changes"]["fill"] = crypt.FillQuality.HIGH
			else:
				# NO :(
				if "crypt" in self.changed[path]["changes"]:
					del self.changed[path]["changes"]["crypt"]
				if "fill" in self.changed[path]["changes"]:
					del self.changed[path]["changes"]["fill"]

			# We should change mountpoint?
			newmountpoint = self.get_mountpoint()
			if newmountpoint != self.current_mountpoint:
				# Yes! We need to change mountpoint!
				self.change_mountpoint(path, newmountpoint)
				# Remove the old mountpoint from the list
				if self.current_mountpoint:
					del self.mountpoints_added[self.current_mountpoint]
			
			# Seed mount_on_install
			self.changed[path]["changes"]["mount_on_install"] = self.mount_on_install.get_active()

			if isLVM and ("format" in self.LVMshare or "size" in self.LVMshare):
				# Show the window, the Apply process will be started by
				# the window
				self.idle_add(self.lvm_apply_window.set_sensitive, True)
				self.idle_add(self.lvm_apply_window.show)
			else:
				if not "PVcreate" in self.changed[path]["changes"]:
					subtext = _("Use the Apply button to save them.")
				else:
					# If we should create a physical volume, urge the
					# user to apply ASAP in order to make it usable for
					# the VGmanage dialog...
					subtext = _("You need to apply your changes in order to use the new LVM physical volume.")
				self.set_header("hold", _("You have some unsaved changes!"), subtext)

				if path in self.previously_changed: self.previously_changed.remove(path)
				if not path in self.touched: self.touched.append(path)
							
				self.manual_populate()
				
				# Ensure isLVM is False, to set sensitiveness later...
				isLVM = False
		
		# Restore sensitivity
		if obj == self.partition_cancel or not isLVM:
			self.objects["parent"].main.set_sensitive(True)
				
	def on_formatbox_change(self, obj):
		""" Called when formatbox has been toggled. """
				
		if obj == self.format_box and obj.get_active():
			# Make the combobox sensitive
			self.idle_add(self.filesystem_combo.set_sensitive, True)
			
			# mount_on_install unsensitive and disabled
			self.idle_add(self.mount_on_install.set_sensitive, False)
			self.mount_on_install.set_active(False)
			
		else:
			# Make it unsensitive
			self.idle_add(self.filesystem_combo.set_sensitive, False)
			# ...and restore the filesystem
			try:
				if self.current_fs:
					self.filesystem_combo.set_active(self.fs_table[self.current_fs])
				else:
					self.filesystem_combo.set_active(-1)
			except:
				self.filesystem_combo.set_active(-1)
			
			# mount_on_install sensitive
			self.idle_add(self.mount_on_install.set_sensitive, True)
		
		if obj in (self.lvm_box, self.crypting_box) and obj.get_active():
			# If lvm_box and crypting_box, also disable "mountpoint" section.
			
			# Clear mountpoint
			self.mountpoint_entry.set_text("")
			self.mountpoint_combo.set_active(-1)
			
			self.idle_add(self.mountpoint_frame.set_sensitive, False)
						
			if obj == self.crypting_box and obj.get_active():
				# crypting_box, show crypting_password_alignment
				self.idle_add(self.crypting_password_alignment.show)
				
				# Reset passwords
				self.crypting_password.set_text("")
				self.crypting_password_confirm.set_text("")
				
				# Set OK button insensitive
				self.on_crypting_password_changed(None)
		elif obj in (self.lvm_box, self.crypting_box):
			# Restore sensitivity to the mountpoint_frame
			self.idle_add(self.mountpoint_frame.set_sensitive, True)
			
			if obj == self.crypting_box:
				# hide password alignment
				self.idle_add(self.crypting_password_alignment.hide)

				# Check if mountpoint is ok (thus enabling the OK button)
				self.on_mountpoint_change(None)

		if obj in (self.lvm_box, self.crypting_box) and obj.get_active() and not self.is_add:
			# Show PVwarning...
			self.idle_add(self.PVwarning.show)
	
	def on_crypting_password_changed(self, obj):
		""" Called when a crypting password entry box has been changed. """
		
		# Get the passwords
		passw1 = self.crypting_password.get_text()
		passw2 = self.crypting_password_confirm.get_text()

		if not passw1:
			# passw1 is empty, set both on old
			self.change_entry_status(self.crypting_password, "hold")
			self.change_entry_status(self.crypting_password_confirm, "hold")
			
			self.idle_add(self.partition_ok.set_sensitive, False)
		elif passw1 == passw2:
			# Ok
			self.change_entry_status(self.crypting_password, "ok")
			self.change_entry_status(self.crypting_password_confirm, "ok")
			
			# Check if mountpoint is ok (thus enabling the OK button)
			self.on_mountpoint_change(None)
		else:
			# No match :/
			failmessage = _("The passwords doesn't match.")
			self.change_entry_status(self.crypting_password, "error", failmessage)
			self.change_entry_status(self.crypting_password_confirm, "error", failmessage)
			
			self.idle_add(self.partition_ok.set_sensitive, False)
	
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

	def on_mount_on_install_window_button_clicked(self, obj):
		""" Called when a button on the mount_on_install window has been clicked. """
		
		self.idle_add(self.mount_on_install_window.hide)
		
		if obj == self.mount_on_install_no:
			# Reset the checkbox
			self.mount_on_install.set_active(False)
		
		# Restore sensitivity
		self.partition_window.set_sensitive(True)

	def on_remove_window_button_clicked(self, obj):
		""" Called when a button on the remove window has been clicked. """
		
		self.idle_add(self.remove_window.hide)
		
		part = self.get_partition_from_selected()

		# is LVM?
		isLVM = False
		if hasattr(part, "isLVM") and part.isLVM: isLVM = True
		
		if obj == self.remove_yes:
			# Yes.
			
			if isLVM:
				# It is LVM, we need to process everything ASAP.
				
				# Populate LVMshare with direction on what we should do...
				self.LVMshare = {
					"type":"remove",
					"obj":part
				}
				
				# Apply!
				self.idle_add(self.lvm_apply)
			else:
				# Remove the partition
				res = lib.delete_partition(part)
				if not res:
					# Failed!
					self.set_header("error", _("Unable to remove the partition."), _("Why did it happen?!"))
				else:
					# Ok!
					self.set_header("hold", _("You have some unsaved changes!"), _("Use the Apply button to save them."))
				
				if not self.get_device_from_selected().path in self.touched: self.touched.append(self.get_device_from_selected().path)
				# Remove changes?
				del self.changed[part.path]
				if part.path in self.touched: self.touched.remove(part.path)
				if part.path in self.previously_changed: self.previously_changed.remove(part.path)
				# Remove eventual mountpoints
				for mpoint, parts in self.mountpoints_added.items():
					if parts == part.path:
						del self.mountpoints_added[mpoint]
						break
				
				self.manual_populate()
		
		# Restore sensitivity
		if obj == self.remove_no or not isLVM:
			self.objects["parent"].main.set_sensitive(True)

	def on_delete_window_button_clicked(self, obj):
		""" Called when a button on the delete window has been clicked. """
		
		self.idle_add(self.delete_window.hide)
		
		dev = self.get_disk_from_selected()

		# is LVM?
		isLVM = False
		if hasattr(dev, "isLVM") and dev.isLVM: isLVM = True
		
		if obj == self.delete_yes:
			# Yes.
			
			if isLVM:
				# It is LVM, we need to process everything ASAP.
				
				# Populate LVMshare with direction on what we should do...
				self.LVMshare = {
					"type":"delete",
					"obj":dev
				}
				
				# Apply!
				self.idle_add(self.lvm_apply)			
			else:
				# Clear the device
				res = lib.delete_all(dev)
				if not res:
					# Failed!
					self.set_header("error", _("Unable to delete all partitions."), _("Why did it happen?!"))
				else:
					# Ok!
					self.set_header("hold", _("You have some unsaved changes!"), _("Use the Apply button to save them."))

				if not self.get_device_from_selected().path in self.touched: self.touched.append(self.get_device_from_selected().path)
				# Remove changes
				val = lib.return_device(self.current_selected["value"])
				for dev, content in self.changed.items():
					if not dev == val and dev.startswith(val):
						del self.changed[dev]
						if dev in self.touched: self.touched.remove(dev)
						if dev in self.previously_changed: self.previously_changed.remove(dev)

						# Remove eventual mountpoints
						for mpoint, parts in self.mountpoints_added.items():
							if parts == dev:
								del self.mountpoints_added[mpoint]
								break

				self.manual_populate()
		
		# Restore sensitivity
		if obj == self.delete_no or not isLVM:
			self.objects["parent"].main.set_sensitive(True)

	def manual_apply(self):
		""" Workaround to get the apply window hidden while doing things. """

		dev = self.get_disk_from_selected()
			
		res = self.apply()

	def return_selected_physicalvolumes(self):
		""" Returns the selected physical volumes on the Add/Edit VG window. """
		
		lst = []
		for name, cbox in self.vgmanage_manage_checkboxes.items():
			if cbox.get_active():
				# cbox is active, we need to use it!
				#lst.append(lvm.PhysicalVolume(device_name=name))
				lst.append(name)
		
		return tuple(lst)

	def on_vgmanage_add_window_button_clicked(self, obj):
		""" Triggered when a button in the vgmanage-add window has been clicked. """
		
		# Hide
		self.idle_add(self.vgmanage_manage_window.hide)
		
		if obj == self.vg_manage_ok:
			# Ok button clicked, populate LVMshare
			
			self.LVMshare = {
				"type":"VGcreate",
				"obj":lvm.VolumeGroup(name=self.vg_manage_entry.get_text()),
				"devices":self.return_selected_physicalvolumes()
			}
				
			# Show the window, the Apply process will be started by
			# the window
			self.LVMrestoreto = self.vgmanage_window
			self.idle_add(self.lvm_apply_window.set_sensitive, True)
			self.idle_add(self.lvm_apply_window.show)
		else:
			self.idle_add(self.vgmanage_window.set_sensitive, True)

	def on_vgmanage_edit_window_button_clicked(self, obj):
		""" Triggered when a button in the vgmanage-edit window has been clicked. """
		
		# Hide
		self.idle_add(self.vgmanage_manage_window.hide)
		
		if obj == self.vg_manage_ok:
			# Ok button clicked, populate LVMshare
			
			self.LVMshare = {
				"type":"VGmodify",
				"obj":lvm.VolumeGroup(name=self.VGname),
				"name":self.vg_manage_entry.get_text(),
				"devices":self.return_selected_physicalvolumes()
			}
				
			# Show the window, the Apply process will be started by
			# the window
			self.LVMrestoreto = self.vgmanage_window
			self.idle_add(self.lvm_apply_window.set_sensitive, True)
			self.idle_add(self.lvm_apply_window.show)
		else:
			self.idle_add(self.vgmanage_window.set_sensitive, True)
	
	def on_vg_manage_entry_changed(self, obj):
		""" Called when vg_manage_entry is changed. """
		
		if self.VGname == False:
			self.idle_add(self.vg_manage_ok.set_sensitive, True)
			return
		
		txt = self.vg_manage_entry.get_text()
		
		if txt == "":
			# No text, no sensitiveness...
			self.idle_add(self.vg_manage_ok.set_sensitive, False)
			self.change_entry_status(self.vg_manage_entry, "hold")
		else:
			# There is text, check if we can use the name...
			
			if txt in lvm.VolumeGroups and not txt == self.VGname:
				self.idle_add(self.vg_manage_ok.set_sensitive, False)
				self.change_entry_status(self.vg_manage_entry, "error", _("Volume group name already used!"))
			elif obj:
				# Called from a true keystroke :)
				# Fire up on_vg_manage_checkbox_changed to check if we can
				# go ahead
				self.idle_add(self.on_vg_manage_checkbox_changed, None)
				self.change_entry_status(self.vg_manage_entry, "ok")
			else:
				self.idle_add(self.vg_manage_ok.set_sensitive, True)
				self.change_entry_status(self.vg_manage_entry, "ok")
	
	def on_vg_manage_checkbox_changed(self, obj):
		""" Called when a checkbox has been clicked. """
		
		if obj and obj.get_active():
			# Called from a true click :)
			# Fire up on_vg_manage_entry_changed to check if we can
			# go ahead
			self.idle_add(self.on_vg_manage_entry_changed, None)
		else:
			# See the other checkboxes
			for cb in self.vgmanage_manage_checkboxes:
				if self.vgmanage_manage_checkboxes[cb].get_active():
					# At least one
					self.idle_add(self.vg_manage_ok.set_sensitive, True)
					return
			
			self.idle_add(self.vg_manage_ok.set_sensitive, False)

	def prepare_vgmanage_manage_window(self, add=True):
		""" Set-ups the vgmanage-manage window to be ready to add
		a new virtual group. """

		# Destroy every child that may be into the viewport
		for child in self.vg_manage_viewport.get_children():
			child.destroy()
		
		self.vgmanage_manage_checkboxes = {}
		
		frame_container = Gtk.VBox()
		frame_container.set_homogeneous(False)
		frame_container.set_spacing(3)
		
		# Generate checkboxes of available physical volumes
		dct = lvm.return_vg_with_pvs()
		if not add:
			# Get selection
			selection = self.vg_treeview.get_selection()
		
			# Get selected item
			model, _iter = selection.get_selected()
			self.VGname = model.get_value(_iter, 0)
			
			# Edit mode, generate also the "Currently Used" frame
			used_frame = Gtk.Frame()
			used_frame.set_shadow_type(Gtk.ShadowType.NONE)
			used_frame_label = Gtk.Label()
			used_frame_label.set_markup("<b>%s</b>" % _("Currently used"))
			used_frame.set_label_widget(used_frame_label)
			
			used_frame_alignment = Gtk.Alignment()
			used_frame_alignment.set_padding(3,0,12,0)

			used_frame_vbox = Gtk.VBox()

			used_frame_alignment.add(used_frame_vbox)
			used_frame.add(used_frame_alignment)

			frame_container.pack_start(used_frame, False, True, 0)
			
			for pv in dct[self.VGname]:
				self.vgmanage_manage_checkboxes[pv["volume"].pv] = Gtk.CheckButton("%s (%s MB)" % (pv["volume"].pv, pv["size"]))
				self.vgmanage_manage_checkboxes[pv["volume"].pv].set_active(True)
				self.vgmanage_manage_checkboxes[pv["volume"].pv].connect(
					"clicked", 
					self.on_vg_manage_checkbox_changed
				)
				used_frame_vbox.pack_start(self.vgmanage_manage_checkboxes[pv["volume"].pv], False, True, 0)
				
				# If this PV is used, set sensitiveness to False
				if pv["volume"].is_used:
					self.vgmanage_manage_checkboxes[pv["volume"].pv].set_sensitive(False)
		else:
			self.VGname = ""
		
		if None in dct:
			# We have some free PVs
			available_frame = Gtk.Frame()
			available_frame.set_shadow_type(Gtk.ShadowType.NONE)
			available_frame_label = Gtk.Label()
			available_frame_label.set_markup("<b>%s</b>" % _("Available"))
			available_frame.set_label_widget(available_frame_label)
			
			available_frame_alignment = Gtk.Alignment()
			available_frame_alignment.set_padding(3,0,12,0)

			available_frame_vbox = Gtk.VBox()

			available_frame_alignment.add(available_frame_vbox)
			available_frame.add(available_frame_alignment)

			frame_container.pack_start(available_frame, False, True, 0)
			
			for pv in dct[None]:
				self.vgmanage_manage_checkboxes[pv["volume"].pv] = Gtk.CheckButton("%s (%s MB)" % (pv["volume"].pv, pv["size"]))
				self.vgmanage_manage_checkboxes[pv["volume"].pv].connect(
					"clicked", 
					self.on_vg_manage_checkbox_changed
				)
				available_frame_vbox.pack_start(self.vgmanage_manage_checkboxes[pv["volume"].pv], False, True, 0)
		
		self.vg_manage_viewport.add(frame_container)

		# Disconnect buttons
		if self.vg_manage_ok_id: self.vg_manage_ok.disconnect(self.vg_manage_ok_id)
		if self.vg_manage_cancel_id: self.vg_manage_cancel.disconnect(self.vg_manage_cancel_id)
		# Reconnect them now, set window title and do a couple of other things...
		if add:
			self.vg_manage_ok_id = self.vg_manage_ok.connect("clicked", self.on_vgmanage_add_window_button_clicked)
			self.vg_manage_cancel_id = self.vg_manage_cancel.connect("clicked", self.on_vgmanage_add_window_button_clicked)
			
			self.vgmanage_manage_window.set_title(_("Add a new volume group"))
			
			# Hide self.vg_manage_editlabel
			self.vg_manage_editlabel.hide()
			
			# Make OK button insensitive
			self.idle_add(self.vg_manage_ok.set_sensitive, False)
		else:
			self.vg_manage_ok_id = self.vg_manage_ok.connect("clicked", self.on_vgmanage_edit_window_button_clicked)
			self.vg_manage_cancel_id = self.vg_manage_cancel.connect("clicked", self.on_vgmanage_edit_window_button_clicked)
			
			self.vgmanage_manage_window.set_title(_("Edit %s") % self.VGname)
			
			# Show self.vg_manage_editlabel
			self.vg_manage_editlabel.show()
			
			# Make OK button sensitive
			self.idle_add(self.vg_manage_ok.set_sensitive, True)
		
		self.vg_manage_entry.set_text(self.VGname)
		if self.VGname == "": self.change_entry_status(self.vg_manage_entry, "hold")
		
		self.vg_manage_viewport.show_all()
		self.idle_add(self.vgmanage_manage_window.set_sensitive, True)

	def on_vgmanage_add_clicked(self, obj):
		""" Called when the add button on the vgmanage window has been clicked. """
		
		self.idle_add(self.vgmanage_window.set_sensitive, False)
		self.idle_add(self.vgmanage_manage_window.set_sensitive, False)
		self.idle_add(self.vgmanage_manage_window.show)
		
		
		self.idle_add(self.prepare_vgmanage_manage_window, True)

	def on_vgmanage_edit_clicked(self, obj):
		""" Called when the edit button on the vgmanage window has been clicked. """
		
		self.idle_add(self.vgmanage_window.set_sensitive, False)
		self.idle_add(self.vgmanage_manage_window.set_sensitive, False)
		self.idle_add(self.vgmanage_manage_window.show)
		
		
		self.idle_add(self.prepare_vgmanage_manage_window, False)

	def on_vgmanage_remove_clicked(self, obj):
		""" Called when the remove button on the vgmanage window has been clicked. """

		self.idle_add(self.vgmanage_window.set_sensitive, False)

		selection = self.vg_treeview.get_selection()
		
		# Get selected item
		model, _iter = selection.get_selected()
		value = model.get_value(_iter, 0)

		self.LVMshare = {
			"type":"VGremove",
			"obj":lvm.VolumeGroup(name=value)
		}
				
		# Show the window, the Apply process will be started by
		# the window
		self.LVMrestoreto = self.vgmanage_window
		self.idle_add(self.lvm_apply_window.set_sensitive, True)
		self.idle_add(self.lvm_apply_window.show)

	def on_vgmanage_window_button_clicked(self, obj):
		""" Called when the close button on the vgmanage window has been clicked. """

		# Make window insensitive
		#self.idle_add(self.vgmanage_window.set_sensitive, False)

		# Refresh
		#self.refresh_manual(noclear=True)
		
		# Make window sensitive
		#self.idle_add(self.vgmanage_window.set_sensitive, True)
		
		# Hide window
		self.vgmanage_window.hide()
		
		# Calling post_vgmanage_population()
		self.idle_add(self.post_vgmanage_population)
	
	def post_vgmanage_population(self):
		""" Do manual populate and set sensitiveness to main. """

		# Regenerate view
		self.manual_populate()

		# Restore sensitivity
		self.idle_add(self.objects["parent"].main.set_sensitive, True)

	def on_vg_treeview_changed(self, obj):
		""" Called when an item on the VG treeview has been selected """
		
		# If the treeview has been changed, we have at least one
		# VG, thus needing the Edit and Remove buttons
		self.idle_add(self.vg_edit_button.set_sensitive, True)
		self.idle_add(self.vg_remove_button.set_sensitive, True)

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
	
	def on_unlock_window_button_clicked(self, obj):
		""" Called when a button on the unlock window has been clicked. """
		
		if obj == self.unlock_ok:
			# Get object
			dev = crypt.LUKSdevices[self.current_selected["value"]]
			try:
				dev.open(self.unlock_entry.get_text())
				self.set_header("info", _("Manual partitioning"), _("Powerful tools for powerful pepole."), appicon="drive-harddisk")
			except CmdError:
				# Failed :(
				self.set_header("error", _("Unable to unlock the volume."), _("You inserted the wrong password."))
			
			lvm.refresh()
			self.idle_add(self.manual_populate)

		# Restore sensitivity
		self.objects["parent"].main.set_sensitive(True)		
		self.idle_add(self.unlock_window.hide)
	
	def on_lvm_apply_window_button_clicked(self, obj):
		""" Called when a button on the LVM apply window has been clicked. """
				
		if obj == self.lvm_apply_yes:
			# Yes.
			# APPLY! :)
			self.lvm_apply_window.set_sensitive(False)
			self.idle_add(self.lvm_apply)
		else:
			# Restore sensitivity
			if self.LVMrestoreto:
				self.LVMrestoreto.set_sensitive(True)
				self.LVMrestoreto = None
			else:
				self.objects["parent"].main.set_sensitive(True)
			
			# Ensure we clear out the LVMshare
			self.LVMshare = {}
		
		#self.apply_window.set_sensitive(True)
		self.idle_add(self.lvm_apply_window.hide)
			
	def manual_frame_creator(self, device, disk, on_lvm=False):
		""" Creates frames etc for the objects passed. """
		
		if not device.path in self.changed: self.changed[device.path] = {"obj":device, "changes":{}}
		
		container = {}
		container["frame_label"] = Gtk.Label()
		if on_lvm:
			_model = _("LVM Volume Group")
		else:
			_model = device.model
		container["frame_label"].set_markup("<b>%s - %s (%s GB)</b>" % (device.path, _model, round(device.getLength(unit="GB"), 2)))
		container["frame"] = Gtk.Frame()
		container["frame"].set_label_widget(container["frame_label"])
		## Create the TreeView 
		# ListStore: /dev/part - system/label - filesystem - format? - size

		#if disk != "notable": partitions = list(disk.partitions) + disk.getFreeSpacePartitions()
		if on_lvm:
			partitions = device.logicalvolumes
		elif disk != "notable":
			partitions = lib.disk_partitions(disk)

		if disk != "notable" and len(partitions) > 0:	
			container["model"] = Gtk.ListStore(str, str, str, str, bool, str, str, object)
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
				LVMcontainer = None
				if hasattr(part, "isLVM") and part.isLVM:
					LVMcontainer = part
					#part = part.partition
					
					
					path = LVMcontainer.path
				else:
					path = part.path

					# Let's see if we can reuse objects in changed to avoid nasty bugs...
					if not "-1" in path and path in self.changed and self.changed[path]["obj"]:
						part = self.changed[path]["obj"]
				
				if not path in self.changed: self.changed[path] = {"obj":part, "changes":{}, "LVMcontainer":LVMcontainer}
				if not self.changed[path]["obj"]: self.changed[path]["obj"] = part

				name = []
				if path in self.distribs:
					name.append(self.distribs[path])
				if (path in crypt.LUKSdevices or "crypt" in self.changed[path]["changes"]) and not "format" in self.changed[path]["changes"] and not ("PVcreate" in self.changed[path]["changes"] and not "crypt" in self.changed[path]["changes"]):
					name.append("Encrypted partition")
				elif name and part.name:
					name.append(part.name)
				elif not path in self.distribs:
					name.append("Normal partition")
				else:
					name.append("")
				
				if int(part.getLength("GB")) > 0:
					# We can use GigaBytes to represent partition size.
					_size = round(part.getLength("GB"), 2)
					_unit = "GB"
				elif int(part.getLength("MB")) > 0:
					# Partition is too small to be represented with gigabytes. Use megabytes instead.
					_size = round(part.getLength("MB"), 2)
					_unit = "MB"
				else:
					## Last try.. using kilobytes
					#_size = round(part.getLength("kB"), 2)
					#_unit = "kB"
					
					# Partition is too small and can be confusing. Simply do not show it.
					continue

				if path in self.changed and "PVcreate" in self.changed[path]["changes"]:
					# We need to make a LVM Physical volume...
					_fs = _("LVM physical volume")
					_to_format = True
				elif path in crypt.LUKSdevices and not crypt.LUKSdevices[path].path and not (path in self.changed and "format" in self.changed[path]["changes"]):
					# Encrypted locked partition
					_fs = _("Locked")
					_to_format = False
				elif path in self.changed and "format" in self.changed[path]["changes"]:
					# We need to format the partition, so don't use the one that parted returns to us
					_fs = self.changed[path]["changes"]["format"]
					_to_format = True
				else:
					# See what parted tells us
					if path in lvm.PhysicalVolumes or path in crypt.LUKSdevices and crypt.LUKSdevices[path].path in lvm.PhysicalVolumes:
						_fs = _("LVM physical volume")
					elif part.fileSystem == None and not part.number == -1 and not part.type == 2:
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
				
				if path in self.changed and "useas" in self.changed[path]["changes"]:
					# Set mountpoint.
					_mpoint = self.changed[path]["changes"]["useas"]
					if _mpoint == None:
						_mpoint = ""
				else:
					_mpoint = ""

				if path in self.previously_changed and (self.changed[path]["changes"] == {} or (len(self.changed[path]["changes"]) == 1 and "useas" in self.changed[path]["changes"] or "mount_on_install" in self.changed[path]["changes"]) or (len(self.changed[path]["changes"]) == 2 and "mount_on_install" in self.changed[path]["changes"]) or self.is_automatic):
					# This was changed previously, "ok" color.
					_bg = self.objects["parent"].return_color("ok")
				elif self.changed[path]["changes"] != {}:
					print "%s was changed" % path
					# This was changed now, "hold" color.
					_bg = self.objects["parent"].return_color("hold")
					
					# Also, there are some changes, so disable the next button.
					if not self.is_automatic: self.on_steps_hold()
				else:
					# No change
					_bg = None
				
				
				container[path] = container["model"].append((path, "/".join(name), _fs, _mpoint, _to_format, "%s %s" % (_size, _unit), _bg, part))
		elif len(partitions) == 0:
			container["treeview"].append_column(Gtk.TreeViewColumn(_("Informations"), Gtk.CellRendererText(), text=1, cell_background=2))
			
			# Need to add an item to say: this drive is empty!
			if on_lvm:
				txt = _("Disk empty or Virtual Group not active!")
			else:
				txt = _("Disk empty!")
			container["notable"] = container["model"].append((device.path, txt))
			container["description"] = "empty" # description.

		container["frame"].add(container["treeview"])

		return container
	
	def manual_populate(self):
		""" Populates the harddisk_container with content. """

		for child in self.harddisk_container.get_children():
			self.idle_add(child.destroy)

		# First loop create the lvm frames
		for name, obj in lvm.VolumeGroups.items():
			
			if not obj.infos["exists"]: continue
			
			self.manual_devices[obj.path] = self.manual_frame_creator(obj, None, on_lvm=True)
			if "description" in self.manual_devices[obj.path]:
				self.treeview_description[self.manual_devices[obj.path]["treeview"]] = self.manual_devices[obj.path]["description"]
			else:
				self.treeview_description[self.manual_devices[obj.path]["treeview"]] = None
			self.idle_add(self.harddisk_container.pack_start, self.manual_devices[obj.path]["frame"], True, True, True)

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
		self.idle_add(self.lock_button.set_sensitive, False)
		self.idle_add(self.newtable_button.set_sensitive, False)
		self.idle_add(self.delete_button.set_sensitive, False)

	def vgmanage_window_populate(self):
		""" Populate the vgmanage window. """
		
		self.vg_store.clear()
		
		# Loop through VGs...
		for vg_name, pvs in lvm.return_vg_with_pvs().items():
			if vg_name == None: continue
			pvs_list = []
			for pv in pvs:
				pvs_list.append(pv["volume"].pv)
			self.vg_store.append((vg_name, "\n".join(pvs_list)))
		
		# Disable Edit and Remove buttons
		self.idle_add(self.vg_edit_button.set_sensitive, False)
		self.idle_add(self.vg_remove_button.set_sensitive, False)
		
		self.idle_add(self.vgmanage_window.set_sensitive, True)

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
	
	def on_lock_button_clicked(self, caller):
		""" Called when the Lock/Unlock partition has been clicked. """
		
		device = crypt.LUKSdevices[self.current_selected["value"]]
		
		if device.path:
			# Unlocked, lock
			device.close()
			lvm.refresh()
			self.idle_add(self.manual_populate)
		else:
			self.idle_add(self.objects["parent"].main.set_sensitive, False)
			self.idle_add(self.unlock_entry.set_text, "")
			self.idle_add(self.unlock_entry.grab_focus)
			self.idle_add(self.unlock_window.show)
		
	
	def on_advanced_clicked(self, caller):
		""" Shows advanced options if caller is the 'Advanced options' button.
		Otherwise it hides them. """
				
		if caller == self.advanced_button:
			# Hide add, remove, edit, advanced, coso_che_separa, refresh, apply
			self.idle_add(self.add_button.hide)
			self.idle_add(self.remove_button.hide)
			self.idle_add(self.edit_button.hide)
			#self.idle_add(self.toolbar_separator.hide)
			self.idle_add(self.lock_button.hide)
			self.idle_add(self.advanced_button.hide)
			self.idle_add(self.coso_che_separa.hide)
			self.idle_add(self.refresh_button.hide)
			self.idle_add(self.apply_button.hide)

			# Show back, newtable, delete, vgmanage
			self.idle_add(self.back_to_normal_button.show)
			self.idle_add(self.newtable_button.show)
			self.idle_add(self.delete_button.show)
			self.idle_add(self.vgmanage_button.show)
		elif caller == self.back_to_normal_button:
			# Show add, remove, edit, advanced, coso_che_separa, refresh, apply
			self.idle_add(self.add_button.show)
			self.idle_add(self.remove_button.show)
			self.idle_add(self.edit_button.show)
			#self.idle_add(self.toolbar_separator.show)
			self.idle_add(self.lock_button.show)
			self.idle_add(self.advanced_button.show)
			self.idle_add(self.coso_che_separa.show)
			self.idle_add(self.refresh_button.show)
			self.idle_add(self.apply_button.show)
			
			# Hide back, newtable, delete, vgmanage
			self.idle_add(self.back_to_normal_button.hide)
			self.idle_add(self.newtable_button.hide)
			self.idle_add(self.delete_button.hide)
			self.idle_add(self.vgmanage_button.hide)

	
	def manual_ready(self, clean=True):
		""" Called when the manual window is ready. """
		
		self.mount_on_install_prepare = False
		
		self.has_swap_warning_showed = False
		
		self.current_selected = None
		
		self.is_add = None
		
		self.LVMshare = {}
		
		self.LVname = ""
		self.VGname = ""
		
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
		self.vg_manage_ok_id = None
		self.vg_manage_cancel_id = None
		
		# The following is used to tell the LVM_apply class what window
		# Should it make sensitive after doing things.
		# If None, the main installer window will be set as sensitive.
		# Otherwise, the Gtk.Window object into the variable will be touched.
		# Please note that the variable will be reset everytime to None.
		self.LVMrestoreto = None

		if self.is_module_virgin or not ("changed" in self.settings and self.settings["changed"]):
			self.set_header("info", _("Manual partitioning"), _("Powerful tools for powerful pepole."), appicon="drive-harddisk")
		else:
			self.set_header("ok", _("You can continue!"), _("Press the Apply button and then Forward to continue."))
		
		# Get windows
		self.partition_window = self.objects["builder"].get_object("partition_window")
		self.newtable_window = self.objects["builder"].get_object("newtable_window")
		self.mount_on_install_window = self.objects["builder"].get_object("mount_on_install_window")
		self.remove_window = self.objects["builder"].get_object("remove_window")
		self.delete_window = self.objects["builder"].get_object("delete_window")
		self.apply_window = self.objects["builder"].get_object("apply_window")
		self.lvm_apply_window = self.objects["builder"].get_object("lvm_apply_window")
		self.unlock_window = self.objects["builder"].get_object("unlock_window")
		self.vgmanage_window = self.objects["builder"].get_object("vgmanage_window")
		self.vgmanage_manage_window = self.objects["builder"].get_object("vgmanage_manage_window")
		
		## Partition window:
		self.partition_window.connect("delete_event", self.child_window_delete)
		self.lv_frame = self.objects["builder"].get_object("lv_frame")
		self.lv_name = self.objects["builder"].get_object("lv_name")
		self.size_frame = self.objects["builder"].get_object("size_frame")
		self.size_manual_radio = self.objects["builder"].get_object("size_manual_radio")
		self.size_adjustment = self.objects["builder"].get_object("size_adjustment")
		self.size_manual_entry = self.objects["builder"].get_object("size_manual_entry")
		self.size_scale_radio = self.objects["builder"].get_object("size_scale_radio")
		self.size_scale_scale = self.objects["builder"].get_object("size_scale_scale")
		self.format_box = self.objects["builder"].get_object("format_box")
		self.lvm_box = self.objects["builder"].get_object("lvm_box")
		self.crypting_box = self.objects["builder"].get_object("crypting_box")
		self.crypting_password_alignment = self.objects["builder"].get_object("crypting_password_alignment")
		self.crypting_password = self.objects["builder"].get_object("crypting_password")
		self.crypting_password_confirm = self.objects["builder"].get_object("crypting_password_confirm")
		self.crypting_random = self.objects["builder"].get_object("crypting_random")
		self.crypting_random_hq = self.objects["builder"].get_object("crypting_random_hq")
		self.do_not_format_box = self.objects["builder"].get_object("do_not_format_box")
		self.PVwarning = self.objects["builder"].get_object("PVwarning")
		# Hold color in PVwarning
		col = Gdk.RGBA()
		col.parse(self.objects["parent"].return_color("hold"))
		self.PVwarning.override_background_color(0, col)
		# ---
		self.filesystem_combo = self.objects["builder"].get_object("filesystem_combo")
		self.mountpoint_frame = self.objects["builder"].get_object("mountpoint_frame")
		self.mountpoint_combo = self.objects["builder"].get_object("mountpoint_combo")
		self.mountpoint_entry = self.objects["builder"].get_object("mountpoint_entry")
		self.mount_on_install = self.objects["builder"].get_object("mount_on_install")
		self.partition_cancel = self.objects["builder"].get_object("partition_cancel")
		self.partition_ok = self.objects["builder"].get_object("partition_ok")
		
		# Connect the logical volume name textbox...
		self.lv_name.connect("changed", self.on_lv_name_change)
		
		# Connect the radios...
		self.size_manual_radio.connect("toggled", self.on_manual_radio_changed)
		self.size_scale_radio.connect("toggled", self.on_manual_radio_changed)
		
		# Connect format box
		self.format_box.connect("toggled", self.on_formatbox_change)
		self.lvm_box.connect("toggled", self.on_formatbox_change)
		self.crypting_box.connect("toggled", self.on_formatbox_change)
		self.do_not_format_box.connect("toggled", self.on_formatbox_change)
		
		self.crypting_password.connect("changed", self.on_crypting_password_changed)
		self.crypting_password_confirm.connect("changed", self.on_crypting_password_changed)

		# Also connect the crypt checkboxes where they belong
		self.crypting_random.connect("toggled", self.on_crypting_random_toggled)
		
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
		
		# Connect mount_on_install
		self.mount_on_install.connect("clicked", self.on_mount_on_install_changed)

				
		## Newtable window:
		self.newtable_window.connect("delete_event", self.child_window_delete)
		self.newtable_no = self.objects["builder"].get_object("newtable_no")
		self.newtable_yes = self.objects["builder"].get_object("newtable_yes")
		self.newtable_no.connect("clicked", self.on_newtable_window_button_clicked)
		self.newtable_yes.connect("clicked", self.on_newtable_window_button_clicked)
		
		## Mount_on_install window
		self.mount_on_install_window.connect("delete_event", self.child_window_delete)
		self.mount_on_install_no = self.objects["builder"].get_object("mount_on_install_no")
		self.mount_on_install_yes = self.objects["builder"].get_object("mount_on_install_yes")
		self.mount_on_install_no.connect("clicked", self.on_mount_on_install_window_button_clicked)
		self.mount_on_install_yes.connect("clicked", self.on_mount_on_install_window_button_clicked)

		## Remove window:
		self.remove_window.connect("delete_event", self.child_window_delete)
		self.remove_no = self.objects["builder"].get_object("remove_no")
		self.remove_yes = self.objects["builder"].get_object("remove_yes")
		self.remove_no.connect("clicked", self.on_remove_window_button_clicked)
		self.remove_yes.connect("clicked", self.on_remove_window_button_clicked)

		## Delete window:
		self.delete_window.connect("delete_event", self.child_window_delete)
		self.delete_no = self.objects["builder"].get_object("delete_no")
		self.delete_yes = self.objects["builder"].get_object("delete_yes")
		self.delete_no.connect("clicked", self.on_delete_window_button_clicked)
		self.delete_yes.connect("clicked", self.on_delete_window_button_clicked)

		## Apply window:
		self.apply_window.connect("delete_event", self.child_window_delete)
		self.apply_no = self.objects["builder"].get_object("apply_no")
		self.apply_yes = self.objects["builder"].get_object("apply_yes")
		self.apply_no.connect("clicked", self.on_apply_window_button_clicked)
		self.apply_yes.connect("clicked", self.on_apply_window_button_clicked)

		## LVM Apply window:
		self.lvm_apply_window.connect("delete_event", self.child_window_delete)
		self.lvm_apply_no = self.objects["builder"].get_object("lvm_apply_no")
		self.lvm_apply_yes = self.objects["builder"].get_object("lvm_apply_yes")
		self.lvm_apply_no.connect("clicked", self.on_lvm_apply_window_button_clicked)
		self.lvm_apply_yes.connect("clicked", self.on_lvm_apply_window_button_clicked)

		## Unlock window:
		self.unlock_window.connect("delete_event", self.child_window_delete)
		self.unlock_entry = self.objects["builder"].get_object("unlock_entry")
		self.unlock_ok = self.objects["builder"].get_object("unlock_ok")
		self.unlock_cancel = self.objects["builder"].get_object("unlock_cancel")
		self.unlock_ok.connect("clicked", self.on_unlock_window_button_clicked)
		self.unlock_cancel.connect("clicked", self.on_unlock_window_button_clicked)

		## Manage LVM Volume Groups window
		self.vgmanage_window.connect("delete_event", self.child_window_delete)
		self.vg_scrolledwindow = self.objects["builder"].get_object("vg_scrolledwindow")
		self.vg_add_button = self.objects["builder"].get_object("vg_add_button")
		self.vg_edit_button = self.objects["builder"].get_object("vg_edit_button")
		self.vg_remove_button = self.objects["builder"].get_object("vg_remove_button")
		self.vg_close_button = self.objects["builder"].get_object("vg_close")
		self.vg_add_button.connect("clicked", self.on_vgmanage_add_clicked)
		self.vg_edit_button.connect("clicked", self.on_vgmanage_edit_clicked)
		self.vg_remove_button.connect("clicked", self.on_vgmanage_remove_clicked)
		self.vg_close_button.connect("clicked", self.on_vgmanage_window_button_clicked)

		# Populate now the vgmanage window
		self.vg_store = Gtk.ListStore(str, str)
		self.vg_treeview = Gtk.TreeView(self.vg_store)
		self.vg_treeview.append_column(Gtk.TreeViewColumn(_("Name"), Gtk.CellRendererText(), text=0))
		self.vg_treeview.append_column(Gtk.TreeViewColumn(_("Physical Volumes"), Gtk.CellRendererText(), text=1))
		self.vg_treeview.show()
		self.vg_treeview.connect("cursor-changed", self.on_vg_treeview_changed)
		
		# Add the treeview to the scrolledwindow
		self.vg_scrolledwindow.add(self.vg_treeview)
		
		## VGmanage - Manage window
		self.vgmanage_manage_window.connect("delete_event", self.child_window_delete, self.vgmanage_window)
		self.vg_manage_ok = self.objects["builder"].get_object("vg_manage_ok")
		self.vg_manage_cancel = self.objects["builder"].get_object("vg_manage_cancel")
		self.vg_manage_entry = self.objects["builder"].get_object("vg_manage_entry")
		self.vg_manage_entry.connect("changed", self.on_vg_manage_entry_changed)
		self.vg_manage_editlabel = self.objects["builder"].get_object("vg_manage_editlabel")
		self.vg_manage_viewport = self.objects["builder"].get_object("vg_manage_viewport")

		# Get toolbar buttons
		self.manual_toolbar = self.objects["builder"].get_object("manual_toolbar")
		self.add_button = self.objects["builder"].get_object("add_button")
		self.remove_button = self.objects["builder"].get_object("remove_button")
		self.edit_button = self.objects["builder"].get_object("edit_button")
		self.toolbar_separator = self.objects["builder"].get_object("toolbar_separator")
		self.lock_button = self.objects["builder"].get_object("lock_button")
		self.advanced_button = self.objects["builder"].get_object("advanced_button")
		self.back_to_normal_button = self.objects["builder"].get_object("back_to_normal_button")
		self.newtable_button = self.objects["builder"].get_object("newtable_button")
		self.delete_button = self.objects["builder"].get_object("delete_button")
		self.vgmanage_button = self.objects["builder"].get_object("vgmanage_button")
		self.coso_che_separa = self.objects["builder"].get_object("coso_che_separa")
		self.refresh_button = self.objects["builder"].get_object("refresh_button")
		self.apply_button = self.objects["builder"].get_object("apply_button")

		# Connect them
		self.add_button.connect("clicked", self.on_add_button_clicked)
		self.edit_button.connect("clicked", self.on_edit_button_clicked)
		self.newtable_button.connect("clicked", self.on_newtable_button_clicked)
		self.remove_button.connect("clicked", self.on_remove_button_clicked)
		self.lock_button.connect("clicked", self.on_lock_button_clicked)
		self.advanced_button.connect("clicked", self.on_advanced_clicked)
		self.back_to_normal_button.connect("clicked", self.on_advanced_clicked)
		self.delete_button.connect("clicked", self.on_delete_button_clicked)
		self.vgmanage_button.connect("clicked", self.on_vgmanage_button_clicked)
		self.refresh_button.connect("clicked", self.refresh_manual)
		self.apply_button.connect("clicked", self.on_apply_button_clicked)
		
		# Trigger advanced buttons hiding by calling on_advanced_clicked
		self.on_advanced_clicked(self.back_to_normal_button)
		
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
		
		self.set_header("info", _("Disk partitioning"), _("Manage your drives"), appicon="drive-harddisk")
		
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
			
			# Check for /boot if / is on an encrypted partition...
			if len(self.mountpoints_added["/"].split("/")) > 3:
				# Root is on a LVM VG.
				vg = os.path.basename(os.path.dirname(self.mountpoints_added["/"]))
				# Check if at least one PV composing the VG is encrypted
				for pv in lvm.return_vg_with_pvs()[vg]:
					for encrypted in crypt.LUKSdevices:
						if pv["volume"].pv == crypt.LUKSdevices[encrypted].mapper_path and not "/boot" in self.mountpoints_added:
							# Yeah
							self.set_header("error", _("You can't continue!"), _("The root partition is on an encrypted device. You need a separated /boot partition on a non-encrypted device."))
							return True
			
			# Do the same for /boot
			if "/boot" in self.mountpoints_added and len(self.mountpoints_added["/boot"].split("/")) > 3:
				# /boot is on a LVM VG.
				vg = os.path.basename(os.path.dirname(self.mountpoints_added["/"]))
				# Check if at least one PV composing the VG is encrypted
				for pv in lvm.return_vg_with_pvs()[vg]:
					for encrypted in crypt.LUKSdevices:
						if pv["volume"].pv == crypt.LUKSdevices[encrypted].mapper_path:
							# Yeah
							self.set_header("error", _("You can't continue!"), _("The /boot partition should not be on an encrypted device."))
							return True
			
			# If in UEFI mode, ensure /boot/efi is selected
			part = lib.return_partition(self.mountpoints_added["/"])
			if not part:
				# We can guess this is an LVM volume group
				part = "gpt"
			else:
				# No LVM VG, get the disk table
				part = part.disk.type
			if "uefidetect.inst" in self.moduleclass.modules_settings and self.moduleclass.modules_settings["uefidetect.inst"]["uefi"] == True and not part == "msdos":
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
		
