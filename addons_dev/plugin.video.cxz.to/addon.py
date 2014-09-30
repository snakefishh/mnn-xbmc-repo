#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib, urllib2, re, sys, os, json, datetime, time
import xbmcplugin, xbmcgui, xbmcaddon, xbmc
from lib import *
from BeautifulSoup import BeautifulSoup
from urlparse import urlparse
addon_name 	= 'plugin.video.cxz.to'
addon 		= xbmcaddon.Addon(id = addon_name)
plugin_handle	= int(sys.argv[1])
xbmcplugin.setContent(plugin_handle, 'movies')
site_url='http://cxz.to'

#AARRGGBB
clGreen	     = '[COLOR FF008000]%s[/COLOR]' 
clDodgerblue = '[COLOR FF1E90FF ]%s[/COLOR]'
clDimgray 	 = '[COLOR FF696969 ]%s[/COLOR]'


def start(params):
	try:
		href= urllib.unquote_plus(params['href'])
	except:
		href=''
	url = site_url+href
	print url
	Data =Get_url(url)
	Soup = BeautifulSoup(Data)

#категории
	header_menu = Soup.find('div', 'b-header__menu')
	header_menu_section = Soup.findAll('a', 'b-header__menu-section-link')
	for section in header_menu_section:
		title = section.string.encode('UTF-8')
		AddFolder(title, 'Cat', {'href':section['href']})

	title = 'Самое просматриваемое'
	AddFolder(title, 'MostViewed')

	AddItem('_'*30+chr(10)+' ')

#Популярные материалы

	pr_page   = Soup.find('a', 'previous-link')
	if pr_page:
		pr_page= pr_page['href']
		AddFolder(clGreen%'< Страница','start',{'href':pr_page,'upd':'upd'})

	section_list = Soup.find('div', 'b-section-list')
	poster_detail = section_list.findAll('a', 'b-poster-detail__link')
	for pop in poster_detail:
		href = pop['href']
		img = pop.find('img' ,src=True)['src']
		title = pop.find('span', 'b-poster-detail__title').string
		field = pop.find('span', 'b-poster-detail__field').string
		title +='  '+field
		AddItem(title.encode('UTF-8'), '', {'href':href}, img=img)

	next_page = Soup.find('a', 'next-link')
	if next_page:
		next_page =next_page['href']
		AddFolder(clGreen%'Страница >','start',{'href':next_page,'upd':'upd'})

	try:
		upd = params['upd']=='upd'
	except:
		upd=False
	xbmcplugin.endOfDirectory(plugin_handle, updateListing=upd)

def MostViewed(params):
	#Самое просматриваемое сейчас

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
		AddItem(title.encode('UTF-8'), '', {'href':href}, img=img)
	xbmcplugin.endOfDirectory(plugin_handle)

def Cat(params):
	url =site_url+urllib.unquote_plus(params['href'])
	Data =Get_url(url)
	Soup = BeautifulSoup(Data)
	tega=Soup.findAll('a', 'b-poster-tile__link')


# расчет страниц
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
##
	for a in tega:
		href = 	a['href']
		img = a.find('img')['src']
		title = a.find('span', 'b-poster-tile__title-full').string.replace('\t','').replace('\n', '')
		AddFolder(title.encode('UTF-8'),'Content',{'href':href}, img=img)


	next_page = Soup.find('a', 'next-link')
	if next_page:
		next_page =next_page['href']
		AddFolder(clGreen%('Страница '+str(pg+2)+' >'),'Cat',{'href':next_page,'upd':'upd'})

	try:
		upd = params['upd']=='upd'
	except:
		upd=False
	xbmcplugin.endOfDirectory(plugin_handle, updateListing=upd)

def Content(params):
	href=urllib.unquote(params['href'])
	url=site_url+href+'?ajax'

	query={}
	query['download']='1'
	query['view']='1'
	query['view_embed']='0'
	query['blocked']='0'
	query['folder_quality']='null'
	query['folder_lang']='null'
	query['folder_translate']='null'
	try:
		query['folder']=params['rel']
	except:
		query['folder']='0'

	for qr in query:
		url+='&'+qr+'='+query[qr]
	Data =Get_url(url)
	Soup = BeautifulSoup(Data)

	li = Soup.findAll('li', 'folder')
	for l in li:
		a = l.find('a', 'title')
		title= a.string
		if title==None:
			title = l.find('a', 'title').b.string
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

		title = '[B]'+clGreen%(title.encode('UTF-8')+' '+sz)+'[/B]'+chr(10)
		title += '[I]'+clDimgray%(details+' '+date)+'[/I]'

		AddFolder(title, 'Content', {'rel':rel, 'href':href})

	li = Soup.findAll('li', 'b-file-new')
	for l in li:
		title = l.find('span', 'b-file-new__material-filename-text')
		if title == None:
			title = l.find('span', 'b-file-new__link-material-filename-text')
		title=title.string
		a= l.find('a', 'b-file-new__link-material-download')
		href = a['href']
		size = a.span.string

		AddItem(title+' '+size,'Play',{'href':href})

	xbmcplugin.endOfDirectory(plugin_handle)

def Play(params):

	link = site_url+urllib.unquote(params['href'])

	item = xbmcgui.ListItem('   ', iconImage = '', thumbnailImage = '')
	item.setInfo(type="Video", infoLabels={"Title":'  '})

	xbmc.Player().play(link, item)