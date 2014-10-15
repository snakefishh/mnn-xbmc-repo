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
#xbmcplugin.setContent(plugin_handle, 'movies')
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
			xbmcMessage('Ошибка Авторизации',5000)
		else:
			return True, LgData
	return False, Data

def start(params):


	#################################



	#################################





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
		AddFolder(title.encode('UTF-8'), 'Content', {'href':href, 'title':title.encode('UTF-8')}, img=imgup, ico=img, cmItems=ContextMenu)

	next_page = Soup.find('a', 'next-link')
	if next_page:
		next_page =next_page['href']
		AddFolder(clGreen%('Страница '+str(pg+2)+' >'),'',{'href':next_page,'upd':'upd'})


	xbmcplugin.endOfDirectory(plugin_handle, updateListing=False, cacheToDisc=True)

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

def SetSort(params):
	cathref = urllib.unquote(params['cathref'])
	s=[['в тренде',  'по дате обновления','по рейтингу', 'по году выпуска', 'по популярности'],
	   ['sort=trend','sort=new',          'sort=rating', 'sort=year',       'sort=popularity']]

	dialog = xbmcgui.Dialog()
	ret = dialog.select('Сортировка', s[0])
	if ret ==-1:
		return

	sort = s[1][ret]
	tmp = cathref.split('?')
	if len(tmp)==1:
		cathref +='?'+sort
	else:
		if 'sort' not in cathref:
			cathref += '&'+sort
		else:
			cathref = tmp[0]+'?'
			tmp = tmp[1].split('&')
			for i in tmp:
				cathref += (i if 'sort' not in i else sort)+'&'
	xbmc.executebuiltin('Container.Update(%s?%s)'%(sys.argv[0],urllib.urlencode({'mode':'Cat','href':cathref, 'upd':'upd'})))

def SetGroup(params):
	cathref = urllib.unquote(params['cathref'])
	with open(addon_data_path+'/filters','rb') as F:
			filterjs = cPickle.load(F)
	for fil in filterjs:
		if fil['title'].encode('UTF-8')== 'Группы':
			break

	k = fil['items'].keys()
	k.insert(0, u'Без Группировки')
	dialog = xbmcgui.Dialog()
	ret = dialog.select('Группы', k)
	if ret ==-1:
		return

	var=k[ret].encode('UTF-8')
	if var=='Без Группировки':
		tmp = cathref.split('?')
		if len(tmp)>1:
			get = '?'+tmp[1]
		else:
			get = ''
		tmp = tmp[0][1:-1].split('/')
		cathref = '/'+tmp[0]+'/'+get

	elif var=='по годам':
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

		tmp = cathref.split('?')
		if len(tmp)>1:
			get = '?'+tmp[1]
		else:
			get = ''
		tmp = tmp[0][1:-1].split('/')
		cathref = '/%s/year/%s/%s'%(tmp[0], y1[ret], get)


	elif var == 'по жанрам':
		href = fil['items'][u'по жанрам']

		Data = Get_url(href)
		Soup =BeautifulSoup(Data)
		main = Soup.find('div', 'main')
		tega = main.findAll('a')
		genres={}
		for a in tega:
			genres[a.string]=a['href']
		g = genres.keys()
		ret = dialog.select('По Жанрам', g)
		if ret ==-1:
			return

		newhref = genres[g[ret]]
		tmp = cathref.split('?')
		if len(tmp)>1:
			tmp1 = re.sub('page=\d+', '', tmp[1])
			cathref = newhref+'?'+tmp1.replace('&','')
		else:
			cathref = newhref
	xbmc.executebuiltin('Container.Update(%s?%s)'%(sys.argv[0],urllib.urlencode({'mode':'Cat','href':cathref, 'upd':'upd'})))


