linstaller - a simple yet powerful GNU/linux installer
======================================================

**linstaller is now in maintenance mode, that means that it won't be developed
further if not to implement some feature related to Semplice Linux.

There are plans to create a new installer from scratch, and that will be the
focus of Semplice's installer-related projects.**

linstaller is a modular and preseedable GNU/Linux distribution
installer, written in python.

It is Semplice Linux-oriented, but thanks to its configuration
system, can be adapted to many Live distributions.

The project's name has three different meanings:
 * LINstaller = LINux installer
 * L'installer = "The installer" in italian
 * L-installer = laiv-installer, which was the name of our
   previous installer.

Install
-------

Use the distutils-based setup.py to install linstaller:

> sudo python2.7 setup.py install

You can then symlink /usr/lib/linstaller/linstaller.py to /usr/bin/linstaller.

Start
-----

To start linstaller you should use this command:

> sudo linstaller -c=semplice start

where 'semplice' is the configuration file of the distribution (currently
only semplice is available).
You can symlink 'semplice' to 'default' and not use the -c switch.

To specify the frontend, you can use the -f switch.

---------------------------------------

&copy; 2011-2012 [Semplice Linux](http://semplice-linux.org) Project. All rights reserved.
Work released under the terms of the [GNU GPL license](http://www.gnu.org/licenses/gpl.html), version 3 or later.
