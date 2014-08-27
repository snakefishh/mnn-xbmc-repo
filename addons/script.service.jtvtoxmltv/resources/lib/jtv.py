#!/usr/bin/python
# -*- coding: utf-8 -*-


import sys
import socket, urllib, zipfile, StringIO, re, struct, os, shutil;
from struct import pack, unpack
from time import time, ctime, mktime
from ctypes import *
from datetime import datetime

def filetime_to_dt(ft):
	(s, ns100) = divmod(ft - 116444736000000000, 10000000)
	dt = datetime.utcfromtimestamp(s)
	dt = dt.replace(microsecond=(ns100 // 10))
	return dt
	
def jtvtoxml(jtvunzip_path, urljtv, locat):
			
	if not os.path.exists(jtvunzip_path):os.mkdir(jtvunzip_path)
		
	if locat=='1':
		webFile = urllib.urlopen(urljtv)
		buf = webFile.read()	
		sio = StringIO.StringIO(buf)
		zip = zipfile.ZipFile(sio, 'r')
	else:
		zip = zipfile.ZipFile(urljtv, 'r')
	
	for name in zip.namelist():
		try:
			unicode_name = name.decode('UTF-8').encode('UTF-8')
		except UnicodeDecodeError:
			unicode_name = name.decode('cp866').encode('UTF-8')

		f = open(jtvunzip_path+unicode_name, 'wb')
		f.write(zip.read(name))
		f.close()
	zip.close() 
	
	files = os.listdir(jtvunzip_path)
	jtvch=[]
	jtvprog=[]
	for ndx in filter(lambda x: x.endswith('.ndx'), files):
	
		fndx = open(jtvunzip_path+ndx, 'rb')
		pdt = os.path.splitext(ndx)[0]
		
		updt=pdt
		pdt= pdt+'.pdt'
		fpdt = open(jtvunzip_path+pdt, 'rb')
		
		tmp1=[]
		try:
			x1 = fndx.read(2)
			for i in xrange(struct.unpack('h',x1)[0]):
				x1 = fndx.read(12)
				struc = struct.unpack('<hqH',x1)
				fpdt.seek(struc[2])
				len1 = fpdt.read(2)
				len1 = struct.unpack('h',len1)[0]
				x1 = fpdt.read(len1)
				
				ftm=struc[1]				
				stm=str(filetime_to_dt(ftm)).replace('-','').replace(':','').replace(' ','')
							
				if not i==0:
					tmp[1]=stm
					tmp1.append(tmp)
				tmp = [stm, '', x1]
					
			tmp[1] = int(stm)+1	
			tmp1.append(tmp)		
												
		except Exception, e:
			print "JTV error: "+str(e)+" "+ndx
		finally:
			fndx.close()
			fpdt.close()
		jtvch.append(updt)
		jtvprog.append(tmp1)
		
	shutil.rmtree(jtvunzip_path)
	return (jtvch, jtvprog)

if __name__ == "__main__":	
	#urljtv   = "http://www.teleguide.info/download/new3/jtv.zip"
	urljtv   = "http://bambuk.tv/files/jtv2.zip"	
	
	jtvunzip_path = os.path.dirname(__file__)+'/jtvunzip/'		
	prg = 	jtvtoxml(jtvunzip_path, urljtv, 1)
	
	