#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib, urllib2, re, sys, os, json, datetime, time
from var import *
from filters import *
from  cxz import cxz
from cache import CacheToFile
from kinopoisk import  kinopoisk
import SimpleDownloader as downloader
xbmcplugin.setContent(plugin_handle, 'movies')

def start(params):
	try:
		href= urllib.unquote_plus(params['href'])
	except:
		href='/?view=detailed'
	cxz_data = cxz(AutErrorMessage=True)
	cxz_data.parse(href)

	if cxz_data.login :
		AddFolder('Избранное', 'Favourites')
	AddFolder('Поиск', 'SearchDlg')

	for section in cxz_data.category:
		AddFolder(section['title'], 'Cat', {'href':section['href']})

	if (addon.getSetting('popular')=='true'):
		AddItem('_'*30+chr(10)+' ')
		if cxz_data.previous_link:
				AddFolder(clGreen%('< Страница '+str(cxz_data.pg)), '',{'href':cxz_data.previous_link}, property={'refresh':'1'})
		GetInfoList = CreateCatItems(cxz_data, True)
		if cxz_data.next_link:
				AddFolder(clGreen%('Страница '+str(cxz_data.pg+2)+' >'), '',{'href':cxz_data.next_link}, property={'refresh':'1'})

	upd = xbmc.getInfoLabel('ListItem.Property(refresh)')=='1'
	xbmcplugin.endOfDirectory(plugin_handle, updateListing=upd, cacheToDisc=False)
	if (('GetInfoList' in locals()) and (GetInfoList)): GetMeta(GetInfoList)


def Cat(params):
	cat_href = urllib.unquote_plus(params['href'])
	cxz_data = cxz()
	cxz_data.parse(cat_href)

	CacheToFile('cache').write(cxz_data.filterjs)

	flTitle = 'Фильтр       : '  +cxz_data.group_selected.encode('UTF-8')

	AddItem('Сортировка : '+cxz_data.sort_selected.encode('UTF-8'), 'SetSort', {'cathref':cat_href}, property={'refresh':'1'})
	AddItem(flTitle,'SetFilter', {'cathref':cat_href}, property={'refresh':'1'})
	AddItem('_'*30+chr(10)+' ')

	if cxz_data.previous_link:
		AddFolder(clGreen%('< Страница '+str(cxz_data.pg)), 'Cat',{'href':cxz_data.previous_link}, property={'refresh':'1'})
	GetInfoList = CreateCatItems(cxz_data, False)
	if cxz_data.next_link:
		AddFolder(clGreen%('Страница '+str(cxz_data.pg+2)+' >'), 'Cat',{'href':cxz_data.next_link}, property={'refresh':'1'})

	upd = xbmc.getInfoLabel('ListItem.Property(refresh)')=='1'
	xbmcplugin.endOfDirectory(plugin_handle, updateListing=upd, cacheToDisc=False)

	if GetInfoList: GetMeta(GetInfoList)


def CreateCatItems(cxz_data, mSerials=False):

	GetInfoList=[]
	for cxz in cxz_data.cxzInfo:

		kino_poisk = kinopoisk()
		kpInfo = kino_poisk.GetLocalInfo(str(cxz['href']))
		if kpInfo and 'kinopoisk' in kpInfo:
			kpInfo = kpInfo['kinopoisk']
		else:
			GetInfoList.append({'href':cxz['href'],'title':cxz['title']})
			kpInfo = None

		ctitle =  titleConstruct(cxz, kpInfo, mSerials)

		ContextMenu =    [(clAliceblue%('cxz.to Информация'), 'XBMC.Action(Info)')]
		ContextMenu.append((clAliceblue%('cxz.to Похожие материалы'), 'XBMC.Action(Info)'))
		ContextMenu.append((clAliceblue%('cxz.to Персоны'), 'XBMC.Action(Info)'))
		if cxz_data.login:
			cmenu={'mode'  :'AddToFavorite', 'mode2' :'favorites', 'mode3' :'add', 'href'  :cxz['href']}
			cmenu1=cmenu.copy()
			cmenu1['mode2']='forlater'
			ContextMenu.append((clAliceblue%('cxz.to Добавить В Избранное'), 'XBMC.RunPlugin(%s)'%uriencode(cmenu)))
			ContextMenu.append((clAliceblue%('cxz.to Отложить на Будущее'),  'XBMC.RunPlugin(%s)'%uriencode(cmenu1)))

		if not kpInfo:
			info ={'type':'video','plot':cxz['plot'],'title':cxz['title'],'year':cxz['year'],'cast':cxz['cast'], 'studio':cxz['country']}
		else:
			info ={'type':'video','plot':kpInfo['plot'],'title':cxz['title'],'year':cxz['year'], 'studio':cxz['country'], 'writer':kpInfo['writer'],'genre':kpInfo['genre'], 'originaltitle':kpInfo['originaltitle']}
			if kpInfo['cast']:
				info['cast'] = kpInfo['cast']

		property={'fanart_image':cxz['imgup']}
		AddFolder(ctitle.encode('UTF-8'), 'Content', {'href':cxz['href'], 'title':cxz['title'].encode('UTF-8')}, info=info, img=cxz['imgup'], ico=cxz['img'], cmItems=ContextMenu,property=property)
	if GetInfoList:return GetInfoList
	return False

