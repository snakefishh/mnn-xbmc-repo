#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib, urllib2, re, sys, os, json, datetime, time
import xbmcplugin, xbmcgui, xbmcaddon, xbmc
from lib import *
from BeautifulSoup import BeautifulSoup
import cPickle
import SimpleDownloader as downloader

addon_name 	= 'plugin.video.cxz.to'
addon 		= xbmcaddon.Addon(id = addon_name)
addon_data_path= xbmc.translatePath(os.path.join("special://profile/addon_data", addon_name))
if (sys.platform == 'win32') or (sys.platform == 'win64'):
	addon_data_path = addon_data_path.decode('utf-8')

plugin_handle	= int(sys.argv[1])
xbmcplugin.setContent(plugin_handle, 'movies')
site_url='http://cxz.to'

class SiteUrlParse:
	cat=''
	group=''
	fl=[]
	language_custom = ''
	translate_custom = ''
	url_qs={}

	def __init__(self, url):
		from urlparse import urlparse, parse_qs
		urlp        = urlparse(url)

		self.url_qs = parse_qs(urlp.query)
		for i in self.url_qs:
			self.url_qs[i]=self.url_qs[i][0]

		r=re.compile('(film_genre|cast|director|year)/(.+?)[$/]').findall(urlp.path)
		if r:
			self.group = r[0][0]+'/'+r[0][1]

		r = re.compile('/fl_(.+?)[$/]').findall(urlp.path)
		if r:
			self.fl = r[0].split('_')
		r = re.compile('/language_custom_(.+?)[$/]').findall(urlp.path)
		if r:
			self.language_custom = r[0]
		r = re.compile('/translate_custom_(.+?)[$/]').findall(urlp.path)
		if r:
			self.translate_custom = r[0]

		url_path = urlp.path.rstrip('/').lstrip('/')
		self.cat = url_path.split('/')[0]

	def con(self):
		url = '/'+self.cat+'/'
		if self.fl:
			url +='fl_'
			for i in self.fl:
				url += i+'_'
			url = url[:-1]+'/'

		if self.group:
			url +=self.group+'/'
		if self.language_custom:
			url += 'language_custom_'+self.language_custom+'/'
		if self.translate_custom:
			url += 'translate_custom_'+self.translate_custom+'/'
		if self.url_qs:
			url +='?'
			for i in self.url_qs:
				url += i+'='+self.url_qs[i]+'&'
			url = url[:-1]
		return url


Headers={}####################################


def Login(login, passw):
	url = site_url+'/login.aspx'
	Post={'login':login, 'passwd':passw, 'remember':'1'}
	Data =Get_url(url, Post=Post, Cookie=True)
	return Data

def Get_url_lg(url, headers={}, Post = None, GETparams={}, JSON=False, Proxy=None, NoMessage=True):

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
			if not NoMessage: xbmcMessage('Ошибка Авторизации',5000)
		else:
			return True, LgData
	return False, Data

def start(params):

	try:
		href= urllib.unquote_plus(params['href'])
	except:
		href='/?view=detailed'

	url = site_url+href
	Login, Data =Get_url_lg(url, NoMessage=False)
	Soup = BeautifulSoup(Data)

	#AddFolder('readpersons1', 'readpersons1')


	if Login:
		AddFolder('Избранное', 'Favourites')
	AddFolder('Поиск', 'SearchDlg')

	header_menu_section = Soup.findAll('a', 'b-header__menu-section-link')
	for section in header_menu_section:
		title = section.string.encode('UTF-8')
		AddFolder(title, 'Cat', {'href':section['href']+'?view=detailed'})

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
		CreateCatItem(pop, True)

	next_page = Soup.find('a', 'next-link')
	if next_page:
		next_page =next_page['href']
		AddFolder(clGreen%('Страница '+str(pg+2)+' >'),'',{'href':next_page,'upd':'upd'})
	try:
		upd = params['upd']=='upd'
	except:
		upd = False
	xbmcplugin.endOfDirectory(plugin_handle, updateListing=upd, cacheToDisc=True)

