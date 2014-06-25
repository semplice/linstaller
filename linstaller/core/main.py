# -*- coding: utf-8 -*-
# linstaller core main library - (C) 2011 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

####
VERSION = "6.1.3"
####

import os, sys, traceback
import subprocess, threading, traceback

# User name
usr = os.getenv("USER")
pid = os.getpid()

# Check if we are imported from somewhere...
if __name__ == "__main__":
	raise CodeError("This file should be imported and not executed!")

# Open a temp file on which store logs and so on...
# LOG HANDLING:
# - linstaller uses /var/log/linstaller to store logs.
if not os.path.exists("/var/log/linstaller"):
	# Make directory
	os.makedirs("/var/log/linstaller")

# Now we can open a file with our pid there.
ourfile = open(os.path.join("/var/log/linstaller","linstaller_latest.log"), "w")

def fileappend(thing, suffix="", to=ourfile):
	""" Writes thing (+ suffix) to to. """
	
	to.write(thing + suffix)
	to.flush()

class fileappend_dummy:
	""" Dummy class that will emulate a file object. We will call fileappend instead. """
	
	def __init__(self, suffix="", to=ourfile):
		self.suffix = suffix
		self.to = to
	
	def write(self, thing):
		""" Using fileappend to write. """
		
		fileappend(thing, self.suffix, self.to)
	
	def fileno(self):
		return self.to.fileno()

# Laiv exception:
class LaivError(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

# External program except:
class CmdError(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

# User except:
class UserError(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

# Faulty code except:
class CodeError(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

# Warning
def warn(message):
	print("W: %s" % message)
	# Append to log
	fileappend("W: %s" % message,"\n")

# Info
def info(message):
	print("I: %s" % message)
	# Append to log
	fileappend("I: %s" % message,"\n")

# Verbose
def verbose(message):
	# Append to log
	fileappend(message,"\n")

# Process execution

def sexec(command, shell=True):
	""" A simple function that will execute a command by invoking execute class. """
	
	# Declare class
	clss = execute(command, shell=shell)
	# Start thread
	clss.start()
	
	# Now we should wait the end...
	status = clss.wait()
	
	if status != 0:
		# An error occoured
		raise CmdError("An error occoured while executing %s" % command)

class execute:
	""" The execute class is a convenient class implemented to easily launch and control an external process. """
	
	def __init__(self, command, shell=True, custom_log=fileappend_dummy(ourfile)):
		self.command = command
		self.shell = shell
		self.custom_log = custom_log
		
		self.pid = None # Err... process not started... so pid is none ;)
	
	def start(self):
		""" The core function. Will launch self.command. """

		# If shell is False, we should pass to Popen a list, instead of a normal string.
		if not self.shell:
			proc = self.command.split(" ")
		else:
			proc = self.command
		
		self.process = subprocess.Popen(proc, shell=self.shell, stdout=self.custom_log, stderr=self.custom_log)
		self.pid = self.process.pid
		
		# Now do whatever you want...
	
	def wait(self):
		""" Waits the end of the process """
		
		self.process.wait()
		return self.process.returncode # We let the thread starter handle this exit status

def bold(txt):
	""" Returns a bold-ed text. """
	bold = "\033[1m"
	res = "\033[0;0m"
	
	return bold + txt + res

def root_check():
	""" Checks if the user is root. """
	
	if os.getuid() is not 0:
		raise UserError("You must be root to use this module.")

def handle_exception(function):
	""" Launches function and logs every exception caught.
	When an exception is caught, sys.exit(1) is invoked. """
	
	try:
		function()
	except:
		excp = sys.exc_info()
		print("".join(traceback.format_exception(excp[0],excp[1],excp[2])))
		verbose("".join(traceback.format_exception(excp[0],excp[1],excp[2])))
		sys.exit(1)

def enum(*sequential, **named):
	
	# Thanks to http://stackoverflow.com/a/1695250
	
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)
