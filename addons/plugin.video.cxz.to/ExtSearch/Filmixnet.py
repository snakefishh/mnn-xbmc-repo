#!/usr/bin/python
# -*- coding: utf-8 -*-

from ExtSearch import Plugin
import urllib, urllib2, re, sys, os, json, datetime, time
import xbmcplugin, xbmcgui, xbmcaddon, xbmc
from lib import *
from BeautifulSoup import BeautifulSoup

plugin_handle = int(sys.argv[1])

class Filmixnet(Plugin):
    Name = 'Filmix.net'

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
        result = self.search_(search)

        if result:
            AddItem(clGreen%('----Найдено на '+self.Name+'----'))
            for res in result:
                AddFolder(res['title'],'External_Search',{'plugin':self.__class__.__name__,'command':'FilmixNet_content', 'href':res['href']}, img=res['img'],ico=res['ico'])
            return
        else:
            return False

    def FilmixNet_content(self, args):
        href = urllib.unquote(args['href'])
        tp, cont = self.Content(href)
        if not tp:return

        cache('playlist').write(cont)

        if len(cont)>1:
            for ple in range(0,len(cont)):
                AddFolder('Плеер '+str(ple+1),'External_Search',{'plugin':self.__class__.__name__,'command':'FilmixNet_content2', 'le':ple})
            return True
        else:
            self.FilmixNet_content2({'le':0})

    def FilmixNet_content2(self, args): #Сезон
        cont = cache('playlist').read()

        if type(cont[int(args['le'])])==dict:
            for i in cont[int(args['le'])]['playlist']:
                AddFolder(i['comment'],'External_Search',{'plugin':self.__class__.__name__,'command':'FilmixNet_content3', 'le':args['le'], 'le2':i['comment'].encode('UTF-8')})
            return True
        else:
            self.FilmixNet_play({'title':' ', 'url':cont[int(args['le'])]})

    def FilmixNet_content3(self, args): #Серия
        le = urllib.unquote(args['le'])
        le2 = urllib.unquote(args['le2'])

        cont = cache('playlist').read()

        for i in cont[int(args['le'])]['playlist']:
            if i['comment'].encode('UTF-8')==le2:
                for j in i['playlist']:
                    AddItem(j['comment'],'External_Search',{'plugin':self.__class__.__name__,'command':'FilmixNet_play', 'title':j['comment'].encode('UTF-8'), 'url':j['file']})
                return True

    def FilmixNet_play(self, args):
        title = urllib.unquote_plus(args['title'])
        url = urllib.unquote(args['url'])
        k = re.compile('\[(.+?)\]').findall(url)
        if k:
            dialog = xbmcgui.Dialog()
            dialog_items =k[0].split(',')
            dlg= dialog.select('Качество Изображения', dialog_items)
            if dlg==-1:return
            url = url.replace('['+k[0]+']', dialog_items[dlg])

        item = xbmcgui.ListItem(title, iconImage = '', thumbnailImage = '')
        item.setInfo(type="Video", infoLabels={"Title":title})
        xbmc.Player().play(url, item)

    def Content(self,href):
        Data = Get_url(href)

        file5 = re.compile('(file5Array = cleanArray.*)').findall(Data)[0]
        file5 = re.compile('\'(.+?)\'').findall(file5)

        fil=[]
        for fl in file5:
            if len(fl)>5:
                fil.append(self.ub(fl))
        if fil:return 'file', fil

        pl5 = re.compile('(pl5Array = cleanArray.*)').findall(Data)[0]
        pl5 = re.compile('\'(.+?)\'').findall(pl5)

        playlst = []
        for pl5x in pl5:
            if len(pl5x)>5:
                js = json.loads(self.ub(Get_url(self.ub(pl5x))))
                playlst.append(js)
        if playlst:return 'pl', playlst
        return '', ''

    def search_(self, s):
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

    def ub(self,d):
        d = d[1:]
        s2=''
        for l in range(0, len(d), 3):
            s2 += unichr(int('0x'+d[l:l+3], 16))
        return s2