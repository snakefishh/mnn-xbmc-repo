#!/usr/bin/python
# -*- coding: utf-8 -*-

''' TODO
Добавить станцию в избранное по id 
индикатор количества слушателей
во второй строке что сейчас играет
получение информации об играющем треке на персоналках

2014 Viktor PetroFF добавил три PlayMode: 'asx', 'wma', 'mp3'
по умолчанию используется 'wma', для эфирных станций используется 'json'
'''

import urllib, urllib2, re, sys, os, json, random
import xbmcplugin, xbmcgui, xbmcaddon, xbmc


_addon_name 	= 'plugin.audio.101'
_addon 			= xbmcaddon.Addon(id = _addon_name)
_addon_url		= sys.argv[0]
plugin_handle	= int(sys.argv[1])
_addon_patch 	= xbmc.translatePath(_addon.getAddonInfo('path'))
if sys.platform == 'win32': _addon_patch = _addon_patch.decode('utf-8')

#sys.path.append(os.path.join(_addon_patch, 'resources', 'lib'))
#from rtmpgw import *

ContextMenuColor = '[COLOR FF4169E1]%s[/COLOR]'

User_Agent = 'Mozilla/5.0 (iPhone; U; CPU iPhone OS 3_0 like Mac OS X; en-us) AppleWebKit/528.18 (KHTML, like Gecko) Version/4.0 Mobile/7A341 Safari/528.16'

url={}
url['authorization']       = 'http://101.ru/api/authorization.php'
url['getgroup']            = 'http://101.ru/api/getgroup.php'
url['getstations']         = 'http://101.ru/api/getstationsbygroup.php?group_id=%s'
url['getfavotitesstation']   ='http://101.ru/?an=favorite_channels'
url['playstation']         = 'http://101.ru/api/getstationstream.php?station_id=%s&quality=2'
url['getfavoritestrack']   = 'http://101.ru/api/getfavoritestrack.php?user_id=%s&authkey=%s&offset=0&count=1000'
url['addtracktofavorites'] = 'http://101.ru/?an=fav_u_new_add&module=channel&id='
url['deletefavoritetrack'] = 'http://101.ru/api/deletefavoritetrack.php?track_id=%s&user_id=%s&authkey=%s'
url['find'] 			   = 'http://101.ru/?an=perstrack_search_result'
url['getplayingtrackinfo'] = 'http://101.ru/api/getplayingtrackinfo.php?station_id='
url['playasxstation']      = 'http://101.ru/new101.php?uid=%s&bit=2'

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
	req.add_header("User-Agent", User_Agent)
	req.add_header("Accept-Encoding","deflate")
	
	for key, val in headers.items():
		req.add_header(key, val)

	try:
		response = urllib2.urlopen(req)
	except (urllib2.HTTPError, urllib2.URLError), e:
		xbmc.log('[101.ru] %s' % e, xbmc.LOGERROR)
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
			xbmc.log('[101.ru] %s' % e, xbmc.LOGERROR)
			xbmcgui.Dialog().ok(' ОШИБКА', str(e))
			return None
			
		if js['status']:
			xbmc.log('[101.ru] %s' % (str(js['errorCode'])+'  '+js['errorMsg'].encode('UTF-8')), xbmc.LOGERROR)
			xbmcgui.Dialog().ok(' ОШИБКА', str(js['errorCode'])+'  '+js['errorMsg'].encode('UTF-8'))
			_addon.setSetting('userid', '')
			return None
		Data = js['result']
	
	return Data

