#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys, os
import xbmcaddon, xbmc
from BeautifulSoup import BeautifulSoup

addon_name = 'plugin.video.cxz.to'
addon 		= xbmcaddon.Addon(id = addon_name)
addon_data_path = xbmc.translatePath(os.path.join("special://profile/addon_data", addon_name))
addon_path = xbmc.translatePath(os.path.join("special://home/addons", addon_name))
if (sys.platform == 'win32') or (sys.platform == 'win64'):
	addon_data_path = addon_data_path.decode('utf-8')
	addon_path      = addon_path
addon_ico = addon_path+'icon.png'
try:
	plugin_handle	= int(sys.argv[1])
except:
	pass
User_Agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:31.0) Gecko/20100101 Firefox/31.0'
site_url='http://cxz.to'