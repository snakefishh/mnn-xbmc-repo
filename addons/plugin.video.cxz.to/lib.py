#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib, urllib2, sys
import xbmcplugin, xbmcgui, xbmcaddon, xbmc

User_Agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:31.0) Gecko/20100101 Firefox/31.0'
	
def Get_url(url, headers={}, Post = None, GETparams={}, JSON=False, Proxy=None, User_Agent= User_Agent):
	if Proxy:
		proxy_h = urllib2.ProxyHandler({'http': Proxy})
		opener = urllib2.build_opener(proxy_h)
		opener.addheaders = [('User-agent', User_Agent)]
		urllib2.install_opener(opener)
	else:
		opener = urllib2.build_opener()
		urllib2.install_opener(opener)	
	if GETparams:
		url = "%s?%s" % (url, urllib.urlencode(GETparams))
	if Post:
		Post = urllib.urlencode(Post)		
	req = urllib2.Request(url, Post)
	req.add_header("User-Agent", User_Agent)
	for key, val in headers.items():
		req.add_header(key, val)
	try:
		response = urllib2.urlopen(req)
		Data=response.read()
		if response.headers.get("Content-Encoding", "") == "gzip":
			import zlib
			Data = zlib.decompressobj(16 + zlib.MAX_WBITS).decompress(Data)
	except Exception, e:
		xbmc.log('['+sys.argv[0]+'] %s' % e, xbmc.LOGERROR)
		xbmcgui.Dialog().ok(' ОШИБКА', str(e))		
		return None		
	response.close()	
	if JSON:
		try:
			js = json.loads(Data)
		except Exception, e:
			xbmc.log('['+sys.argv[0]+'] %s' % e, xbmc.LOGERROR)
			xbmcgui.Dialog().ok(' ОШИБКА', str(e))
			return None
		Data = js	
	return Data

def AddItem(title, mode='', url={}, isFolder=False, img='', ico='', info={}, property={}):
	if mode: url['mode'] = mode
	uri = '%s?%s' % (sys.argv[0], urllib.urlencode(url))
	item = xbmcgui.ListItem(title, iconImage = ico, thumbnailImage = img)
	if info:
		type = info['type']
		del(info['type'])
		item.setInfo(type=type, infoLabels=info)						
	if 	property:
		for key in property:
			item.setProperty(key, property[key])
	xbmcplugin.addDirectoryItem(int(sys.argv[1]), uri, item, isFolder)

def AddFolder(title, mode='', url={}, isFolder=True, img='', ico='', info={}, property={}):
	AddItem(title=title, mode=mode, url=url, isFolder=isFolder, img=img, ico=ico, info=info, property=property)