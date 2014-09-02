#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib, urllib2, re, sys, os, json, datetime
import xbmcplugin, xbmcgui, xbmcaddon, xbmc
#from BeautifulSoup import BeautifulSoup, CData as CData1

_addon_name 	= 'plugin.video.smart.tvrain.ru'
_addon 			= xbmcaddon.Addon(id = _addon_name)
_addon_url		= sys.argv[0]
plugin_handle	= int(sys.argv[1])
_addon_patch 	= xbmc.translatePath(_addon.getAddonInfo('path'))
if sys.platform == 'win32': _addon_patch = _addon_patch.decode('utf-8')

#sys.path.append(os.path.join(_addon_patch, 'resources', 'lib'))
#xbmcplugin.setContent(plugin_handle, 'movies')

User_Agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:31.0) Gecko/20100101 Firefox/31.0'
url = {}
url['schedule'] = 'https://api.tvrain.ru/api_v2/schedule/'                       #программа
url['ourchoice']= 'https://api.tvrain.ru/api_v2/widgets/ourchoice/'              #наш выбор
url['popular']= 'https://api.tvrain.ru/api_v2/widgets/popular/'                  #популярное


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
	
def Get_url(url, headers={}, Post = None, GETparams={}, JSON=False, Proxy=None, retinfo=False):
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
	except (urllib2.HTTPError, urllib2.URLError), e:
		xbmc.log('[plugin.video.peers.tv] %s' % e, xbmc.LOGERROR)
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
			xbmc.log('[plugin.video.peers.tv] %s' % e, xbmc.LOGERROR)
			xbmcgui.Dialog().ok(' ОШИБКА', str(e))
			return None
		Data = js	
	if retinfo:return Data, response.info()
	else:return Data

def start(params):

		uri = '%s?%s' % (sys.argv[0], urllib.urlencode({'mode':'programscat'}))
		item = xbmcgui.ListItem('Программы', iconImage = '', thumbnailImage = '')
		item.setInfo(type="Video", infoLabels={"Title": 'Программы'})
		xbmcplugin.addDirectoryItem(plugin_handle, uri, item, True)		
				
		uri = '%s?%s' % (sys.argv[0], urllib.urlencode({'mode':'ourchoice'}))
		item = xbmcgui.ListItem('Наш Выбор', iconImage = '', thumbnailImage = '')
		item.setInfo(type="Video", infoLabels={"Title": 'Наш Выбор'})
		xbmcplugin.addDirectoryItem(plugin_handle, uri, item, True)		
		
		uri = '%s?%s' % (sys.argv[0], urllib.urlencode({'mode':'popular'}))
		item = xbmcgui.ListItem('Популярное', iconImage = '', thumbnailImage = '')
		item.setInfo(type="Video", infoLabels={"Title": 'Популярное'})
		xbmcplugin.addDirectoryItem(plugin_handle, uri, item, True)		
		
		xbmcplugin.endOfDirectory(plugin_handle)
	
	
	
	
def ourchoice(params):
	
	Headers ={'User-Agent'                  :'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:31.0) Gecko/20100101 Firefox/31.0',
		      'Accept'                      :'application/tvrain.api.2.8+json',
			  'Accept-Language'             :'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
			  'Accept-Encoding'             :'gzip, deflate',
			  'X-User-Agent'                :'TV Client (Browser); API_CONSUMER_KEY=a908545f-80af-4f99-8dac-fb012cec',
			  'Content-Type'                :'application/x-www-form-urlencoded',
			  'X-Result-Define-Thumb-Width' :'200',
			  'X-Result-Define-Thumb-height':'110',
			  'Referer'                     :'http://smarttv.tvrain.ru/',
			  'Origin'                      :'http://smarttv.tvrain.ru',
			 
			  'Connection'                  :'keep-alive',
	         }

	url_ = url['ourchoice']
	Data = Get_url(url_, Headers, JSON=True)
	for i in Data:
		uri = '%s?%s' % (sys.argv[0], urllib.urlencode({'mode':'play', 'id':i['id']}))
		item = xbmcgui.ListItem(i['name'].encode('UTF-8'), iconImage = '', thumbnailImage = '')
		item.setInfo(type="Video", infoLabels={"Title": 'Наш Выбор'})
		xbmcplugin.addDirectoryItem(plugin_handle, uri, item, True)		
		
	xbmcplugin.endOfDirectory(plugin_handle)
	


