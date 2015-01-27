#!/usr/bin/python
# -*- coding: utf-8 -*-

from ExtSearch import Plugin
import urllib, urllib2, re, sys, os, json, datetime, time
import xbmcplugin, xbmcgui, xbmcaddon, xbmc
from lib import *
from BeautifulSoup import BeautifulSoup
plugin_handle = int(sys.argv[1])

class Treetv(Plugin):
    Name = 'Tree.tv (Пока не работает)'

    def Command(self, args):
        try:
            if (args['plugin'] == self.__class__.__name__)or(args['plugin'] =='all'):
                run = getattr(self, args['command'])
                result = run(args)
                return result
            else:
                return False
        except:
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
                print item
                img = item.find('div', 'preview').find('img')['src']

                item_content = item.find('div', 'item_content')
                a = item_content.find('a')
                href = a['href']
                title = a.string
                AddFolder(title,'External_Search',{'plugin':self.__class__.__name__,'command':'', 'href':href}, img='http://tree.tv'+img,ico='http://tree.tv'+img)
            return 'closedir'
