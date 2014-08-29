#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib, urllib2, re, sys, os, json, datetime
import xbmcplugin, xbmcgui, xbmcaddon, xbmc
from BeautifulSoup import BeautifulSoup, CData as CData1

_addon_name 	= 'plugin.video.peers.tv'
_addon 			= xbmcaddon.Addon(id = _addon_name)
_addon_url		= sys.argv[0]
plugin_handle	= int(sys.argv[1])
_addon_patch 	= xbmc.translatePath(_addon.getAddonInfo('path'))
if sys.platform == 'win32': _addon_patch = _addon_patch.decode('utf-8')

#sys.path.append(os.path.join(_addon_patch, 'resources', 'lib'))
xbmcplugin.setContent(plugin_handle, 'movies')

User_Agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:31.0) Gecko/20100101 Firefox/31.0'

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

def checkproxy(proxy):
	try:
		proxy_h = urllib2.ProxyHandler({'http': proxy})
		opener = urllib2.build_opener(proxy_h)

		opener.addheaders = [('User-agent', User_Agent)]
		urllib2.install_opener(opener)
		req=urllib2.Request('http://www.google.com')
		response=urllib2.urlopen(req)
		if (response.read().index('<title>Google</title>'))>=0:
			return True
	except:
		return False
	return True
	
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
	return Data

def getchannels():
	if _addon.getSetting("proxy")=='true': proxy=_addon.getSetting("proxyip") 
	else: proxy=''
	Data  = Get_url('http://peers.tv', Proxy=proxy)
	if not Data:return(1)
	
	soup = BeautifulSoup(Data)	
	
	cdata = soup.find(text=re.compile("cntv\._cc_program_init = cntv\.program\.init\.bind"))		
	liveurl = re.compile('"url": "(.+?)".+?"stream": "(.+?)"').findall(str(cdata))	
	distlu={}
	for lu in liveurl:
		distlu[lu[0]]=str(lu[1]).replace('\\', '')

	progch = soup.find('dl', id="prog-chalist")
	alltega= progch.findAll('a')

	if alltega:
		for tega in alltega:
			try:
				locked=tega['class']
			except:
				locked=''
			
			channelAlias = re.match('/program/(.+?)/' ,tega['href']).group(1)			
			channelId    = tega['data-id']
			img          = tega.i.img['src']
			title =tega.b.contents[0].encode('UTF-8')
			if locked:
				title = '[L] '+title
				
			
			oldpng = re.search('/([0-9]+?).png', img).group(1)
			newpng = img.replace(oldpng, str(int(oldpng)-2))		
			img = 'http://peers.tv'+newpng 

			uri = '%s?%s' % (sys.argv[0], urllib.urlencode({'mode':'getprogram' if _addon.getSetting("arh")=='true' else 'getmenu', 'id':channelId, 'channelAlias':channelAlias,'liveurl':distlu[channelAlias]}))
			item = xbmcgui.ListItem(title, iconImage = img, thumbnailImage = img)
			item.setInfo(type="Video", infoLabels={"Title": title})
			xbmcplugin.addDirectoryItem(plugin_handle, uri, item, True)					
		xbmcplugin.endOfDirectory(plugin_handle)

def getmenu(params):	
	liveurl = urllib.unquote_plus(params['liveurl'])
	uri = '%s?%s' % (sys.argv[0], urllib.urlencode({'mode':'play','title':'' ,'playurl':liveurl}))
	item = xbmcgui.ListItem('Прямая трансляция', iconImage = '', thumbnailImage = '')
	xbmcplugin.addDirectoryItem(plugin_handle, uri, item, False)
	
	uri = '%s?%s' % (sys.argv[0], urllib.urlencode({'mode':'getprogram', 'id':params['id'], 'channelAlias':params['channelAlias'], 'liveurl':liveurl}))
	item = xbmcgui.ListItem('АРХИВ', iconImage = '', thumbnailImage = '')
	xbmcplugin.addDirectoryItem(plugin_handle, uri, item, True)					
		
	xbmcplugin.endOfDirectory(plugin_handle)
				
