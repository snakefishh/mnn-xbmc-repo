#!/usr/bin/python
# -*- coding: utf-8 -*-
from addon import *
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

params = get_params()

try:
	mode = params['mode']
	#del params['mode']
except:
	mode = 'start'
try: 
	func = globals()[mode]
except:
	func = None
if func: func(params)
