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
import time

from linstaller.core.main import info,warn,verbose

import t9n.library
_ = t9n.library.translation_init("linstaller")

# FIXME: These variables should be in distribution's configuration file.
min_size = 0.2 # In GB.
rec_size = 0.3 # In GB.

# Convert min_size and rec_size in MB.
min_size *= 1000
rec_size *= 1000

# FIXME
obj_old = False

# Resize actions enum
ResizeAction = m.enum("GROW", "SHRINK")

supported = {
	"ext2" : ("/sbin/mkfs.ext2",""),
	"ext3" : ("/sbin/mkfs.ext3",""),
	"ext4" : ("/sbin/mkfs.ext4",""),
	"fat32" : ("/sbin/mkfs.vfat","-F 32"),
	"fat16" : ("/sbin/mkfs.vfat","-F 16"),
	"ntfs" : ("/sbin/mkfs.ntfs","-Q"), # lol
	"hfs+" : ("/sbin/mkfs.hfsplus",""),
	"jfs" : ("/sbin/mkfs.jfs",""),
	"btrfs" : ("/sbin/mkfs.btrfs",""),
	"reiserfs" : ("/sbin/mkfs.reiser4","-f"),
	"xfs" : ("/sbin/mkfs.xfs",""),
	"linux-swap(v1)" : ("/sbin/mkswap",""),
}

supported_tables = {
	"mbr" : "msdos",
	"gpt" : "gpt",
}

supported_resize = {
	"ext2" : ("/sbin/resize2fs","%(device)s %(size)sK"),
	"ext3" : ("/sbin/resize2fs","%(device)s %(size)sK"),
	"ext4" : ("/sbin/resize2fs","%(device)s %(size)sK"),
	"fat32" : ("/usr/sbin/fatresize","--size %(size)sk %(device)s"),
	"fat16" : ("/usr/sbin/fatresize","--size %(size)sk %(device)s"),
	"ntfs" : ("/sbin/ntfsresize","--size %(size)sk %(device)s"),
	"hfs+" : None,
	# JFS doesn't support shrinking?
#	"btrfs" : ("/sbin/btrfs filesystem resize %(size)sM %(mountpoint)s"),
	"reiserfs" : None,
	# XFS doesn't support shrinking?
	"linux-swap(v1)" : None,
}

flags = {
	"boot":_ped.PARTITION_BOOT,
}