def HeadAsx_url(url, TimeOut=4):
	req = urllib2.Request(url)
	#req.get_method = lambda : 'HEAD'
	#req.add_header("User-Agent", User_Agent)
	req.add_header("User-Agent","NSPlayer/4.1.0.3856")
	req.add_header("Accept","*/*")
	req.add_header("Accept-Encoding","deflate")
	req.add_header("Pragma","no-cache,rate=1.000000,request-context=2,"
					"xPlayStrm=1,xClientGUID={7FF0343D-0C80-4c7f-806C-3F6E8C24855D},"
					"stream-switch-count=1,stream-switch-entry=ffff:1:0,stream-time=0")
	req.add_header("Connection","close")

	retcode = 400

	try:
		response = urllib2.urlopen(req, timeout=TimeOut)
		retcode = response.getcode()		
		response.close()
	#except socket.timeout:
		#retcode = 408
	except urllib2.HTTPError, e:
		retcode = e.code
	except urllib2.URLError:
		pass
	except:
		retcode = 408

	return retcode

def ParseAsx(asx, Shuffle=True):
	lst = []
	if (asx and len(asx) > 0):
		asx = re.sub('<ref\\s+href', '<ref href', asx)
		asx = re.sub('href\\s*=\\s*"', 'href="', asx)
		asx = re.sub('(?<=://)([^\\?]+)\\?[^"]*"', '\\1"', asx)
		regex = re.compile('(?<=<ref\\shref=")mms://[^"]*', re.I)
		lst = regex.findall(asx)
		if len(lst) > 0:
			lst = lst[1:]
			if Shuffle:
				random.shuffle(lst)

	return lst

def authorization():
	param = {}
	param['login']   = _addon.getSetting('username')
	param['passw']   = _addon.getSetting('password')

	if not(len(param['login']) and len(param['passw'])):return False
	
	if param['login'] != _addon.getSetting('username_old') or param['passw'] != _addon.getSetting('password_old'):
		_addon.setSetting('userid', '')
		
	if _addon.getSetting('userid'): return True
	
	js = Get_url(url['authorization'], Post = param, JSON=True)
	if js:
		_addon.setSetting('userid', js['id'])
		_addon.setSetting('authkey', js['authkey'])
		_addon.setSetting('username_old',param['login'] )
		_addon.setSetting('password_old',param['passw']  )
		return True
		
	
	_addon.setSetting('userid', '')
	_addon.setSetting('authkey', '')
	
	return False
	
def getgroup():
	if authorization():
		uri = '%s?%s' % (sys.argv[0], urllib.urlencode({'mode':'izbrannoe', 'userid':_addon.getSetting('userid'), 'authkey':_addon.getSetting('authkey')}))
		item = xbmcgui.ListItem('ИЗБРАННОЕ')
		xbmcplugin.addDirectoryItem(plugin_handle, uri, item, True)
		
		uri = '%s?%s' % (sys.argv[0], urllib.urlencode({'mode':'getmyst', 'id':_addon.getSetting('userid')}))
		item = xbmcgui.ListItem('МОЁ РАДИО')
		xbmcplugin.addDirectoryItem(plugin_handle, uri, item, True)

	
	js = Get_url(url['getgroup'],JSON=True)	
	if js:
		for i in js:
			title = i['name'].encode('UTF-8')
			img = i['picUrl']
			id = i['group_id']
			uri = '%s?%s' % (sys.argv[0], urllib.urlencode({'mode':'getstations', 'id':id}))
			item = xbmcgui.ListItem(title, iconImage = img, thumbnailImage = img)
			item.setInfo(type="Music", infoLabels={"Title": title})
			xbmcplugin.addDirectoryItem(plugin_handle, uri, item, True)		
		
		## Персональные+
		uri = '%s?%s' % (sys.argv[0], urllib.urlencode({'mode':'getstations', 'id':'-1'}))
		item = xbmcgui.ListItem('Персональные', iconImage = img, thumbnailImage = img)
		item.setInfo(type="Music", infoLabels={"Title": 'Персональные'})
		xbmcplugin.addDirectoryItem(plugin_handle, uri, item, True)		
		
		xbmcplugin.endOfDirectory(plugin_handle)

		
