#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib2, urllib
import xbmc, xbmcaddon
from datetime import datetime, timedelta
from time import time
import sys, os, re, time, json
import sqlite3 as db
import hashlib
addon_name = 'plugin.video.videomore.ru'

update_pr_time     = 24

def construct_get(action, keys={}, app_id='VM4AndrPho', id='undef'):	
	#com.ctcmediagroup.videomore.apk\smali\com\ctcmediagroup\videomore\utils\DeviceManager.smali   CERTSE_YKE_NOHEP	
	api_sig = '1d5107871b12acabb235ef45f49ee967'
	
	keys['app_id']=app_id
	keys['id']=id
	url = 'http://videomore.ru/api/'+action+'.json?'
	url_get = ''
	for i in sorted(keys):
		if keys[i]:
			url_get += i+'='+keys[i]+'&'
	url_get = url_get[0:-1]
	sig=url_get+api_sig
	md5 = hashlib.md5()
	md5.update(sig)
	url_get += '&sig='+md5.hexdigest()
	return 	url+url_get

def Get_url(url, JSON=False):
	req = urllib2.Request(url)
	#req.add_header("User-Agent", User_Agent)
	try:
		response = urllib2.urlopen(req)
	except (urllib2.HTTPError, urllib2.URLError), e:
		xbmc.log('[%s] %s' %(addon_name, e), xbmc.LOGERROR)
		return None	
	try:
		Data=response.read()
		if response.headers.get("Content-Encoding", "") == "gzip":
			import zlib
			Data = zlib.decompressobj(16 + zlib.MAX_WBITS).decompress(Data)
	except urllib2.HTTPError:
		return None		
	response.close()	
	if JSON:
		try:
			js = json.loads(Data)
		except Exception, e:
			xbmc.log('[%s] %s' %(addon_name, e), xbmc.LOGERROR)
			return None
		Data = js		
	return Data

