#!/usr/bin/python
# -*- coding: utf-8 -*-

from var import *
from lib import *
from cache import CacheToDb


class cxz():

	def __init__(self, AutErrorMessage = False):
		#self.site_url='http://cxz.to'
		self.site_url=site_url
		self.login = False
		self.AutErrorMessage = AutErrorMessage
		self.previous_link = None
		self.next_link     = None
		self.cxzInfo ={}

	#TODO убрать BeautifulSoup из кеша
	def fileManager(self, href, folder):
		def recur(data, result):
			rez =[]
			li_ = data.findAll('li', recursive=False)
			for l in li_:
				li = l
				if li.find('ul'):li.find('ul').extract()

				if not li.find('a'):continue
				#-------------------------------------------------------------

				rel = re.compile("parent_id:\s?'?([\d]+)").findall(li.a['rel'])
				info = {}
				if rel:#Папки
					info['parent']= rel = rel[0]

					try:
						info['title'] = li.a.b.string
					except:
						title_ = li.a.contents
						if len(title_)>1:
							info['title'] = title_[0]+BeautifulSoup(str(title_[1])).find('font').string
						else:
							info['title'] = title_[0]

					quality_list= re.compile("quality_list:\s?'([^']+)").findall(li.a['rel'])
					if quality_list:
						info['quality_list'] = quality_list[0]
					else:
						info['quality_list'] = None

					lang = li.a['class']
					lang = re.compile('\sm\-(\w+)\s').findall(lang)
					if lang:
						info['lang']=lang[0].upper()+' '

					info['next'] = 'folder' if (li.find('a', 'folder-filelist'))== None else 'filelist'
					info['folder'] = 'folder'
				else:#Файлы
					try:
						info['qual'] = li.find('span', 'video-qulaity').string
					except:
						pass
					info['parent'] =  '' #re.compile('(series-.*)').findall(li['class'])[0]
					info['folder'] = 'file'

					title = li.find('span', 'b-file-new__material-filename-text')
					if title == None:
						title = li.find('span', 'b-file-new__link-material-filename-text')
					info['title']=title.string

					a= li.find('a', 'b-file-new__link-material')
					info['href'] =''
					if a:
						info['href']= a['href']

					a= li.find('a', 'b-file-new__link-material-download')
					info['only_download'] = 'only-download' in a['class']
					info['href_dl'] = a['href']
					info['size'] = a.span.string

				#---------------------------------------------------------------------
				rez.append(info)
				ul = li.find('ul', recursive=False)
				if ul:
					js = {info['parent']:recur(ul, result)}
					result.append(js)
			return rez

		url=self.site_url+href+'?ajax&folder='
		cache = CacheToDb('fileManager.db', 0.1)
		result = cache.get(url+folder, '')

		if not result:
			Data =Get_url(url+folder, Cookie=True)

			Soup = BeautifulSoup(Data)
			isBlocked = Soup.find('div', id='file-block-text')!=None
			ul = Soup.find('ul', recursive=False)
			result =[]
			if folder =='0':
				js = {folder:[recur(ul,result),isBlocked]}
			else:
				js = {folder:recur(ul,result)}
			result.append(js)
			for r in result:
				cache.get(url+r.keys()[0], lambda x:[30*60,x], r[r.keys()[0]])
			result = r[r.keys()[0]]

		if folder == '0':
			self.isBlocked = result[1]
			return result[0]
		return  result

	def parse(self, href):
		self.url = self.site_url+ href
		Data =self.Get_url_lg()
		Soup = BeautifulSoup(Data)
		header_menu_section = Soup.findAll('a', 'b-header__menu-section-link')

		#Категории
		if header_menu_section:
			self.category = []
			for section in header_menu_section:
				cat_el={}
				cat_el['title'] = section.string.encode('UTF-8')
				cat_el['href']  = section['href'] if '?view=detailed' in section['href'] else section['href']+'?view=detailed'
				self.category.append(cat_el)

		#Paginator
		pl = Soup.find('a', 'previous-link')
		if pl:
			self.previous_link = pl['href']
			self.pg = re.compile('page=(\d+?$)').findall(self.previous_link)
			if self.pg:
				self.pg =int(self.pg[0])+1
			else:
				self.pg=1
		else:
			self.pg=0

		nl = Soup.find('a', 'next-link')
		if nl:
			self.next_link =nl['href']

		#Текущая сортировка
		sort_selected  = Soup.find('span', 'b-section-controls__sort-selected-item selected')
		if sort_selected:
			self.sort_selected = sort_selected.string

		#Текущая группировка
		group_selected = Soup.findAll(True, 'b-section-controls__title-item')
		if group_selected:
			tmp=''
			for i in group_selected:
				try:
					tmp+=i.span.string +','
				except:
					try:
						tmp+=i.h1.string +','
					except:
						pass
			self.group_selected = tmp[:-1]
		else:
			self.group_selected = None

		#Фильтры
		section_menu = Soup.find('div', 'b-section-menu')
		if section_menu:
			tegul = section_menu.findAll('ul')
			self.filterjs=[]
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
						if a['href']<>'#':
							items[item_title]=a['href']
					rec['items']=items
					self.filterjs.append(rec)

		#Список фильмов / Информация
		section_list = Soup.find('div', 'b-section-list')
		poster_detail = section_list.findAll('a', 'b-poster-detail__link')
		self.cxzInfo=[]
		for pop in poster_detail:
			cxzInfoItem ={}
			cxzInfoItem['href'] = pop['href']
			cxzInfoItem['img']   = 'http:'+pop.find('img' ,src=True)['src']

			cxzInfoItem['imgup'] = cxzInfoItem['img'].replace('/6/', '/1/')
			cxzInfoItem['title'] = pop.find('span', 'b-poster-detail__title').string
			tmp = pop.findAll('span', 'b-poster-detail__field')
			field = tmp[0].string
			cxzInfoItem['country'] = field.split(u'●')[1].strip()

			year  = re.compile('(\d{4})').findall(field)
			if year:
				cxzInfoItem['year'] =year[0]
			else:
				cxzInfoItem['year']  =''

			cast = tmp[1].string
			if cast:
				cxzInfoItem['cast'] = cast.split(',')
			else:
				cxzInfoItem['cast']=[]
			cxzInfoItem['plot']  = pop.find('span', 'b-poster-detail__description').contents[0]
			cxzInfoItem['vote_positive'] = pop.find('span', 'b-poster-detail__vote-positive').string
			cxzInfoItem['vote_negative'] = pop.find('span', 'b-poster-detail__vote-negative').string
			quality = pop.findAll('span', 'quality')
			cxzInfoItem['quality'] = ''
			for qual in quality:
				cxzInfoItem['quality'] += qual['class'].replace('quality', '').replace('m-','').replace(' ', '')+','
			cxzInfoItem['quality'] = cxzInfoItem['quality'][:-1].upper()
			self.cxzInfo.append(cxzInfoItem)

	def search(self, s):
		self.url = self.site_url+ s
		Data =self.Get_url_lg()
		Soup = BeautifulSoup(Data)

		Sresult = Soup.find('div', 'b-search-page__results')
		if Sresult == None:
			return None

		Sresult = Soup.findAll('a', 'b-search-page__results-item')

		SearchInfoItems =[]
		for a in Sresult:
			SearchInfoItem ={}
			SearchInfoItem['href'] = a['href']
			SearchInfoItem['title'] = a.find('span', 'b-search-page__results-item-title').string
			try:
				SearchInfoItem['year'] = re.compile('\((\d{4})[\)-]+',re.UNICODE).findall(SearchInfoItem['title'])[0]
			except:
				SearchInfoItem['year'] = ''
			else:
				SearchInfoItem['title'] = re.sub('\(\d{4}[\)-]+.*','',SearchInfoItem['title'])

			SearchInfoItem['img'] = 'http:'+a.find('span', 'b-search-page__results-item-image').img['src']
			SearchInfoItem['imgup'] = SearchInfoItem['img'].replace('/13/', '/1/')
			plot = a.find('span', 'b-search-page__results-item-description')

			SearchInfoItem['plot'] = str(plot).replace('<strong>','').replace('</strong>','').\
				replace('<span class="b-search-page__results-item-description">','').replace('</span>','').replace('<br />', '\n')

			SearchInfoItem['vote_positive'] =a.find('span', 'b-search-page__results-item-rating-positive').string
			SearchInfoItem['vote_negative'] =a.find('span','b-search-page__results-item-rating-negative').string
			SearchInfoItem['country'] = ''
			SearchInfoItems.append(SearchInfoItem)
		return SearchInfoItems

	def contententPage(self, href):
		#TODO поличить для сериала
		Data = Get_url(self.site_url+href, Cookie=True)
		Soup = BeautifulSoup(Data)
		self.contententPageInfo = {}
		try:
			title_origin = Soup.find('div', 'b-tab-item__title-origin').string
		except:
			title_origin = Soup.find('div', 'b-tab-item__title-inner').span.string

		self.contententPageInfo['title_origin'] = str(title_origin.strip().encode('UTF-8'))

		info = Soup.find('div', 'item-info')
		try:
			self.contententPageInfo['year'] = str(info.find('a',href = re.compile('.*/year/.*')).span.string)
		except:
			self.contententPageInfo['year'] = ''

		try:
			self.contententPageInfo['firstdirector']= str(info.find('span', itemprop="director").a.span.string.encode('UTF-8'))
		except:
			self.contententPageInfo['firstdirector']=''

		director_itemprop= info.findAll('span', itemprop="director")
		if director_itemprop:
			directors =[]
			for d_item in director_itemprop:
				directors.append({'name':str(d_item.find('a')['href']), 'href': str(d_item.find('span', itemprop="name").string)})
			self.contententPageInfo['director']= directors

		actor_itemprop= info.findAll('span', itemprop="actor")
		if actor_itemprop:
			actors =[]
			for a_item in actor_itemprop:
				actors.append({'name':str(a_item.find('a')['href']), 'href': str(a_item.find('span', itemprop="name").string)})
			self.contententPageInfo['cast']= actors

		leading = info.findAll('a', href=re.compile('.*/leader/.*'))
		if leading:
			leadings =[]
			for l in leading:
				leadings.append({'name':str(l.span.string), 'href':str(l['href'])})
			self.contententPageInfo['leading']= leadings

	def similar(self, data):
		Soup = BeautifulSoup(data)
		sim = Soup.find('div', 'b-similar')
		if not sim:
			return
		links = sim.findAll('a', 'b-poster-new__link')
		if not links:
			return
		items = []
		for link in links:
			item ={}
			item['href'] = link['href']
			img = link.find('span', 'b-poster-new__image-poster')['style']
			tmp = re.compile("(http:\/\/[^']+)").findall(img)
			if tmp:
				item['img'] = tmp[0]
				item['imgup'] = tmp[0].replace('/9/', '/1/')
			else:
				item['img'] = ''
				item['imgup'] = ''
			item['title'] = link.find('span', 'm-poster-new__full_title').string.encode('UTF-8')
			items.append(item)
		return items

	def favourites_category(self, page):
		self.url =self.site_url+'/myfavourites.aspx?page='+page
		Data =self.Get_url_lg()
		if not self.login:return
		Soup= BeautifulSoup(Data)
		category = Soup.findAll('div', 'b-category')
		items = []
		for cat in category:
			title = cat.find('span', 'section-title').b.string
			rel = cat.find('a', 'b-add')['rel']
			rel=rel.replace('{','').replace('}','').replace(' ','').replace("'",'')
			rel= rel.split(',')
			section    =rel[0].split(':')[1]
			subsection =rel[1].split(':')[1]
			items.append({'title':title,'section':section, 'subsection':subsection})
		return items

	def favourites_content(self, section, subsection, page, curpage):
		url = self.site_url+'/myfavourites.aspx?ajax&'
		ajax={
			'section'    :section,
			'subsection' :subsection,
			'rows'       :'2',
			'curpage'    :curpage,
			'action'     :'get_list',
			'setrows'    :'4',
			'page'       : page
			}
		url += urllib.urlencode(ajax)
		js = Get_url(url, JSON=True, Cookie=True)

		result = {}
		result['maxpages'] = js['maxpages']
		result['islast'] =js['islast']
		Data= js['content']
		#hack
		Data = re.sub('</?p[^>]*>','teg_p',Data)

		Soup = BeautifulSoup(Data,convertEntities=BeautifulSoup.HTML_ENTITIES)
		tega = Soup.findAll('a', 'm-video')

		result['items'] = []
		for a in tega:
			item = {}
			item['href'] = a['href']
			item['img']  = 'http:'+ re.compile("url\s*\('(.+?)'\)").findall(a['style'])[0]
			item['imgup'] = item['img'].replace('/13/', '/1/')
			item['country'] =''
			title= a.find('b', 'subject-link')
			title = title.span.string
			ser_parse=filename2match(title)
			year = re.compile('\((\d{4})[\)-]+',re.UNICODE).findall(title)
			if year:
				item['year'] = year[0]
			else:
				item['year'] =''
			item['title'] = re.sub('teg_p.*teg_p','',title)
			if ser_parse:
				item['tvshowtitle']=item['title']
				item['season']=ser_parse['season']
				item['episode']=ser_parse['episode']

			result['items'].append(item)
		return result

	def add_to_favorite(self, href, mode, mode2):
		if mode2=='add':
			#url = 'http://cxz.to/item/user_votes/'
			url = site_url+'/item/user_votes/'
			s = href.split('/')[-1]
			s = s.split('-')[0]
			url = url+s
			headders = {'Accept':'*/*',
						'Accept-Encoding':'gzip, deflate',
						'Accept-Language':'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
						'X-Requested-With':'XMLHttpRequest'
						}
			json = Get_url(url,JSON=True,headers=headders,Cookie=True)
			if (json['item_status']['favorites']==1) or (json['item_status']['forlater']==1):
				return 'Материал Уже Есть В Избранном'

		id = re.compile('\/(\w+)-').findall(href)[0]
		url = self.site_url+'/addto/%s/%s?json'%(mode, id)

		Data =Get_url(url, JSON=True, Cookie=True)
		return Data['ok']

	def Login(self, login, passw):
		url = self.site_url+'/login.aspx'
		headders = {'X-Requested-With':'XMLHttpRequest'}
		Post={'login':login, 'passwd':passw, 'remember':'1'}
		Data =Get_url(url,headers=headders, Post=Post, Cookie=True)
		return Data

	def Get_url_lg(self, headers={}, Post = None, GETparams={}, JSON=False, Proxy=None):

		login =addon.getSetting('User')
		passw =addon.getSetting('password')
		old_login =addon.getSetting('oldUser')
		old_passw =addon.getSetting('oldpassword')

		if (old_login!=login)or(passw!=old_passw):
			DelCookie()
			addon.setSetting('oldUser', login)
			addon.setSetting('oldpassword', passw)

		Data = Get_url(self.url, headers, Post, GETparams, JSON, Proxy, Cookie=(login and passw))

		if login and passw:
			Soup = BeautifulSoup(Data)
			lg = Soup.find('a', 'b-header__user-profile')
			if not lg:
				DelCookie()
				LgData= self.Login(login, passw)
				LgData = Get_url(self.url, headers, Post, GETparams, JSON, Proxy, Cookie=(login and passw))
				Soup = BeautifulSoup(LgData)
				lg = Soup.find('a', 'b-header__user-profile')
			else:
				self.login = True
				return Data
			if not lg:
				if self.AutErrorMessage: xbmcMessage('Ошибка Авторизации',5000)
			else:
				self.login = True
				return LgData
		self.login = False
		return Data