def getstations(params):
	url_ = url['getstations'] % (params['id'])
	
	js = Get_url(url_, JSON=True)
	if js:	
		for i in js:
			title = i['name'].encode('UTF-8')
			img = i['picUrl']
			id = i['id']
							
			if i['group_id']=='-1':
				playmode='rtmp'
			else: 
				playmode=_addon.getSetting('defaultplaymode')
			
			uri = '%s?%s' % (sys.argv[0], urllib.urlencode({'mode':'play', 'id':id, 'playmode':playmode, 'title':title}))
			item = xbmcgui.ListItem(title, iconImage = img, thumbnailImage = img)
			item.setInfo(type="Music", infoLabels={"Title": title})
		
			#if authorization():
			if _addon.getSetting('userid'):
				txt = ContextMenuColor % ('101.ru Добавить в Избранное')
				uri1 = 'XBMC.RunPlugin(%s?%s)' % (sys.argv[0],urllib.urlencode({'mode':'addfavorite', 'id':id, 'group_id':i['group_id']}))
				item.addContextMenuItems([(txt, uri1,)], replaceItems=False)
		
			xbmcplugin.addDirectoryItem(plugin_handle, uri, item)
		xbmcplugin.endOfDirectory(plugin_handle)

def izbrannoe(params):	
	authkey=_addon.getSetting('authkey').split('::')
	
	url_=url['getfavotitesstation']
	Headers= {'Cookie':'autologin='+authkey[2]+'; login='+authkey[1]}
	Data = Get_url(url_, Headers)
	
	links = re.compile('<h2 class="title"><a href="(.+?)">(.+?)</a></h2>').findall(Data)
	playmode = ''
	for url1,title in links:
		url2 = re.findall('userid=([0-9]+)', url1)
		if url2: 
			playmode ='rtmp'
		else:
			url2 = re.findall('channel=([0-9]+)', url1)
			if url2: playmode =_addon.getSetting('defaultplaymode')
		
		if playmode:
			if url2[0] == _addon.getSetting('userid'): continue
			uri = '%s?%s' % (sys.argv[0], urllib.urlencode({'mode':'play', 'id':url2[0], 'playmode':playmode, 'title':title}))
			item = xbmcgui.ListItem(title, iconImage = '', thumbnailImage = '')
			item.setInfo(type="Music", infoLabels={"Title": title})
			
			txt = ContextMenuColor % ('101.ru Удалить из Избранного')
			uri1 = 'XBMC.RunPlugin(%s?%s)' % (sys.argv[0],urllib.urlencode({'mode':'delfavorite', 'id':url2[0], 'group_id':'-1' if playmode =='rtmp' else '1'}))
			item.addContextMenuItems([(txt, uri1,)], replaceItems=False)
			
			xbmcplugin.addDirectoryItem(plugin_handle, uri, item)
	xbmcplugin.endOfDirectory(plugin_handle)

def NewListItem():
	title =  urllib.unquote_plus(params['title'])
	item = xbmcgui.ListItem(params['title'],'plugin.audio.101-'+params['id']+'-'+params['playmode'], iconImage = '', thumbnailImage = '')
	item.setInfo(type="Music", infoLabels={"Title":title})
	return item
	
