#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib, urllib2, re, sys, os, json, datetime, time
import xbmcplugin, xbmcgui, xbmcaddon, xbmc
from lib import *
from BeautifulSoup import BeautifulSoup
from urlparse import urlparse
addon_name 	= 'plugin.video.cxz.to'
addon 		= xbmcaddon.Addon(id = addon_name)
addon_data_path= xbmc.translatePath(os.path.join("special://profile/addon_data", addon_name))
if (sys.platform == 'win32') or (sys.platform == 'win64'):
	addon_data_path = addon_data_path.decode('utf-8')

plugin_handle	= int(sys.argv[1])
xbmcplugin.setContent(plugin_handle, 'movies')
site_url='http://cxz.to'

#AARRGGBB
clGreen	     = '[COLOR FF008000]%s[/COLOR]' 
clDodgerblue = '[COLOR FF1E90FF ]%s[/COLOR]'
clDimgray 	 = '[COLOR FF696969 ]%s[/COLOR]'
clAliceblue  = '[COLOR FFF0F8FF ]%s[/COLOR]'

Headers={}####################################


def Login(login, passw):
	url = site_url+'/login.aspx'
	Post={'login':login, 'passwd':passw, 'remember':'1'}
	Data =Get_url(url, Post=Post, Cookie=True)
	return Data

def Get_url_lg(url, headers={}, Post = None, GETparams={}, JSON=False, Proxy=None):

	login =addon.getSetting('User')
	passw =addon.getSetting('password')
	old_login =addon.getSetting('oldUser')
	old_passw =addon.getSetting('oldpassword')

	if (old_login!=login)or(passw!=old_passw):
		DelCookie()
		addon.setSetting('oldUser', login)
		addon.setSetting('oldpassword', passw)

	Data = Get_url(url, headers, Post, GETparams, JSON, Proxy, Cookie=(login and passw))

	if login and passw:
		Soup = BeautifulSoup(Data)
		lg = Soup.find('a', 'b-header__user-profile')
		if not lg:
			DelCookie()
			LgData= Login(login, passw)
			Soup = BeautifulSoup(LgData)
			lg = Soup.find('a', 'b-header__user-profile')
		else:
			return True, Data
		if not lg:
			xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")' % (addon_name, 'Ошибка Авторизации', 100, 100))
		else:
			return True, LgData
	return False, Data

def start(params):
	try:
		href= urllib.unquote_plus(params['href'])
	except:
		href=''
	url = site_url+href
	Login, Data =Get_url_lg(url)
	Soup = BeautifulSoup(Data)

	if Login:
		AddFolder('Избранное', 'Favourites')
	AddFolder('Поиск', 'SearchDlg')

	#header_menu = Soup.find('div', 'b-header__menu')
	header_menu_section = Soup.findAll('a', 'b-header__menu-section-link')
	for section in header_menu_section:
		title = section.string.encode('UTF-8')
		AddFolder(title, 'Cat', {'href':section['href']})

	#title = 'Самое просматриваемое'
	#AddFolder(title, 'MostViewed')

	AddItem('_'*30+chr(10)+' ')

	pr_page   = Soup.find('a', 'previous-link')
	if pr_page:
		pr_page= pr_page['href']
		pg = re.compile('page=(\d+?$)').findall(pr_page)
		if pg:
			pg =int(pg[0])+1
		else:
			pg=1
		AddFolder(clGreen%('< Страница '+str(pg)),'',{'href':pr_page,'upd':'upd'})
	else:
		pg=0

	section_list = Soup.find('div', 'b-section-list')
	poster_detail = section_list.findAll('a', 'b-poster-detail__link')
	for pop in poster_detail:
		href = pop['href']
		img   = pop.find('img' ,src=True)['src']
		imgup = img.replace('/6/', '/1/')
		title = pop.find('span', 'b-poster-detail__title').string
		field = pop.find('span', 'b-poster-detail__field').string
		title +='  '+field

		ContextMenu=[]
		if Login:
			cmenu={'mode'  :'ADFav',
				   'mode2' :'favorites',
				   'mode3' :'add',
				   'href'  :href}
			cmenu1=cmenu.copy()
			cmenu1['mode2']='forlater'
			ContextMenu = [(clAliceblue%('cxz.to Добавить В Избранное'), 'XBMC.RunPlugin(%s)'%uriencode(cmenu)),
						   (clAliceblue%('cxz.to Отложить на Будущее'), 'XBMC.RunPlugin(%s)'%uriencode(cmenu1))]
		AddFolder(title.encode('UTF-8'), 'Content', {'href':href}, img=imgup, ico=img, cmItems=ContextMenu)

	next_page = Soup.find('a', 'next-link')
	if next_page:
		next_page =next_page['href']
		AddFolder(clGreen%('Страница '+str(pg+2)+' >'),'',{'href':next_page,'upd':'upd'})

	try:
		upd = params['upd']=='upd'
	except:
		upd=False
	xbmcplugin.endOfDirectory(plugin_handle, updateListing=upd)

