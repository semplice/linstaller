# -*- coding: utf-8 -*-
# partdisks library. - (C) 2011-12 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import parted as p
import _ped
import linstaller.core.main as m
import operator
import os
import commands

from linstaller.core.main import info,warn,verbose

global devices
global disks

# FIXME: These variables should be in distribution's configuration file.
min_size = 0.2 # In GB.
rec_size = 0.3 # In GB.

# Convert min_size and rec_size in MB.
min_size *= 1024
rec_size *= 1024

# FIXME
obj_old = False

supported = {
	"ext2" : ("/sbin/mkfs.ext2",""),
	"ext3" : ("/sbin/mkfs.ext3",""),
	"ext4" : ("/sbin/mkfs.ext4",""),
	"fat32" : ("/sbin/mkfs.vfat","-F 32"),
	"ntfs" : ("/sbin/mkfs.ntfs","-Q"), # lol
	"hfs+" : ("/sbin/mkfs.hfsplus",""),
	"jfs" : ("/sbin/mkfs.jfs",""),
	"btrfs" : ("/sbin/mkfs.btrfs",""),
	"reiserfs" : ("/sbin/mkfs.reiser4",""),
	"xfs" : ("/sbin/mkfs.xfs",""),
	"linux-swap(v1)" : ("/sbin/mkswap",""),
	}

supported_tables = {
	"mbr" : "msdos",
}

flags = {
	"boot":_ped.PARTITION_BOOT,
}


def is_disk(dsk):
	""" Checks if dsk is a disk. Returns True if so.
	
	It does perform checks only on the string passed, so it may not
	be accurate. """
	
	if not dsk[-1] in ("-","1","2","3","4","5","6","7","8","9","0"):
		# Is a disk
		return True
	else:
		return False

def MbToSector(mbs):
    """ Convert Megabytes in sectors"""

    return ( mbs * 1024 * 1024 ) / 512

def swap_available(deep=False):
	""" check if there is a swap partition available (True/False) """
	
	swaps = []
	
	for disk, obj in disks.iteritems():
		try:
			for part in obj._partitions:
				if part.fileSystem:
					if "linux-swap" in part.fileSystem.type:
						# YAY!
						swaps.append(part)
						if not deep: return part
		except AttributeError:
			pass

	if deep:
		return swaps
	else:
		return False

def return_memory():
	""" Returns all RAM size. """
	
	mem = open("/proc/meminfo")
	memline = mem.readline()
	mem.close()
	
	# We have now something like this: 'MemTotal:        2073952 kB\n'
	# We only want 2073952, so remove other lines.
	memline = memline.split(" ")
	memline = int(memline[-2])
	
	# We do not want KiloBytes, but MegaBytes...
	return memline / 1024

def return_device(dev):
	""" Returns a device from a partition (str) """
	
	while dev[-1] in ("-","-1","1","2","3","4","5","6","7","8","9","0"):
		dev = dev[:-1]
	
	return dev

def return_devices(onlyusb=False):
	""" Returns a list of devices. """
	
	# We will check /proc/partitions.
	devices = {}
	disks = {}
	with open("/proc/partitions") as part:
		for line in part.readlines():
			# Drop "\n"
			line = line.replace("\n","")
			
			# Split lines by " "
			line = line.split(" ")
			
			# Last line is what we need.
			device = line[-1]
			
			if device in ("name",""):
				# This is the first/second line of /proc/partitions, skipping...
				continue
									
			if is_disk(device):
				# This is not a partition, but an entire device. We can continue.

				devices[device] = p.device.Device(path="/dev/%s" % device)
				try:
					disks[device] = p.disk.Disk(device=devices[device])
				except p.disk._ped.DiskLabelException:
					# Deal with invalid partition tables
					verbose("Unable to obtain a disk object of /dev/%s - No partition table?" % device)
					disks[device] = "notable"
				
				if onlyusb:
					# Check if it is an usb device...
					if commands.getoutput("udevadm info --query=property -n /dev/%s | grep ID_BUS" % device) != "ID_BUS=usb":
						# It isn't. Remove.
						del devices[device]
						del disks[device]
			
	return devices, disks