def SearchDlg(params):
	Kb = xbmc.Keyboard()
	Kb.setHeading('Поиск')
	Kb.doModal()
	if not Kb.isConfirmed(): return
	search = Kb.getText()
	Search({'search':search, 'page':'0'})

def Search(params):
	search = urllib.unquote(params['search'])
	cxz_data = cxz()
	result = cxz_data.search('/search.aspx?search='+search+'&page='+params['page'])

	if result == None:
		dialog = xbmcgui.Dialog()
		if dialog.yesno('Поиск:', 'На cxz.to ничего не найдено. Искать на других сайтах?'):
			External_Search({'plugin':'all', 'command':'Search','search':search})
		return

	ItemNotInfo = []
	for item in result:
		kino_poisk = kinopoisk()
		kpInfo = kino_poisk.GetLocalInfo(str(item['href']))
		if kpInfo and 'kinopoisk' in kpInfo:
			kpInfo = kpInfo['kinopoisk']
		else:
			ItemNotInfo.append({'href':str(item['href']), 'title':str(item['title'].encode('UTF-8'))})

		ctitle =  titleConstruct(item, kpInfo, True)

		ContextMenu=[]
		if cxz_data.login:
			cmenu={'mode'  :'AddToFavorite',
				   'mode2' :'favorites',
				   'mode3' :'add',
				   'href'  :item['href']}
			cmenu1=cmenu.copy()
			cmenu1['mode2']='forlater'
			ContextMenu = [(clAliceblue%('cxz.to Добавить В Избранное'), 'XBMC.RunPlugin(%s)'%uriencode(cmenu)),
						   (clAliceblue%('cxz.to Отложить на Будущее'), 'XBMC.RunPlugin(%s)'%uriencode(cmenu1))]

		if ItemNotInfo:
			info ={'type':'video','plot':item['plot'],'title':item['title']}
			#info ={'type':'video','plot':cxz['plot'],'title':cxz['title'],'year':cxz['year']}
		else:
			info ={'type':'video','plot':kpInfo['plot'],'title':item['title'],'year':item['year'], 'studio':item['country'], 'writer':kpInfo['writer'],'genre':kpInfo['genre'], 'originaltitle':kpInfo['originaltitle']}
			if kpInfo['cast']:
				info['cast'] = kpInfo['cast']

		property={'fanart_image':item['imgup']}
		AddFolder(ctitle.encode('UTF-8'), 'Content', {'href':item['href'], 'title' :item['title'].encode('UTF-8')}, ico=item['img'], img=item['imgup'], info=info, property=property, cmItems=ContextMenu)

	xbmcplugin.endOfDirectory(plugin_handle)
	if ItemNotInfo:
		xbmc.executeJSONRPC('{ "jsonrpc": "2.0", "method": "JSONRPC.NotifyAll", "params": {"sender": "%s", "message": "scrapper", "data":%s}, "id": 1 }'%(addon_name, json.dumps(ItemNotInfo)))