def MostViewed(params):
	url = site_url
	Data =Get_url(url)
	Soup = BeautifulSoup(Data)
	nowviewed = Soup.find('div', 'b-nowviewed__posters')
	posters = nowviewed.findAll('a', 'b-poster-new__link')
	for poster in posters:
		href = poster['href']
		title = poster.find('span', 'm-poster-new__short_title').string
		st_img = poster.find('span', 'b-poster-new__image-poster')['style']
		img=re.compile("url\('(.+?)'\)").findall(st_img)[0]
		imgup = img.replace('/6/', '/1/')
		AddFolder(title.encode('UTF-8'), 'Content', {'href':href}, img=imgup, ico=img)
	xbmcplugin.endOfDirectory(plugin_handle)

def Cat(params):
	url =site_url+urllib.unquote_plus(params['href'])
	Login, Data =Get_url_lg(url)
	Soup = BeautifulSoup(Data)
	tega=Soup.findAll('a', 'b-poster-tile__link')

	pr_page   = Soup.find('a', 'previous-link')
	if pr_page:
		pr_page= pr_page['href']
		pg = re.compile('page=(\d+?$)').findall(pr_page)
		if pg:
			pg =int(pg[0])+1
		else:
			pg=1
		AddFolder(clGreen%('< Страница '+str(pg)),'Cat',{'href':pr_page,'upd':'upd'})
	else:
		pg=0

	for a in tega:
		href = 	a['href']
		img = a.find('img')['src']
		imgup = img.replace('/6/', '/1/')
		title  = a.find('span', 'b-poster-tile__title-full').string.replace('\t','').replace('\n', '')
		detail = a.find('span', 'b-poster-tile__title-info-items').string

		ContextMenu=[]
		if Login:
			cmenu={'mode'  :'ADFav',
				   'mode2' :'favorites',
				   'mode3' :'add',
				   'href'  :href}
			cmenu1=cmenu.copy()
			cmenu1['mode2']='forlater'
			ContextMenu = [(clAliceblue%('cxz.to Добавить В Избранное'), 'XBMC.RunPlugin(%s)'%uriencode(cmenu)),
						   (clAliceblue%('cxz.to Отложить на Будущее'), 'XBMC.RunPlugin(%s)'%uriencode(cmenu1))]
		AddFolder(title.encode('UTF-8')+'  '+detail.encode('UTF-8'),'Content',{'href':href}, img=imgup,ico=img, cmItems=ContextMenu)

	next_page = Soup.find('a', 'next-link')
	if next_page:
		next_page =next_page['href']
		AddFolder(clGreen%('Страница '+str(pg+2)+' >'),'Cat',{'href':next_page,'upd':'upd'})

	try:
		upd = params['upd']=='upd'
	except:
		upd=False
	xbmcplugin.endOfDirectory(plugin_handle, updateListing=upd)

def Favourites(params):
	AddFolder('В процессе',    'Favourites2', {'page':'inprocess'})
	AddFolder('Рекомендуемое', 'Favourites2', {'page':'recommended'})
	AddFolder('Избранное',     'Favourites2', {'page':'favorites'})
	AddFolder('На будущее',    'Favourites2', {'page':'forlater'})
	AddFolder('Я рекомендую',  'Favourites2', {'page':'irecommended'})
	AddFolder('Завершенное',   'Favourites2', {'page':'finished'})
	xbmcplugin.endOfDirectory(plugin_handle)

