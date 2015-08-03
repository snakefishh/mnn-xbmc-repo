#!/usr/bin/python
# -*- coding: utf-8 -*-import os

import sys, os
import xbmc

Plugins = []

class Plugin(object):
	Name = ''
	def Command(self, args):
		pass

def LoadPlugins():
	Ppath = xbmc.translatePath(os.path.join("special://home/addons", 'plugin.video.cxz.to', 'ExtSearch'))
	if (sys.platform == 'win32') or (sys.platform == 'win64'):
		Ppath = Ppath.decode('utf-8')
	for file_name in os.listdir(Ppath):
		if file_name.endswith (".py"):
			module_name = file_name[: -3]
			__import__('ExtSearch.'+module_name, None, None, [''])

	for plugin in Plugin.__subclasses__():
		p = plugin()
		Plugins.append(p)
	return