def Content(params):
	ctitle=urllib.unquote(params['title'])
	href=urllib.unquote(params['href'])
	try:
		folder=params['rel']
	except:
		folder='0'

	cxz_ = cxz()
	cxz_fm = cxz_.fileManager(href,folder)

	if folder == '0':
		try:
			xbmcaddon.Addon(id = 'plugin.video.torrenter')
		except:
			pass
		else:
			item = xbmcgui.ListItem('Передать в torrenter',)
			uri = '%s?%s' % ('plugin://plugin.video.torrenter/', urllib.urlencode({'action':'search','url':ctitle}))
			xbmcplugin.addDirectoryItem(int(sys.argv[1]), uri, item, isFolder=True)

		if (addon.getSetting('alt_if_block')=='true') or cxz_.isBlocked:
			try:
				AddFolder((clRed%'Некоторые файлы заблокированы ' if cxz_.isBlocked else '')+ 'Альтернативы', 'External_Search', {'plugin':'all', 'command':'Search','search':ctitle.split('/')[0]})
			except:
				AddFolder((clRed%'Некоторые файлы заблокированы ' if cxz_.isBlocked else '')+ 'Альтернативы', 'External_Search', {'plugin':'all', 'command':'Search','search':ctitle.split('/')[0].encode('UTF-8')})
		AddItem('_'*30+chr(10)+' ','')

	for item in  cxz_fm:
		title = '[B]'+(item['lang'] if 'lang' in item else '')+item['title']+'[/B]'

		if 'filelist' in item['next']:
			AddFolder(title, 'Content_files', {'rel':item['parent'], 'href':href, 'title':ctitle, 'quality_list':item['quality_list']})
		else:
			AddFolder(title, 'Content', {'rel':item['parent'], 'href':href, 'title':ctitle})
	xbmcplugin.endOfDirectory(plugin_handle, cacheToDisc=False)
	addon.setSetting('quality', '0')
	addon.setSetting('VSFull', 'true' if addon.getSetting('VideoSourceB')=='false' else 'false')

def Content_files(params):
	ctitle=urllib.unquote(params['title'])
	href=urllib.unquote(params['href'])
	folder=params['rel']
	quality_list=urllib.unquote(params['quality_list'])
	quality_list = quality_list.split(',')
	cur_quality = int(addon.getSetting('quality'))
	VSFull = (addon.getSetting('VSFull')=='true')
	short_link = (addon.getSetting('short_link')=='true')

	cxz_fm = cxz().fileManager(href,folder)

	if quality_list[0]!='None':
		qSelectTitle = ''
		for i in range(0,len(quality_list)):
			if i == cur_quality:
				ii = clGreen%quality_list[i]
			else:
				ii = quality_list[i]
			qSelectTitle += ii+' '
		AddItem('Качество: '+qSelectTitle, 'Content_files_refresh', {'max':len(quality_list)})


	if VSFull:
		vsTitle = clGreen%'Полный '+'Оптимизированный'
	else:
		vsTitle = 'Полный '+clGreen%'Оптимизированный'
	AddItem('Источник: '+vsTitle, 'Content_files_refresh', {})

	for item in cxz_fm:
		if 'qual' in item:
			qual = item['qual']
		else:
			qual = quality_list[0]

		if (quality_list[0]!='None')and(qual != quality_list[cur_quality])and(qual != quality_list[cur_quality]+'p'):
			continue

		cmenu ={'mode'  :'download', 'href':item['href_dl'], 'title':item['title']}
		ContextMenu = [(clAliceblue%('cxz.to Скачать файл'), 'XBMC.RunPlugin(%s)'%uriencode(cmenu))]

		info={'type':'Video','title':ctitle}
		if '/serials/' in href or '/tvshow/' in href or '/cartoonserials/' in href:
			results=filename2match(item['title'])
			if results:
				info['tvshowtitle']=ctitle
				info['title']=ctitle
				info['season']=results['season']
				info['episode']=results['episode']

		#prop = {}
		#if VSFull or item['only_download']:

		sh_href_dl	= item['href_dl']
		if short_link:
			dl = re.compile('(\.\d+\.\d+\.\d+\.\d+)').findall(sh_href_dl)
			if dl:
				sh_href_dl = sh_href_dl.replace(dl[0], '')
		prop={'IsPlayable':'true'}
		AddItem(('[only Full] ' if item['only_download'] and not VSFull else '')+item['title']+' '+item['size'],'Play',{'href':item['href'], 'href_dl':sh_href_dl, 'only_download':str(item['only_download'])}, info=info, property=prop, cmItems=ContextMenu)
	xbmcplugin.endOfDirectory(plugin_handle)

def Content_files_refresh(params):
	try:
		max = int(params['max'])
	except:
		addon.setSetting('VSFull','false' if addon.getSetting('VSFull')=='true' else 'true')
	else:
		cur_quality = int(addon.getSetting('quality'))

		if cur_quality == max-1:
			addon.setSetting('quality', '0')
		else:
			addon.setSetting('quality', str(cur_quality+1))
	xbmc.executebuiltin('Container.Refresh')