def play(params):	
	playmode = params['playmode']

	try: url1   =  urllib.unquote_plus(params['url'])
	except: pass
	
	playList = xbmc.PlayList(xbmc.PLAYLIST_MUSIC)
	playList.clear()

	if playmode == '2': #wma затем mp3
		asx = Get_url(url['playasxstation'] % (params['id']))
		lst = ParseAsx(asx)
		for uri in lst:
			playList.add(uri, NewListItem())

		js = Get_url(url['playstation'] % (params['id']), JSON=True)
		if (js and len(js['playlist']) > 1):
			entry = js['playlist'][0]
			if playList.size() > 1:
				playList.add(entry['url'], NewListItem(), 1)
			else:
				playList.add(entry['url'], NewListItem())
			entry = js['playlist'][1]
			if playList.size() > 3:
				playList.add(entry['url'], NewListItem(), 3)
			else:
				playList.add(entry['url'], NewListItem())
	elif playmode == '3': #mp3 затем wma
		js = Get_url(url['playstation'] % (params['id']), JSON=True)
		if js:
			for i in js['playlist']:
				playList.add(i['url'], NewListItem())
		asx = Get_url(url['playasxstation'] % (params['id']))
		lst = ParseAsx(asx)
		if len(lst) > 1:
			hc = HeadAsx_url(lst[0].replace('mms','http'))
			#xbmc.log('hc=%d'%hc, xbmc.LOGDEBUG);
			if hc == 200:
				if playList.size() > 1:
					playList.add(lst[0], NewListItem(), 1)
				else:
					playList.add(lst[0], NewListItem())
				if playList.size() > 3:
					playList.add(lst[1], NewListItem(), 3)
				else:
					playList.add(lst[1], NewListItem())
	elif playmode == '1': #только wma
		asx = Get_url(url['playasxstation'] % (params['id']))
		#xbmc.log(asx, xbmc.LOGDEBUG);
		lst = ParseAsx(asx)
		for uri in lst:
			playList.add(uri, NewListItem())
	elif playmode == '0': #только mp3
		js = Get_url(url['playstation'] % (params['id']), JSON=True)
		if js:
			for i in js['playlist']:
				playList.add(i['url'], NewListItem())
	elif playmode == 'track':
		playList.add(url1,NewListItem())
	elif playmode == 'rtmp':

		header1 = '|Referer=' + urllib.quote_plus('www.101.ru')
		header2 = '&Range=' + urllib.quote_plus('')			
				
		Url_ = 'rtmp://wz7.101.ru/pradio22/'+params['id']+'///main'+header1+header2
		playpath = 'main'
		swfUrl = "http://101.ru/static/js/uppod/uppod.swf"
		
		item = NewListItem()
		item.setProperty('PlayPath', playpath)
		item.setProperty('swfUrl', swfUrl)
		item.setProperty('mimetype', 'video/flv')
		
		playList.add(Url_,item)

	if playList.size() > 0:
		xbmc.Player().play(playList)
		
def addfavorite(params):
	if params['group_id'] == '-1':
		url_= 'http://m.101.ru/ajax/actionfavorite.php?actfav=addchannel&channel=%s&typechannel=personal' %(params['id'])
	else:
		url_= 'http://m.101.ru/ajax/actionfavorite.php?actfav=addchannel&channel=%s' %(params['id'])
	
	authkey=_addon.getSetting('authkey').split('::')	
	Headers= {'X-Requested-With':'XMLHttpRequest',
              'Referer':'http://101.ru/',
			  'Cookie':'autologin='+authkey[2]+'; login='+authkey[1]
			  }	
	Data = Get_url(url_, Headers)	
	xbmcgui.Dialog().ok('plugin.audio.101', Data)


def delfavorite(params):
	if params['group_id'] == '-1':
		url_= 'http://m.101.ru/ajax/actionfavorite.php?actfav=del&channel=%s&typechannel=personal' %(params['id'])
	else:
		url_= 'http://m.101.ru/ajax/actionfavorite.php?actfav=del&channel=%s&typechannel=channel' %(params['id'])
		
	authkey=_addon.getSetting('authkey').split('::')	
	Headers= {'X-Requested-With':'XMLHttpRequest',
              'Referer':'http://101.ru/',
			  'Cookie':'autologin='+authkey[2]+'; login='+authkey[1]
			  }	
	Data = Get_url(url_, Headers)	
	xbmcgui.Dialog().ok('plugin.audio.101', Data)
		
	xbmc.executebuiltin('Container.Refresh')

