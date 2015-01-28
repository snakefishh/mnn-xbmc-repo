#!/usr/bin/python
# -*- coding: utf-8 -*-

from ExtSearch import Plugin
import urllib, urllib2, re, sys, os, json, datetime, time
import xbmcplugin, xbmcgui, xbmcaddon, xbmc
from lib import *
from BeautifulSoup import BeautifulSoup

plugin_handle = int(sys.argv[1])

class c911to (Plugin):
	Name = '911.to (пока не работает)'

	def Command(self, args):
		if (args['plugin'] == self.__class__.__name__)or(args['plugin'] =='all'):
			try:
				run = getattr(self, args['command'])
				result = run(args)
				return result
			except:
				return False
		else:
			return False

	def Search(self,args):
		search = urllib.unquote(args['search'])
		search = search.strip()

		url = 'http://911.to/ajax/search_movie'
		headers ={'Accept':'*/*',
			      'Accept-Encoding':'gzip, deflate',
				  'Accept-Language':'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
				  'Cache-Control':'no-cache',
				 # 'Connection':'keep-alive',
				  #'Content-Length':str(30+5),
				  'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
				  #'Host':'911.to',
				  'Pragma':'no-cache',
				  'Referer':'http://911.to/',
				  'User-Agent':'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:35.0) Gecko/20100101 Firefox/35.0',
				  'X-Requested-With':'XMLHttpRequest',
				  }

		Data = Get_url(url,Post={'term':search},headers=headers)

		if Data and('ничего не найдено' not in Data):
			Soup = BeautifulSoup(Data)
			items = Soup.findAll('div', 'box clearfix')
			if items:
				AddItem(clGreen%('----Найдено на '+self.Name+'----'))
				for item in items:
					img = item.find('div', 'image').find('img')['src']
					info = item.find('div', 'info')
					dt = str(info)
					try:
						dt = re.search('(\d{4})<br',dt).group(1)
					except:
						dt =''

					href = info.find('a')['href']
					title = info.find('a').string
					AddFolder(title+' ('+dt+')','External_Search',{'plugin':self.__class__.__name__,'command':'', 'href':href}, img=img,ico=img)
				return 'closedir'
