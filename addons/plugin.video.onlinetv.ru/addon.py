#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib, urllib2, re, sys, os, json, datetime, time
import xbmcplugin, xbmcgui, xbmcaddon, xbmc
from lib import *
from BeautifulSoup import BeautifulSoup
from urlparse import urlparse
addon_name 	= 'plugin.video.onlinetv.ru'
addon 		= xbmcaddon.Addon(id = addon_name)
plugin_handle	= int(sys.argv[1])
xbmcplugin.setContent(plugin_handle, 'movies')
 	
months = {'янв':'1', 'фев':'2', 'мар':'3', 'апр':'4', 'май':'5', 'мая':'5', 'июн':'6', 'июл':'7', 'авг':'8', 'сен':'9', 'окт':'10', 'ноя':'11', 'дек':'12'}

#AARRGGBB
clGreen	     = '[COLOR FF008000]%s[/COLOR]' 
clDodgerblue = '[COLOR FF1E90FF ]%s[/COLOR]'
clDimgray 	 = '[COLOR FF696969 ]%s[/COLOR]'

def start(params):
	AddItem('В Эфире и Анонсы', url={'mode':'Live'})
	AddItem('Новости Дня',      url={'mode':'News'})
	AddItem('Проекты',          url={'mode':'Projects'})
	AddItem('Весь Архив',       url={'mode':'GetArchive', 'page':1, 'dirupd':'0'})
	AddItem('Поиск',            url={'mode':'Search'})
	xbmcplugin.endOfDirectory(plugin_handle)

def Search(params):
	kb = xbmc.Keyboard('', 'Поиск')
	kb.doModal()
	if (not kb.isConfirmed()): return(1)
	q = kb.getText()
	
	url ='http://www.onlinetv.ru/project/search/?q=%s'%(q)
	Data  = Get_url(url)
	if not Data: return(1)
	soup = BeautifulSoup(Data)
	soup = soup.find('div', id='search_result')
	result = soup.findAll('div', 'item')
	for res in result:
		img  = res.find('img', src=True)['src']
		a = res.find('a', 'name')
		title = a.string.encode('UTF-8').replace('&quot;', '"')
		href  = a['href']
		#desc  = res.find('p').string
		prg_name = res.find('h2').a.string.encode('UTF-8')
		dt = res.find('span', 'date').string
		dt_re = re.match('(\d\d?) (.{3}).*? (\d{4})', dt)
		if dt_re:
			mon = months[dt_re.group(2).encode('UTF-8')]		
			day = dt_re.group(1) if len(dt_re.group(1))==2 else '0'+dt_re.group(1)
			dt = day+'/'+mon+'/'+dt_re.group(3)
		else:
			dt = '-/-/-'	
		tcUrl = 'rtmp://213.85.95.122:1935/archive'
		app   = 'archive'
		pr    = 'mp4:'		
		url_ = {'mode':'PlayDlg','title':title, 'url':href,'redirect':'true','tcUrl':tcUrl, 'app':app, 'pr':pr}			
		AddItem('(%s) %s'%(dt.encode('UTF-8'), clDimgray%prg_name+' : '+title), url=url_, ico= img)
	xbmcplugin.endOfDirectory(plugin_handle)
	
