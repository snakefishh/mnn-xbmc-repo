#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib, urllib2, cookielib, sys, os,json
import xbmcplugin, xbmcgui, xbmcaddon, xbmc

addon_name 	= sys.argv[0].replace('plugin://', '')
addon_data_path = xbmc.translatePath(os.path.join("special://profile/addon_data", addon_name))
addon_path = xbmc.translatePath(os.path.join("special://home/addons", addon_name))
if (sys.platform == 'win32') or (sys.platform == 'win64'):
	addon_data_path = addon_data_path.decode('utf-8')
	addon_path      = addon_path
addon_ico = addon_path+'icon.png'

cookie_path =addon_data_path+'cookie'

#AARRGGBB
AA=lambda cl,ff:cl.replace(' FF', ff)
clGreen	     = '[COLOR FF008000]%s[/COLOR]'
clDodgerblue = '[COLOR FF1E90FF]%s[/COLOR]'
clDimgray 	 = '[COLOR FF696969]%s[/COLOR]'
clAliceblue  = '[COLOR FFF0F8FF]%s[/COLOR]'
clRed        = '[COLOR FFFF0000]%s[/COLOR]'
clPGreen     = '[COLOR FF98FB98]%s[/COLOR]'



User_Agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:31.0) Gecko/20100101 Firefox/31.0'

def xbmcMessage(mess, tm, h=addon_name):
	xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")' % (h, mess, tm, addon_ico))

def uriencode(p):
	 return '%s?%s' % (sys.argv[0], urllib.urlencode(p))

def DelCookie():
	if os.path.exists(cookie_path):
		os.remove(cookie_path)

def Get_url(url, headers={}, Post = None, GETparams={}, JSON=False, Proxy=None, Cookie=False, User_Agent= User_Agent):
	h=[]
	if Proxy:
		(urllib2.ProxyHandler({'http': Proxy}))
	if Cookie:
		if not os.path.exists(os.path.dirname(addon_data_path)):
				os.makedirs(os.path.dirname(addon_data_path))
		cookie = cookielib.LWPCookieJar(cookie_path)
		if os.path.exists(cookie_path):
			cookie.load()
		h.append(urllib2.HTTPCookieProcessor(cookie))
	if h:
		opener = urllib2.build_opener(*h)
		if User_Agent: opener.addheaders = [('User-agent', User_Agent)]
		urllib2.install_opener(opener)

	if GETparams:
		url = "%s?%s" % (url, urllib.urlencode(GETparams))

	if Post:
		Post = urllib.urlencode(Post)		

	req = urllib2.Request(url, Post)
	if User_Agent: req.add_header("User-Agent", User_Agent)
	for key, val in headers.items():
		req.add_header(key, val)

	try:
		response = urllib2.urlopen(req)
		Data=response.read()
		if response.headers.get("Content-Encoding", "") == "gzip":
			import zlib
			Data = zlib.decompressobj(16 + zlib.MAX_WBITS).decompress(Data)
	except Exception, e:
		xbmc.log('['+addon_name+'] %s' % e, xbmc.LOGERROR)
		xbmcgui.Dialog().ok(' ОШИБКА', str(e))		
		return None		
	response.close()	
	if JSON:
		import json
		try:
			js = json.loads(Data)
		except Exception, e:
			xbmc.log('['+addon_name+'] %s' % e, xbmc.LOGERROR)
			xbmcgui.Dialog().ok(' ОШИБКА', str(e))
			return None
		Data = js	
	if Cookie: cookie.save()
	return Data

def AddItem(title, mode='', url={}, isFolder=False, img='', ico='', info={}, property={}, cmItems=[]):
	if mode: url['mode'] = mode
	uri = '%s?%s' % (sys.argv[0], urllib.urlencode(url))
	item = xbmcgui.ListItem(title, iconImage = ico, thumbnailImage = img)
	if cmItems:
		item.addContextMenuItems(cmItems)
	if info:
		type = info['type']
		del(info['type'])
		item.setInfo(type=type, infoLabels=info)						
	if 	property:
		for key in property:
			item.setProperty(key, property[key])
	xbmcplugin.addDirectoryItem(int(sys.argv[1]), uri, item, isFolder)

def AddFolder(title, mode='', url={}, isFolder=True, img='', ico='', info={}, property={}, cmItems=[]):
	AddItem(title=title, mode=mode, url=url, isFolder=isFolder, img=img, ico=ico, info=info, property=property, cmItems=cmItems)

class cache():
	file_name = ''
	mode = ''
	def __init__(self, file_name, mode = 'json'):
		if not os.path.exists(addon_data_path):
				os.makedirs(addon_data_path)
		self.file_name = file_name
		self.mode = mode

	def write(self,data):
		F = open(addon_data_path+'/'+self.file_name, 'w')
		json.dump(data, F)
		F.close()

	def read(self):
		F = open(addon_data_path+'/'+self.file_name, 'r')
		data = json.load(F)
		F.close()
		return data


