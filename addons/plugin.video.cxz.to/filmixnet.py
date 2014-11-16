#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib, urllib2, re, sys, os, json, datetime, time
import xbmcplugin, xbmcgui, xbmcaddon, xbmc
from lib import *
from BeautifulSoup import BeautifulSoup

def ub(d):
	d = d[1:]
	s2=''
	for l in range(0, len(d), 3):
		s2 += unichr(int('0x'+d[l:l+3], 16))
	return s2

def search(s):
	headers={'Accept': '*/*',
	         'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
	         'Accept-Encoding': 'gzip, deflate',
	         'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
	         'X-Requested-With': 'XMLHttpRequest',
	         'Pragma': 'no-cache',
	         'Cache-Control': 'no-cache',
	         'Referer': 'http://filmix.net/index.php?do=search',

	         'Connection': 'keep-alive'
	        }

	Post = {'change_search':'0','count_blocks':'0','story':s,
			'country':'0','year_one':'0','year_range_ot':'0','year_range_do':'0','ganrs[]':'0',
			'imdb_ot':'0','imdb_do':'10','imdbk_ot':'0','imdbk_do':'10','sortr':'none','sortd':'all','sort':'asc'}

	Data = Get_url('http://filmix.net/engine/ajax/search_new.php?do=search&mode=advanced',headers=headers, Post=Post)
	Soup = BeautifulSoup(Data.decode('cp1251'))
	divff = Soup.findAll('div', 'ff')

	sd = []
	for res in divff:
		a = res.find('div', 'zagolovok').a
		href = a['href']
		title = a.string
		ico = res.find('img')['src']
		img = ico.replace('/thumbs/','/')
		sd.append({'href':href,'title':title,'ico':ico,'img':img})
	return sd

def Content(href):
	Data = Get_url(href)

	file5 = re.compile('(file5Array = cleanArray.*)').findall(Data)[0]
	file5 = re.compile('\'(.+?)\'').findall(file5)

	fil=[]
	for fl in file5:
		if len(fl)>5:
			fil.append(ub(fl))
	if fil:return 'file', fil

	pl5 = re.compile('(pl5Array = cleanArray.*)').findall(Data)[0]
	pl5 = re.compile('\'(.+?)\'').findall(pl5)

	playlst = []
	for pl5x in pl5:
		if len(pl5x)>5:
			js = json.loads(ub(Get_url(ub(pl5x))))
			playlst.append(js)
	if playlst:return 'pl', playlst
	return '', ''
