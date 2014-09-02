#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib, urllib2, re, sys, os, json, datetime
import xbmcplugin, xbmcgui, xbmcaddon, xbmc

_addon_name 	= 'plugin.video.smart.tvrain.ru'
_addon 			= xbmcaddon.Addon(id = _addon_name)
plugin_handle	= int(sys.argv[1])
#_addon_patch 	= xbmc.translatePath(_addon.getAddonInfo('path'))
#if sys.platform == 'win32': _addon_patch = _addon_patch.decode('utf-8')

#sys.path.append(os.path.join(_addon_patch, 'resources', 'lib'))
#xbmcplugin.setContent(plugin_handle, 'movies')

Headers ={'Accept'                      :'application/tvrain.api.2.8+json',
          'Accept-Language'             :'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
          'Accept-Encoding'             :'gzip, deflate',
          'X-User-Agent'                :'TV Client (Browser); API_CONSUMER_KEY=a908545f-80af-4f99-8dac-fb012cec',
          'Content-Type'                :'application/x-www-form-urlencoded',
          'Referer'                     :'http://smarttv.tvrain.ru/',
          'Origin'                      :'http://smarttv.tvrain.ru', 
          'Connection'                  :'keep-alive',
		  }

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
	
def Get_url(url, headers={}, Post = None, GETparams={}, JSON=False):
	
	if GETparams:
		url = "%s?%s" % (url, urllib.urlencode(GETparams))
	if Post:
		Post = urllib.urlencode(Post)		
	req = urllib2.Request(url, Post)
	#req.add_header("User-Agent", User_Agent)
	
	for key, val in headers.items():
		req.add_header(key, val)
	try:
		response = urllib2.urlopen(req)
	except (urllib2.HTTPError, urllib2.URLError), e:
		xbmc.log('[%s] %s' %(_addon_name, e), xbmc.LOGERROR)
		xbmcgui.Dialog().ok(' ОШИБКА', str(e))
		return None	
	try:
		Data=response.read()
		if response.headers.get("Content-Encoding", "") == "gzip":
			import zlib
			Data = zlib.decompressobj(16 + zlib.MAX_WBITS).decompress(Data)
	except urllib2.HTTPError:
		return None		
	response.close()	
	if JSON:
		try:
			js = json.loads(Data)
		except Exception, e:
			xbmc.log('[%s] %s' %(_addon_name, e), xbmc.LOGERROR)
			xbmcgui.Dialog().ok(' ОШИБКА', str(e))
			return None
		Data = js		
	return Data

def start(params):
	def add_dir(title, mode, img=''):
		uri = '%s?%s' % (sys.argv[0], urllib.urlencode({'mode':mode}))
		item = xbmcgui.ListItem(title, iconImage = img, thumbnailImage = img)
		xbmcplugin.addDirectoryItem(plugin_handle, uri, item, True)	
				
	#add_dir('Эфир', 'live')
	add_dir('Программы', 'programscat')
	add_dir('Наш Выбор', 'ourchoice')
	add_dir('Популярное', 'popular')
		
	xbmcplugin.endOfDirectory(plugin_handle)
	
	
def live(params):
	
	url_ = 'https://api.tvrain.ru/api_v2/live/'
	Data = Get_url(url_, Headers, JSON=True)
	print Data
	
	for i in Data:
		print Data[i][0]['label'].encode('UTF-8')
	
	
def ourchoice(params):

	url_ = 'https://api.tvrain.ru/api_v2/widgets/ourchoice/'
	Data = Get_url(url_, Headers, JSON=True)
	for i in Data:
		uri = '%s?%s' % (sys.argv[0], urllib.urlencode({'mode':'play', 'id':i['id']}))
		item = xbmcgui.ListItem(i['name'].encode('UTF-8'), iconImage = '', thumbnailImage = '')
		item.setInfo(type="Video", infoLabels={"Title": 'Наш Выбор'})
		xbmcplugin.addDirectoryItem(plugin_handle, uri, item, True)		
		
	xbmcplugin.endOfDirectory(plugin_handle)
	
def popular(params):

	url_ = 'https://api.tvrain.ru/api_v2/widgets/popular/' 
	Data = Get_url(url_, Headers, JSON=True)

	for i in Data['elements']:
		uri = '%s?%s' % (sys.argv[0], urllib.urlencode({'mode':'play', 'id':i['id']}))
		item = xbmcgui.ListItem(i['name'].encode('UTF-8'), iconImage = '', thumbnailImage = '')
		item.setInfo(type="Video", infoLabels={"Title": ''})
		xbmcplugin.addDirectoryItem(plugin_handle, uri, item, True)		
		
	xbmcplugin.endOfDirectory(plugin_handle)	
	
