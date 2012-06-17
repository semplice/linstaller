# -*- coding: utf-8 -*-
# linstaller glade frontend - (C) 2012 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a frontend of linstaller, should not be executed as a standalone application.

from gi.repository import Gtk, Gdk, GObject

import linstaller.core.main as m
from linstaller.core.main import warn,info,verbose

import linstaller.core.frontend

import time

import t9n.library
_ = t9n.library.translation_init("linstaller")

class Frontend(linstaller.core.frontend.Frontend):
	def __init__(self, moduleclass):

		linstaller.core.frontend.Frontend.__init__(self, moduleclass)

		self.is_module_virgin = True

		self.objects = None
		self.steps = None
		
		# idle_add function
		self.idle_add = GObject.idle_add
		
		# As this frontend handle previous/next modules, we need to not overwrite user-selected items with seeds when jumping from a module to another.
		# Thus, we need to continue writing to self.modules_settings[module] if it exists.
		_mod = moduleclass.package.replace("linstaller.modules.","")
		if _mod.split(".")[-1] == "front":
			_mod = _mod.split(".")
			del _mod[-1]
			_mod = ".".join(_mod)
		if _mod in moduleclass.modules_settings and not "_preexecuted" in moduleclass.modules_settings[_mod]:
			self.settings = moduleclass.modules_settings[_mod]
			self.is_module_virgin = False
	
	def change_entry_status(self, obj, status, tooltip=None):
		""" Changes entry secondary icon for object. """
		
		self.idle_add(self.objects["parent"].change_entry_status, obj, status, tooltip)
	
	def steps_init(self, okmessage={"title":_("You can continue!"), "message":_("Press forward to continue.")}, holdmessage={"title":_("Please complete all forms."), "message":_("You need to complete the following forms:")}, errormessage={"title":_("Please fix these errors before continuing."), "message":"You need to fix these errors before continuing:"}):
		""" Initiate steps. """
		
		self.steps = []
		self.steps_fail = {}
		self.steps_index = {}
		self.steps_ok = okmessage
		self.steps_hold = holdmessage
		self.steps_error = errormessage
	
	def steps_set_index(self, index):
		""" Declares the step index. """
		
		self.steps_index = index
	
	def steps_check(self):
		""" Checks for steps on hold. """

		if self.steps_fail != {}:
			# There are some errors, handle only them
			errors = []
			for step, description in self.steps_fail.items():
				errors.append(" - " + description)
			self.set_header("error", self.steps_error["title"], self.steps_error["message"] + "\n" + "\n".join(errors))
			self.on_steps_fail()
			return

		onhold = []
		for step, description in self.steps_index.items():
			if not step in self.steps:
				# The step is not on the list of completed steps. Put the thing on hold.
				onhold.append(" - " + description)
		
		if onhold == []:
			# onhold is empty, so we can continue!
			self.set_header("ok", self.steps_ok["title"], self.steps_ok["message"])
			self.on_steps_ok()
		else:
			# onhold is not empty, putting everything on hold!
			self.set_header("hold", self.steps_hold["title"], self.steps_hold["message"] + "\n" + "\n".join(onhold))
			self.on_steps_hold()

	def steps_completed(self, step):
		""" Adds to self.steps the completed step. """
		
		if not step in self.steps:
			self.steps.append(step)
		self.steps_failed_remove(step)
	
	def steps_uncompleted(self, step):
		""" Removes from self.steps the uncompleted step """
		
		if step in self.steps:
			self.steps.remove(step)
		self.steps_failed_remove(step)
	
	def steps_failed(self, step, message):
		""" Adds step to the index_fail """
	
		self.steps_fail[step] = message
		self.steps_check()
	
	def steps_add(self, step, message):
		""" Adds step to the index """
		
		self.steps_index[step] = message
		self.steps_check()
	
	def steps_remove(self, step):
		""" Removes step from the index """
		
		if step in self.steps_index:
			del self.steps_index[step]
		
		self.steps_check()
	
	def steps_failed_remove(self, step):
		""" Removes step from the index_fail """
		
		if step in self.steps_fail:
			del self.steps_fail[step]
		self.steps_check()
	
	def on_steps_ok(self):
		""" Called when all steps are completed. """
		
		# Set next button sensitivity to True
		self.idle_add(self.objects["parent"].next_button.set_sensitive, True)
	
	def on_steps_hold(self):
		""" Called when some steps are on hold. """
		
		# Set next button sensitivity to False
		self.idle_add(self.objects["parent"].next_button.set_sensitive, False)
	
	def on_steps_fail(self):
		""" Called when some steps are failed. """
		
		# Set next button sensitivity to False
		self.idle_add(self.objects["parent"].next_button.set_sensitive, False)

	def on_objects_ready(self):
		""" Called when the module objects are ready. """
				
		# Set next button sensitivity to True
		self.idle_add(self.objects["parent"].next_button.set_sensitive, True)

	def start(self):
		""" This function, the one that other frontends normally override, will only wait.
		The glade service, which MUST be awake and alive, will handle everything.
		
		Developers should override the ready() function. """
		
		while self.res == False:
			time.sleep(0.3)
		
		print("res changed! it's now %s" % self.res)
		return self.res
	
	def set_header(self, icon, title, subtitle):
		""" Sets header. """
		
		self.idle_add(self.objects["parent"].set_header, icon, title, subtitle)
	
	def hide(self, obj):
		""" Hides the selected object.
		Use this method instead of the stock hide on the object to avoid hangs and freezes. """
		
		self.idle_add(obj.hide)
	
	#def module_casper(self, obj):
	#	""" Return casper, but before change page. """
	#	
	#	
	
	def ready(self):
		""" Ovveride this function to manage frontend objects (declared onto the self.objects dictionary). """
		
		pass
