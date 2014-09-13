#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib, urllib2, re
import xbmcplugin, xbmcgui, xbmcaddon, xbmc
from BeautifulSoup import BeautifulSoup
_addon_name 	= 'plugin.video.goodline.cam'
_addon 			= xbmcaddon.Addon(id = _addon_name)
plugin_handle	= int(sys.argv[1])

#xbmcplugin.setContent(plugin_handle, 'movies')

User_Agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:31.0) Gecko/20100101 Firefox/31.0'
Headers    ='|User-Agent=' + urllib.quote_plus('Mozilla/5.0 (Windows NT 6.1; WOW64; rv:31.0) Gecko/20100101 Firefox/31.0')+'&Referer='    + urllib.quote_plus('http://pdd.a42.ru/vendors/osmf/SMPHLS.swf')

def get_params():
	param=[]
	paramstring=sys.argv[2]
	if len(paramstring)>=2:
		params=sys.argv[2]
		cleanedparams=params.replace('?','')
		if (params[len(params)-1]=='/'):
			params=params[0:len(params)-2]
		pairsofparams=cleanedparams.split('&')
		param={}
		for i in range(len(pairsofparams)):
			splitparams={}
			splitparams=pairsofparams[i].split('=')
			if (len(splitparams))==2:
				param[splitparams[0]]=splitparams[1]   
	return param

def AddItem(title, url={}, isFolder=True, img='', ico='', info={}, property={}):
	uri = '%s?%s' % (sys.argv[0], urllib.urlencode(url))
	item = xbmcgui.ListItem(title, iconImage = ico, thumbnailImage = img)
	if info:
		type = info['type']
		del(info['type'])
		item.setInfo(type=type, infoLabels=info)						
	if 	property:
		for key in property:
			item.setProperty(key, property[key])
	xbmcplugin.addDirectoryItem(plugin_handle, uri, item, isFolder)

def Get_url(url):
	req = urllib2.Request(url)
	req.add_header("User-Agent", User_Agent)	
	try:
		response = urllib2.urlopen(req)
		Data=response.read()
	except (urllib2.HTTPError, urllib2.URLError), e:
		xbmc.log(_addon_name+ ' %s' % e, xbmc.LOGERROR)
		xbmcgui.Dialog().ok(' ОШИБКА', str(e))
		return None		
	response.close()
	return Data

def start(params):
	playList.clear()
	Data  = Get_url('http://pdd.a42.ru/camera/')
	if not Data:return(1)
	soup = BeautifulSoup(Data)	
	ul = soup.findAll('ul' ,id="cities")
	cities = re.compile('data-city="(.+?)">(.+?)</a></li>').findall(str(ul))
	for city in cities:
		AddItem(city[1], url={'mode':'kam','city':city[1]})
		kam = soup.findAll('a', attrs={"class" : "maplink"}, href=re.compile('camera#'+city [0]+'.+?'))
		for j in kam:		
			Url = j['data-url']
			PLitem = xbmcgui.ListItem(city[1]+' - '+j.string.encode('UTF-8'), iconImage = '', thumbnailImage = '')
			PLitem.setInfo(type="Video", infoLabels={"Title":j.string.encode('UTF-8')})
			PLitem.setProperty("cityname",city[1])
			playList.add(Url+Headers,PLitem, -1)
		
	xbmcplugin.endOfDirectory(plugin_handle)

def kam(params):
	city = urllib.unquote_plus(params['city'])
	for j in range(0, playList.size()):
		
		it = playList.__getitem__(int(j))
		if (it.getProperty('cityname') == city):
			
			AddItem(it.getLabel(), url={'mode':'play','pos':j}, isFolder=False)
	xbmcplugin.endOfDirectory(plugin_handle)	

def play(params):
	u  = playList.__getitem__(int(params['pos'])).getfilename()
	it = playList.__getitem__(int(params['pos']))	
	xbmc.Player().play(u, it)

#---------------------------
playList = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
params = get_params()
try:
	mode = params['mode']
	del params['mode']
except:
	mode = 'start'
try: 
	func = globals()[mode]
except:
	func = None
if func: func(params)