def Favourites(params):
	AddFolder('Избранное',     'Favourites_cat', {'page':'favorites'})
	AddFolder('На будущее',    'Favourites_cat', {'page':'forlater'})
	AddFolder('В процессе',    'Favourites_cat', {'page':'inprocess'})
	AddFolder('Завершенное',   'Favourites_cat', {'page':'finished'})
	AddFolder('Рекомендуемое', 'Favourites_cat', {'page':'recommended'})
	AddFolder('Я рекомендую',  'Favourites_cat', {'page':'irecommended'})
	#AddFolder('Персоны',       'GetPersonFav')
	xbmcplugin.endOfDirectory(plugin_handle)

#TODO Переход по страницам ксли режим без категорий?
def Favourites_cat(params):
	cxz_data = cxz()
	items = cxz_data.favourites_category(params['page'])
	GetInfoList=[]
	for item in items:
		url ={'section':item['section'], 'subsection':item['subsection'], 'page':params['page'], 'curpage':'0'}
		if addon.getSetting('categorize') =='true':
			AddFolder(item['title'].encode('UTF-8'), 'Favourites_cont', url)
		else:
			rez = Favourites_cont(url)
			if rez:
				for i in rez:
					GetInfoList.append(i)
	xbmcplugin.endOfDirectory(plugin_handle)
	if GetInfoList: GetMeta(GetInfoList)

def Favourites_cont(params):
	section = params['section']
	subsection = params['subsection']
	curpage= params['curpage']
	page = params['page']
	categorize = addon.getSetting('categorize')
	cxz_data = cxz()
	data = cxz_data.favourites_content(section, subsection, page, curpage)

	if (int(curpage)>0):
		url ={'section':section, 'subsection':subsection, 'page':page,
			  'curpage':str(int(curpage)-1)}
		AddFolder(clGreen%('< Страница '+str(int(curpage))), 'Favourites_cont', url, property={'refresh':'1'})

	ItemNotInfo = []
	for item in  data['items']:
		kino_poisk = kinopoisk()
		kpInfo = kino_poisk.GetLocalInfo(str(item['href']))

		if kpInfo and 'kinopoisk' in kpInfo:
			kpInfo = kpInfo['kinopoisk']
		else:
			ItemNotInfo.append({'href':str(item['href']), 'title':str(item['title'].encode('UTF-8'))})

		ContextMenu=[]
		if page!='recommended':
			cmenu={'mode'  :'AddToFavorite', 'mode2' :page, 'mode3' :'del', 'href'  :item['href']}
			ContextMenu = [(clAliceblue%('cxz.to Удалить Из Категории'), 'XBMC.RunPlugin(%s)'%uriencode(cmenu))]

		if not kpInfo:
			info ={'type':'video','year':item['year'],'title':item['title']}
			#info ={'type':'video','plot':cxz['plot'],'title':cxz['title'],'year':cxz['year']}
		else:
			info ={'type':'video','plot':kpInfo['plot'],'title':item['title'],'year':item['year'], 'studio':item['country'], 'writer':kpInfo['writer'],'genre':kpInfo['genre'], 'originaltitle':kpInfo['originaltitle']}
			if kpInfo['cast']:
				info['cast'] = kpInfo['cast']

		AddFolder(item['title'].encode('UTF-8'), 'Content',{'href':item['href'], 'title':item['title'].encode('UTF-8')}, img=item['imgup'], ico=item['img'],info=info, cmItems=ContextMenu)

	if data['islast']=='false':
		url ={'section':section, 'subsection':subsection, 'page':page, 'curpage':str(int(curpage)+1)}
		AddFolder(clGreen%('Страница '+str(int(curpage)+2)+' >'), 'Favourites_cont', url, property={'refresh':'1'})

	upd = xbmc.getInfoLabel('ListItem.Property(refresh)')=='1'
	if categorize == 'true':
		xbmcplugin.endOfDirectory(plugin_handle, updateListing=upd)
		if ItemNotInfo:
			xbmc.executeJSONRPC('{ "jsonrpc": "2.0", "method": "JSONRPC.NotifyAll", "params": {"sender": "%s", "message": "scrapper", "data":%s}, "id": 1 }'%(addon_name, json.dumps(ItemNotInfo)))
	else:
		return ItemNotInfo

def AddToFavorite(params):
	href = urllib.unquote(params['href'])
	cxz_data = cxz()
	mess = cxz_data.add_to_favorite(href, params['mode2'], params['mode3'] )
	xbmcMessage(mess.encode('UTF-8'), 7000)