def device_sort(dct):
	""" Transforms dct in a list where devices are listed before partitions.
	
	Returns the newly created list and the original dictionary. """
	
	lst = []
	
	for key, value in dct.items():
		if not key in lst:
			if is_disk(key):
				# Add straigtly to list
				lst.append(key)
			else:
				if not return_device(key) in lst:
					lst.append(return_device(key)) # Append the disk if it is not already listed
				lst.append(key)
	
	return lst, dct

def restore_devices(onlyusb=False):
	""" Restores *real* structure. """
	
	global devices
	global disks
	
	devices, disks = return_devices(onlyusb=onlyusb)

def return_partition(partition):
	""" Returns a partition object which matches 'partition' """
	
	# Strip /dev/, if any
	partition = partition.replace("/dev/","")
	
	# Get device
	dev = return_device(partition)
	dev = disks[dev]
	
	# Search for partition
	for part in dev._partitions:
		if part.path == "/dev/%s" % partition:
			# Found.
			return part
	
	# If we are here, nothing found.
	return None

def setFlag(partition, flag):
	""" Sets the specified flag into the partition (which must be a parted.Partition object) """
	
	return partition.setFlag(flags[flag])

def unsetFlag(partition, flag):
	""" Unsets the specified flag into the partition (which must be a parted.Partition object) """
	
	return partition.unsetFlag(flags[flag])

def add_partition(obj, start, size, type, filesystem):
	""" Adds a new partition to the obj device. """

	# Create Geometry and Constraint
	cons = p.Constraint(device=obj.device)
	geom = p.Geometry(device=obj.device, start=start, length=size)
	
	if filesystem:
		filesystem = p.FileSystem(type=filesystem, geometry=geom)
	else:
		filesystem = None
	
	# New partition object
	part = p.Partition(disk=obj, fs=filesystem, type=type, geometry=geom)
	
	# Update constraint
	cons = p.Constraint(exactGeom=geom)
   
	# Add partition to the disk.
	result = obj.addPartition(partition=part, constraint=cons)
		
	if not result:
		# failed :(
		return result
	else:
		return part

def delete_partition(obj):
	""" Deletes partition from disk. """
	disk = obj.disk
	
	# Remove this partition
	return disk.deletePartition(obj)

def get_supported_filesystems():
	""" Returns a list of supported filesystems. """
	
	_supported = {}
	
	for key, value in supported.items():
		frontend = value[0]
		if os.path.exists(frontend):
			# All good. mkfs.<filesystem> exists. Add to list.
			_supported[key] = value
	
	return _supported

def commit(obj, touched):
	""" Commits the changes at obj. """
	
	if type(obj) == p.partition.Partition:
		if not obj.path in touched:
			# Nothing to commit
			return
		
		# Umount...
		if is_mounted(obj.path):
			umount(parted_part=obj)
		
		# If obj is a partition, use disk.
		obj = obj.disk
	elif type(obj) == p.device.Device:
		if not obj.path in touched:
			# Nothing to commit
			return
		
		# If obj is a device, get appropriate disk
		try:
			obj = disks[obj]
		except KeyError:
			verbose("Unable to get an appropriate disk. This may happen when returning back after a partition table creation.")
			return
	else:
		if not obj.device.path in touched:
			# Nothing to commit
			return
	
	obj.commit()

def format_partition_for_real(obj, fs):
	""" Uses mkfs.* to format partition. """	

	# Get an appropriate frontend
	frontend = get_supported_filesystems()[fs]
	
	_app = frontend[0] # Application (e.g /sbin/mkfs.ext4)
	_opt = frontend[1] # Options of the application.
	
	# Umount...
	if is_mounted(obj.path):
		umount(parted_part=obj)
	
	_opt = "%s %s" % (obj.path, _opt)
	
	# BEGIN FORMATTING!!!!111111!!!!!!!!!!!!!1111111111111111
	mkfs = m.execute("%s %s" % (_app, _opt))
	mkfs.start() # START!!!111111111!!!!!!!!!!!!!!!111111111111111
	
	# Return object to frontend, it should handle all.
	return mkfs