def Favourites2(params):
	url =site_url+'/myfavourites.aspx?page='+params['page']
	Login, Data =Get_url_lg(url)
	if not Login:return
	Soup= BeautifulSoup(Data)
	category = Soup.findAll('div', 'b-category')
	for cat in category:
		title = cat.find('span', 'section-title').b.string
		rel = cat.find('a', 'b-add')['rel']
		rel=rel.replace('{','').replace('}','').replace(' ','').replace("'",'')
		rel= rel.split(',')
		section    =rel[0].split(':')[1]
		subsection =rel[1].split(':')[1]
		url ={'section':section, 'subsection':subsection, 'page':params['page'], 'curpage':'0'}
		AddFolder(title.encode('UTF-8'), 'GetFavourites', url)
	xbmcplugin.endOfDirectory(plugin_handle)

def GetFavourites(params):
	curpage= params['curpage']
	page = params['page']
	url = site_url+'/myfavourites.aspx?ajax&'
	ajax={
		'section'    :params['section'],
		'subsection' :params['subsection'],
		'rows'       :'2',
		'curpage'    :curpage,
		'action'     :'get_list',
		'setrows'    :'4',
		'page'       : page
		}
	url += urllib.urlencode(ajax)
	js = Get_url(url, JSON=True, Cookie=True)
	maxpages = js['maxpages']
	Data= js['content']
	Soup = BeautifulSoup(Data)
	tega = Soup.findAll('a')

	if (int(curpage)>0):
		url ={'section':params['section'], 'subsection':params['subsection'], 'page':params['page'],
			  'curpage':str(int(curpage)-1),'upd':'upd'}
		AddFolder(clGreen%('< Страница '+str(int(curpage))), 'GetFavourites', url)
	for a in tega:
		href = a['href']
		img  = re.compile("url\s*\('(.+?)'\)").findall(a['style'])[0]
		imgup = img.replace('/13/', '/1/')
		title= a.find('span').string

		ContextMenu=[]
		if page!='recommended':
			cmenu={'mode'  :'ADFav',
				   'mode2' :page,
				   'mode3' :'del',
				   'href'  :href}
			ContextMenu = [(clAliceblue%('cxz.to Удалить Из Категории'), 'XBMC.RunPlugin(%s)'%uriencode(cmenu))]
		AddFolder(title.encode('UTF-8'), 'Content',{'href':href}, img=imgup, ico=img, cmItems=ContextMenu)

	if (int(curpage)<int(maxpages)-1):
		url ={'section':params['section'], 'subsection':params['subsection'], 'page':page,
			  'curpage':str(int(curpage)+1),'upd':'upd'}
		AddFolder(clGreen%('Страница '+str(int(curpage)+2)+' >'), 'GetFavourites', url)

	try:
		upd = params['upd']=='upd'
	except:
		upd=False
	xbmcplugin.endOfDirectory(plugin_handle, updateListing=upd)

def SearchDlg(params):
	Kb = xbmc.Keyboard()
	Kb.setHeading('Поиск')
	Kb.doModal()
	if not Kb.isConfirmed(): return
	search = Kb.getText()
	Search({'search':search, 'page':'0'})

def Search(params):
	def parse(page):
		page = page['href']
		page = page.split('?')[1].split('&')
		nsearch = page[0].split('=')[1].encode('UTF-8')
		if len(page)==2:
			npage   = page[1].split('=')[1]
		else:
			npage='0'
		return  nsearch, npage

	url= site_url+'/search.aspx?search='+params['search']+'&page='+params['page']

	Login, Data =Get_url_lg(url)

	Soup = BeautifulSoup(Data)
	try:
		Sresult = Soup.find('div', 'main')
		Sresult =Sresult.findAll('table', recursive=False)
	except:
		xbmcMessage('Ничего не найдено', 7000)
		return

	pr_page = Soup.find('a', 'previous-link')
	if pr_page:
		ps = parse(pr_page)
		AddFolder(clGreen%('< Страница '+str(int(ps[1])+1)),'Search',{'search':ps[0], 'page':str(ps[1]),'upd':'upd'})

	for table in Sresult:
		tr_s = table.findAll('tr', recursive=False)
		for tr in tr_s:
			a = tr.find('a', 'title')
			href  = a['href']
			title = a.string
			img = tr.find('img')['src']
			imgup = img.replace('/5/', '/1/')

			ContextMenu=[]
			if Login:
				cmenu={'mode'  :'ADFav',
					   'mode2' :'favorites',
					   'mode3' :'add',
					   'href'  :href}
				cmenu1=cmenu.copy()
				cmenu1['mode2']='forlater'
				ContextMenu = [(clAliceblue%('cxz.to Добавить В Избранное'), 'XBMC.RunPlugin(%s)'%uriencode(cmenu)),
							   (clAliceblue%('cxz.to Отложить на Будущее'), 'XBMC.RunPlugin(%s)'%uriencode(cmenu1))]
			AddFolder(title, 'Content', {'href':href}, ico=img, img=imgup, cmItems=ContextMenu)

	next_page = Soup.find('a', 'next-link')
	if next_page:
		ps = parse(next_page)
		AddFolder(clGreen%('Страница '+str(int(ps[1])+1)+' >'),'Search',{'search':ps[0], 'page':str(ps[1]), 'upd':'upd'})
	try:
		upd = params['upd']=='upd'
	except:
		upd=False
	xbmcplugin.endOfDirectory(plugin_handle, updateListing=upd)

