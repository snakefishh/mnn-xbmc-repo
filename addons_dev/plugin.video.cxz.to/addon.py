#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib, urllib2, re, sys, os, json, datetime, time
import xbmcplugin, xbmcgui, xbmcaddon, xbmc
from lib import *
from BeautifulSoup import BeautifulSoup
from urlparse import urlparse
addon_name 	= 'plugin.video.cxz.to'
addon 		= xbmcaddon.Addon(id = addon_name)
plugin_handle	= int(sys.argv[1])
xbmcplugin.setContent(plugin_handle, 'movies')
 	

#AARRGGBB
clGreen	     = '[COLOR FF008000]%s[/COLOR]' 
clDodgerblue = '[COLOR FF1E90FF ]%s[/COLOR]'
clDimgray 	 = '[COLOR FF696969 ]%s[/COLOR]'

def start(params):
	AddItem('1', url={'mode':''})
	AddItem('2', url={'mode':''})
	AddItem('3', url={'mode':''})
	AddItem('4', url={'mode':''})
	AddItem('5', url={'mode':''})
	xbmcplugin.endOfDirectory(plugin_handle)