def new_table(obj, tabletype):
	""" Uses parted's mktable command to create a new partition table. """
	
	table = supported_tables[tabletype]
	device = obj
	
	prted = m.execute("parted -s %s mktable %s" % (obj.path, table))
	prted.start()
	
	# Return object to frontend
	return prted

def format_partition(obj, fs):
	""" Formats partition with fs """

	# Generate a new filesystem object
	fs = p.FileSystem(type=fs, geometry=obj.geometry)
	
	obj.fileSystem = fs

def resize_partition(obj, newLength):
	""" Puts the end of obj at newEnd """
	
	# Update partition's geometry
	obj.geometry.length = newLength
	
	# Create a new constraint
	cons = p.Constraint(exactGeom=obj.geometry)
	
	# maximize the partition at the given constraint.
	obj.disk.maximizePartition(obj, cons)

def delete_all(obj):
	""" Deletes all partitions on obj (a Disk object). """
	
#	if type(obj) == p.device.Device:
#		# Its a device.
#		print disks
#		disk = disks[obj.path.replace("/d]
	
	# Remove all
	umount_bulk(obj.device.path) # Before, umount all mounted partitions
	return obj.deleteAllPartitions()

def is_mounted(obj):
	""" Checks if obj is mounted.
	obj can be either a partition object in /dev, or a mount point.
	
	Returns a dictionary with informations on the object if True, otherwise returns False.
	"""
		
	clss = m.execute("LANG=C mount | grep -w %s" % obj, custom_log=m.subprocess.PIPE)
	# Start
	clss.start()
	
	# Wait
	status = clss.wait()
	
	# output...
	output = clss.process.communicate()
	
	if not output or status != 0:
		return False
	else:
		# Split opts.
		for line in output:
			# It should be one.
			items = line.split(" ")
			return {"path":items[0], "mountpoint":items[2], "type":items[4], "options":items[-1].replace("(","").replace(")","").replace("\n","")}


def mount_partition(parted_part=None, path=None, opts=False, target=False, check=True):
	""" Mounts a partition. You can use parted_part or path.
	parted_part is a Partition object of pyparted.
	path is a str that contains the device in /dev (e.g. '/dev/sda1')
	"""
	
	# Check args
	if parted_part:
		path = parted_part.path
	elif not path:
		# Not parted_part, nor path.
		raise m.UserError("mount_partition called without parted_part and without path!")
	
	# Check if path exists...
	if not os.path.exists(path): raise m.UserError("%s does not exist!" % path)
	
	# Generate a mount point
	_directory = path.replace("/","") # Strip all /. We should have something like this: devsda1.
	_mountpoint = os.path.join("/linstaller/mountpoints", _directory)
	if target:
		# Supersede _mountpoint with target
		_mountpoint = target
	if not os.path.exists(_mountpoint):
		os.makedirs(_mountpoint) # Create directory
	else:
		# Mountpoint already exists. See if it is mounted...
		if os.path.ismount(_mountpoint) and check:
			# Check if the _mountpoint is the place of the partition we want.
			infos = is_mounted(path)
			if not infos:
				# Not mounted. Here is mounted *another* partition
				raise m.CmdError("in %s there is mounted another partition!" % _mountpoint)
			
			# It is mounted. We can directly return this mountpoint.
			if opts:
				for opt in opts.split(","):
					if not opt in is_mounted(path)["options"]:
						# It is mounted, but the options are not here
						# Remount.
						m.sexec("mount -o %s,remount %s %s" % (opts, path, _mountpoint))
						
			return _mountpoint
	
	# Check if the partition is already mounted on another mountpoint.
	if is_mounted(path) and check:
		# It is mounted.
		
		_mountpoint = is_mounted(path)["mountpoint"]
		
		if opts:
			for opt in opts.split(","):
				if not opt in is_mounted(path)["options"]:
					# It is mounted, but the options are not here
					# Remount.
					m.sexec("mount -o %s,remount %s %s" % (opts, path, _mountpoint))
		
		return _mountpoint
	
	# Mount. Finally!
	if opts:
		opts = "-o %s" % opts
	else:
		opts = ""
	m.sexec("mount %s %s %s" % (opts, path, _mountpoint))
	
	# Return mountpoint
	return _mountpoint