sample_mountpoints = {
	None : _("Do not set a mountpoint."),
	"swap" : _("Swap"),
	"/" : _("Root (/)"),
	"/home" : _("Home Partition (/home)"),
	"/usr" : _("Global applications (/usr)"),
	"/boot/efi" : _("EFI boot partition (/boot/efi)")
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
    """ Convert Megabytes in sectors """

    return ( mbs * 1000 * 1000 ) / 512

def KbToSector(kbs):
	""" Convert Kilobytes in sectors """
	
	return ( kbs * 1000 ) / 512

def swap_available(deep=False, disksd=None):
	""" check if there is a swap partition available (True/False) """
	
	if not disksd: disksd = disks
	
	swaps = []
	
	for disk, obj in disksd.iteritems():
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
	return memline / 1000

def return_device(dev):
	""" Returns a device from a partition (str) """
	
	while dev[-1] in ("-","-1","1","2","3","4","5","6","7","8","9","0"):
		dev = dev[:-1]
	
	return dev

def return_devices(onlyusb=False, withorder=False):
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
	
	lst.sort()
	
	return lst, dct

def restore_devices(onlyusb=False):
	""" Restores *real* structure. """

	devices, disks = return_devices(onlyusb=onlyusb)
	
	global devices
	global disks
	
def disk_partitions(disk):
	""" Given a disk object, returns the list of all partitions, included the freespace ones. """

	partitions = []
	partition = disk.getFirstPartition()
	
	while partition:		
		if partition.type & p.PARTITION_FREESPACE or \
			not partition.type & p.PARTITION_METADATA or \
			not partition.type & p.PARTITION_PROTECTED:
		
			partitions.append(partition)
		
		pednxt = partition.disk.getPedDisk().next_partition(partition.getPedPartition())
		if not pednxt: break
		partition = p.Partition(disk=partition.disk, PedPartition=pednxt)

	return partitions

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

def maxGrow(partition):
	""" Given a partition, it calculates the maximum it can grow, by looking at the subsequent partition. """
	
	current = partition.getLength("MB")
	
	#nxt = partition.nextPartition()
	pednxt = partition.disk.getPedDisk().next_partition(partition.getPedPartition())
	if not pednxt: return current
	nxt = p.Partition(disk=partition.disk, PedPartition=pednxt)
	if nxt.type & p.PARTITION_FREESPACE:
		current += nxt.getLength("MB")
	
	return current	

def add_partition(obj, start, size, type, filesystem):
	""" Adds a new partition to the obj device. """

	# Create Geometry and Constraint
	cons = p.Constraint(device=obj.device)
	geom = p.Geometry(device=obj.device, start=start+2048, length=size)
	
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
		try:
			if is_mounted(obj.path):
				umount(parted_part=obj)
		except:
			return False
		
		# If obj is a partition, use disk.
		obj = obj.disk
	elif type(obj) == p.device.Device:
		if not obj.path in touched:
			# Nothing to commit
			return
		
		# If obj is a device, get appropriate disk
		try:
			obj = disks[return_device(obj.path).replace("/dev/","")]
		except KeyError:
			verbose("Unable to get an appropriate disk. This may happen when returning back after a partition table creation.")
			return
	else:
		if not obj.device.path in touched:
			# Nothing to commit
			return
	
	try:
		obj.commit()
	except:
		return False

def prepareforEFI(partition):
	""" Sets boot flag and type to EFI System Partition on the partition object. """
	
	partition.setFlag(p.PARTITION_BOOT)
	
	# Uh, it seems that by setting the boot flag we are marking the 
	# partition as EFI system partition. AWESOME!

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
	#return obj.disk.maximizePartition(obj, cons)
	return obj.disk.setPartitionGeometry(obj, cons, start=obj.geometry.start, end=obj.geometry.end)

def resize_partition_for_real(obj, newLength, action, path=None, fs=None):
	""" Given a partition object and the new start and end, this
	will resize the partition's filesystem. """

	# newLength from MB to KB, rounded minus one
	newLengthKiB = int((newLength*1000)/1.024)-1 # KiB, needed by resize2fs
	newLength = int(newLength*1000)-1 # KB, used by conforming applications

	# Get filesystem
	if not fs:
		fs = obj.fileSystem.type
	if fs.startswith("ext"):
		# ext* filesystems uses resize2fs, which uses kibibytes even if
		# they call them kilobytes
		newLength = newLengthKiB
	
	# Get an appropriate resizer
	if fs in supported_resize:
		resizer = supported_resize[fs]
	else:
		m.verbose("Resizer unavailable for %s. This may be an issue ;)" % fs)
		return
	
	if not resizer:
		# Handled internally by parted
		obj.fileSystem.resize(obj.geometry)
		return
	
	if not path:
		path = obj.path
	
	_app = resizer[0]
	_opt = resizer[1] % {"device":path, "size":newLength, "mountpoint":"FIXME"}

	# Umount...
	if fs not in ("btrfs") and is_mounted(obj.path):
		umount(parted_part=obj)
	
	# BEGIN RESIZING!!!!111111!!!!!!!!!!!!!1111111111111111
	process = m.execute("%s %s" % (_app, _opt))
	process.start() # START!!!111111111!!!!!!!!!!!!!!!111111111111111
	
	# Return object to frontend.
	return process

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


def mount_partition(parted_part=None, path=None, opts=False, typ=None, target=False, check=True):
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
	if path.startswith("/") and not os.path.exists(path): raise m.UserError("%s does not exist!" % path)
	
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
	if typ:
		typ = "-t %s" % typ
	else:
		typ = ""
	m.sexec("mount %s %s %s %s" % (typ, opts, path, _mountpoint))
	
	# Return mountpoint
	return _mountpoint

def umount(parted_part=None, path=None, tries=0):
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
	try:
		m.sexec("umount %s" % path)
	except m.CmdError, e:
		# Failed, retry after two seconds
		time.sleep(2)
		if tries < 5:
			# max 5 tries
			return umount(parted_part=parted_part, path=path, tries=tries+1)
		else:
			raise e
		

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
	
	#distribs = {"/dev/sdb1": "Inter Linux"}
	
	return distribs

def automatic_precheck(by="freespace", distribs=None):
	""" Performs a check on obj (a Disk object) to see if the user can install the distribution in that disk.
	
	distribs is a distribution dictionary as returned by check_distributions(). Default is None.
	
	Returns a modified Disk object with the change applied (if by="freespace") or a list of modified Disk objects (if by="delete").
	"""
	
	if swap_available():
		swap = swap_available()
	else:
		swap = None
	
	if by == "freespace":
		for name, obj in disks.items():
			device = obj.device
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
					if (size == rec_size or size > rec_size) and (obj.partitions == 4 or obj.partitions > 4):
						# Uh cool! This partition can be used for a full semplice experience.
						# But before, we should check if there is already a swap partition.
						return part, swap
	elif by == "delete":
		delete = {}
		for name, obj in disks.items():
			device = obj.device
						
			if not distribs:
				# No distributions.
				return None, None
			
			for path, name in distribs.iteritems():
				# Assume that we are happy with swap
				# Get a partition object
				if not return_device(device.path) in path:
					continue
				part = obj.getPartitionByPath(path)
				if not part:
					# We should never get here
					continue
				
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

				
	return None, None

class automatic_check_ng:
	""" Automatic check class. """
	
	def __init__(self, distribs={}, efi=None, onlyusb=False, is_echo=False, crypt_enabled=False):
		""" Set required variables. """
		
		self.onlyusb = onlyusb
		self.is_echo = is_echo
		self.crypt_enabled = crypt_enabled
		
		self.dev, self.dis = return_devices(onlyusb=self.onlyusb)
		
		self.distribs = distribs
		
		self.efi = efi
		
		# Check for swap
		if swap_available():
			self.swap = swap_available()
		else:
			self.swap = None
	
		#self.swap = None
	
	def swap_calc(self):
		""" Calculates the amount of swap to create.
		Returns the result in MB.
		"""
		
		mem = return_memory()
		if mem < 1023:
			# We should multiply by 2 mem.
			mem *= 2
		else:
			# 2 GB.
			mem = 2048
		return round(mem, 2)

	def __common_create_part(self, obj, part, starts=None, length=None, filesystem="ext4"):
		""" Creates partition. """
		
		# Get were we start
		if not starts: starts = part.geometry.start
						
		# Get length.
		if not length: length = part.geometry.length
				
		# Create.
		#part = add_partition(obj, start=starts, size=length, type=p.PARTITION_NORMAL, filesystem="ext4")
		#return part
		try:
			part = add_partition(obj, start=starts, size=length, type=p.PARTITION_NORMAL, filesystem=filesystem)
		except:
			return None
		
		return part
	
	def __common_create_efip(self, obj, part):
		""" Creates EFI system partition. """
		
		if obj.type == "msdos": return None, None, None # Skip if this disk is MBR.
		
		# Get were we start
		starts = part.geometry.start
						
		# Get length (40 MB)
		length = MbToSector(40)
		
		# calculate start and length for the swap/"/" partition to be created later...
		startsn = starts + length
		lengthn = part.geometry.length - length
		
		# Ok, we can now make a new efi partition.
		try:
			efi = add_partition(obj, start=starts, size=length, type=p.PARTITION_NORMAL, filesystem="fat32")
			efi.setFlag(p.PARTITION_BOOT)
		except:
			return False, None, None
		
		return efi, startsn, lengthn
	
	def __common_create_swap(self, obj, part, starts=None, length=None):
		""" Creates swap partition. """

		# Get were we start
		if not starts: starts = part.geometry.start
						
		# Get length.
		if not length: length = part.geometry.length
		
		# See if we *can*
		mem = MbToSector(self.swap_calc())
				
		# calculate start and length for the / partition to be created later...
		startsn = starts + mem
		lengthn = length - mem

		# Ok, we can now make a new swap partition.
		try:
			swap = add_partition(obj, start=starts, size=mem, type=p.PARTITION_NORMAL, filesystem="linux-swap(v1)")
		except:
			return False, None, None
		
		return swap, startsn, lengthn
	
	def __common_delete_partition(self, part):
		""" Deletes partition. """
		
		return delete_partition(part)


	def __common(self, obj, part, size, noswap=False):
		""" Common routines to create required partitions. """
				
		if not part.number < 0:
			# A real partition. We need to delete it...
			start = part.geometry.start
			res = self.__common_delete_partition(part)
			part = obj.getPartitionBySector(start)
		
		if self.swap or noswap:
			# Swap is available and we will use that.
			
			# EFI?
			if self.efi:
				efi, startsn, lengthn = self.__common_create_efip(obj, part)
				part = self.__common_create_part(obj, part, starts=startsn, length=lengthn)
			else:
				efi = None
				part = self.__common_create_part(obj, part)
						
			if noswap:
				return {"swap": False, "part":part, "efi": efi}
			else:
				return {"swap": None, "part":part, "efi": efi}
		else:
			# Swap is not available, we need to create one, then add the part

			# EFI?
			if self.efi:
				efi, startsn, lengthn = self.__common_create_efip(obj, part)
				swap, startsn, lengthn = self.__common_create_swap(obj, part, starts=startsn, length=lengthn)
				part = self.__common_create_part(obj, part, starts=startsn, length=lengthn)
			else:
				efi = None
				swap, startsn, lengthn = self.__common_create_swap(obj, part)
				part = self.__common_create_part(obj, part, starts=startsn, length=lengthn)

			#part = self.__common_create_part(obj, part, starts=startsn, length=lengthn) # add part
			
			return {"swap":swap, "part":part, "efi": efi}

	def by_freespace(self):
		""" Returns possible solutions by looking only at freespace partitions. """

		if self.is_echo:
			# Disable on echo
			return {}, []

		result_dict = {} # "freespaceX" : (dev, dis)
		order = []
		
		current = 0
		
		for name, obj in self.dis.items():

			if obj == "notable": continue

			# We need to retrieve fresh devices/disks lists and work on them
			dev, dis = return_devices()

			obj = dis[obj.device.path.replace("/dev/","")] # Get the proper disk object
			#device = obj.device
			# See if there are freespace partitions out there...
			parts = obj.getFreeSpacePartitions()
			if parts:
				# Yes!
				
				# Check the size of the partitions...
				part_sizes = {}
				for part in parts:
					size = round(part.getLength("MB"), 2)
					# Add part object and size in part_sizes
					part_sizes[part] = size
				
				# Now sort them by value...
				part_sizes = sorted(part_sizes.iteritems(), key=operator.itemgetter(1), reverse=True)
				# We are now looking at then from bigger to smaller.

				for tupl in part_sizes:
					part, size = tupl
					result = None
					swapwarning = False
					
					if self.swap:
						# Swap already in, go straight check of required space
						swapwarning = "exist"
						if (size == rec_size or size > rec_size):
							# ok!
							result = self.__common(obj, part, size)
					else:
						# We need to keep in mind the swap, too.
						swapsize = self.swap_calc()
						size1 = size - swapsize
						if (size1 == rec_size or size > rec_size):
							# ok!
							result = self.__common(obj, part, size)
						elif (size == rec_size or size > rec_size):
							# need to set a warning of some sort due to swap not being available
							swapwarning = True
							result = self.__common(obj, part, size, noswap=True)
					
					# Finally add to result_dict
					if result:
						if "part" in result and result["part"] == None:
							# Skip if part is None... something wrong happened ;)
							continue
						
						current += 1
						order.append("freespace%s" % current)
						result_dict["freespace%s" % current] = {"result":result, "swapwarning":swapwarning, "freesize":size, "disk":obj, "device":obj.device}
							
		return result_dict, order

	def by_delete(self):
		""" Returns possible solutions by looking only at systems to delete. """

		if self.is_echo:
			# Disable on echo
			return {}, []

		result_dict = {} # "deleteX" : (dev, dis)
		order = []
		
		current = 0

		for name, obj in self.dis.items():
			if obj == "notable": continue
			
			for path, name in self.distribs.iteritems():
				
				result = None
				swapwarning = False
				
				# Assume that we are happy with swap
				# Get a partition object
				if not return_device(obj.device.path) in path:
					continue
				
				# We need to retrieve fresh devices/disks lists and work on them
				dev, dis = return_devices()
				
				obj = dis[obj.device.path.replace("/dev/","")] # Get the proper disk object
				
				part = obj.getPartitionByPath(path)
				if not part:
					# wait?! o_O
					continue
				
				# Check size
				size = round(part.getLength("MB"), 2)

				if self.swap:
					# Swap already in, go straight check of required space
					swapwarning = "exist"
					if (size == rec_size or size > rec_size):
						# ok!
						result = self.__common(obj, part, size)
				else:
					# We need to keep in mind the swap, too.
					swapsize = self.swap_calc()
					size1 = size - swapsize
					if (size1 == rec_size or size > rec_size):
						# ok!
						result = self.__common(obj, part, size)
					elif (size == rec_size or size > rec_size):
						# need to set a warning of some sort due to swap not being available
						swapwarning = True
						result = self.__common(obj, part, size, noswap=True)
				
				# Finally add to result_dict
				if result:
					if "part" in result and result["part"] == None:
						# Skip if part is None... something wrong happened ;)
						continue
							
					current += 1
					order.append("delete%s" % current)
					result_dict["delete%s" % current] = {"result":result, "system":name, "swapwarning":swapwarning, "disk":obj, "device":obj.device}
							
		return result_dict, order


	def by_clear(self):
		""" Returns possible solutions by looking only at hard disks to clear. """

		if self.is_echo:
			# Disable on echo
			return {}, []

		result_dict = {} # "zclearX" : (dev, dis)
		order = []
		
		current = 0

		for name, obj in self.dis.items():
			if obj == "notable": continue

			# We need to retrieve fresh devices/disks lists and work on them
			dev, dis = return_devices()
			
			obj = dis[obj.device.path.replace("/dev/","")] # Get the proper disk object
			
			if len(obj.partitions) == 0:
				continue # Skip empty hard disks
			
			# Remove all partitions
			obj.deleteAllPartitions()

			part = obj.getFreeSpacePartitions()[0]
			size = round(part.getLength("MB"), 2)
			
			result = None
			swapwarning = False
			
			# Redetect swap
			## Due to some issues, swap_available() will redetect a swap partition that MAY have been deleted.
			## We need to use deep.
			self.swaps = swap_available(deep=True)
			self.swap = None
			for swap in self.swaps:
				if not swap.path.startswith(obj.device.path):
					self.swap = swap
					break
			
			if self.swap:
				# Swap already in, go straight check of required space
				swapwarning = "exist"
				if (size == rec_size or size > rec_size):
					# ok!
					result = self.__common(obj, part, size)
			else:
				# We need to keep in mind the swap, too.
				swapsize = self.swap_calc()
				size1 = size - swapsize
				if (size1 == rec_size or size > rec_size):
					# ok!
					result = self.__common(obj, part, size)
				elif (size == rec_size or size > rec_size):
					# need to set a warning of some sort due to swap not being available
					swapwarning = True
					result = self.__common(obj, part, size, noswap=True)
					
			# Finally add to result_dict
			if result:
				if "part" in result and result["part"] == None:
					# Skip if part is None... something wrong happened ;)
					continue

				current += 1
				order.append("clear%s" % current)
				result_dict["clear%s" % current] = {"result":result, "swapwarning":swapwarning, "model":obj.device.model, "disk":obj, "device":obj.device}
							
		return result_dict, order

	def by_echo(self):
		""" Returns possible root partitions, without touching them.
		
		Used by "echo". """
		
		if not self.is_echo:
			# Enable only on echo
			return {}, []
		
		result_dict = {} # "echoX" : (dev, dis)
		order = []
		
		current = 0

		for name, obj in self.dis.items():
			if obj == "notable": continue
			
			if len(obj.partitions) == 0:
				# No partitions, we need to create one!
				freespacepart = obj.getFreeSpacePartitions()[0]
				
				result = self.__common_create_part(obj, freespacepart, filesystem="ext2")
				
				current += 1
				order.append("echo%s" % current)
				result_dict["echo%s" % current] = {"result":{"part":result, "swap":False, "efi":False, "format":"ext2"}, "model":obj.device.model, "disk":obj, "device":obj.device}

				continue
				
			for part in obj.partitions:
				# Skip non-ext* and non-fat32 partitions
				if part.fileSystem and part.fileSystem.type not in ("fat32", "ext2", "ext3", "ext4"): continue
				
				current += 1
				order.append("echo%s" % current)
				result_dict["echo%s" % current] = {"result":{"part":part, "swap":False, "efi":False, "format":None}, "model":obj.device.model, "disk":obj, "device":obj.device}

		return result_dict, order
	
	def by_notable(self):
		""" Handle table-less disks. """
		
		#if self.is_echo:
		#	# Disable on echo
		#	return {}, []

		result_dict = {} # "notableX" : (dev, dis)
		order = []
		
		current = 0

		for name, obj in self.dis.items():
			if obj != "notable": continue
			
			current += 1
			order.append("notable%s" % current)
			result_dict["notable%s" % current] = {"result":{"part":None, "swap":None, "efi":None, "format":None}, "disk":"notable", "device":self.dev[name], "model":self.dev[name].model}
		
		return result_dict, order
	
	def by_crypt_device(self):
		""" Returns possible solutions by looking only at hard disks. """
		
		if self.is_echo:
			# Disable on echo
			return {}, []
		
		result_dict = {} # "crypt_deviceX" : (dev, dis)
		order = []
		
		current = 0
		
		for name, obj in self.dis.items():
			if obj == "notable": continue
			
			current += 1
			order.append("crypt_device%s" % current)
			result_dict["crypt_device%s" % current] = {"result":{"part":None, "swap":None, "efi":None, "format":None}, "disk":self.dis[name], "device":self.dev[name], "model":self.dev[name].model}
		
		return result_dict, order
	
	def main(self):
		""" Checks for solutions for the automatic partitioner.
		Every solution is applied on a virtual Disk object.
		"""

		# Check by notable
		notable, notableord = self.by_notable()

		if not self.crypt_enabled:
			# Check by freespace
			free, freeord = self.by_freespace()
			
			# Check by delete
			dele, deleord = self.by_delete()
			
			# Check by clear
			clea, cleaord = self.by_clear()
			
			# Check by echo
			echo, echoord = self.by_echo()
			
			results = dict(notable.items() + free.items() + dele.items() + clea.items() + echo.items())
			order = notableord + freeord + deleord + cleaord + echoord
		else:
			# Check by crypt_device
			
			cryptd, cryptdord = self.by_crypt_device()
			
			results = dict(notable.items() + cryptd.items())
			order = notableord + cryptdord
		
		return results, order
	

def automatic_do(part, swap, by="freespace"):
	""" Does the magic. """
	
	warnings = []
	
	if by == "freespace":
		# We have a defined freespace partition, so we will do everything there.
		
		# We should create a swap partition?
		if not swap:
			# Yes.
			
			# First, see if we *can*.
			mem = return_memory()
			if mem < 1023:
				# We should multiply by 2 mem.
				mem *= 2
			else:
				# 2 GB.
				mem = 2048
				mem = round(mem, 2)

			if size > mem:
				# First check. mem is small than size. That's good.
				if (size - mem) < rec_size:
					# If we create a new swap partition, the distribution-oriented partition will be less than the recommended size.
					# So we should display _min_warning.
					_min_warning = True
					# Otherwise, it's all good.
	

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
							try:
								part = add_partition(obj, start=starts, size=length, type=p.PARTITION_NORMAL, filesystem="ext4")
								return part, swap, swap_created
							except:
								verbose("Unable to add a partition (reached the partition limit?)")
								return False, False, False

						
						# Get were part starts
						starts = part.geometry.start
						
						# Ok, we can continue.
						# First, we should *remove* this partition.
						#obj.removePartition(part)
						
						# Ok, we can now make a new swap partition.
						try:
							swap = add_partition(obj, start=starts, size=MbToSector(mem), type=p.PARTITION_NORMAL, filesystem="linux-swap(v1)")
						except:
							verbose("Unable to add a partition (reached the partition limit?)")
													
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
					try:
						part = add_partition(obj, start=starts, size=length, type=p.PARTITION_NORMAL, filesystem="ext4")
						return part, swap, swap_created
					except:
						verbose("Unable to add a partition (reached the partition limit?)")
						return False, False, False

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
