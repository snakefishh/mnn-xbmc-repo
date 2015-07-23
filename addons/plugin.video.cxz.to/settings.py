#!/usr/bin/python
# -*- coding: utf-8 -*-

import xbmcaddon, xbmcgui, sys
from var import addon_name

addon 	= xbmcaddon.Addon(id = addon_name)

def itemformatsettings():
	dialog = xbmcgui.Dialog()
	sh ={'Название, Год, Страна, (Качество, Рейтинг)'  :'/s[S] /s/t /y ● /c (/q [COLOR 80008000]↑/vp[/COLOR] [COLOR 80FF0000]↓/vn[/COLOR])',
		 'Название, (Качество, Рейтинг)'               :'/s[S] /s/t (/q [COLOR 80008000]↑/vp[/COLOR] [COLOR 80FF0000]↓/vn[/COLOR])',
		 'Название'                                            :'/s[S] /s/t'
		}
	ret = dialog.select('Шаблоны', sh.keys())
	if ret==-1:
		return
	addon.setSetting('item_format',sh[sh.keys()[ret]])
	addon.openSettings()

if sys.argv[1]=='itemformatsettings':
	itemformatsettings()
	sys.exit()