def umount(parted_part=None, path=None):
	""" Unmounts a partition. You can use parted_part or path.
	parted_part is a Partition object of pyparted.
	path is a str that contains the device in /dev (e.g. '/dev/sda1')
	"""
	
	# Check args
	if parted_part:
		path = parted_part.path
	elif not path:
		# Not parted_part, nor path.
		raise m.UserError("mount_partition called without parted_part and without path!")
	
	# Check if it is mounted...
	if not is_mounted(path): raise m.UserError("%s is not mounted!" % path)
	
	# Unmount.
	m.sexec("umount %s" % path)

def umount_bulk(basepath):
	""" Umounts all partitions that begins with basepath.
	
	Example: umount_bulk("/dev/sda")
	umounts /dev/sda1, /dev/sda2, /dev/sda3 etc...
	"""
	
	# Obtain only the file name
	basepath = os.path.basename(basepath)
	
	for _file in os.listdir("/dev"):
		if basepath in _file:
			# Check if it is mounted
			if is_mounted(os.path.join("/dev",_file)):
				# Yes, so umount
				umount(path=os.path.join("/dev",_file))

def write_memory(changed):
	""" Writes, in memory, the changes made. """
	
	failed = {}
	
	for name, changes in changed.items():
		verbose("Writing changes of %s in memory..." % name)
		
		# get object
		obj = changes["obj"]
		
		for thing, value in changes["changes"].items():
			# Write the changes
			
			result = True
			
			# Before, delete.
			if thing == "delete" and value == True:
				# Delete.
				# Delete is used only on partitions. We can safely pass this object to delete_partition: it is for sure a Partition object.
				
				changes["changes"].clear()
				
				result = delete_partition(obj) # Actually return, as if a partition is *deleted* it can be used anymore.

			elif thing == "deleteall" and value == True:
				# Delete all partitions on obj
				# Deleteall is used only on disks. We can safely pass this object to delete_all: it is for sure a Disk object.

				changes["changes"].clear()

				result =  delete_all(obj) # Actually return, as if a disk is *cleared* its partition can't be used anymore.
			elif thing == "resize":
				# Resize.
				# Resize is used only on partitions. We can safely pass this object to resize_partition: it is for sure a Partition object.

				del changes["changes"][thing]

				result = resize_partition(obj, value)
			elif thing == "format":
				# Format.
				# Format is used only on partitions. We can safely pass this object to resize_partition: it is for sure a Partition object.

				del changes["changes"][thing]

				result = format_partition(obj, value)
			
			if not result: failed[name] = thing
		
	return failed
	

def check_distributions(obj=False):
	""" Checks all partitions in Device/Partition object to discover other distributions.
	If obj is not specified, returns a list of *all* distributions on *all* disks. """
	
	# Start os-prober
	clss = m.execute("LANG=C os-prober", custom_log=m.subprocess.PIPE)
	# Start
	clss.start()
	
	# Wait
	status = clss.wait()
	
	# output...
	output = clss.process.communicate()[0].split("\n")
	
	distribs = {}
		
	for line in output:
		if not line:
			continue
			
		line = line.split(":")
		if obj:
			# We should limit results to the ones that are relevant in obj.device.path.
			if not obj.path in line[0]:
				continue # Not a partition on obj.device; skip.

		distribs[line[0]] = line[1] # Add.
	
	return distribs