def getprogram(params):
	liveurl = urllib.unquote_plus(params['liveurl'])	
	updateListing=True
	try:
		prgdate = urllib.unquote_plus(params["date"])
	except:
		prgdate = datetime.date.today().strftime('%m/%d/%Y ')
		updateListing=False
		
	prgdate_url = prgdate[6:10]+'-'+prgdate[0:2]+'-'+prgdate[3:5]
	url_ = 'http://peers.tv/ajax/program/%s/%s/'%(params['id'],prgdate_url)	
	
	if _addon.getSetting("proxy")=='true': proxy=_addon.getSetting("proxyip") 
	else: proxy=''
	js = Get_url(url_,JSON=True, Proxy=proxy)
	if not js:return(1)
	
	prgdatelst   = js['week']
	if _addon.getSetting("sort")=='0':
		prgdatelst.reverse()
	prgdate      = js['date']
	prgtelecasts = js['telecasts']
	
	for k in prgdatelst:
		if k['recs']==True:
			prgtitle = k['date'][3:5]+'/'+k['date'][0:2]+'/'+k['date'][6:10]
			uri = '%s?%s' % (sys.argv[0], urllib.urlencode({'mode':'getprogram', 'id':params['id'], 'date':k['date'], 'channelAlias':params['channelAlias'], 'liveurl':liveurl}))
			item = xbmcgui.ListItem(prgtitle, iconImage = '', thumbnailImage = '')
			xbmcplugin.addDirectoryItem(plugin_handle, uri, item, True)	
		
		if (k['date']==prgdate)and((updateListing) or (_addon.getSetting("opendey")=='true')):
			for i in prgtelecasts:
				title = i['title'].encode('UTF-8')
				chinfo  = i['info'].encode('UTF-8')
				title_time =str(i['time'])[11:16]+'-'+ str(i['ends'])[11:16]+' '
				qqq = title_time+title							
				img ='http://peers.tv'+i['image']				
				filesurl=''
				
				try:
					onair =i['onair']
				except:
					onair =''							
				
				ctitle = title
				if onair:
					ctitle = '[COLOR FFE169E1]%s[/COLOR]'%(title)
					filesurl = liveurl		
				else:
					for j in i['files']:
						filesurl = j['movie']	
					if filesurl: 
						ctitle = '[COLOR FF4169E1]%s[/COLOR]'%(title)
							
				info = {}
				info["title"] = title
				info['plot']  = i['desc'].replace('&nbsp;',' ').replace('&laquo;', '"').replace('&raquo;', '"').replace('&mdash;', '-').replace('<br />',chr(13)).replace('&#x2011;', '-')
				
				uri = '%s?%s' % (sys.argv[0], urllib.urlencode({'mode':'play','title':chinfo+': '+title ,'playurl':filesurl}))
				item = xbmcgui.ListItem('    '+title_time+ctitle, iconImage = img, thumbnailImage = img)
				item.setProperty('fanart_image', img)
				item.setInfo(type="Video", infoLabels=info)
				xbmcplugin.addDirectoryItem(plugin_handle, uri, item, False)				
	xbmcplugin.endOfDirectory(plugin_handle, updateListing=updateListing)

def play(params):	
	if (params['playurl']==''):return None		
	
####################3	
	title = urllib.unquote_plus(params['title'])
	Url_  = urllib.unquote_plus(params['playurl'])	

	playList = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
	playList.clear()	
	
	item = xbmcgui.ListItem(title, iconImage = '', thumbnailImage = '')
	item.setInfo(type="Video", infoLabels={"Title":title})				
				
	playList.add(Url_,item)
	xbmc.Player().play(playList)
		
############################	
#	title = urllib.unquote_plus(params['title'])
#	Url_  = urllib.unquote_plus(params['playurl'])	
#	
#	Data=Get_url(Url_)
#	links = re.compile('(http://.+?\.ts)').findall(Data)
#	
#	#print links
#	
#	#sys.exit()
#	
#	playList = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
#	playList.clear()
#		
#			
#	for Url_ in links:
#		Url_ = Url_ .replace('/16/','/126/')
#		print Url_ 
#		item = xbmcgui.ListItem(title, iconImage = '', thumbnailImage = '')
#		item.setInfo(type="Video", infoLabels={"Title":title})		
#		playList.add(Url_,item)
#	xbmc.Player().play(playList)
#		
################################
	

#---------------------------
params = get_params()
mode = None
try:
	mode = params["mode"]
except:
	pass
if   mode == None:
	getchannels()
elif mode == 'getprogram':
	getprogram(params)
elif mode == 'getmenu':
	getmenu(params)	
elif mode == 'play':
	play(params)
