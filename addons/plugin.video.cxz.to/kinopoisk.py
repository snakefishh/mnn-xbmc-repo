#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib, urllib2, re, sys, os, json, datetime, time, random, collections
from lib import *
from var import *
from cache import CacheToDb
from  cxz import cxz
from BeautifulSoup import  BeautifulStoneSoup

class kinopoisk:
	def __init__(self):
		self.cache = CacheToDb('kinopoisk.db', 0.1)

	def GetLocalInfo(self, cxzid):
		res = self.cache.get('cxz:'+cxzid, None)
		if not res:
			return None
		info = None
		if res['kpid']:
			info  = self.cache.get('kp:'+res['kpid'], None, res['kpid'])
		return {'cxz':res, 'kinopoisk':info}

	def GetInfo(self, cxzid):
		res = self.cache.get('cxz:'+cxzid, self._cxz, cxzid)
		if not res:
			return None
		info = None
		if res['kpid']:
			info  = self.cache.get('kp:'+res['kpid'], self._getinfo, res['kpid'])
		return {'cxz':res, 'kinopoisk':info}

	def _cxz(self, href):
		cxz_data = cxz()
		cxz_data.contententPage(href)
		res = self._search(str(cxz_data.contententPageInfo['title_origin']), str(cxz_data.contententPageInfo['year']))

		cxz_data.contententPage(href)
		cxzInfo = cxz_data.contententPageInfo
		cxzInfo['kpid'] = res
		#TODO Время хранения информации для cxz
		return True, cxzInfo

	def _search(self, title, year='', director=''):
		p = '1.9.1'
		g = {'callback':'jQuery'+(p+'{:.17}'.format(random.random())).replace('.', '')+'_'+str(time.time()*101),
			 'q':title,
			 'query_id':random.random(),
			 'type':'jsonp',
			 'topsuggest':'true'
			}
		url = 'http://www.kinopoisk.ru/handler_search.php?%s'%urllib.urlencode(g)
		headers = {'Accept':'*/*',
					'Accept-Encoding':'gzip, deflate, sdch',
					'Accept-Language':'ru-RU,ru;q=0.8,en-US;q=0.6,en;q=0.4',
					'Connection':'keep-alive',
					'Referer':'http://www.kinopoisk.ru/',
					'User-Agent':User_Agent
				  }
		Data = Get_url(url, headers=headers)
		js=json.loads(Data.replace(g['callback'],'')[1:-1])
		del(js['query_id'])
		if not js: return None
		for j in sorted(js):
			jsyear = re.compile('(\d{4})').findall(js[j]['year'])
			if jsyear:
				if jsyear[0]==year:
					id = js[j]['id']
					return id
		return js['0']['id']

	def GetRating(self,id):

		self.GetInfo(id)

		url = 'http://rating.kinopoisk.ru/'+str(id)+'.xml'
		Data = Get_url(url)
		if Data:
			xml = BeautifulStoneSoup(Data)
			try:
				kp = xml.find('kp_rating')
				r_kp = kp.string.encode('UTF-8')
				v_kp = kp['num_vote'].encode('UTF-8')
			except:
				r_kp = '-'
				v_kp = '-'
			try:
				imdb = xml.find('imdb_rating')
				r_imdb =  imdb.string.encode('UTF-8')
				v_imdb = imdb['num_vote'].encode('UTF-8')
			except:
				r_imdb =  '-'
				v_imdb =  '-'
			return r_kp, v_kp, r_imdb, v_imdb
		else:
			return '-', '-', '-', '-'


	def _getinfo(self,id):
		headers = {'User-Agent': User_Agent,
				   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
				   'Accept-Language': 'ru-ru,ru;q=0.8,en-us;q=0.5,en;q=0.3',
				   'Cache-Control': 'no-cache',
				   'Referer': 'http://www.kinopoisk.ru/level/7/'
				  }
		url = 'http://www.kinopoisk.ru/film/' + id + '/'
		Data = Get_url(url,headers=headers).decode('windows-1251')
		if not Data: return None
		Data = re.sub('<br[^>]*','\n',Data)
		Soup = BeautifulSoup(Data, convertEntities=BeautifulSoup.HTML_ENTITIES)

		FilmInfo = Soup.find('div', id='viewFilmInfoWrapper')
		if not FilmInfo : return None

		Info = {}
		Info['title']         = str(FilmInfo.find('div', id='headerFilm').h1.string)
		Info['originaltitle'] = str(FilmInfo.find('span', itemprop='alternativeHeadline').string)

		plot =Soup.find('div', itemprop='description')
		Info['plot'] =''
		if plot:
			Info['plot'] = str(plot.string)

		info_film   = FilmInfo.find('table', 'info').findAll('tr')

		Info['cast'] =[]
		try:
			info_actors = FilmInfo.find('div', id='actorList').ul.findAll('li')
		except:
			pass
		else:
			Info['cast'] = [str(x.find('a').string) for x in info_actors if not '...' in str(x)]

		lst={}
		for i in info_film:
			td = i.findAll('td')
			lst[td[0].string] = td[1]

		tags ={'year':u'год','country':u'страна','tagline':u'слоган','director':u'режиссер','writer':u'сценарий','genre':u'жанр',
			   'runtime':u'время'}

		for tag in tags:
			value = ', '.join([str(x.string) for x in lst[tags[tag]].findAll('a')])
			if not value:
				value= ', '.join([str(x.string) for x in lst[tags[tag]]])
			Info[tag] = value.replace(', ...','').replace(', слова', '')

		return True, Info