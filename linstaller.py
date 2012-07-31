#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
# linstaller main executable - (C) 2011 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#

import linstaller.core.main as m
import linstaller.core.config as config
import linstaller.core.modulehelper as mh
import linstaller.core.servicehelper as sh
from linstaller.core.main import warn, info, verbose

import exceptions

import t9n.library
_ = t9n.library.translation_init("linstaller")

import os, sys

import time

lastres = None

def close_services():
	for service, obj in service_started.items():
		obj.close()

def modulechange_services(module):
	for service, obj in service_started.items():
		obj.do_module_change(module)

def caspered_services(status):
	for service, obj in service_started.items():
		obj.do_caspered(status)

def launch_module(module, special):
	""" Launches module.
	special is a list that contains all the 'special' modules.
	"""

	global reboot
	
	mname = module.split(".")
	# Check if the module is front or inst... (if not, leave everything as-is)
	if mname[-1] in ("front", "inst"):
		del mname[-1] # Remove. Useless.
	mname = ".".join(mname)
	
	# Adjust cfg.module to read "module:<modulename>"
	cfg.module = "module:%s" % mname

	# Start module
	try:
		# Load module...
		mod = mh.Module(module)
		modclass = mod.load(main_settings, modules_settings, service_started, cfg)
		
		# It is special? Add to executed_special.
		if module in special:
			executed_special.append(module)

		modulechange_services(modclass)
		res = modclass.start()		
	except exceptions.SystemExit:
		return "exit"
	except:
		# Something nasty happened.
		# We should revert any 'special' changes (mounts, etc).
		
		verbose("Something nasty happened. Reverting special changes.")
		
		executed_special.reverse() # Reverse.
		for modu in executed_special:
			verbose("Reverting %s" % modu)
			_revert = mh.Module(modu)
			_revertc = _revert.load(main_settings, modules_settings, service_started, cfg)
			
			# Revert
			_revertc.revert()
		
		# close services
		close_services()
		
		# Now raise the original exception	
		print sys.exc_info()[0]
		raise
		
	# Update modules_settings
	if not module.split(".")[-1] == "inst":
		# Frontend. Add only the module name
		modules_settings[mname] = modclass.return_settings()
	else:
		# .inst module. Add it anyway, but with ".inst"
		modules_settings[module] = modclass.return_settings()

	if res == "restart":
		# restart module.
		return launch_module(module, special)
	elif res == "kthxbye":
		# Reboot
		return "kthxbye"
	elif res == "fullrestart":
		# restart linstaller
		return "fullrestart"
	elif res == "back":
		# go back.
		return "back"
	elif res == "casper":
		# execute last res
		return "casper"

def loop_modules(startfrom=1):
	""" Loop modules.
	
	If startfrom is used, the loop will start at that specific module. (int)
	"""

	global lastres

	if startfrom < 1:
		startfrom = 1

	count = 0
	
	for module in main_settings["modules"].split(" "):
		if module and module not in _removemodules:
			count += 1
			if count < startfrom: continue
			res = launch_module(module, main_settings["special"].split(" "))
			if res == "casper":
				
				# We should trigger the on_caspered signal to services, just in case..
				caspered_services(lastres)
				
				res = lastres
			else:
				lastres = res
			
			if res in ("exit", "kthxbye", "fullrestart"):
				return res # Exit.
			elif res == "back":
				print "going back"
				return loop_modules(startfrom=count-1)

## Welcome to linstaller :)
## This is the main executable, and should be called with something like this:
##  linstaller --config=<configuration> start
## where <configuration> should be a configuration file in /etc/linstaller (without path).
## if --config is omitted, will be used "default" by default.

verbose("started linstaller - version %s" % m.VERSION)

_action = False
_config = "default"
_frontend = "cli"
_modules = False
#_services = ["sample", "glade"]
_services = False
_removemodules = []

preseeds = {}

# Parse arguments
for arg in sys.argv:
	# Split = arguments
	arg = arg.split("=")
	if arg[0] in ("--config","-c"):
		# Require second argument
		if len(arg) < 2: raise m.UserError("--config requires an argument!")
		_config = arg[1]
	elif arg[0] in ("--frontend","-f"):
		# Require second argument
		if len(arg) < 2: raise m.UserError("--frontend requires an argument!")
		_frontend = arg[1]
	elif arg[0] in ("--modules","-m"):
		# Require second argument
		if len(arg) < 2: raise m.UserError("--modules requires an argument!")
		_modules = arg[1]
	elif arg[0] in ("--services","-s"):
		# Require second argument
		if len(arg) < 2: raise m.UserError("--services requires an argument!")
		_services = arg[1].split(" ")
	elif arg[0] in ("--remove","-r"):
		# Require second argument
		if len(arg) < 2: raise m.UserError("--remove requires an argument!")
		_removemodules = arg[1].split(" ")
	elif arg[0] == "help":
		_action = "help"
	elif arg[0] == "start":
		_action = "start"
	elif arg[0][0] == ":":
		# Preseed.
		__module, __option, __value = arg[0].split(":")[1:] # Get seed
		
		if not __module in preseeds:
			# Create a new dictionary
			preseeds[__module] = {}
		
		# Add the seed
		preseeds[__module][__option] = __value

