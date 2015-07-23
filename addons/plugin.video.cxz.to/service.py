#!/usr/bin/python
# -*- coding: utf-8 -*-

import xbmc, xbmcgui, json, random
from var import addon_name
from kinopoisk import  kinopoisk

class Progress():
	def __init__(self, header):
		self.progr = xbmcgui.DialogProgressBG()
		self.progr.create(header)
		self.progr.update(0)
	def update(self, count, current, mess):
		percent = (float(current)/float(count))*100
		self.progr.update(int(percent), message=mess)
	def clouse(self):
		self.progr.close()
	def __del__(self):
		self.progr.close()


class Stack():
	def __init__(self):
		self._stack =[]
		self._lock = False

	def push(self, x):
		while self._lock:
			xbmc.sleep(50)
		self.lock()
		for i in x:
			#self._stack.insert(0,x)
			if i in self._stack:
				self._stack.remove(i)
			self._stack.append(i)
		self.unlock()

	def pop(self):
		while self._lock:
			xbmc.sleep(50)
		self.lock()
		value = self._stack.pop()
		self.unlock()
		return  value

	def len(self):
		return len(self._stack)

	def lock(self):
		self._lock = True
	def unlock(self):
		self._lock = False


class Service(xbmc.Monitor):
	def __init__(self, *args, **kwargs):
		xbmc.Monitor.__init__(self)
		self.Scrapper_stack= Stack()
		self.start_count =0
	def Run(self):
		while True:
			if xbmc.abortRequested:
				break
			if S.Scrapper_stack.len() and not S.Scrapper_stack._lock:self.scrapper()

			xbmc.sleep(500)

	def onNotification(self,sender,method,data):
		if sender!=addon_name:return

		if method == 'Other.scrapper':
			d = json.loads(data)
			if d:

				self.Scrapper_stack.push([{'cxzto refresh container':xbmc.getInfoLabel('Container.FolderPath')}])
				self.Scrapper_stack.push(d)
				self.start_count = self.Scrapper_stack.len()

	def scrapper(self):
		kp = kinopoisk()

		self.progress = Progress('Загрузка MetaData...')

		while self.Scrapper_stack.len():
			d = self.Scrapper_stack.pop()
			if isinstance(d, dict)and('cxzto refresh container' in d.keys()):
				if (d['cxzto refresh container']==xbmc.getInfoLabel('Container.FolderPath')):
					xbmc.executebuiltin('Container.Refresh')
				break

			self.progress.update(self.start_count, self.start_count-self.Scrapper_stack.len(), d['title'])
			#try:
			kp.GetInfo(d['href'])
			#except:
			#	pass
			if xbmc.abortRequested:
				self.progress.clouse()
				return

			xbmc.sleep(50)
		self.progress.clouse()


if __name__ == '__main__':
	S = Service()
	S.Run()