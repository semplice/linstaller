# -*- coding: utf-8 -*-
# linstaller core config library - (C) 2011 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import os

import linstaller.core.main as m
try:
	import ConfigParser as cparser # Python 2.x
except:
	import configparser as cparser # Python 3.x

configpath = "/etc/linstaller"

class Config:
	def __init__(self, file, initial=False, frontend=None):
		""" This class will read a configfile. /etc/pylaivng is already inserted, so for file you only need to pass subdirectory and file, for example distributions/semplice. """
		
		self.configpath = configpath
		
		self.is_fork = False # at least for now.
		self.is_frontend = False # at least for now.
		
		self.path = os.path.join(self.configpath,file)
		if os.path.islink(self.path):
			# Is a link, read it.
			self.path = os.readlink(self.path)
		self.initial = initial
		if not os.path.exists(self.path):
			raise m.UserError(self.path + " does not exist!")
		
		if os.path.exists("%s.%s" % (self.path, frontend)):
			# Handle configuration file per-frontend, if it exist.
			# It is basically a fork config without the linstaller:extends section, which we will add.
			self.path = "%s.%s" % (self.path, frontend)
			self.is_frontend = True
		
		# Open the file, if it is initial just open it in ram...
		self.config = cparser.SafeConfigParser()
		if not initial: self.config.read(self.path)
		
		if self.is_frontend:
			# it is frontend ;) Add the linstaller:extends
			if not self.has_section("linstaller:extends"):
				self.add("linstaller:extends")
			self.set("linstaller:extends", "source", file)
			
			# For now on, treat it as a normal fork :)
		
		# Should check if it is a fork
		if self.has_section("linstaller:extends"):
			# The fork section is there...
			if self.has_option("linstaller:extends","source"):
				# Ok, the source option is there. We should get it and load the source configuration file, too.
				self.source = str(self.get("linstaller:extends","source"))
				
				# Yes! this is a fork
				self.is_fork = True
				
				# Load source
				self.config_source = cparser.SafeConfigParser()
				self.config_source.read(os.path.join(self.configpath,self.source))
				
				self._fork_merge_refactored(self.config_source, self.config)
	
	def _fork_merge_refactored(self, source, fork):
		""" Merges sources into fork """

		# Remove pylaivng:fork section
		fork.remove_section("linstaller:extends")

		# We should use configparser's internal defs, instead of ours, as we default to self.config.
		sections = source.sections() # get all sections of source.
		
		for sect in sections:
			# Section exists?
			if not fork.has_section(sect):
				# no. so add it
				fork.add_section(sect)
			
			# Insert all options (but not overwrite)
			options = source.options(sect)
			for opt in options:
				if not fork.has_option(sect, opt):
					fork.set(sect, opt, source.get(sect, opt))
				else:
					# Get fork option to see if it has <old>
					new = fork.get(sect, opt)
					if "<old>" in new:
						# Ok, get source option and set anyway
						fork.set(sect, opt, new.replace("<old>",source.get(sect,opt)))
		
		# If there is another pylaivng:fork section, It has been added from source.
		# So this is a fork of a fork. Or a fork of a fork of a fork.
		# Or a fork of a fork of a fork of a fork
		# Or... boring.
		
		if fork.has_section("linstaller:extends"):
			if fork.has_option("linstaller:extends","source"):
				src = str(fork.get("linstaller:extends","source"))
								
				# Load new source
				src_file = cparser.SafeConfigParser()
				src_file.read(os.path.join(self.configpath,src))
				
				# Run another instance of _fork_merge_refactored
				self._fork_merge_refactored(src_file, fork)
		else:
			# We can continue and check for the items to remove
			_sections = fork.sections()
			for _sect in _sections:
				_options = fork.options(_sect)
				for opt in _options:
					# Split all items
					_items = fork.get(_sect,opt).split(" ")
					for _itm in _items:
						if "<remove:" in _itm:
							# Set the option without this <remove:> and the item it removes...
							fork.set(_sect, opt, fork.get(_sect,opt).replace(_itm,"").replace(_itm[8:-1],""))

	def has_section(self, section):
		""" This function will check if section 'section' is present into the config file. """
		return self.config.has_section(section)
	
	def has_option(self, section, option):
		""" This function will check if option is present into the section 'section' into the config file."""
		return self.config.has_option(section, option)
	
	def get(self, section, thing):
		""" This function will get a value from the configfile. """
		return self.config.get(section, thing)
	
	def add(self, section):
		""" This function will add a section in the configfile. """
		self.config.add_section(section)
	
	def set(self, section, thing, value):
		""" This function will set a value in the configfile. """
		self.config.set(section, thing, value)					
	
	def __del__(self):
		""" Cleanup """
		del self.config

class ConfigRead(Config):
	""" Simple class to read config files. """
	def __init__(self, file, module=False, initial=False, frontend=None):
		
		Config.__init__(self, file, initial, frontend)
		self.module = module # Module ("section") name.
	
	def printv(self, opt, section=False):
		""" This function will get the requested value from section. """
		
		# If section = false, copy the default self.module, if any
		if not section:
			section = self.module
		
		if self.has_option(section, opt):
			value = self.get(section, opt)
			if value.lower() == "true":
				return True
			elif value.lower() == "false":
				return False
			elif value.lower() == "none":
				return None
			else:
				return value
		else:
			return False
