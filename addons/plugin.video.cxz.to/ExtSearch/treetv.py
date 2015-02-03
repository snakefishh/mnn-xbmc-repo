﻿#!/usr/bin/python
# -*- coding: utf-8 -*-

from ExtSearch import Plugin
import urllib, urllib2, re, sys, os, json, datetime, time
import xbmcplugin, xbmcgui, xbmcaddon, xbmc
from lib import *
from BeautifulSoup import BeautifulSoup
plugin_handle = int(sys.argv[1])

class Treetv(Plugin):
    Name = 'Tree.tv'

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
        search = urllib.unquote_plus(args['search'])
        url = 'http://tree.tv/search'
        Data = Get_url(url,Post={'usersearch':search})
        Soup =BeautifulSoup(Data)
        main = Soup.find('div', 'main_content')
        items = main.findAll('div', 'item')

        if items:
            AddItem(clGreen%('----Найдено на '+self.Name+'----'))
            for item in items:
                tmp = item.find('div', 'preview')
                img = tmp.find('img', alt=re.compile('.+'))
                if img:
                    img = img['src']
                else:
                    img = ''
                item_content = item.find('div', 'item_content')
                a = item_content.find('a')
                href = a['href']
                title = a.string
                AddFolder(title,'External_Search',{'plugin':self.__class__.__name__,'command':'Content', 'href':href}, img='http://tree.tv'+img,ico='http://tree.tv'+img)
            return True

    def Content(self, args):
        href = urllib.unquote_plus(args['href'])
        url = 'http://tree.tv'+href
        Data = Get_url(url)
        Soup = BeautifulSoup(Data)
        aitems = Soup.findAll('div', 'accordion_item')
        if not aitems:
            return True

        sjson = re.compile("source' : \$\.parseJSON\('([^\)]+)'").findall(Data)
        if not sjson:
            return False
        else:
            sjson =sjson[0]

        F = open(addon_data_path+'/treetv_playlist', 'w')
        json.dump(sjson, F)
        F.close()

        for aitem in aitems:
            ahead = aitem.find('div', 'folder_name')
            if ahead:
                atitle = ahead.a['title']
                data_folder = ahead['data-folder']
                AddFolder(atitle,'External_Search', {'plugin':self.__class__.__name__,'command':'Content2', 'dfolder':data_folder})

        return True

    def Content2(self,args):
        dfolder = args['dfolder']

        F = open(addon_data_path+'/treetv_playlist', 'r')
        Data = json.load(F)
        F.close()

        js_ = json.loads(Data)

        for js in js_[dfolder]:
            data = str(js_[dfolder][js])
            AddFolder(str(js),'External_Search', {'plugin':self.__class__.__name__,'command':'Content3', 'dfolder':dfolder, 'ql':str(js)})
        return True

    def Content3(self,args):
        F = open(addon_data_path+'/treetv_playlist', 'r')
        Data = json.load(F)
        F.close()
        js_ = json.loads(Data)

        dfolder = args['dfolder']
        ql = args['ql']

        for con in js_[dfolder][ql]:
            title = con.split('/')[-1]
            AddItem(title ,'External_Search',{'plugin':self.__class__.__name__,'command':'Play', 'title':title, 'url':con})

        return True

    def Play(self,args):
        title = urllib.unquote_plus(args['title'])
        url = urllib.unquote(args['url'])

        item = xbmcgui.ListItem(title, iconImage = '', thumbnailImage = '')
        item.setInfo(type="Video", infoLabels={"Title":title})
        xbmc.Player().play(url, item)