#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib, urllib2, re, sys, os, json, datetime, time
from lib import *
from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup

class NoRedirect(urllib2.HTTPRedirectHandler):
    def http_error_302(self, req, fp, code, msg, headers):
        infourl = urllib.addinfourl(fp, headers, req.get_full_url())
        infourl.status = code
        infourl.code = code
        return infourl



def Search(title, year='', director=''):
	url = 'http://www.kinopoisk.ru/index.php?level=7&from=forma&result=adv&m_act%5Bfrom%5D=forma&m_act%5Bwhat%5D=content&m_act%5Bfind%5D='+ urllib.quote_plus(title)
	if year:
		url =url+'&m_act%5Byear%5D='+urllib.quote_plus(year)
#	if director:
#		url =url+'&m_act%5Bcast%5D='+urllib.quote_plus(director)

	opener = urllib2.build_opener(NoRedirect())
	urllib2.install_opener(opener)

	req = urllib2.Request(url)
	req.add_header('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')
	req.add_header('Accept-Encoding', 'gzip, deflate')
	req.add_header('Accept-Language', 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3')
	req.add_header('Connection', 'keep-alive')
	req.add_header('Referer', 'http://www.kinopoisk.ru/s/')
	req.add_header('User-Agent', User_Agent)

	response = urllib2.urlopen(req)

	id = response.info().get('Location')
	if id:
		id = re.search('\/film\/(\d*)\/',id).group(1)
		return id

	Data =response.read()
	if response.headers.get("Content-Encoding", "") == "gzip":
			import zlib
			Data = zlib.decompressobj(16 + zlib.MAX_WBITS).decompress(Data)

	Soup = BeautifulSoup(Data)
	try:
		info = Soup.find('div', 'info').p.a['href']
		id = re.search('\/film\/(\d+?)/',info).group(1)
	except:
		return None
	return id

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
