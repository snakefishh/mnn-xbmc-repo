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


#AARRGGBB
clGreen	     = '[COLOR FF008000]%s[/COLOR]' 
clDodgerblue = '[COLOR FF1E90FF ]%s[/COLOR]'
clDimgray 	 = '[COLOR FF696969 ]%s[/COLOR]'


def start(params):
	url = 'http://cxz.to/'
	Data =Get_url(url)
	Soup = BeautifulSoup(Data)

#категории
	header_menu = Soup.find('div', 'b-header__menu')
	header_menu_section = Soup.findAll('a', 'b-header__menu-section-link')
	for section in header_menu_section:
		print section['href']
		print section.string.encode('UTF-8')


#Самое просматриваемое сейчас

	nowviewed = Soup.find('div', 'b-nowviewed__posters')
	posters = nowviewed.findAll('a', 'b-poster-new__link')
	for poster in posters:
		href = poster['href']
		title = poster.find('span', 'm-poster-new__short_title').string
		img = poster.find('span', 'b-poster-new__image-poster')['style']

		print href
		print title.encode('UTF-8')
		print img

#Популярные материалы

	section_list = Soup.find('div', 'b-section-list')
	poster_detail = section_list.findAll('a', 'b-poster-detail__link')
	for pop in poster_detail:
		href = pop['href']
		img = pop.find('img' ,src=True)['src']
		title = pop.find('span', 'b-poster-detail__title').string
		field = pop.find('span', 'b-poster-detail__field').string
		title +='  '+field

		print href
		print title.encode('UTF-8')
		print img