def getmyst(params):
	
	uri = '%s?%s' % (sys.argv[0], urllib.urlencode({'mode':'play', 'id':params['id'],'playmode':'rtmp', 'title':'Моё Радио'}))
	item = xbmcgui.ListItem('Слушать')
	xbmcplugin.addDirectoryItem(plugin_handle, uri, item, False)
	
	uri = '%s?%s' % (sys.argv[0], urllib.urlencode({'mode':'getmytracks', 'id':'mytracks', 'userid':_addon.getSetting('userid'), 'authkey':_addon.getSetting('authkey')}))
	item = xbmcgui.ListItem('Треки')
	xbmcplugin.addDirectoryItem(plugin_handle, uri, item, True)
		
	uri = '%s?mode=findtracks&offset=0&ftext=0' % (sys.argv[0])
	item = xbmcgui.ListItem('Поиск')
	xbmcplugin.addDirectoryItem(plugin_handle, uri, item, True)
	
	uri = '%s?%s' % (sys.argv[0], urllib.urlencode({'mode':'addcurrenttrack'}))
	item = xbmcgui.ListItem('Добавить текущий трек в Моё радио')
	xbmcplugin.addDirectoryItem(plugin_handle, uri, item, True)	
	xbmcplugin.endOfDirectory(plugin_handle)
	
def getmytracks(params):
	url_ = url['getfavoritestrack'] %(_addon.getSetting('userid'),_addon.getSetting('authkey'))
	
	js = Get_url(url_, JSON=True)
	if js:	
		for i in js:
			title   = i['name']
			urlt    = i['url']
			trackid = i['id']
			uri = '%s?mode=play&url=%s&playmode=%s&id=%s&title=%s' % (sys.argv[0],urlt,'track',trackid, title)
			item = xbmcgui.ListItem(title, iconImage = '', thumbnailImage = '')
			item.setInfo(type="Music", infoLabels={"Title": title})	
			
			txt = ContextMenuColor % ('101.ru Удалить из моёго радио')
			uri1 = 'XBMC.RunPlugin(%s?%s)' % (sys.argv[0],urllib.urlencode({'mode':'deletefavoritetrack', 'id':trackid}))
			item.addContextMenuItems([(txt, uri1,)], replaceItems=False)
			
			xbmcplugin.addDirectoryItem(plugin_handle, uri, item)
		xbmcplugin.endOfDirectory(plugin_handle)

def deletefavoritetrack(params):
	url_ = url['deletefavoritetrack']%(params['id'], _addon.getSetting('userid'), _addon.getSetting('authkey'))
	js = Get_url(url_, JSON=True)
	xbmc.executebuiltin('Container.Refresh')

def findtracks(params):	
	ftext=urllib.unquote(params['ftext'])
	offsetn=params['offset']
	
	if offsetn=='0':
		if ftext=='0':
			kb = xbmc.Keyboard('', 'Поиск', False)
			kb.doModal()
			if not kb.isConfirmed(): return
			ftext=kb.getText()	
		furl=url['find']
	else:
		furl=url['find']+'&offset='+offsetn
		
	PData={}
	PData['search'] = ftext
	
	i=0
	while i<3:
					
		Headers ={'X-Requested-With':'XMLHttpRequest',
				  'Referer'         :'http://101.ru/?an=personal_edit&userid='+_addon.getSetting('userid')
				  }		
		Data = Get_url(furl, Headers, Post = PData)		
		
		links = re.compile('<a class="js play search_playbut" href="#" setting=\'{"playerid":"search_(.+?)"}\' flashvars=\'{"file":"(.+?)"}\' element=".search_playbut"><i class="icon"></i>(.+?)</a>').findall(Data)
		for id,url_,title in links:				
						
			uri = '%s?%s' % (sys.argv[0], urllib.urlencode({'mode':'play', 'url':url_, 'playmode':'track', 'id':id, 'title':title}))
			#item = xbmcgui.ListItem(title.decode('cp1251').encode('UTF-8'), iconImage = '', thumbnailImage = '')
			item = xbmcgui.ListItem(title, iconImage = '', thumbnailImage = '')
			item.setInfo(type="Music", infoLabels={"Title": title})

			txt = ContextMenuColor % ('101.ru Добавить в моё радио')
			uri1 = 'XBMC.RunPlugin(%s?%s)' % (sys.argv[0],urllib.urlencode({'mode':'addtracktofavorites', 'id':id}))
			item.addContextMenuItems([(txt, uri1)], replaceItems=False)
			xbmcplugin.addDirectoryItem(plugin_handle, uri, item, False)
			
		offset = re.compile('id="offset(.+?)"><input type="button"').findall(Data)
		
		if offset:i=i+1;furl=furl+'&offset='+offset[0]
		else: i=3
	
	if offset:
		uri = u'%s?%s' % (sys.argv[0], urllib.urlencode({'mode':'findtracks', 'offset':offset[0], 'ftext':ftext}))
		item = xbmcgui.ListItem(ContextMenuColor % ('ЕЩЁ РЕЗУЛЬТАТЫ'), iconImage = '', thumbnailImage = '')
		xbmcplugin.addDirectoryItem(plugin_handle, uri, item, True)
	
	xbmcplugin.endOfDirectory(plugin_handle)	
	