def Live(params):
	url ='http://www.onlinetv.ru/'
	Data  = Get_url(url)
	if not Data: return(1)
	soup = BeautifulSoup(Data)
	scr =soup.find(text=re.compile('JSON.stringify'))
	js_str = re.compile('({"data": ?\[.+?\]})').findall(str(scr.encode('UTF-8')))[0]
	js = json.loads(js_str)
	UTC_MCS=re.compile('UTC_MCS ?= ?(\d{16})').findall(Data)[0]
	now = datetime.datetime.utcfromtimestamp(((int(UTC_MCS)//1000)+14400000)//1000)
	for i in js['data']:				
		try:
			pub_date = datetime.datetime.strptime(i['pub_date'], '%Y-%m-%dT%H:%M:%SZ')	
		except TypeError:
			pub_date = datetime.datetime.fromtimestamp(time.mktime(time.strptime(i['pub_date'], '%Y-%m-%dT%H:%M:%SZ')))

		zn= 1 if time.timezone>=0 else -1
		td= datetime.timedelta(hours=abs(time.timezone/(60*60)))
		dt=pub_date-td*zn
		dt_str= dt.strftime('%d/%m %H:%M')
		
		img = 'http://media.onlinetv.ru/resize/160/90/'+i['root_img']
		if pub_date < now:	
			tcUrl = 'rtmp://213.85.95.122:1935/event'
			app   = 'event'	
			pr    = 'no'		
			url = '/video/%s/'%(i['id'])
			url_ = {'mode':'PlayDlg','title':i['header'].encode('UTF-8'), 'redirect':'true', 'tcUrl':tcUrl, 'app':app, 'pr':pr, 'url':url}
			AddItem(clGreen%('В Эфире')+' (%s) '%(dt_str)+i['header'].encode('UTF-8'), url=url_, ico= img)
		else:
			AddItem(clDodgerblue%('Анонс')+ ' (%s)   '%(dt_str)+i['header'].encode('UTF-8'), url={'mode':''},ico= img, isFolder =False)
	xbmcplugin.endOfDirectory(plugin_handle)
		
def News(params):
	Data  = Get_url('http://www.onlinetv.ru/')
	if not Data:return(1)
	soup = BeautifulSoup(Data)
	url=soup('a', id="menu_news")[0]['href']
	if not url: return(1)
	PlayDlg({'url':urllib.quote(url), 'title':'Новости Дня', 'redirect':'false'})
	
def Projects(params):
	Data  = Get_url('http://www.onlinetv.ru/')
	if not Data:return(1)
	soup = BeautifulSoup(Data)
	li = soup('li', 'top_submenu-list_item')
	for i in range(0,len(li)):
		soup2 = BeautifulSoup(str(li[i]))
		project_id = re.compile('/project/(.+?)/').findall(str(soup2('a')[0]['href']))[0]
		top_submenu_info = soup.find('div', 'top_submenu-info_item item'+project_id)
		img = top_submenu_info.find('img', src=True)['src']
		desc = top_submenu_info.find('div', 'top_submenu-description').a.string.encode('UTF-8')
		title = soup2('a')[0].string.encode('UTF-8')
		AddItem(title, ico= img, url={'mode':'GetArchive', 'project_id':project_id, 'page':1, 'dirupd':'0'}, info={'type':'Video', 'plot':desc})#, property={'fanart_image':img})
	xbmcplugin.endOfDirectory(plugin_handle)

def GetArchive(params):
	try:
		project_id= params['project_id']
	except:
		project_id= None	
	updateListing= (True if params['dirupd']=='1' else False)	 	
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
	
	if page>1:
		if project_id:
			itemUrl= {'mode':'GetArchive', 'project_id':params['project_id'], 'page':str(page-1), 'dirupd':'1'}
		else:
			itemUrl= {'mode':'GetArchive', 'page':str(page-1), 'dirupd':'1'}
		ctitle = clGreen%('< Страница '+str(page-1)+' из ' +str(tPage))
		AddItem(ctitle, url=itemUrl)
	
	subitem_project = soup('div', 'subitem')		
	for i in range(0,len(subitem_project)):
		soup = BeautifulSoup(str(subitem_project[i]))	
		href  = soup('a', 'name')[0]['href']
		href = href.replace('&trailer=1', '')
		title = str(soup('a', 'name')[0].string)
		img = soup.find('img', src=True)['src']
		
		dt = soup.find('div', 'time').string
		dt_re = re.match('(\d\d?) (.{3}).*? (\d{4})', dt)
		if dt_re:
			mon = months[dt_re.group(2).encode('UTF-8')]		
			day = dt_re.group(1) if len(dt_re.group(1))==2 else '0'+dt_re.group(1)
			dt = day+'/'+mon+'/'+dt_re.group(3)
		else:
			dt = '-/-/-'
		
		tcUrl = 'rtmp://213.85.95.122:1935/archive'
		app   = 'archive'
		pr    = 'mp4:'		
		url_ = {'mode':'PlayDlg','title':title, 'url':href,'redirect':'true','tcUrl':tcUrl, 'app':app, 'pr':pr}
		AddItem('(%s)  %s'%(dt.encode('UTF-8'), title), url= url_, ico= img)
	if page < tPage:
		if project_id:
			itemUrl= {'mode':'GetArchive', 'project_id':params['project_id'], 'page':str(page+1), 'dirupd':'1'}
		else:
			itemUrl= {'mode':'GetArchive', 'page':str(page+1), 'dirupd':'1'}		
		ctitle = clGreen%('Страница >  '+str(page+1)+' из ' +str(tPage))
		AddItem(ctitle, url=itemUrl)
	xbmcplugin.endOfDirectory(plugin_handle, updateListing= updateListing)
		
def PlayDlg(params):
	def AddI(title, uri):
		item = xbmcgui.ListItem(title)
		xbmcplugin.addDirectoryItem(plugin_handle, uri, item, isFolder=False)		
	uri = sys.argv[0]+'?'
	for i in params:
		uri+= i+'='+params[i]+'&'
	uri += 'mode=Play&'	
	uri_= uri+'qual=1'
	AddI('Высокое качество', uri_)
	uri_= uri+'qual=2'
	AddI('Среднее качество', uri_)
	uri_= uri+'qual=3'
	AddI('Поток для мобильных', uri_)	
	xbmcplugin.endOfDirectory(plugin_handle)

			
def Play(params):
	redirect = params['redirect']
		
	url ='http://www.onlinetv.ru'+urllib.unquote(params['url'])
	title = urllib.unquote(params['title'])
	try:
		tcUrl_ = urllib.unquote(params['tcUrl'])
		pr_ = urllib.unquote(params['pr'])
		app_ = urllib.unquote(params['app'])
	except:
		tcUrl_ = ''
		pr_ = ''
		app_ = ''
	
	Data  = Get_url(url)
	if not Data: return(1)
	
	soup = BeautifulSoup(Data)	
	scr =soup.find(text=re.compile('swfobject.embedSWF'))
	print scr
	if not scr: return None
	scr= scr.replace(' ','').replace('\n','').replace('\r','')

	swfUrl  = re.compile('swfobject.embedSWF\("(.+?)"').findall(str(scr.encode('UTF-8')))[0]
	rtmp    = re.compile('file:"(.+?)"').findall(str(scr.encode('UTF-8')))
	rtmp    = rtmp[0].split(',')
	rtmpPr =  (pr_ if (redirect=='true')and(pr_!='no') else '')
	if len(rtmp)==2:
		rtmpPlayHQ  = rtmpPr + rtmp[1]
	else:
		rtmpPlayHQ =rtmpPr + rtmp[0]  #None
	
	rtmpPlay    = rtmpPr + rtmp[0]
	tcUrl       = re.compile('streamer:"(.+?)"').findall(str(scr.encode('UTF-8')))[0]
	tcUrl       = tcUrl_ if redirect=='true' else tcUrl.split('::')[0]
	app         = app_ if redirect=='true' else urlparse(tcUrl).path[1::]
		
	mobileVideo = re.compile('sourcesrc="(.+?)"').findall(str(scr.encode('UTF-8')))[0]

	xbmc.executebuiltin('Action(Back)')
	if params['qual']=='1':
		link=tcUrl+' app='+app+' swfUrl='+swfUrl+' PlayPath='+rtmpPlayHQ		
	elif params['qual']=='2':
		link=tcUrl+' app='+app+' swfUrl='+swfUrl+' PlayPath='+rtmpPlay
	else:
		link = mobileVideo

	item = xbmcgui.ListItem(title, iconImage = '', thumbnailImage = '')
	item.setInfo(type="Video", infoLabels={"Title":title})
	
	xbmc.Player().play(link, item)