def SetFilter(params):
	cathref = urllib.unquote(params['cathref'])
	with open(addon_data_path+'/filters','rb') as F:
			filterjs = cPickle.load(F)

	dialog = xbmcgui.Dialog()

	while True:
		f=[]
		for fil in filterjs:
			try:    check = fil['check']
			except: check = ''
			if fil['title'].encode('UTF-8')!= 'Группы':
				title = fil['title'].encode('UTF-8')
				if check:
					title += '  : '+check
				f.append(title)
		f.append(clGreen%'<Применить>')

		ret = dialog.select('Группы', f)
		if ret ==-1:
			return
		if ret==len(f)-1:
			break

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

		ret = dialog.select('Группы', f_1)
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

	fl=''
	fl2=''
	for fil in filterjs:
		try:    check = fil['check']
		except: check = ''
		if fil['title'].encode('UTF-8')!= 'Группы':
			title = fil['title'].encode('UTF-8')
			if check:
				tmp = fil['items'][check.decode('UTF-8')].split('/')[-2]
				print tmp
				if 'fl_' in tmp:
					fl += tmp
				else:
					fl2 += tmp+'/'

	newhref = '/'+ cathref.split('/')[1]+('/fl'+fl.replace('fl_','_')+'/' if fl else '/') +fl2
	tmp = cathref.split('?')
	if len(tmp)>1:
		tmp1 = re.sub('page=\d+', '', tmp[1])
		cathref = newhref+'?'+tmp1.replace('&','')
	else:
		cathref = newhref


	xbmc.executebuiltin('Container.Update(%s?%s)'%(sys.argv[0],urllib.urlencode({'mode':'Cat','href':cathref, 'upd':'upd'})))

def Cat(params):
	cat_href = urllib.unquote_plus(params['href'])
	url =site_url+ cat_href

	Login, Data =Get_url_lg(url)
	Soup = BeautifulSoup(Data)

	sort_selected  = Soup.find('span', 'b-section-controls__sort-selected-item selected').string
	is_fil_selected   = False
	group_selected = Soup.find(True, 'm-section-controls__title-item_position_last').h1.string

	section_menu = Soup.find('div', 'b-section-menu')
	tegul = section_menu.findAll('ul')
	filterjs=[]
	for ul in tegul:
		rec ={}
		menu_title = ul.find('b', 'b-section-menu__item-title')
		if menu_title:
			rec['title']=menu_title.string
			tega = ul.findAll('a', 'selected')
			if tega :is_fil_selected=True

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


	grTitle = 'Группа        : '+ (group_selected.encode('UTF-8') if not is_fil_selected else '')
	flTitle = 'Фильтр       : '  + (group_selected.encode('UTF-8') if is_fil_selected else '')

	AddItem('Сортировка : '+sort_selected.encode('UTF-8'), 'SetSort', {'cathref':cat_href})
	AddItem(grTitle,'SetGroup',{'cathref':cat_href})
	AddItem(flTitle,'SetFilter', {'cathref':cat_href})
	AddItem('_'*30+chr(10)+' ')




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
		title = title.encode('UTF-8')+'  '+detail.encode('UTF-8')

		ContextMenu=[]
		if Login:
			cmenu={'mode'  :'ADFav',
				   'mode2' :'favorites',
				   'mode3' :'add',
				   'href'  :href,
				  }
			cmenu1=cmenu.copy()
			cmenu1['mode2']='forlater'
			ContextMenu = [(clAliceblue%('cxz.to Добавить В Избранное'), 'XBMC.RunPlugin(%s)'%uriencode(cmenu)),
						   (clAliceblue%('cxz.to Отложить на Будущее'), 'XBMC.RunPlugin(%s)'%uriencode(cmenu1))]
		AddFolder(title ,'Content',{'href':href, 'title' :title}, img=imgup,ico=img, cmItems=ContextMenu)

	next_page = Soup.find('a', 'next-link')
	if next_page:
		next_page =next_page['href']
		AddFolder(clGreen%('Страница '+str(pg+2)+' >'),'Cat',{'href':next_page,'upd':'upd'})
	try:
		upd = params['upd']=='upd'
	except:
		upd=False
	xbmcplugin.endOfDirectory(plugin_handle, updateListing=upd, cacheToDisc=True)



###################################################################################


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
			AddFolder(title, 'Content', {'href':href, 'title' :title}, ico=img, img=imgup, cmItems=ContextMenu)

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
		AddFolder(title, 'Content', {'rel':rel, 'href':href, 'title':ctitle})
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
			AddItem('   '+title+' '+size,'Play',{'href':href, 'href_dl':href_dl}, info=info, property=prop, cmItems=ContextMenu)
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
	print name, url

	dl = downloader.SimpleDownloader()
	dl.download(name.decode('UTF-8'), {'url': url, 'download_path':dir})
