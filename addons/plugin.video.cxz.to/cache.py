#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import time
import threading
import pickle, json
import xbmcvfs
from var import *

from sqlite3 import dbapi2 as sqlite

rtrCache_lock = threading.RLock()

class CacheToDb:
	def __init__(self, name, version, expire=0, size=0, step=100):
		self.name = name
		self.version = version
		self._connect()
		if expire:
			self.expire(expire)
		if size:
			self.size(size, step)

	def get(self, token, callback, *param, **kwargs):
		cur = self.db.cursor()
		cur.execute('select expire,data from cache where id=? limit 1', (token, ))
		row = cur.fetchone()
		cur.close()

		if row:
			if row[0] and row[0] < int(time.time()):
				pass
			else:
				try:
					obj = pickle.loads(row[1])
				except:
					pass
				else:
					return obj

		if not callback: return False
		response = callback(*param, **kwargs)

		if response[0]:
			obj = sqlite.Binary(pickle.dumps(response[1]))
			curtime = int(time.time())
			cur = self.db.cursor()
			if isinstance(response[0], bool):
				cur.execute('replace into cache(id,addtime,expire,data) values(?,?,?,?)', (token, curtime, None, obj))
			else:
				cur.execute('replace into cache(id,addtime,expire,data) values(?,?,?,?)',
				           (token, curtime, curtime + response[0], obj))
			self.db.commit()
			cur.close()

		return response[1]

	def expire(self, expire):
		# with rtrCache_lock:
		cur = self.db.cursor()
		cur.execute('delete from cache where addtime<?', (int(time.time()) - expire, ))
		self.db.commit()
		cur.close()

	def size(self, size, step=100):
		# with rtrCache_lock:
		while True:
			if os.path.getsize(self.filename) < size:
				break
			cur = self.db.cursor()
			cur.execute('select id from cache order by addtime asc limit ?', (step, ))
			rows = cur.fetchall()
			if not rows:
				cur.close()
				break
			cur.execute('delete from cache where id in (' + ','.join(len(rows) * '?') + ')', [x[0] for x in rows])
			self.db.commit()
			cur.close()

	def flush(self):
		# with rtrCache_lock:
		cur = self.db.cursor()
		cur.execute('delete from cache')
		self.db.commit()
		cur.close()

	def _connect(self):
		with rtrCache_lock:

			if not os.path.exists(addon_data_path):
				os.makedirs(addon_data_path)

			self.filename = os.path.join(addon_data_path, self.name)

			first = False
			if not xbmcvfs.exists(self.filename):
				first = True

			self.db = sqlite.connect(self.filename, check_same_thread=False)
			if not first:
				cur = self.db.cursor()
				try:
					cur.execute('select version from db_ver')
					row = cur.fetchone()
					if not row or float(row[0]) != self.version:
						cur.execute('drop table cache')
						cur.execute('drop table if exists db_ver')
						first = True
				except:
					cur.execute('drop table cache')
					first = True
				self.db.commit()
				cur.close()

			if first:
				cur = self.db.cursor()
				cur.execute('pragma auto_vacuum=1')
				cur.execute('create table cache(id varchar(255) unique, addtime integer, expire integer, data blob)')
				cur.execute('create index time on cache(addtime asc)')
				cur.execute('create table db_ver(version real)')
				cur.execute('insert into db_ver(version) values(?)', (self.version, ))
				self.db.commit()
				cur.close()

class CacheToFile():
	file_name = ''
	mode = ''
	def __init__(self, file_name, mode = 'json'):
		if not os.path.exists(addon_data_path):
				os.makedirs(addon_data_path)
		self.file_name = file_name
		self.mode = mode

	def write(self,data):
		F = open(addon_data_path+'/'+self.file_name, 'w')
		json.dump(data, F)
		F.close()

	def read(self):
		F = open(addon_data_path+'/'+self.file_name, 'r')
		data = json.load(F)
		F.close()
		return data