#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib, urllib2, re, sys, os, json, datetime, time

import xbmcplugin, xbmcgui, xbmcaddon, xbmc

_addon_name 	 = 'plugin.video.smart.tvrain.ru'
_addon 			 = xbmcaddon.Addon(id = _addon_name)
_addon_patch 	 = xbmc.translatePath(_addon.getAddonInfo('path'))

if (sys.platform == 'win32') or (sys.platform == 'win64'):
	_addon_patch     = _addon_patch.decode('utf-8')

plugin_handle	= int(sys.argv[1])
xbmcplugin.setContent(plugin_handle, 'movies')

Headers ={'Accept'                      :'application/tvrain.api.2.8+json',
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
	
def Get_url(url, headers={}, JSON=False):
	req = urllib2.Request(url)
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
	except Exception, e:
		xbmc.log('[%s] %s' %(_addon_name, e), xbmc.LOGERROR)
		xbmcgui.Dialog().ok(' ОШИБКА', str(e))
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
	
def start(params):
	AddItem('Эфир',              {'mode':'live'})
	#AddItem('Последние передачи',{'mode':'schedule'})			
	AddItem('Популярное',        {'mode':'popular'})
	AddItem('Наш Выбор',         {'mode':'ourchoice'})
	AddItem('Программы',         {'mode':'programscat'})
	xbmcplugin.endOfDirectory(plugin_handle)
		
def schedule(params): 
	try:
		program_id= params['program_id']
	except:
		program_id = None	
	if not program_id:
		url_ = 'https://api.tvrain.ru/api_v2/schedule/2014-09-11'
		Data = Get_url(url_, Headers, JSON=True)
		#print Data
		for i in Data:
			str_dt = re.match('^.{3}, \d\d .{3} \d\d \d\d:\d\d:\d\d', i['date_start']).group(0) #Fri, 12 Sep 14 06:00:00 
			dt = datetime.fromtimestamp(time.mktime(time.strptime(str_dt, '%a, %d %b %y %H:%M:%S')))
			title = '[COLOR FF4169E1]%s  [/COLOR]'%(dt.strftime('%d/%m %H:%M'))+ i['program_name']
			AddItem(title, url={'mode':'schedule', 'program_id':i['program_id'], 'date_start':i['date_start']}, img = i['tv_img'])
	else:
		url_ = 'https://api.tvrain.ru/api_v2/programs/%s/articles/'%(program_id)
		date_start =urllib.unquote_plus(params['date_start'])
		Data = Get_url(url_, Headers, JSON=True)
		for i in Data['elements']:
			#if i['date_active_start']==params['date_start']:
			print '====='
			print date_start
			print i['date_active_start']
	
	xbmcplugin.endOfDirectory(plugin_handle)

def live(params):
	url_ = 'https://api.tvrain.ru/api_v2/live/'
	Data = Get_url(url_, Headers, JSON=True)
		
	for i in Data['RTMP']:
		AddItem(i['label'].encode('UTF-8'), url={'mode':'PlayRtmp', 'url':i['url']}, isFolder=False)
	xbmcplugin.endOfDirectory(plugin_handle)		
		
def ourchoice(params):
	url_ = 'https://api.tvrain.ru/api_v2/widgets/ourchoice/'
	Data = Get_url(url_, Headers, JSON=True)	
	for i in Data:	
		info={'type':'Video', 'Title':'Наш Выбор', 'plot':i['name'].encode('UTF-8'), 'genre':'Наш Выбор', 'rating':5.7}
		property={'fanart_image':i['preview_img']}
		AddItem(i['name'].encode('UTF-8'), {'mode':'play', 'id':i['id']}, isFolder=False, img= i['preview_img'], info=info, property=property)		
	xbmcplugin.endOfDirectory(plugin_handle)
	
def popular(params):
	try:
		period=params['period']
	except:
		period = None	
	if period:
		novideo = _addon.getSetting('novideo')
		Headers_=Headers
		Headers_['X-Result-Define-Period'] = '%s'%(period)
		url_ = 'https://api.tvrain.ru/api_v2/widgets/popular/' 
		Data = Get_url(url_, Headers, JSON=True)
		for i in Data['elements']:
			if i['program_id'] == 1018: #нет видио
				if novideo == 'true': continue
				title ='[NO Video] '+ i['name'].encode('UTF-8')
			else:
				title = i['name'].encode('UTF-8')
			
			info={'type':'Video', 'Title':'Популярное', 'plot':title,'genre':'Популярное'}
			property={'fanart_image':i['preview_img']}
			AddItem(title, {'mode':'play', 'id':i['id']}, isFolder=False, img= i['preview_img'], info=info, property=property)			
	else:
		AddItem('За Неделю',     {'mode':'popular','period':'1w' })
		AddItem('За Месяц',      {'mode':'popular','period':'1m' })
		AddItem('За Три Месяца', {'mode':'popular','period':'3m' })
		AddItem('За Полгода',    {'mode':'popular','period':'6m' })
		AddItem('За Год',        {'mode':'popular','period':'12m' })
		AddItem('За Всё Время',  {'mode':'popular','period':'forever' })
	xbmcplugin.endOfDirectory(plugin_handle)		
	
def programscat(params):
	url_ = 'https://api.tvrain.ru/api_v2/programs/categories/'
	Data = Get_url(url_, Headers, JSON=True)

	AddItem('Популярные программы', {'mode':'programs', 'catid':'pop'})	
	for i in Data['elements']:
		AddItem(Data['elements'][i].encode('UTF-8'), {'mode':'programs', 'catid':i}, isFolder=True)			
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
			info={'type':'Video', 'Title': i['name'].encode('UTF-8'), 'plot':i['preview_text'],'genre':i['name'].encode('UTF-8')}
			property={'fanart_image':i['preview_img']}
			AddItem(i['name'].encode('UTF-8'), {'mode':'programid','id':i['id']}, img=i['preview_img'], info=info, property=property)		
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
		info= {'type':'Video', 'Title': i['name'].encode('UTF-8'), 'plot':i['name'].encode('UTF-8')}
		property={'fanart_image':i['preview_img']}
		t = ('[Full] ' if i['is_full']==1 else '')+ i['name'].encode('UTF-8')
		AddItem(t, {'mode':'play','id':i['id']}, isFolder=False, img=i['preview_img'], info=info, property=property)		
	if current_page<total_pages:
		title = 'Далее > %s из %s'%(str(current_page+1),str(total_pages))
		AddItem(title, {'mode':'programid','id':params['id'],'page':current_page+1})	
	xbmcplugin.endOfDirectory(plugin_handle)	
			
def play(params):	
	url_ = 'https://api.tvrain.ru/api_v2/articles/%s/videos/' %(params['id'])
	
	Data = Get_url(url_, Headers, JSON=True)
	
	if not Data:return
	dialog = xbmcgui.Dialog()
	dialog_items = []
	for i in Data[0]['mp4']:
		dialog_items.append(i)		
	dlg= dialog.select('Качество Изображения', dialog_items)		
	
	playList = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
	playList.clear()	
				
	for ch in range(0, len(Data)):
		item = xbmcgui.ListItem('Дождь- '+Data[ch]['name'].encode('UTF-8'), iconImage = '', thumbnailImage = '')
		Url_  = Data[ch]['mp4'][dialog_items[dlg]]
		playList.add(Url_,item)
		
	xbmc.Player().play(playList)

def PlayRtmp(params):	
	Url = urllib.unquote_plus(params['url'])	
	playList = xbmc.PlayList(xbmc.PLAYLIST_MUSIC)
	playList.clear()		
	item = xbmcgui.ListItem('Live', iconImage = '', thumbnailImage = '')
	item.setInfo(type="Video", infoLabels={"Title":'Live'})	
	item.setProperty('uid', 'http://tvrain.ru/player/uppod/uppod.swf')
	item.setProperty('file', Url)
	item.setProperty('st', 'tvrain.ru/player/uppod/video174-1087.txt')	
	item.setProperty('mimetype', 'video/flv')	
	playList.add(Url,item)
	xbmc.Player().play(playList)

#---------------------------
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
