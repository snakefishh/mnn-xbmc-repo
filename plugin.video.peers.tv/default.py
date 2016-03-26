#!/usr/bin/python
# -*- coding: utf-8 -*-


import xbmc
import xbmcaddon
import xbmcplugin
import sys
import peerstv

PLUGIN_ID = 'plugin.video.peers.tv'

__settings__ = xbmcaddon.Addon(id=PLUGIN_ID)
PROXY = __settings__.getSetting("proxy")
PROXY_IP = __settings__.getSetting("proxyip")
SORT = int(__settings__.getSetting("sort"))

PLUGIN_HANDLE = int(sys.argv[1])
xbmcplugin.setContent(PLUGIN_HANDLE, 'movies')


def get_params():
    param = []
    paramstring = sys.argv[2]
    if len(paramstring) >= 2:
        params = sys.argv[2]
        cleanedparams = params.replace('?', '')
        if (params[len(params) - 1] == '/'):
            params = params[0:len(params) - 2]
        pairsofparams = cleanedparams.split('&')
        param = {}
        for i in range(len(pairsofparams)):
            splitparams = pairsofparams[i].split('=')
            if (len(splitparams)) == 2:
                param[splitparams[0]] = splitparams[1]
    return param


params = get_params()
xbmc.log('[plugin.video.peers.tv] params %s' % params, xbmc.LOGNOTICE)
mode = None
try:
    mode = params["mode"]
except:
    pass

if mode is None:
    peerstv.load_channels(PLUGIN_HANDLE)
elif mode == 'getprogram':
    peerstv.get_tv_program(params, PLUGIN_HANDLE, SORT)
elif mode == 'play':
    peerstv.play(params)