def Cat(params):
	cat_href = urllib.unquote_plus(params['href'])
	url =site_url+ cat_href

	Login, Data =Get_url_lg(url)
	Soup = BeautifulSoup(Data)

	sort_selected  = Soup.find('span', 'b-section-controls__sort-selected-item selected').string
	group_selected = Soup.findAll(True, 'b-section-controls__title-item')
	tmp=''
	for i in group_selected:
		try:
			tmp+=i.span.string +','
		except:
			try:
				tmp+=i.h1.string +','
			except:
				pass
	group_selected = tmp[:-1]

	section_menu = Soup.find('div', 'b-section-menu')
	tegul = section_menu.findAll('ul')
	filterjs=[]
	for ul in tegul:
		rec ={}
		menu_title = ul.find('b', 'b-section-menu__item-title')
		if menu_title:
			rec['title']=menu_title.string
			tega = ul.findAll('a')
			items = {}
			for a in tega:
				item_title = a.string
				if not item_title: item_title = a.find('span').string
				if a['href']<>'#':#???????????????????????????
					items[item_title]=a['href']
			rec['items']=items

			filterjs.append(rec)
	try:
		with open(addon_data_path+'/filters','wb') as F:
			cPickle.dump(filterjs,F)
	except:
		if not os.path.exists(addon_data_path):
				os.makedirs(addon_data_path)
		with open(addon_data_path+'/filters','wb') as F:
			cPickle.dump(filterjs,F)

	flTitle = 'Фильтр       : '  + group_selected.encode('UTF-8')
	AddItem('Сортировка : '+sort_selected.encode('UTF-8'), 'SetSort', {'cathref':cat_href})
	AddItem(flTitle,'SetFilter', {'cathref':cat_href})
	AddItem('_'*30+chr(10)+' ')

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

	section_list = Soup.find('div', 'b-section-list')

	poster_detail = section_list.findAll('a', 'b-poster-detail__link')


	for pop in poster_detail:
		CreateCatItem(pop)

	next_page = Soup.find('a', 'next-link')
	if next_page:
		next_page =next_page['href']
		AddFolder(clGreen%('Страница '+str(pg+2)+' >'),'Cat',{'href':next_page,'upd':'upd'})
	try:
		upd = params['upd']=='upd'
	except:
		upd=False
	xbmcplugin.endOfDirectory(plugin_handle, updateListing=upd, cacheToDisc=True)

def CreateCatItem(pop, mSerials=False):
	href = pop['href']
	img   = pop.find('img' ,src=True)['src']
	imgup = img.replace('/6/', '/1/')
	title = pop.find('span', 'b-poster-detail__title').string
	tmp = pop.findAll('span', 'b-poster-detail__field')
	field = tmp[0].string
	year  =re.compile('(\d{4})').findall(field)[0]
	cast = tmp[1].string
	if cast:
		cast = cast.split(',')
	else:
		cast=[]
	plot  = pop.find('span', 'b-poster-detail__description').contents[0]
	vote_positive = pop.find('span', 'b-poster-detail__vote-positive').string
	vote_negative = pop.find('span', 'b-poster-detail__vote-negative').string
	quality = pop.findAll('span', 'quality')
	allquality = ''
	for qual in quality:
		allquality += qual['class'].replace('quality', '').replace('m-','').replace(' ', '')+','
	allquality = allquality[:-1].upper()

	ctitle =('[S] ' if mSerials and 'serials' in href else '')+title+'  '+field+u' (%s ↑%s ↓%s)'%(allquality, AA(clGreen,'80')%vote_positive,AA(clRed,'80')%vote_negative)

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

	info ={'type':'video','plot':plot,'title':title,'year':year,'cast':cast}
	property={'fanart_image':imgup}
	AddFolder(ctitle.encode('UTF-8'), 'Content', {'href':href, 'title':title.encode('UTF-8')}, info=info, img=imgup, ico=img, cmItems=ContextMenu,property=property)

def SetSort(params):
	caturl = SiteUrlParse(urllib.unquote(params['cathref']))
	s=[['в тренде',  'по дате обновления','по рейтингу', 'по году выпуска', 'по популярности'],
	   ['trend',     'new',               'rating',      'year',            'popularity']]
	dialog = xbmcgui.Dialog()
	ret = dialog.select('Сортировка', s[0])
	if ret ==-1:
		return
	caturl.url_qs['sort']=s[1][ret]
	xbmc.executebuiltin('Container.Update(%s?%s)'%(sys.argv[0],urllib.urlencode({'mode':'Cat','href':caturl.con(), 'upd':'upd'})))

