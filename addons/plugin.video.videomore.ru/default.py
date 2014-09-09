#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib, urllib2, re, sys, os, json, datetime
import xbmcplugin, xbmcgui, xbmcaddon, xbmc


_addon_name 	 = 'plugin.video.videomore.ru'
_addon 			 = xbmcaddon.Addon(id = _addon_name)
_addon_patch 	 = xbmc.translatePath(_addon.getAddonInfo('path'))
_addon_data_path = xbmc.translatePath( os.path.join( "special://profile/addon_data", _addon_name) )
if (sys.platform == 'win32') or (sys.platform == 'win64'):
	_addon_patch     = _addon_patch.decode('utf-8')
	_addon_data_path = _addon_data_path.decode('utf-8')

sys.path.append(os.path.join(_addon_patch, 'resources', 'lib'))
from database import Database
db_name = os.path.join(_addon_data_path, 'base.db')




#xbmcplugin.setContent(plugin_handle, 'movies')

plugin_handle	= int(sys.argv[1])
def get_params():
	param=[]
	paramstring=sys.argv[2]
	if len(paramstring)>=2:
		params=sys.argv[2]
		cleanedparams=params.replace('?','')
		if (params[len(params)-1]=='/'):
			params=params[0:len(params)-2]
		pairsofparams=cleanedparams.split('&')
		param={}
		for i in range(len(pairsofparams)):
			splitparams={}
			splitparams=pairsofparams[i].split('=')
			if (len(splitparams))==2:
				param[splitparams[0]]=splitparams[1]   
	return param
	
def start(params):
	def add_dir(title,mode, moder, img=''):
		uri = '%s?%s' % (sys.argv[0], urllib.urlencode({'mode':mode,'moder':moder}))
		item = xbmcgui.ListItem(title, iconImage = img, thumbnailImage = img)
		xbmcplugin.addDirectoryItem(plugin_handle, uri, item, True)	

	try:
		mod = params['moder']
	except:
		add_dir('Категории', '', '1')
		add_dir('Каналы'   , '', '2')
	else:
		if mod == '1':
			add_dir('Популярные', 'get_cat', '0')
			add_dir('Сериалы', 'get_cat', '2')
			add_dir('Шоу', 'get_cat', '1')
			add_dir('Программы', 'get_cat', '3')
		elif  mod == '2':
			add_dir('СТС', 'get_ch', '1')
			add_dir('Домашний', 'get_ch', '2')
			add_dir('Перец', 'get_ch', '5')
			add_dir('-----', 'get_ch', '0')
			#add_dir('РЕН-ТВ', 'get_ch', '3')
			#add_dir('5 Канал', 'get_ch', '4')
	xbmcplugin.endOfDirectory(plugin_handle)
	
def get_cat(params):
	db = Database(db_name)

	Cat = db.GetByCategory(params['moder'])
	
	for i in Cat:
		uri = '%s?%s' % (sys.argv[0], urllib.urlencode({'mode':'season', 'id':i[0]}))
		item = xbmcgui.ListItem(i[1], iconImage = '', thumbnailImage = '')
		xbmcplugin.addDirectoryItem(plugin_handle, uri, item, True)		
		
	xbmcplugin.endOfDirectory(plugin_handle)

def get_ch(params):	
	db = Database(db_name)

	Ch = db.GetByChannel(params['moder'])
		
	for i in Ch:
		uri = '%s?%s' % (sys.argv[0], urllib.urlencode({'mode':'season','id':i[0]}))
		item = xbmcgui.ListItem(i[1], iconImage = '', thumbnailImage = '')
		xbmcplugin.addDirectoryItem(plugin_handle, uri, item, True)		
			
	xbmcplugin.endOfDirectory(plugin_handle)	
		
def season(params):
	db = Database(db_name)
	sea = db. GetSeasons(params['id'])
	
	for i in sea:	
		uri = '%s?%s' % (sys.argv[0], urllib.urlencode({'mode':'tracks','id':params['id'], 'seas':i[0]}))
		item = xbmcgui.ListItem(i[2].encode('UTF-8'), iconImage = '', thumbnailImage = '')
		xbmcplugin.addDirectoryItem(plugin_handle, uri, item, True)	

	xbmcplugin.endOfDirectory(plugin_handle)	

def tracks(params):
	db = Database(db_name)
	tracks = db.GetTracksOfSeason(params['id'],params['seas'])
	
	for i in tracks:
		uri = '%s?%s' % (sys.argv[0], urllib.urlencode({'mode':'play', 'title':i[0].encode('UTF-8'), 'url':i[1]}))
		item = xbmcgui.ListItem(i[0].encode('UTF-8'), iconImage = '', thumbnailImage = '')
		xbmcplugin.addDirectoryItem(plugin_handle, uri, item, True)	

	xbmcplugin.endOfDirectory(plugin_handle)	
		
def play(params):
	uri =urllib.unquote_plus(params['url'])
	title =urllib.unquote_plus(params['title'])
	playList = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
	playList.clear()	
	
	#db = Database(db_name)
	#db.search('войны')
	
	item = xbmcgui.ListItem(title, iconImage = '', thumbnailImage = '')				
	playList.add(uri,item)
	xbmc.Player().play(playList)
		
#---------------------------
params = get_params()
mode = None
try:
	mode = params["mode"]
except:
	pass
if     mode == None:
	start(params)
elif   mode == 'get_cat':
	get_cat(params)
elif   mode == 'get_ch':
	get_ch(params)	
elif   mode == 'season':
	season(params)	
elif   mode == 'tracks':
	tracks(params)	
elif   mode == 'play':
	play(params)		
	