def automatic_check(obj, by="freespace", swap_created=False):
	""" Performs a check on obj (a Disk object) to see if the user can install the distribution in that disk. """
	
	device = obj.device
	if swap_available():
		swap = swap_available()
	else:
		swap = None
	
	_min_warning = False
	_swap_warning = False
	
	choices = {}
	
	# First check if there is enough free space on the device.
	if by == "freespace":
		if obj.getFreeSpacePartitions():
			# There is!
			# Check the size of the partitions...
			part_sizes = {}
			for part in obj.getFreeSpacePartitions():
				size = round(part.getLength("MB"), 2)
				# Add part object and size in part_sizes
				part_sizes[part] = size
			
			# Now sort them by value...
			part_sizes = sorted(part_sizes.iteritems(), key=operator.itemgetter(1), reverse=True)
			
			for tupl in part_sizes:
				part, size = tupl
				# We are now looking at them from bigger to smaller.
				if size == rec_size or size > rec_size:
					# Uh cool! This partition can be used for a full semplice experience.
					# But before, we should check if there is already a swap partition.
					if swap:
						# yeah! So use all of this space for the distribution.
						# partitionize this free_space as ext4.
						
						# Get were we start
						starts = part.geometry.start
						
						# Get length.
						length = part.geometry.length
						
						# Remove this partition
						#obj.removePartition(part)
						
						# Add the new one
						try:
							part = add_partition(obj, start=starts, size=length, type=p.PARTITION_NORMAL, filesystem="ext4")
							return part, swap, swap_created
						except:
							verbose("Unable to add a partition (reached the partition limit?)")
							return False, False, False
					else:
						# We should create a swap partition.
						
						# First, see if we *can*.
						mem = return_memory()
						if mem < 1023:
							# We should multiply by 2 mem.
							mem *= 2
						else:
							# 2 GB.
							mem = 2048
						mem = round(mem, 2)
						
						print mem
						print size
						
						if size > mem:
							# First check. mem is small than size. That's good.
							if (size - mem) < rec_size:
								# If we create a new swap partition, the distribution-oriented partition will be less than the recommended size.
								# So we should display _min_warning.
								_min_warning = True
								# Otherwise, it's all good.
						else:
							# We cannot add a new swap partition.
							
							# Get were we start
							starts = part.geometry.start
							
							# Get length.
							length = part.geometry.length
							
							# Remove this partition
							#obj.removePartition(part)
							
							# Add the new one
							part = add_partition(obj, start=starts, size=length, type=p.PARTITION_NORMAL, filesystem="ext4")
							
							return part, swap, swap_created
						
						# Get were part starts
						starts = part.geometry.start
						
						# Ok, we can continue.
						# First, we should *remove* this partition.
						#obj.removePartition(part)
						
						# Ok, we can now make a new swap partition.
						swap = add_partition(obj, start=starts, size=MbToSector(mem), type=p.PARTITION_NORMAL, filesystem="linux-swap(v1)")
						
						# We can now run again this.
						return automatic_check(obj, by="freespace", swap_created=True)
				elif size == min_size or size > min_size:
					# Minimal semplice experience. And no swap.
					# Get were we start
					starts = part.geometry.start
								
					# Get length.
					length = part.geometry.length
					
					# Remove this partition
					#obj.deletePartition(part)
								
					# Add the new one
					part = add_partition(obj, start=starts, size=length, type=p.PARTITION_NORMAL, filesystem="ext4")

					return part, swap, swap_created
				else:
					# No way :(
					
					return None, None, None
		else:
			# No way :(
			
			return None, None, None
	elif by == "delete":
		# Check distributions, by obj.
		distribs = check_distributions(obj.device)
		
		delete = {}
		
		if not distribs:
			# No distributions.
			return None, None
		
		for path, name in distribs.iteritems():
			# Assume that we are happy with swap
			# Get a partition object
			part = obj.getPartitionByPath(path)
			if not part:
				# We should never get here
				raise main.CodeError("An error! o_O")
			
			# Check size
			if part.getLength("MB") > min_size or part.getLength("MB") == min_size:
				# We can.
				delete[part] = name
		
		# Now sort them by value...
		delete = sorted(delete.iteritems(), key=operator.itemgetter(1), reverse=True)
		
		# Get an available swap partition.
		swap = swap_available()
		
		# Return.
		return delete, swap
	
				
restore_devices()
