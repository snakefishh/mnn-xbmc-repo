#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, datetime, re
from BeautifulSoup import BeautifulSoup
from lib import *
from cache import CacheToFile

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


def SetSort(params):
	caturl = SiteUrlParse(urllib.unquote(params['cathref']))
	s=[['в тренде',  'по дате обновления','по рейтингу', 'по году выпуска', 'по популярности'],
	   ['trend',     'new',               'rating',      'year',            'popularity']]
	dialog = xbmcgui.Dialog()
	ret = dialog.select('Сортировка', s[0])
	if ret ==-1:
		return
	caturl.url_qs['sort']=s[1][ret]
	if 'page' in caturl.url_qs:del caturl.url_qs['page']
	xbmc.executebuiltin('Container.Update(%s?%s)'%(sys.argv[0],urllib.urlencode({'mode':'Cat','href':caturl.con(), 'upd':'upd'})))

def SetGroup(params):

	caturl = SiteUrlParse(urllib.unquote(params['cathref']))

	filterjs = CacheToFile('cache').read()

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
		for i in reversed(range(int(y10[ret][0:4]), int(y10[ret][-4:])+1)):
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
	if 'page' in caturl.url_qs:del caturl.url_qs['page']
	xbmc.executebuiltin('Container.Update(%s?%s)'%(sys.argv[0],urllib.urlencode({'mode':'Cat','href':caturl.con(), 'upd':'upd'})))

def CheckDB():
	class Progress(object):
		total = 0
		cur = 0
		title =''
		pDialog = xbmcgui.DialogProgress()
		def __init__(self):
			self.pDialog.create('Загрузка:')
			self.pDialog.update(0, self.title)
		def update(self, count, blockSize, totalSize):
			percent = int((self.cur-1)*(100/self.total)+(count*blockSize*100/totalSize)/self.total)
			self.pDialog.update(percent, self.title)
		def __del__(self):
			self.pDialog.close()
	import zipfile

	if (os.path.exists(addon_data_path+'/films_directors.db'))and(os.path.exists(addon_data_path+'/films_casts.db')):
		return True
	else:
		dialog = xbmcgui.Dialog()
		if dialog.yesno('Установить Базу:','Для поиска по Персонам', 'Необходимо загрузить дополнительную Базу', 'Загрузить Сейчас?'):
			url = 'http://mnn-xbmc-repo.googlecode.com/svn/trunk/addons/plugin.video.cxz.to.db/'
			Progr = Progress()
			try:
				dir = urllib.urlopen(url).read()
				Soup = BeautifulSoup(dir)
				li = Soup.findAll('li')
				db = []
				for l in li:
					href = l.a['href']
					if '.zip' in href:
						db.append(href)
				Progr.total = len(db)
				Progr.cur = 0
				for name in db:
					Progr.cur+=1
					Progr.title=name
					urllib.urlretrieve(url+'/'+name, addon_data_path+'/'+name,reporthook=Progr.update)
					zip_handler = zipfile.ZipFile(addon_data_path+'/'+name, 'r')
					zip_handler.extractall(addon_data_path)
				del(Progr)
				return True
			except:
				xbmcMessage('Не удалось установить Базу, попробуйте позже',5000)
				del(Progr)
				return False
		else:
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

	filterjs = CacheToFile('cache').read()

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
		f.append(clGreen%'[B]Применить/Сброс[/B]')

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
	if 'page' in caturl.url_qs:del caturl.url_qs['page']

	xbmc.executebuiltin('Container.Update(%s?%s)'%(sys.argv[0],urllib.urlencode({'mode':'Cat','href':caturl.con(), 'upd':'upd'})))
