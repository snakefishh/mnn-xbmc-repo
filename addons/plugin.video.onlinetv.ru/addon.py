#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib, urllib2, re, sys, os, json, datetime
import xbmcplugin, xbmcgui, xbmcaddon, xbmc
from BeautifulSoup import BeautifulSoup
from urlparse import urlparse
_addon_name 	= 'plugin.video.onlinetv.ru'
_addon 			= xbmcaddon.Addon(id = _addon_name)
_addon_url		= sys.argv[0]
plugin_handle	= int(sys.argv[1])
_addon_patch 	= xbmc.translatePath(_addon.getAddonInfo('path'))
if sys.platform == 'win32': _addon_patch = _addon_patch.decode('utf-8')

#xbmcplugin.setContent(plugin_handle, 'movies')

User_Agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:31.0) Gecko/20100101 Firefox/31.0'

	
def Get_url(url, headers={}, Post = None, GETparams={}, JSON=False, Proxy=None):
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
		xbmc.log('['+_addon_name+'] %s' % e, xbmc.LOGERROR)
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
			xbmc.log('['+_addon_name+'] %s' % e, xbmc.LOGERROR)
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
	AddItem('Новости Дня', url={'mode':'News'})
	AddItem('Проекты',     url={'mode':'Projects'})
	AddItem('Весь Архив',  url={'mode':'GetArchive', 'page':1})
	xbmcplugin.endOfDirectory(plugin_handle)
	
def News(params):
	Data  = Get_url('http://www.onlinetv.ru/')
	if not Data:return(1)	
	soup = BeautifulSoup(Data)	
	url=soup('a', id="menu_news")[0]['href']
	if not url: return(1)
	Play({'url':url, 'redirect':False})
	
def Projects(params):
	Data  = Get_url('http://www.onlinetv.ru/')
	if not Data:return(1)	
	soup = BeautifulSoup(Data)	
	li = soup('li', 'top_submenu-list_item')
	for i in range(0,len(li)):
		soup = BeautifulSoup(str(li[i]))
		project_id = re.compile('/project/(.+?)/').findall(str(soup('a')[0]['href']))[0]
		AddItem(soup('a')[0].string.encode('UTF-8'), url={'mode':'GetArchive', 'project_id':project_id, 'page':1})
	xbmcplugin.endOfDirectory(plugin_handle)	
	
def GetArchive(params):
	try:
		project_id= params['project_id']
	except:
		project_id= None
		
	page= int(params['page'])
	if project_id: 
		url ='http://www.onlinetv.ru/arch_load/?project_id=%s&page=%s' %(project_id, page)
	else:
		url ='http://www.onlinetv.ru/arch_load/?page=%s' %(page)
	Data  = Get_url(url)
	if not Data:return(1)
	soup = BeautifulSoup(Data)
	tPage = int(soup.find('input', id='pnum')['value'])

	for br in soup.findAll('br'):
		br.extract()
	
	subitem_project = soup('div', 'subitem')
	for i in range(0,len(subitem_project)):
		soup = BeautifulSoup(str(subitem_project[i]))
		href  = soup('a', 'name')[0]['href']
		href = href.replace('&trailer=1', '')
		title = str(soup('a', 'name')[0].string)
		AddItem(title, url={'mode':'Play', 'url':href,'redirect':True})	
	if page < tPage:
		if project_id:
			itemUrl= {'mode':'Project', 'project_id':params['project_id'], 'page':str(page+1)}
		else:
			itemUrl= {'mode':'Project', 'page':str(page+1)}
		AddItem('Далее >  '+str(page+1)+' из ' +str(tPage), url=itemUrl)
	xbmcplugin.endOfDirectory(plugin_handle)
		
def Play(params):
	redirect = params['redirect']
	url ='http://www.onlinetv.ru'+urllib.unquote(params['url'])
	Data  = Get_url(url)
	
	soup = BeautifulSoup(Data)	
	scr =soup.find(text=re.compile('swfobject.embedSWF'))
	scr= scr.replace(' ','').replace('\n','').replace('\r','')

	swfUrl      = re.compile('swfobject.embedSWF\("(.+?)"').findall(str(scr.encode('UTF-8')))[0]
	rtmpPlay    = re.compile('file:"(.+?)"').findall(str(scr.encode('UTF-8')))
	rtmpPlay    = rtmpPlay[0].split(',')
	if len(rtmpPlay)==2:
		rtmpPlayHQ  = ('mp4:' if redirect else '')+ rtmpPlay[1]
	else:
		rtmpPlayHQ =('mp4:' if redirect else '')+ rtmpPlay[0]  #None
	rtmpPlay    = ('mp4:' if redirect else '')+ rtmpPlay[0]
	tcUrl       = re.compile('streamer:"(.+?)"').findall(str(scr.encode('UTF-8')))[0]
	tcUrl       = 'rtmp://213.85.95.122:1935/archive' if redirect else tcUrl.split('::')[0]
	app         = 'archive' if redirect else urlparse(tcUrl).path[1::]
		
	mobileVideo = re.compile('sourcesrc="(.+?)"').findall(str(scr.encode('UTF-8')))[0]

	dialog = xbmcgui.Dialog()
	dlg= dialog.select('Выбор потока:', ['Высокое качество', 'Среднее качество', 'Поток для мобильных'])
	if dlg==2:
		link = mobileVideo
	else:
		if dlg==0:
			link=tcUrl+rtmpPlayHQ+' app='+app+' swfUrl='+swfUrl+' PlayPath='+rtmpPlayHQ
		else:
			link=tcUrl+rtmpPlay+' app='+app+' swfUrl='+swfUrl+' PlayPath='+rtmpPlay
			
	item = xbmcgui.ListItem('', iconImage = '', thumbnailImage = '')
	item.setInfo(type="Video", infoLabels={"Title":''})

	#item.setProperty('mimetype', 'video/flv')
	#item.setProperty('flashVer', 'WIN 15,0,0,152')
	xbmc.Player().play(link, item) 