def Content(params):
	href=urllib.unquote(params['href'])
	url=site_url+href+'?ajax'

	query={}
#	query['download']='1'
#	query['view']='1'
#	query['view_embed']='0'
#	query['blocked']='0'
#	query['folder_quality']='null'
#	query['folder_lang']='null'
#	query['folder_translate']='null'
	try:
		query['folder']=params['rel']
	except:
		query['folder']='0'

	for qr in query:
		url+='&'+qr+'='+query[qr]

	Data =Get_url(url, Cookie=True)
	Soup = BeautifulSoup(Data)

	li = Soup.findAll('li', 'folder')
	isFolders=False
	for l in li:
		a = l.find('a', 'title')
		title= a.string
		if title==None:
			title = l.find('a', 'title').b.string
		lang = a['class']
		lang = re.compile('\sm\-(\w+)\s').findall(lang)
		if lang:
			lang=lang[0].upper()+' '
		else:
			lang=''

		rel = re.compile('\d+').findall(a['rel'])[0]
		size = l.findAll('span','material-size')
		sz=''
		for size_ in size:
			sz+=' '+size_.string
		sz = sz.encode('UTF-8').replace('&nbsp;', ' ')

		details = l.find('span', 'material-details').string
		details =details.encode('UTF-8').replace('&nbsp;', ' ')
		date = l.find('span','material-date').string
		date= date.encode('UTF-8')

		title = '[B]'+lang.encode('UTF-8')+title.encode('UTF-8')+' '+sz+'[/B]'+chr(10)
		title += '      [I]'+clDimgray%(details+' '+date)+'[/I]'
		AddFolder(title, 'Content', {'rel':rel, 'href':href})
		isFolders=True

	li = Soup.findAll('li', 'b-file-new')
	if True:#not isFolders:
		for l in li:
			title = l.find('span', 'b-file-new__material-filename-text')
			if title == None:
				title = l.find('span', 'b-file-new__link-material-filename-text')
			title=title.string
			a= l.find('a', 'b-file-new__link-material-download')
			href = a['href']
			size = a.span.string
			AddItem('   '+title+' '+size,'Play',{'href':href})
	xbmcplugin.endOfDirectory(plugin_handle)

def ADFav(params):
	href = urllib.unquote(params['href'])
	mode = params['mode2']
	if params['mode3']=='add':
		url = site_url+href
		Login, Data =Get_url_lg(url)
		if not Login: return
		Soup=BeautifulSoup(Data)

		add_to = Soup.find('div', 'b-tab-item__add-to')
		infav   =add_to.findAll(True, style='display: none;')

		f = False
		for i in infav:
			future    = i.find('span', 'b-tab-item__add-to-future-inner')
			favourite = i.find('span', 'b-tab-item__add-to-favourite-inner')
			if (future)and(mode=='forlater'): f=True
			if (favourite)and(mode=='favorites'): f = True
		if f:
			xbmcMessage('Материал Уже Есть В Избранном',7000)
			return

	id = re.compile('\/(\w+)-').findall(href)[0]
	url = site_url+'/addto/%s/%s?json'%(mode, id)
	Data =Get_url(url, JSON=True, Cookie=True)
	xbmcMessage(Data['ok'].encode('UTF-8'), 7000)
	if params['mode3']=='del':
		xbmc.sleep(1000)
		xbmc.executebuiltin('Container.Refresh')

def Play(params):

	link = site_url+urllib.unquote(params['href'])

	item = xbmcgui.ListItem('   ', iconImage = '', thumbnailImage = '')
	item.setInfo(type="Video", infoLabels={"Title":'  '})

	xbmc.Player().play(link, item)