def programscat(params):

	url_ = 'https://api.tvrain.ru/api_v2/programs/categories/'
	Data = Get_url(url_, Headers, JSON=True)

	uri = '%s?%s' % (sys.argv[0], urllib.urlencode({'mode':'programs', 'catid':'pop'}))
	item = xbmcgui.ListItem('Популярное', iconImage = '', thumbnailImage = '')
	item.setInfo(type="Video", infoLabels={"Title": ''})
	xbmcplugin.addDirectoryItem(plugin_handle, uri, item, True)		
	
	
	for i in Data['elements']:
		uri = '%s?%s' % (sys.argv[0], urllib.urlencode({'mode':'programs', 'catid':i}))
		item = xbmcgui.ListItem(Data['elements'][i].encode('UTF-8'), iconImage = '', thumbnailImage = '')
		item.setInfo(type="Video", infoLabels={"Title": ''})
		xbmcplugin.addDirectoryItem(plugin_handle, uri, item, True)		
		
	xbmcplugin.endOfDirectory(plugin_handle)
	
def programs(params):
	
	Headers_=Headers
	Headers_['X-Result-Define-Pagination']='1/250' #Почему 250
	
	url_ = 'https://api.tvrain.ru/api_v2/programs/'
	Data = Get_url(url_, Headers_, JSON=True)
	
	if params['catid']=='pop':
		filter='is_cool'
		filterzn='1'
	else:
		filter='category_id'
		filterzn=params['catid']
	
	for i in Data['elements']:	
		if str(i[filter])==filterzn:
		
			uri = '%s?%s' % (sys.argv[0], urllib.urlencode({'mode':'programid','id':i['id']}))
			item = xbmcgui.ListItem(i['name'].encode('UTF-8'), iconImage = '', thumbnailImage = '')
			item.setInfo(type="Video", infoLabels={"Title": i['name'].encode('UTF-8')})
			xbmcplugin.addDirectoryItem(plugin_handle, uri, item, True)		
		
	xbmcplugin.endOfDirectory(plugin_handle)
	
def programid(params):
	
	try:
		page = params['page']
	except:
		page ='1'
	
	Headers_=Headers
	Headers_['X-Result-Define-Pagination'] = '%s/20'%(page)#номер страницы / элементов в странице]
	url_ = 'https://api.tvrain.ru/api_v2/programs/%s/articles/'%(params['id'])
	Data = Get_url(url_, Headers_, JSON=True)

	current_page = Data['current_page']
	total_pages  = Data['total_pages']

	for i in Data['elements']:
		print i
		uri = '%s?%s' % (sys.argv[0], urllib.urlencode({'mode':'play','id':i['id']}))
		item = xbmcgui.ListItem(i['name'].encode('UTF-8'), iconImage = '', thumbnailImage = '')
		item.setInfo(type="Video", infoLabels={"Title": i['name'].encode('UTF-8')})
		xbmcplugin.addDirectoryItem(plugin_handle, uri, item, True)	
	
	print current_page, total_pages
	if current_page<total_pages:
		uri = '%s?%s' % (sys.argv[0], urllib.urlencode({'mode':'programid','id':params['id'],'page':current_page+1}))
		item = xbmcgui.ListItem('Далее > %s из %s'%(str(current_page+1),str(total_pages)), iconImage = '', thumbnailImage = '')
		xbmcplugin.addDirectoryItem(plugin_handle, uri, item, True)	
	
	xbmcplugin.endOfDirectory(plugin_handle)	
			
def play(params):
	
	url_ = 'https://api.tvrain.ru/api_v2/articles/%s/videos/' %(params['id'])
	Data = Get_url(url_, Headers, JSON=True)
	playList = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
	playList.clear()	
	for i in Data:
		try: 
			Url_  = i['mp4']['480p']
		except:
			try: 
				Url_  = i['mp4']['360p']
			except:
				Url_  = i['mp4']['720p']	
		
		item = xbmcgui.ListItem('Дождь- '+i['name'].encode('UTF-8'), iconImage = '', thumbnailImage = '')				
		playList.add(Url_,item)
	xbmc.Player().play(playList)
		
#---------------------------
params = get_params()
mode = None
try:
	mode = params["mode"]
except:
	pass
if   mode == None:
	start(params)
elif mode == 'live':
	live(params)
elif mode == 'ourchoice':
	ourchoice(params)
elif mode == 'popular':
	popular(params)
elif mode == 'programscat':
	programscat(params)
elif mode == 'programs':
	programs(params)
elif mode == 'programid':
	programid(params)	
elif mode == 'play':
	play(params)
	
	