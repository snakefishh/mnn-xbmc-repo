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
			run = getattr(self, args['command'])
			result = run(args)
			return result
		else:
			return False

	def Search(self,args):
		search = urllib.unquote_plus(args['search'])

		url = 'http://911.to/ajax/search_movie'
		Data = Get_url(url,Post={'term':search},headers={'X-Requested-With':'XMLHttpRequest','User-Agent':User_Agent})
		if Data:
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

