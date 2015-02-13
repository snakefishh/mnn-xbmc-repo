#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib, urllib2, re, sys, os, json, datetime, time, random, collections
from lib import *
from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup

def Search(title, year='', director=''):
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
	for j in sorted(js):
		jsyear = re.compile('(\d{4})').findall(js[j]['year'])
		if jsyear:
			if jsyear[0]==year:
				id = js[j]['id']
				print id
				return id
	return 	js['0']['id']

def GetRating(id):
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