def popular(params):
	
	Headers ={'User-Agent'                  :'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:31.0) Gecko/20100101 Firefox/31.0',
		      'Accept'                      :'application/tvrain.api.2.8+json',
			  'Accept-Language'             :'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
			  'Accept-Encoding'             :'gzip, deflate',
			  'X-User-Agent'                :'TV Client (Browser); API_CONSUMER_KEY=a908545f-80af-4f99-8dac-fb012cec',
			  'Content-Type'                :'application/x-www-form-urlencoded',
			  'X-Result-Define-Thumb-Width' :'200',
			  'X-Result-Define-Thumb-height':'110',
			  'Referer'                     :'http://smarttv.tvrain.ru/',
			  'Origin'                      :'http://smarttv.tvrain.ru',
			 
			  'Connection'                  :'keep-alive',
	         }

	url_ = url['popular']
	Data = Get_url(url_, Headers, JSON=True)

	for i in Data['elements']:
		uri = '%s?%s' % (sys.argv[0], urllib.urlencode({'mode':'play', 'id':i['id']}))
		item = xbmcgui.ListItem(i['name'].encode('UTF-8'), iconImage = '', thumbnailImage = '')
		item.setInfo(type="Video", infoLabels={"Title": 'Наш Выбор'})
		xbmcplugin.addDirectoryItem(plugin_handle, uri, item, True)		
		
	xbmcplugin.endOfDirectory(plugin_handle)	
	
def programscat(params):

	Headers ={'User-Agent'                  :'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:31.0) Gecko/20100101 Firefox/31.0',
		      'Accept'                      :'application/tvrain.api.2.8+json',
			  'Accept-Language'             :'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
			  'Accept-Encoding'             :'gzip, deflate',
			  'X-User-Agent'                :'TV Client (Browser); API_CONSUMER_KEY=a908545f-80af-4f99-8dac-fb012cec',
			  'Content-Type'                :'application/x-www-form-urlencoded',
			  'Referer'                     :'http://smarttv.tvrain.ru/',
			  'Origin'                      :'http://smarttv.tvrain.ru',
			 
			  'Connection'                  :'keep-alive',
	         }

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


	Headers ={'User-Agent'                  :'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:31.0) Gecko/20100101 Firefox/31.0',
		      'Accept'                      :'application/tvrain.api.2.8+json',
			  'Accept-Language'             :'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
			  'Accept-Encoding'             :'gzip, deflate',
			  'X-User-Agent'                :'TV Client (Browser); API_CONSUMER_KEY=a908545f-80af-4f99-8dac-fb012cec',
			  'Content-Type'                :'application/x-www-form-urlencoded',
			  'X-Result-Define-Thumb-Width' :'200',
			  'X-Result-Define-Thumb-height':'266',
			  'X-Result-Define-Pagination'	:'1/250', #откуда 250 ()
			  'Referer'                     :'http://smarttv.tvrain.ru/',
			  'Origin'                      :'http://smarttv.tvrain.ru',
			 
			  'Connection'                  :'keep-alive',
	         }
	
	url_ = 'https://api.tvrain.ru/api_v2/programs/'
	Data = Get_url(url_, Headers, JSON=True)
	
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
	


	Headers ={'User-Agent'                     :'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:31.0) Gecko/20100101 Firefox/31.0',
		      'Accept'                         :'application/tvrain.api.2.8+json',
			  'Accept-Language'                :'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
			  'Accept-Encoding'                :'gzip, deflate',
			  'X-User-Agent'                   :'TV Client (Browser); API_CONSUMER_KEY=a908545f-80af-4f99-8dac-fb012cec',
			  'Content-Type'                   :'application/x-www-form-urlencoded',
			  'X-Result-Define-Thumb-Width'    :'200',
			  'X-Result-Define-Thumb-height'   :'110',
			  'X-Result-Define-Video-Only-Flag':'1',
			  'X-Result-Define-Pagination'	   :'1/20',#номер страницы / элементов в странице
			  'Referer'                        :'http://smarttv.tvrain.ru/',
			  'Origin'                         :'http://smarttv.tvrain.ru', 
			  'Connection'                     :'keep-alive',
	         }

	url_ = 'https://api.tvrain.ru/api_v2/programs/%s/articles/'%(params['id'])
	Data = Get_url(url_, Headers, JSON=True)


	current_page = Data['current_page']
	total_pages  = Data['total_pages']
	for i in Data['elements']:
		print i
		uri = '%s?%s' % (sys.argv[0], urllib.urlencode({'mode':'play','id':i['id']}))
		item = xbmcgui.ListItem(i['name'].encode('UTF-8'), iconImage = '', thumbnailImage = '')
		item.setInfo(type="Video", infoLabels={"Title": i['name'].encode('UTF-8')})
		xbmcplugin.addDirectoryItem(plugin_handle, uri, item, True)	
	
	
	
	
	xbmcplugin.endOfDirectory(plugin_handle)	
		

	
