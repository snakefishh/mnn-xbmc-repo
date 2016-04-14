#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib, urllib2, cookielib, json, re
from var import *
import xbmcplugin, xbmcgui
import pickle

cookie_path =addon_data_path+'/cookie'

#AARRGGBB
AA=lambda cl,ff:cl.replace(' FF', ff)
clGreen	     = '[COLOR FF008000]%s[/COLOR]'
clDodgerblue = '[COLOR FF1E90FF]%s[/COLOR]'
clDimgray 	 = '[COLOR FF696969]%s[/COLOR]'
clAliceblue  = '[COLOR FFF0F8FF]%s[/COLOR]'
clRed        = '[COLOR FFFF0000]%s[/COLOR]'
clPGreen     = '[COLOR FF98FB98]%s[/COLOR]'


def xbmcMessage(mess, tm, h=addon_name):
	xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")' % (h, mess, tm, addon_ico))

def uriencode(p):
	return '%s?%s' % (sys.argv[0], urllib.urlencode(p))

def DelCookie():
	if os.path.exists(cookie_path):
		os.remove(cookie_path)

#TODO кеширование страниц?
def Get_url(url, headers={}, Post = None, GETparams={}, JSON=False, Proxy=None, Cookie=False, User_Agent= User_Agent):
	h=[]
	if Proxy:
		(urllib2.ProxyHandler({'http': Proxy}))

	if GETparams:
		url = "%s?%s" % (url, urllib.urlencode(GETparams))

	if Post:
		Post = urllib.urlencode(Post)		

	req = urllib2.Request(url, Post)
	if User_Agent: req.add_header("User-Agent", User_Agent)
	if Cookie:
		cookie={}
		if not os.path.exists(os.path.dirname(addon_data_path)):
				os.makedirs(os.path.dirname(addon_data_path))
		if os.path.exists(cookie_path):
			cookie_f=open(cookie_path, 'r')

			try:
				cookie = pickle.load(cookie_f)
			except:
				pass

			cookie_f.close()
			coo =''
			for key in cookie.keys():
				coo+= key+"=" + cookie[key] + ";"
			req.add_header("Cookie",coo)

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
		#xbmcgui.Dialog().ok(' ОШИБКА', str(e))
		return None		
	zz=''
	if response.headers.has_key('Set-Cookie'):
		zz = str(response.headers)

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
	if Cookie and zz:
		print zz
		matches = re.findall('(?m)Set-Cookie: (.+?)=(.+?);', zz)
		for m in matches:
			cookie[m[0]]=m[1]
		cookie_f = open(cookie_path, 'w')
		pickle.dump(cookie,cookie_f)
		cookie_f.close()
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

def filename2match(filename):
	results={'label':filename}
	urls=['(.+)s(\d+)e(\d+)','(.+)s(\d+)\.e(\d+)', '(.+) [\[|\(](\d+)[x|-](\d+)[\]|\)]', '(.+) (\d+)[x|-](\d+)', 's(\d+)e(\d+)\.?([^.]+)']
	for file in urls:
		match=re.compile(file, re.I | re.IGNORECASE).findall(filename)
		if match:
			results['showtitle'], results['season'], results['episode']=match[0]
			results['showtitle']=results['showtitle'].replace('.',' ').replace('_',' ').strip().replace('The Daily Show','The Daily Show With Jon Stewart')
			return results