def SetGroup(params):

	caturl = SiteUrlParse(urllib.unquote(params['cathref']))

	with open(addon_data_path+'/filters','rb') as F:
			filterjs = cPickle.load(F)
	for fil in filterjs:
		if fil['title'].encode('UTF-8')== 'Группы':
			break

	k = fil['items'].keys()
	dialog = xbmcgui.Dialog()
	ret = dialog.select('Группы', k)
	if ret ==-1:
		return

	var=k[ret].encode('UTF-8')
	if var=='по годам':
		now_year = int(datetime.date.today().year)
		q1 = now_year%10
		q2 = int(now_year//10)*10
		y10 = []
		y10.append(str(q2)+' - '+str(q2+q1))
		for i in range(q2-10,1920,-10):
			y10.append(str(i)+' - '+str(i+9))
		ret = dialog.select('По Годам', y10)
		if ret ==-1:
			return
		y1=[]
		for i in range(int(y10[ret][0:4]), int(y10[ret][-4:])+1):
			y1.append(str(i))
		ret = dialog.select('По Годам', y1)
		if ret ==-1:
			return

		caturl.group = 'year/'+y1[ret]

	elif var == 'по жанрам':
		href = fil['items'][u'по жанрам']

		Data = Get_url(href)
		Soup =BeautifulSoup(Data)
		main = Soup.find('div', 'main')
		tega = main.findAll('a')
		genres={}
		for a in tega:
			try:
				a.parent['class']
			except:
				genres[a.string]='/'.join((a['href'].rstrip('/').lstrip('/')).split('/')[1:])
		g = genres.keys()
		ret = dialog.select('По Жанрам', g)
		if ret ==-1:
			return

		caturl.group=genres[g[ret]]

	elif var =='по режиссёрам':
		if not CheckDB():
			return
		rez = Search_in_bd('films_directors')
		if rez == '0':
			return
		caturl.group ='director/'+rez

	elif var =='по актёрам':
		if not CheckDB():
			return
		rez = Search_in_bd('films_casts')
		if rez == '0':
			return
		caturl.group ='cast/'+rez

	caturl.fl=[]
	caturl.language_custom = ''
	caturl.translate_custom = ''
	xbmc.executebuiltin('Container.Update(%s?%s)'%(sys.argv[0],urllib.urlencode({'mode':'Cat','href':caturl.con(), 'upd':'upd'})))

def CheckDB():
	import zipfile
	if (os.path.exists(addon_data_path+'/films_directors.db'))and(os.path.exists(addon_data_path+'/films_casts.db')):
		return True
	else:
		dialog = xbmcgui.Dialog()
		if dialog.yesno('Установить Базу:','Для поиска по Персонам Необходимо загрузить дополнительную Базу', '        Загрузить Сейчас?'):
			url = 'http://mnn-xbmc-repo.googlecode.com/svn/trunk/addons/plugin.video.cxz.to.db/'
			db = []
			try:
				dir = urllib.urlopen(url).read()
				Soup = BeautifulSoup(dir)
				li = Soup.findAll('li')
				for l in li:
					href = l.a['href']
					if '.zip' in href:
						urllib.urlretrieve(url+'/'+href, addon_data_path+'/'+href)
						zip_handler = zipfile.ZipFile(addon_data_path+'/'+href, 'r')
						zip_handler.extractall(addon_data_path)
				return True
			except:
				xbmcMessage('Не удалось установить Базу, попробуйте позже')
				return False
	return False

def Search_in_bd(base_name):
		import sqlite3

		Kb = xbmc.Keyboard()
		Kb.setHeading('Поиск')
		Kb.doModal()
		if not Kb.isConfirmed(): return '0'
		search = Kb.getText()
		search = search.strip()

		search = search.decode('UTF-8').lower().encode('UTF-8')

		sql_ = 'SELECT name, url FROM data WHERE LOWER(name) LIKE "%%%s%%"'
		if not ' ' in search:
			sql_ = sql_%search
		else:
#			search = search.replace('   ',' ').replace('  ', ' ')
			search = search.split(' ')
			sql_ = sql_+' OR LOWER(name) LIKE "%%%s%%"'
			sql_ = sql_%(search[0]+'%'+search[1], search[1]+'%'+search[0])

		con = sqlite3.connect(addon_data_path+'/'+base_name+'.db')
		con.create_function("LOWER", 1, lambda s:s.lower())
		cur = con.cursor()
		cur.execute(sql_)
		cur.execute(sql_)
		search_db = cur.fetchall()
		cur.close()

		dialog = xbmcgui.Dialog()
		if not search_db:
			dialog.ok('','Ничего не найдено')
			return '0'
		dlgzn = []
		for i in search_db:
			dlgzn.append(i[0])

		dlg = dialog.select('1111111',dlgzn)
		if dlg == -1:return '0'
		rez = search_db[dlg][1]
		if rez[len(rez)-1]=='/':
			rez = rez[:-1]
		rez = rez.split('/')
		rez = rez[len(rez)-1]
		return rez

def SetFilter(params):
	caturl = SiteUrlParse(urllib.unquote(params['cathref']))
	with open(addon_data_path+'/filters','rb') as F:
			filterjs = cPickle.load(F)

	dialog = xbmcgui.Dialog()

	while True:
		f=[]
		for fil in filterjs:
			try:    check = fil['check']
			except: check = ''
			title = fil['title'].encode('UTF-8')
			if check:
				title += '  : '+check
			f.append(title)
		f.append(clGreen%'             [B]Применить/Сброс[/B]')

		ret = dialog.select('Фильтр', f)
		if ret ==-1:
			return
		if ret==len(f)-1:
			break
		if f[ret]=='Группы':
			SetGroup({'cathref':caturl.con()})
			return

		for fil in filterjs:
			tit = fil['title'].encode('UTF-8')
			if (tit in f[ret])and(tit!='Группы'):
				break
		f_1=[]
		for i in fil['items']:
			try:    check = fil['check']
			except: check = ''

			if i.encode('UTF-8')==check:
				title = '[x] '+i.encode('UTF-8')
			else:
				title = '[ ] '+i.encode('UTF-8')

			f_1.append(title)

		ret = dialog.select('Фильтр', f_1)
		if ret ==-1:
			continue

		ch_title = fil['title']
		check    = f_1[ret][4:]
		for i in filterjs:
			if i['title']==ch_title:
				try:
					i['check']
				except:
					i['check']=''
				i['check']= check if i['check']!= check else ''

	fl=[]
	l_c=''
	t_c=''
	for fil in filterjs:
		try:    check = fil['check']
		except: check = ''
		if fil['title'].encode('UTF-8')!= 'Группы':
			title = fil['title'].encode('UTF-8')
			if check:
				tmp = fil['items'][check.decode('UTF-8')].split('/')[-2]
				if 'fl_' in tmp:
					fl.append(tmp.replace('fl_', ''))
				else:
					if 'language_custom' in tmp:
						l_c += tmp.replace('language_custom_', '')
					elif 'translate_custom' in tmp:
						t_c +=tmp.replace('translate_custom_', '')



	caturl.fl=fl
	caturl.language_custom = l_c
	caturl.translate_custom = t_c
	caturl.group=''

	xbmc.executebuiltin('Container.Update(%s?%s)'%(sys.argv[0],urllib.urlencode({'mode':'Cat','href':caturl.con(), 'upd':'upd'})))

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
		AddFolder(title.encode('UTF-8'), 'Content',{'href':href, 'title':title.encode('UTF-8')}, img=imgup, ico=img, cmItems=ContextMenu)

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

	search = urllib.unquote(params['search'])
	url= site_url+'/search.aspx?search='+search+'&page='+params['page']

	Login, Data =Get_url_lg(url)
	Soup = BeautifulSoup(Data)

	Sresult = Soup.find('div', 'b-search-page__results')
	if Sresult == None:
		xbmcMessage('Ничего не найдено', 7000)
		return

	Sresult = Soup.findAll('a', 'b-search-page__results-item')

	for a in Sresult:
		href = a['href']
		title = a.find('span', 'b-search-page__results-item-title').string
		img = a.find('span', 'b-search-page__results-item-image').img['src']
		imgup = img.replace('/13/', '/1/')
		plot = a.find('span', 'b-search-page__results-item-description')
		plot = str(plot).replace('<strong>','').replace('</strong>','').replace('<span class="b-search-page__results-item-description">','').replace('</span>','')
		vote_positive =a.find('span', 'b-search-page__results-item-rating-positive').string
		vote_negative =a.find('span','b-search-page__results-item-rating-negative').string
		ctitle =('[S] ' if 'serials' in href else '')+title+'  '+u' (↑%s ↓%s)'%( AA(clGreen,'80')%vote_positive,AA(clRed,'80')%vote_negative)

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

		info ={'type':'video','plot':plot,'title':title}
		property={'fanart_image':imgup}
		AddFolder(ctitle, 'Content', {'href':href, 'title' :title}, ico=img, img=imgup, info=info, property=property, cmItems=ContextMenu)

	xbmcplugin.endOfDirectory(plugin_handle)


def Content(params):
	ctitle=urllib.unquote(params['title'])
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
	isBlocked = Soup.find('div', id='file-block-text')!=None

	AddFolder('Дополнительно','Content_plus',{'href':href})

	try:
		torrenter = xbmcaddon.Addon(id = 'plugin.video.torrenter')
	except:
		torrenter = False

	if torrenter:
		item = xbmcgui.ListItem('Передать в torrenter',)
		uri = '%s?%s' % ('plugin://plugin.video.torrenter/', urllib.urlencode({'action':'search','url':ctitle}))
		xbmcplugin.addDirectoryItem(int(sys.argv[1]), uri, item, isFolder=True)

	AddFolder((clRed%'Некоторые файлы заблокированы ' if isBlocked else '')+ 'Альтернативы', 'External_Search', {'plugin':'all', 'command':'Search','search':ctitle})
	AddItem('_'*30+chr(10)+' ','')

	li = Soup.findAll('li', 'folder')
	isFolders=False
	isSubFolder = False
	for l in li:
		try:
			isSubFolder = l.parent.parent['class']=='folder'
		except:
			isSubFolder = False

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
		AddFolder(('   ' if isSubFolder else '')+title, 'Content', {'rel':rel, 'href':href, 'title':ctitle})
		isFolders=True

	li = Soup.findAll('li', 'b-file-new')
	if True:#not isFolders:
		for l in li:
			try:
				title = l.find('span', 'b-file-new__material-filename-text')
				if title == None:
					title = l.find('span', 'b-file-new__link-material-filename-text')
				title=title.string
				a= l.find('a', 'b-file-new__link-material')
				href= a['href']
				a= l.find('a', 'b-file-new__link-material-download')
				href_dl = a['href']
				size = a.span.string
			except:
				continue
			cmenu={'mode'  :'download', 'href':href_dl, 'title':title}
			ContextMenu = [(clAliceblue%('cxz.to Скачать файл'), 'XBMC.RunPlugin(%s)'%uriencode(cmenu))]
			info={'type':'Video','title':ctitle}
			prop={'IsPlayable':'true'}

			AddItem(('   ' if isFolders else '')+('   ' if isSubFolder else '')+title+' '+size,'Play',{'href':href, 'href_dl':href_dl}, info=info, property=prop, cmItems=ContextMenu)
	xbmcplugin.endOfDirectory(plugin_handle)

def Content_plus(params):
	import kinopoisk

	href=urllib.unquote(params['href'])
	url=site_url+href
	Data =Get_url(url, Cookie=True)
	Soup = BeautifulSoup(Data)

	try:
		title_origin = Soup.find('div', 'b-tab-item__title-origin').string
	except:
		title_origin = Soup.find('div', 'b-tab-item__title-inner').span.string

	title_origin = title_origin.strip().encode('UTF-8')

	info = Soup.find('div', 'item-info')
	try:
		year = info.find('a',href = re.compile('.*/year/.*')).span.string
	except:
		year = ''
	try:
		director= info.find('span', itemprop="director").a.span.string
	except:
		director=''
	kp_id = kinopoisk.Search(title_origin, year, director)
	if kp_id:
		AddItem('Кинопоиск: %s (%s), IMDB: %s (%s)'%kinopoisk.GetRating(kp_id))

	director_itemprop= info.findAll('span', itemprop="director")
	if director_itemprop:
		AddItem(clGreen%'Режисёр:')
		for d_item in director_itemprop:
			director_href = d_item.find('a')['href']
			director_name = d_item.find('span', itemprop="name").string
			ContextMenu = [(clAliceblue%('cxz.to Поиск во всех категориях'), 'Container.Update(%s?%s)'%(sys.argv[0],urllib.urlencode({'mode':'Search','search':director_name, 'page':'0'})))]
			AddFolder(director_name, 'Cat', {'href':director_href+'/?view=detailed'}, cmItems=ContextMenu)

	actor_itemprop= info.findAll('span', itemprop="actor")
	if actor_itemprop:
		AddItem(clGreen%'Актёры:')
		for a_item in actor_itemprop:
			actor_href = a_item.find('a')['href']
			actor_name = a_item.find('span', itemprop="name").string
			ContextMenu = [(clAliceblue%('cxz.to Поиск во всех категориях'), 'Container.Update(%s?%s)'%(sys.argv[0],urllib.urlencode({'mode':'Search','search':actor_name, 'page':'0'})))]
			AddFolder(actor_name, 'Cat', {'href':actor_href+'/?view=detailed'}, cmItems=ContextMenu)

	leading = info.findAll('a', href=re.compile('.*/leader/.*'))
	if leading:
		AddItem(clGreen%'Ведущие:')
		for l in leading:
			l_href = l['href']
			l_name = l.span.string
			ContextMenu = [(clAliceblue%('cxz.to Поиск во всех категориях'), 'Container.Update(%s?%s)'%(sys.argv[0],urllib.urlencode({'mode':'Search','search':l_name, 'page':'0'})))]
			AddFolder(l_name, 'Cat', {'href':l_href+'/?view=detailed'}, cmItems=ContextMenu)

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
	link    = site_url+urllib.unquote(params['href'])
	link_dl = site_url+urllib.unquote(params['href_dl'])

	try:
		with open(addon_data_path+'/playlist','rb') as F:
			LocalPL = cPickle.load(F)
	except:
		if not os.path.exists(os.path.dirname(addon_data_path)):
				os.makedirs(os.path.dirname(addon_data_path))
		LocalPL={}

	file_id = link.split('=')[1]

	try:
		path = LocalPL[file_id]
	except:
		Login, Data = Get_url_lg(link)
		playlist = re.compile("(?s)playlist:\s*\[\s*\{\s*(.+?)\s*\}\s*\]").findall(Data)
		if not playlist: return

		playlist= playlist[0].replace('\n','').replace('\t','').replace(' ','').replace('download_url','')
		urls = re.compile("url:'([^']+).+?file_id:'([^']+)").findall(playlist)

		if not urls:return
		pl={}
		for i in urls:
			pl[i[1]]= site_url+i[0]
		with open(addon_data_path+'/playlist','wb') as F:
			cPickle.dump(pl,F)
		path = pl[file_id]

	VideoSource =addon.getSetting('VideoSource')
	if VideoSource=='0':
		dialog = xbmcgui.Dialog()
		dialog_items =['Источник 1 (Лучшее Качество)' ,'Источник 2 (Облегченный)']
		dlg= dialog.select('Источник:', dialog_items)
		if dlg!=1:
			path = link_dl
	elif VideoSource=='1':
		path = link_dl


	item = xbmcgui.ListItem(path=path)

	#title  = xbmc.getInfoLabel('Listitem.Title')
	#title = title+''
	#item.setInfo('video', infoLabels={'title':title})
	item.setProperty('mimetype', 'video/flv')

	xbmcplugin.setResolvedUrl(plugin_handle, True, item)

def download(params):
	dir  =addon.getSetting('DownloadDir')
	if not os.path.exists(dir):
		xbmcMessage('Неверный путь для загрузки',7000)

	url  = site_url+urllib.unquote(params['href'])
	name= urllib.unquote_plus(params['title'])

	dl = downloader.SimpleDownloader()
	dl.download(name.decode('UTF-8'), {'url': url, 'download_path':dir})


#--------------------------------

def External_Search(params):
	import ExtSearch.ExtSearch as ExtSearch

	ExtSearch.LoadPlugins()
	closedir = False
	for p in ExtSearch.Plugins:
		rez = p.Command(params)
		if rez:
			if 'closedir' in rez: closedir =True

	if closedir: xbmcplugin.endOfDirectory(plugin_handle)