if not _action:
	print _("You have to pass at least an action!")
	_action = "help"

if _action == "help":
	print _("SYNTAX: %s <options> [ACTION] <:seed:option:value>") % sys.argv[0]
	print
	print _("Recognized options:")
	print _(" -c|--config		- Selects the configuration file to read")
	print _(" -f|--frontend		- Selects the frontend to use (def: cli)")
	print _(" -m|--modules		- Overrides the modules to be executed")
	print _(" -s|--services		- Overrides the services to be executed")
	print _(" -r|--remove		- Removes the specified modules from the modules list")
	print
	print _("Recognized actions:")
	print _(" help			- Displays this help message, then exits.")
	print _(" start			- Starts the installer.")
	print
	print _("Preseeding:")
	print _(""" linstaller supports preseeding. Seeds can be specified into the
 configuration file of the distribution, or with the notation below:
 
 :module:option:value
 
 Examples:
 
 :userhost:root:True		- Enables root
 :language:ask:True		- Asks for language
 :partdisks:swap_noformat:True	- Does not format swap partition
""")

	sys.exit(0)
elif _action == "start":	
	if not os.path.join(config.configpath, _config):
		raise m.UserError(_("%s does not exist! Adjust --config accordingly." % _config))
	else:
		verbose("Selected configuration file: %s" % _config)
	
	# Ohhh yay :) This action that will actually start the installer and its appropriate frontend.
	
	# Create target directory
	if not os.path.exists("/linstaller/target"):
		os.makedirs("/linstaller/target")
	
	# Load configuration file
	cfg = config.ConfigRead(_config, "linstaller")
		
	# Populate main_settings
	main_settings = {}
	main_settings["frontend"] = _frontend
	main_settings["distro"] = cfg.printv("distribution")
	if not _modules:
		main_settings["modules"] = cfg.printv("modules")
	else:
		# Modules specified via --modules option
		main_settings["modules"] = _modules
	if not _services:
		main_settings["services"] = cfg.printv("services")
		if main_settings["services"]:
			main_settings["services"].split(" ")
		else:
			main_settings["services"] = []
	else:
		# Modules specified via --modules option
		main_settings["services"] = _services # _services are already splitted.
	main_settings["special"] = cfg.printv("special")
	
	# If the frontend is glade, autostart the glade service.
	if main_settings["frontend"] == "glade" and "glade" not in main_settings["services"]:
		main_settings["services"].append("glade")
	
	verbose("Frontend: %s" % main_settings["frontend"])
	verbose("Distro: %s" % main_settings["distro"])
	verbose("Modules: %s" % main_settings["modules"])
	verbose("Services: %s" % " ".join(main_settings["services"]))
	
	# Create modules_settings
	modules_settings = {}

	# Merge the seeds eventually specified
	for module, seeds in preseeds.items():
		# Add section, if not-existent
		if not cfg.has_section("module:%s" % module):
			cfg.add("module:%s" % module)
		
		# Set option, value:
		for option, value in seeds.items():
			verbose("Setting %(option)s = %(value)s in %(module)s" % {"option":option, "value":value, "module":module})
			cfg.set("module:%s" % module, option, value)
			
		# Fill modules settings too, will be overriden by the frontend if the module runs.
		modules_settings[module] = seeds
		modules_settings[module]["_preexecuted"] = True # The module has only been PREexecuted, not executed. It will be removed when the module runs.

	# Start services
	service_started = {} # started services
	service_space = {} # services share space
	if main_settings["services"]:
		for service in main_settings["services"]:
			srv = sh.Service(service)
			srvclass = srv.load(main_settings, service_space, cfg)
			
			# Start.
			srvclass.start()
			while srvclass.is_ready == False:
				time.sleep(0.1) # Wait until the service is ready
			
			service_started[service] = srvclass

	# 'special' modules executed
	executed_special = []
	
	# Begin loop modules...
	res = loop_modules()

	# Finished installation. Revert changes made to the system.
	executed_special.reverse() # Reverse.
	for modu in executed_special:
		verbose("Reverting %s" % modu)
		_revert = mh.Module(modu)
		_revertc = _revert.load(main_settings, modules_settings, service_started, cfg)
		
		# Revert
		_revertc.revert()
	
	# close services
	close_services()
	
	if res == "kthxbye":
		# We should reboot?
		verbose("KTHXBYE")
		m.sexec("reboot")
	elif res == "fullrestart":
		verbose("Doing full linstaller restart, as requested.")
		
		# Parse args
		args = []
		for arg in sys.argv:
			if " " in arg:
				arg = arg.replace(" ","\ ")
			args.append(arg)
		
		sys.exit(os.system(" ".join(args)))
	
	sys.exit(0)

