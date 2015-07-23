#!/usr/bin/python
# -*- coding: utf-8 -*-

from ExtSearch import Plugin
import urllib, urllib2, re, sys, os, json, datetime, time
import xbmcplugin, xbmcgui, xbmcaddon, xbmc
from lib import *
from cache import CacheToFile
from BeautifulSoup import BeautifulSoup

plugin_handle = int(sys.argv[1])

class c911to (Plugin):
	Name = '911.to test'

	def Command(self, args):
		#return False
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
					AddFolder(title+' ('+dt+')','External_Search',{'plugin':self.__class__.__name__,'command':'Content', 'href':href}, img=img,ico=img)
				return True

	def Content(self,args):
		href = urllib.unquote('http://911.to'+args['href'])

		Data =Get_url(href,Cookie=True)
		Soup = BeautifulSoup(Data)

		reg = re.compile('\d+?:\{size:([1-9,\.]+?),url:"([^"]+)"',re.MULTILINE|re.DOTALL)

		js={}
		if '/movies/' in href:
			Soup = Soup.find('div', 'tab-content')
			cont = reg.findall(str(Soup).replace('\n','').replace(' ',''))
			js_cont = {}
			for cnt in cont:
				ind = cnt[1].split('/')[-1].split('.')[0]
				js_cont[ind] = {'href':cnt[1],'size':cnt[0]}
			js_s = {}
			js_s['0'] = js_cont
			js['0'] = js_s

		elif '/serials/' in href:
			Soup = Soup.find('div', 'season-content')
			seasons = Soup.findAll('div', id=re.compile('season-\d+'))
			for season in seasons:
				episodes = season.findAll('div', 'row')
				js_episode = {}
				for episode in episodes:
					cont = reg.findall(str(Soup).replace('\n','').replace(' ',''))
					js_cont = {}
					for cnt in cont:
						ind = cnt[1].split('/')[-1].split('.')[0]
						js_cont[ind] = {'href':cnt[1],'size':cnt[0]}
					js_episode[episode.div.string.encode('UTF-8').replace(' ','').replace('\n',' ')]=js_cont
				js[season['id']] = js_episode
				AddFolder(season['id'] ,'External_Search',{'plugin':self.__class__.__name__,'command':'Episodes','season':season['id']})

		('playlist_ext').write(js)

		if '/movies/' in href: self.Qual({'season':'0','episode':'0'})
		return True

	def Episodes(self,args):
		cont =CacheToFile('playlist_ext').read()

		for c in sorted(cont[args['season']], key = lambda k:int(re.compile('\d*').findall(k)[0])):
			AddFolder(c.encode('UTF-8') ,'External_Search',{'plugin':self.__class__.__name__,'command':'Qual','season':args['season'],'episode':c.encode('UTF-8')})
		return True

	def Qual(self,args):
		cont = CacheToFile('playlist_ext').read()

		for c in sorted(cont[args['season']][urllib.unquote(args['episode']).decode('UTF-8')], key = lambda k:int(k.replace('p','')),reverse=True):
			href = cont[args['season']][urllib.unquote(args['episode']).decode('UTF-8')][c]['href']
			AddFolder(c, 'External_Search',{'plugin':self.__class__.__name__,'command':'Play','href':href})
		return True

	def Play(self,args):
		href = urllib.unquote(args['href'])
		url = 'http://911.to'+href

		item = xbmcgui.ListItem('', iconImage = '', thumbnailImage = '')
		item.setInfo(type="Video", infoLabels={"Title":''})
		xbmc.Player().play(url, item)