def play(params):
	Headers ={'User-Agent'                  :'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:31.0) Gecko/20100101 Firefox/31.0',
		      'Accept'                      :'application/tvrain.api.2.8+json',
			  'Accept-Language'             :'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
			  'Accept-Encoding'             :'gzip, deflate',
			  'X-User-Agent'                :'TV Client (Browser); API_CONSUMER_KEY=a908545f-80af-4f99-8dac-fb012cec',
			  'Content-Type'                :'application/x-www-form-urlencoded',
			  'X-Result-Define-Thumb-Width' :'200',
			  'X-Result-Define-Thumb-height':'110',
			  'Referer'                     :'http://smarttv.tvrain.ru/',
			  'Origin'                      :'http://smarttv.tvrain.ru',
			 
			  'Connection'                  :'keep-alive',
	         }
	
	
	url_ = 'https://api.tvrain.ru/api_v2/articles/%s/videos/' %(params['id'])
	Data = Get_url(url_, Headers, JSON=True)
	print Data	

	
	#title = urllib.unquote_plus(params['title'])
	#Url_  = urllib.unquote_plus(params['playurl'])	
	try: 
		Url_  = Data[0]['mp4']['480p']
	except:
		try: 
			Url_  = Data[0]['mp4']['360p']
		except:
			Url_  = Data[0]['mp4']['720p']	
	
	
	playList = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
	playList.clear()	
	
	item = xbmcgui.ListItem('', iconImage = '', thumbnailImage = '')
	#item.setInfo(type="Video", infoLabels={"Title":title})				
				
	playList.add(Url_,item)
	xbmc.Player().play(playList)
	
	
#	url_ = 'https://api.tvrain.ru/api_v2/articles/374827/videos/' #374827 из widgets/ourchoice/
#	Data = Get_url(url_, Headers, JSON=True)
#	print Data	


		
####################Дополнительная информация по программе можно https://api.tvrain.ru/api_v2/programs/
#	url_ = 'https://api.tvrain.ru/api_v2/programs/1804/'
#	Data = Get_url(url_, Headers, JSON=True)
#	print Data
#	print Data['1804']['detail_text'].encode('UTF-8')

		
		
		
################Выбор потока и качества для live
#
#	url_ = 'https://api.tvrain.ru/api_v2/live/'
#	Data = Get_url(url_, Headers, JSON=True)
#	print Data
#	
#	for i in Data:
#		print Data[i][0]['label'].encode('UTF-8')

#---------------------------
params = get_params()
mode = None
try:
	mode = params["mode"]
except:
	pass
if   mode == None:
	start(params)
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
	
	