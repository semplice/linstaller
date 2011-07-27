#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
# linstaller main executable - (C) 2011 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#

import linstaller.core.main as m
import linstaller.core.config as config
import linstaller.core.modulehelper as mh
from linstaller.core.main import warn, info, verbose

import t9n.library
_ = t9n.library.translation_init("linstaller")

import os, sys

def launch_module(module):
	# Adjust cfg.module to read "module:<modulename>"
	cfg.module = "module:%s" % module.split(".")[0]
	
	# Load module...
	mod = mh.Module(module)
	modclass = mod.load(main_settings, modules_settings, cfg)
	
	# Start module
	res = modclass.start()

	# Update modules_settings
	modules_settings[module.split(".")[0]] = modclass.return_settings()

	if res == "restart":
		# restart module.
		return launch_module(module)


## Welcome the linstaller :)
## This is the main executable, and should be called with something like this:
##  linstaller --config=<configuration> start
## where <configuration> should be a configuration file in /etc/linstaller (without path).
## if --config is omitted, will be used "default" by default.

verbose("linstaller started - version %s" % m.VERSION)

_action = False
_config = "default"

# Parse arguments
for arg in sys.argv:
	# Split = arguments
	arg = arg.split("=")
	if arg[0] in ("--config","-c"):
		# Require second argument
		if len(arg) < 2: raise m.UserError("--config requires an argument!")
		_config = arg[1]
	elif arg[0] == "help":
		_action = "help"
	elif arg[0] == "start":
		_action = "start"

if not _action:
	print _("You need to pass at least an action!")
	_action = "help"

if _action == "help":
	print _("SYNTAX: %s <options> [ACTION]") % sys.argv[0]
	print
	print _("Recognized options:")
	print _(" -c|--config		- Selects the configuration file to read")
	print
	print _("Recognized actions:")
	print _(" help			- Displays this help message, then exits.")
	print _(" start			- Starts the installer.")
	sys.exit(0)
elif _action == "start":
	
	if not os.path.join(config.configpath, _config):
		raise m.UserError(_("%s does not exist! Adjust --config accordingly." % _config))
	else:
		verbose("Selected configuration file: %s" % _config)
	
	# Ohhh yay :) This action that will actually start the installer and its appropriate frontend.
	
	# Load configuration file
	cfg = config.ConfigRead(_config, "linstaller")
	
	# Populate main_settings
	main_settings = {}
	main_settings["frontend"] = cfg.printv("frontend")
	main_settings["distro"] = cfg.printv("distribution")
	main_settings["modules"] = cfg.printv("modules")
	
	verbose("Frontend: %s" % main_settings["frontend"])
	verbose("Distro: %s" % main_settings["distro"])
	verbose("Modules: %s" % main_settings["modules"])
	
	# Create modules_settings
	modules_settings = {}
	
	# Begin loop modules...
	for module in main_settings["modules"].split(" "):
		if module:
			launch_module(module)