def addtracktofavorites(params):	
	url_=url['addtracktofavorites']+params['id']
	authkey=_addon.getSetting('authkey').split('::')	
	Headers ={'X-Requested-With':'XMLHttpRequest',
		   'Referer'		 :'http://101.ru/?an=personal_edit&userid='+_addon.getSetting('userid'),
		   'Cookie'			 :'autologin='+authkey[2]+'; login='+authkey[1]
		   }
	
	Data = Get_url(url_, Headers, JSON=False)
	js = json.loads(Data)
		
	xbmc.log('[101.ru] %s' % (str(js['message'].encode('UTF-8'))), xbmc.LOGERROR)
	xbmcgui.Dialog().ok(_addon_name, str(js['message'].encode('UTF-8')))

def addcurrenttrack(params):
	if not xbmc.Player().isPlayingAudio():
		xbmc.executebuiltin("XBMC.Notification(plugin.audio.101, Audio не проигрывается, 5000)")
		return
	
	playlist = xbmc.PlayList(xbmc.PLAYLIST_MUSIC)
	try:
		cur = playlist[0].getLabel2()
		cur=cur.split('-')
		if cur[0] != 'plugin.audio.101': raise
		cur_id=cur[1]
		cur_pm=cur[2]
	except:
		xbmc.executebuiltin("XBMC.Notification(plugin.audio.101, Ошибка или Радио не 101.ru, 5000)")
		return
		
	if cur_pm == 'track':		
		param = {}
		param['id']  = cur_id
		addtracktofavorites(param)		
	else:#elif (cur_pm == 'json') or (cur_pm == 'rtmp'):
		url_ = url['getplayingtrackinfo']+cur_id
		
		js = Get_url(url_, JSON=True)
		if js:
			param = {}
			param['id']  = js['id']
			addtracktofavorites(param)
					
#---------------------------
params = get_params()
mode = None
try:
	mode = params["mode"]
except:
	pass
if   mode == None:
	getgroup()	
elif mode == 'getmyst':
	getmyst(params)	
elif mode == 'getmytracks':
	getmytracks(params)	
elif mode == 'getstations':
	getstations(params)
elif mode == 'izbrannoe':
	izbrannoe(params)
elif mode == 'play':
	play(params)
elif mode == 'addfavorite':
	addfavorite(params)
elif mode == 'delfavorite':
	delfavorite(params)
elif mode == 'addtracktofavorites':
	addtracktofavorites(params)
elif mode == 'deletefavoritetrack':
	deletefavoritetrack(params)
elif mode == 'findtracks':
	findtracks(params)
elif mode == 'addtracktofavorites':
	addtracktofavorites(params)
elif mode == 'addcurrenttrack':
	addcurrenttrack(params)