#	if params['mode3']=='del':
#		xbmc.sleep(2000)
#		xbmc.executebuiltin('Container.Refresh')

def AddPersonFav(params):
	pass

def GetPersonFav(params):
	pass

def Play(params):
	#TODO Отделить оптимизированнный

	link    = site_url+urllib.unquote(params['href'])
	link_dl = site_url+urllib.unquote(params['href_dl'])
	
	#################################################

	import 	httplib
	class RedirectH(urllib2.HTTPRedirectHandler):
		def http_error_301(self, req, fp, code, msg, headers): 
			result = urllib2.HTTPRedirectHandler.http_error_301(self, req, fp, code, msg, headers)
			result.status = code
			return result

		def http_error_302(self, req, fp, code, msg, headers):   
			result = urllib2.HTTPRedirectHandler.http_error_302(self, req, fp, code, msg, headers)
			result.status = code			
			return result
	
	request = urllib2.Request(link_dl)
	
	opener = urllib2.build_opener(RedirectH())
	f = opener.open(request)

	link_dl = f.url

	#################################################
	
	only_download = params['only_download']

	if addon.getSetting('VSFull')=='true' or only_download == 'True':
		path = link_dl
		
		
		item = xbmcgui.ListItem(path=path)
		#item.setProperty('mimetype', 'video/flv')
		xbmcplugin.setResolvedUrl(plugin_handle, True, item)	
	
	else:
		try:
			LocalPL = CacheToFile('playlist_cxz').read()
		except:
			LocalPL={}

		file_id = link.split('=')[1]
		try:
			path = LocalPL[file_id]
		except:

			headders = {
			'X-Requested-With':'XMLHttpRequest'
			}

			link = link.replace('view', 'view_iframe')+ '&isStartRequest=true'
			Data = Get_url(link,JSON=True, headers=headders,Cookie=False)

			if not Data: return
			try:
				urls = Data['actionsData']['files']
			except:
				urls =''
			if not urls:return
			pl={}
			for i in urls:
				pl[i['id']]= site_url+i['url']

			CacheToFile('playlist_cxz').write(pl)
			path = pl[file_id]

		#title  = xbmc.getInfoLabel('Listitem.Title')
		item = xbmcgui.ListItem(path=path)

		#item.setInfo('video', infoLabels={'title':title})
		#item.setProperty('mimetype', 'video/flv')

		xbmcplugin.setResolvedUrl(plugin_handle, True, item)
		#xbmc.Player().play(path,item)


def download(params):
	dir  =addon.getSetting('DownloadDir')
	if not os.path.exists(dir):
		xbmcMessage('Неверный путь для загрузки',7000)

	url  = site_url+urllib.unquote(params['href'])
	name= urllib.unquote_plus(params['title'])

	dl = downloader.SimpleDownloader()
	dl.download(name.decode('UTF-8'), {'url': url, 'download_path':dir})

def titleConstruct(cxz, kp, mSerials):
	item_format = addon.getSetting('item_format').decode('UTF-8')
	mark_ser = re.compile('\/s(.+?)\/s').findall(item_format)

	l = lambda s,k: s[k] if k in s  else ' '
	formats = {'/t':l(cxz,'title'), '/y':l(cxz,'year'), '/c':l(cxz,'country'), '/q':l(cxz,'quality'),
			   '/vp':l(cxz,'vote_positive'), '/vn':l(cxz,'vote_negative'), '/h':l(cxz,'href')}
	if mark_ser:
		mark_ser = mark_ser[0]
		if mSerials and 'serials' in cxz['href']:
			item_format = item_format.replace('/s'+mark_ser+'/s', mark_ser)
		else:
			item_format = item_format.replace('/s'+mark_ser+'/s','')

	for f in formats:
		item_format = item_format.replace(f, formats[f])

	return item_format

def GetMeta(data):
	if addon.getSetting('scrab_meta')=='true':
		xbmc.executeJSONRPC('{ "jsonrpc": "2.0", "method": "JSONRPC.NotifyAll", "params": {"sender": "%s", "message": "scrapper", "data":%s}, "id": 1 }'%(addon_name, json.dumps(data)))

#--------------------------------

def External_Search(params):
	import ExtSearch.ExtSearch as ExtSearch
	ExtSearch.LoadPlugins()
	closedir = False
	for p in ExtSearch.Plugins:
		rez = p.Command(params)
		if rez:
			closedir =True
	if closedir: xbmcplugin.endOfDirectory(plugin_handle)
