#!/usr/bin/python
# -*- coding: utf-8 -*-

import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import os
import math
from datetime import datetime, timedelta
from time import mktime, strftime


_addon_name 	= 'script.service.jtvtoxmltv'
_addon 			= xbmcaddon.Addon(id = _addon_name)
__icon__        = _addon.getAddonInfo('icon')
_addon_patch 	= xbmc.translatePath(_addon.getAddonInfo('path'))
tmp_path        = xbmc.translatePath( os.path.join( "special://temp", _addon_name ) )
addon_data_path = xbmc.translatePath( os.path.join( "special://profile/addon_data", _addon_name))

if (sys.platform == 'win32') or (sys.platform == 'win64'):
	_addon_patch    = _addon_patch.decode('utf-8')
	tmp_path        = tmp_path.decode('utf-8')
	addon_data_path = addon_data_path.decode('utf-8')
sys.path.append(os.path.join(_addon_patch, 'resources', 'lib'))
from jtv import *

s={}
s['enabled']        = _addon.getSetting("enabled")
s['interval']       = _addon.getSetting("interval")
s['onstart']        = _addon.getSetting("onstart")
s['path']           = _addon.getSetting("path")
s['jtvpath']        = _addon.getSetting("jtvpath")
s['jtvurl']         = _addon.getSetting("jtvurl")
s['savepath']       = _addon.getSetting("savepath")
s['savepathfolder'] = _addon.getSetting("savepathfolder")
s['namefile']       = _addon.getSetting("namefile")
s['nextstart']      = _addon.getSetting("nextstart")
s['notalert']       = _addon.getSetting("notalert")
s['codepage']       = _addon.getSetting("codepage")

def settimer(h,m,s):
	xbmc.executebuiltin('XBMC.AlarmClock(jtv,XBMC.RunScript(script.service.jtvtoxmltv, onTimer),%s:%s:%s ,silent)'%(h,m,s))
	#xbmc.executebuiltin('XBMC.AlarmClock(jtv,XBMC.RunScript(script.service.jtvtoxmltv, onTimer),%s:%s:%s)'%(0,0,20))
	
def getjtv():	
	
	if s['path']=='1':
		urljtv = s['jtvurl']
	else:
		urljtv = s['jtvpath']
		
	if s['savepath']=='1':
		ph = xbmc.translatePath( os.path.join( "special://profile/addon_data", "pvr.iptvsimple"))
		nxmltv = ph + "/" + s['namefile']
	elif s['savepath']=='2':
		nxmltv = s['savepathfolder'] + s['namefile']
	else:
		nxmltv = addon_data_path + "/" + s['namefile']
		
	jtvunzip_path = xbmc.translatePath(os.path.join(tmp_path, 'jtvunzip/'))
	prg=jtvtoxml(jtvunzip_path, urljtv, s['path'])
	

#++++++++++++++++++++++++++++постобработка++++++++++++++++++++++++++++++++++	
	xmlzag = '<?xml version="1.0" encoding="utf-8" ?>\n\n<tv>\n'
	xmlcan = '<channel id="%s">\n<display-name lang="ru">%s</display-name>\n</channel>\n'
	xmlprog= '<programme start="%s" stop="%s" channel="%s">\n<title lang="ru">%s</title>\n</programme>\n'

	xmltv=''
	xmltv2=''
#---------------------------------------	
#по m3u (bambuk)

#	webFile = urllib.urlopen(urlm3u)
#	buf = webFile.read()
#	qqq=re.compile('#EXTINF:-1 tvg-name="([0-9]+)" ,(.*)').findall(buf)
#	webFile.close()
#
#	for key, title in qqq:
#		try:
#			ind =prg[0].index(key)
#		except:
#			continue
#		
#		xmltv = xmltv + xmlcan % (key, title)
#		
#		for j in prg[1][ind]:
#			xmltv2 = xmltv2+ xmlprog % (j[0], j[1], key, j[2])
#	
	

#-----------------------------------------------
#по имени jtv
	ind=0
	for i in prg[0]:
		dec=i
		xmltv = xmltv + xmlcan %(dec, dec)
		for j in prg[1][ind]:
			xmltv2 = xmltv2+ xmlprog % (j[0], j[1], dec, j[2].decode(s['codepage']).encode('UTF-8'))
		ind=ind+1	
	
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

	fxmltv = open(nxmltv,'w')
	fxmltv.write(xmlzag+xmltv+xmltv2+'\n</tv>')
	fxmltv.close()
	
#++++++++++++++++++++++++++++++++++++++++++++++++++++++
	
	if s['notalert']=='false':xbmc.executebuiltin('XBMC.Notification(%s ,%s, 10, %s)'%(_addon_name, 'Программа обновлена', __icon__))
	

if sys.argv[1] == 'start':
	if s['enabled']=='false': sys.exit()
	
	if not os.path.exists(addon_data_path):
		os.makedirs(addon_data_path)
		
	if s['onstart']=='true':
		settimer(0,0,30)
	else:
		
		try:
			dtsettings=datetime.strptime(s['nextstart'], "%Y-%m-%d %H:%M:%S") 
		except:
			dtsettings=datetime.now()
			_addon.setSetting("nextstart", dtsettings.strftime('%Y-%m-%d %H:%M:%S'))
		
		if (datetime.now()>=dtsettings):
			settimer(0,0,5)
		else:
			nextstart =dtsettings-datetime.now()
			nextstarts=nextstart.total_seconds()
			h=int(nextstarts//3600)
			m=int((nextstarts//60)%60)
			settimer(str(h),str(m),'0')
		
elif sys.argv[1] == 'chsettings':
	xbmc.executebuiltin('XBMC.CancelAlarm(jtv, silent)')
	if s['enabled']=='true': settimer(0,0,5)
	
elif sys.argv[1] == 'onTimer':	
	getjtv()
	nextstart = datetime.now()+timedelta(days=int(s['interval']))
	_addon.setSetting("nextstart", nextstart.strftime('%Y-%m-%d %H:%M:%S'))
	xbmc.executebuiltin('XBMC.CancelAlarm(jtv, silent)')
	settimer(str(int(s['interval'])*24),'0','0')
	
elif sys.argv[1] == 'update':	
	xbmc.executebuiltin('XBMC.AlarmClock(jtv,XBMC.RunScript(script.service.jtvtoxmltv, onTimer),%s:%s:%s)'%(0,0,5))
	#getjtv()

elif  sys.argv[1] == 'IptvSimple_settings':
	xbmc.executebuiltin('Addon.OpenSettings(pvr.iptvsimple)')
	xbmc.executebuiltin('SetFocus(201)')
	xbmc.executebuiltin('SetFocus(102)')
	#xbmc.executebuiltin('Action(Select)')
	

else:
	_addon.openSettings()
	#xbmcplugin.endOfDirectory(int(sys.argv[1]))

	