class Database:
	def __init__( self, db_name ):
		self.addon_name = 'plugin.video.videomore.ru'
		self.addon = xbmcaddon.Addon(id = self.addon_name)       
		self.addon_path =   xbmc.translatePath(self.addon.getAddonInfo('path'))
		self.data_path = xbmc.translatePath( os.path.join( 'special://profile/addon_data', self.addon_name) )	   
		if (sys.platform == 'win32') or (sys.platform == 'win64'):
			self.addon_path = self.addon_path.decode('utf-8')
			self.data_path = self.data_path.decode('utf-8')

		self.db_name = db_name
		self.connection = 0
		self.cursor = 0
		self.error = 0
				
		self.Create()
    
	def Create(self):
		if not os.path.exists(self.db_name):
			if not os.path.exists(os.path.dirname(self.db_name)):
				os.makedirs(os.path.dirname(self.db_name))
			
			sql_cr_path = os.path.join(self.addon_path, 'resources/base.sql')
			f = open(sql_cr_path, 'r')
			sql = f.read()
			sql = sql.split('--')
			f.close()
			
			conn = db.connect(database=self.db_name)
			cur = conn.cursor()
			for st in sql:
				cur.execute(st)
			conn.commit()
			cur.close()

	def Remove(self):
		if os.path.exists(self.db_name):
			try:
				os.remove(self.db_name)
			except:
				return False
		return True
		
	def Clear(self):
		self.Connect()	
		self.cursor.execute('DELETE FROM projects')
		self.cursor.execute('DELETE FROM seasons')
		self.cursor.execute('DELETE FROM tracks')
		self.cursor.execute('UPDATE settings SET lastupdate = "" WHERE id = 1;')
		self.connection.commit()
		self.Disconnect()
	
	def Connect(self):
		self.connection = db.connect(database=self.db_name)
		try:
			self.cursor = self.connection.cursor()
		except Exception, e:
			self.error = e
    
	def Disconnect(self):
		self.cursor.close()
	
	def GetProjectsLastUpdate(self):
		self.Connect()	
		self.cursor.execute('SELECT lastupdate FROM settings WHERE id = 1')
		lu = self.cursor.fetchone()
		if (lu[0] == None) or (lu[0] ==''):
			self.Disconnect()
			return None
		else:
			#dt = datetime.datetime.strptime(lu[0], '%Y-%m-%d %H:%M:%S.%f')
			dt = datetime.fromtimestamp(time.mktime(time.strptime(lu[0], '%Y-%m-%d %H:%M:%S.%f')))
			self.Disconnect()
			return dt
		
	def UpdateProjects(self):
		self.Connect()
		self.cursor.execute('SELECT md5 FROM projects')
		md5_db = self.cursor.fetchall()
		md5_db_sp = []
		for i in md5_db:
			md5_db_sp.append(i[0])
		
		self.cursor.execute('DELETE FROM projects')
		self.cursor.execute('DELETE FROM seasons')
		
		for c_id in range(0, 4):
			uri = construct_get('projects', {'category_id':str(c_id)})
			Data = Get_url(uri,JSON=True)
			if not Data:return None
			
			for i in Data:
				md5 = hashlib.md5()
				md5.update(str(i))					
				isupd = '0'
				if not (md5.hexdigest()) in md5_db_sp: isupd = '1'
				
				if i['channel_ids'][0] == 'no_channel': #Вроде СТС
					c_ids = '1'
				else:
					c_ids = i['channel_ids'][0]
				self.cursor.execute('INSERT INTO projects (project_id, title, category_id, channel_ids, overall_count, md5, isupdate, thumbnail) VALUES ("%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s");' % (i['id'], i['title'], i['category_id'], c_ids, i['overall_count'], md5.hexdigest(), isupd, i['big_thumbnail']))			
		
				if i['category_id'] != '0':
					for j in i['project_seasons']:				
						self.cursor.execute('INSERT INTO seasons (project_id, season, pos, title) VALUES ("%s", "%s", "%s", "%s");' %(i['id'], j, i['project_seasons'][j]['pos'], i['project_seasons'][j]['title']))
				del(md5)
		self.cursor.execute('UPDATE settings SET lastupdate = "%s"' % datetime.now())
		self.connection.commit()
		self.Disconnect()
		
	def GetByCategory(self, cat_id):
		lastupdate = self.GetProjectsLastUpdate()
		if  (not lastupdate) or ((datetime.now()- timedelta(hours = update_pr_time)) > lastupdate):
			self.UpdateProjects()
		self.Connect()
		self.cursor.execute('SELECT project_id, title, thumbnail FROM projects WHERE category_id =%s'%(cat_id))
		cat = self.cursor.fetchall()
		self.Disconnect()
		return cat
		
	def GetByChannel(self, ch_id):
		lastupdate = self.GetProjectsLastUpdate()
		if  (not lastupdate) or ((datetime.now()- timedelta(hours = update_pr_time)) > lastupdate):
			self.UpdateProjects()			
		self.Connect()
		self.cursor.execute('SELECT  project_id, title, thumbnail FROM projects WHERE channel_ids =%s  AND category_id <> 0' %(ch_id))
		ch = self.cursor.fetchall()
		self.Disconnect()
		return ch
	
	def GetSeasons(self, id):
		self.Connect()
		self.cursor.execute('SELECT season, pos, title FROM seasons WHERE project_id =%s ORDER BY pos' %(id))
		sea = self.cursor.fetchall()
		self.Disconnect()
		return sea
		
	def UpdateTracks(self, id):
		self.cursor.execute('DELETE FROM tracks WHERE project_id=%s' %(id))
		self.cursor.execute('SELECT overall_count FROM projects WHERE project_id =%s' %(id))
		oc = self.cursor.fetchone()		

		page10 = oc[0]//10.
		if page10 != oc[0]/10.:
			page10+=1

		for j in range(int(page10)):
			uri = construct_get('tracks', {'project_id':str(id),'per_page':'10', 'page':str(j+1) })			
			Data = Get_url(uri,JSON=True)
			if not Data:return None
			for i in Data:
				self.cursor.execute('INSERT INTO tracks (project_id, season, episode_of_season, title, tvurl, thumbnail) VALUES ("%s", "%s", "%s", "%s", "%s", "%s");'%(id, i['season_id'], i['episode_of_season'], i['title'].replace('"','\''), i['tv'], i['big_thumbnail_url']))			
			self.cursor.execute('UPDATE projects SET isupdate=0 WHERE project_id="%s"'% (id))
		self.connection.commit()

	
	def GetTracksOfSeason(self, id, Seas):
		self.Connect()
		self.cursor.execute('SELECT isupdate FROM projects WHERE project_id =%s' %(id))
		tlu = self.cursor.fetchone()
		if tlu[0] == 1:
			self.UpdateTracks(id)				
		self.cursor.execute('SELECT title, tvurl, thumbnail FROM tracks WHERE project_id=%s AND season=%s ORDER BY episode_of_season' %(id, Seas))
		tr = self.cursor.fetchall()
		self.Disconnect()
		return tr
	
	def search(self, val):
		self.Connect()
		uri = construct_get('suggestions', {'q':val})
		Data = Get_url(uri,JSON=True)
		if not Data:return None
		self.Disconnect()
		return Data
				