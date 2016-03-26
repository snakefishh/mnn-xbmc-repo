#!/usr/bin/python
# -*- coding: utf-8 -*-


import xbmcplugin
import xbmcgui
import xbmc
import urllib
import sys
import json
import datetime
import re
import requests
import xml.etree.ElementTree as ElementTree
import time
from time import mktime

import HTMLParser

html = HTMLParser.HTMLParser()

Android_User_Agent = 'Peers.TV/6.10.2 Android/4.4.4 phone/Galaxy Tab E/arm64'
Player_User_Agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:35.0) Gecko/20100101 Firefox/35.0'

ARCHIVE_FILE_URL = "http://hls.peers.tv/playlist/program/%s.m3u8?rnd=626&t=%s"
CHANNEL_LIST_URL = "http://api.peers.tv/peerstv/2/"
SCHEDULE_FOR_DAY_URL = 'http://api.peers.tv/tvguide/2/schedule.json?channel=%s&dates=%s'
SCHEDULE_FOR_WEEK_URL = 'http://peers.tv/ajax/program/%s/%s/'


def get(url, headers=None, data=None):
    if data is None:
        data = {}
    if headers is None:
        headers = {}
    session = requests.session()
    headers["User-Agent"] = Player_User_Agent
    return session.get(url, data=data, headers=headers)


def load_channels(plugin_handle=None):
    channel_list = get(CHANNEL_LIST_URL)
    root = ElementTree.fromstring(channel_list.content)

    namespace = {
        'p': 'http://xspf.org/ns/0/',
        'vlc': 'http://www.videolan.org/vlc/playlist/ns/0/',
        'cn': 'http://www.cn.ru',
        'inetra': 'http://www.inetra.ru'
    }

    xbmcplugin.addSortMethod(plugin_handle, xbmcplugin.SORT_METHOD_TITLE)

    channels = root.findall("./p:trackList/p:track", namespace)
    for channel in channels:
        liveurl = channel.find("./p:location", namespace).text
        title = channel.find("./p:title", namespace).text
        img = channel.find("./p:image", namespace).text
        inetra = channel.find('./p:extension[@application="http://www.inetra.ru"]', namespace)
        channel_info = inetra.find("./inetra:channel-inf", namespace)
        stream_info = inetra.find("./inetra:stream-inf", namespace)
        channel_id = channel_info.find("./p:channel-id", namespace).text
        territory_id_match = re.search("/(\d+)/", liveurl)
        territory_id = territory_id_match.group(1) if territory_id_match is not None else None
        if territory_id is None:
            territory_id_element = channel_info.find("./p:territory-id", namespace)
            territory_id = territory_id_element.text if territory_id_element is not None else 16

        has_archive = channel_info.find("./p:recordable", namespace).text == "false"
        access_allowed = stream_info.find("./p:access", namespace).text == "allowed"

        if access_allowed:
            uri = '%s?%s' % (sys.argv[0], urllib.urlencode(
                {'mode': 'getprogram',
                 'id': channel_id,
                 'liveurl': liveurl,
                 'territory_id': territory_id,
                 'access_allowed': access_allowed,
                 'has_archive': has_archive
                 }))

            item = xbmcgui.ListItem(title, iconImage=img, thumbnailImage=img)
            item.setInfo(type="Video", infoLabels={"Title": title})
            xbmcplugin.addDirectoryItem(plugin_handle, uri, item, isFolder=True, totalItems=len(channels))

    xbmcplugin.endOfDirectory(plugin_handle)


def get_tv_program(params, plugin_handle=None, sort_mode=0):
    # we could parse the results of schedule_old.json request here but maybe android api is more stable

    today = datetime.date.today()

    liveurl = urllib.unquote_plus(params['liveurl'])
    channel_id = params['id']

    xbmc.log('[plugin.video.peers.tv] params %s' % params, xbmc.LOGNOTICE)

    update_list = True
    if "date" in params:
        program_requested_for_date = urllib.unquote_plus(params["date"])
    else:
        update_list = False
        program_requested_for_date = today.strftime('%Y-%m-%d')

    schedule_dates_url = SCHEDULE_FOR_WEEK_URL % (channel_id, program_requested_for_date)
    xbmc.log('[plugin.video.peers.tv] loading %s' % schedule_dates_url, xbmc.LOGNOTICE)
    js = json.loads(get(schedule_dates_url).content)
    if not js:
        xbmc.log('[plugin.video.peers.tv] json not loaded', xbmc.LOGERROR)
        return

    scheduled_dates = js['week']
    if sort_mode == 0:
        scheduled_dates.reverse()

    for schedule in scheduled_dates:

        schedule_date = datetime.datetime.fromtimestamp(mktime(time.strptime(schedule["date"], "%m/%d/%Y"))).date()
        schedule_date_string = "%s-%02d-%02d" % (schedule_date.year, schedule_date.month, schedule_date.day)

        if schedule_date <= today:  # we don't need schedule for future
            uri_params = params.copy()
            uri_params["date"] = schedule_date_string
            uri_params["liveurl"] = liveurl

            is_selected_date = schedule_date_string == program_requested_for_date
            if is_selected_date and schedule_date == today:
                title = "Прямая трансляция"
                uri = '%s?%s' % (sys.argv[0],
                                 urllib.urlencode({'mode': 'play', 'title': title, 'playurl': liveurl}))
                item = xbmcgui.ListItem('[COLOR FFFE2E2E]%s - %s[/COLOR]' % (schedule_date_string, title))
            elif schedule["recs"]:
                uri = '%s?%s' % (sys.argv[0], urllib.urlencode(uri_params))
                item = xbmcgui.ListItem(schedule_date_string)
            else:
                uri = None
                item = None

            if item is not None:
                xbmcplugin.addDirectoryItem(plugin_handle, uri, item, isFolder=not is_selected_date)

            if is_selected_date:
                timezone_regex = re.compile("\s*GMT[\+-]\d{4}", re.IGNORECASE)
                telecasts_list = js["telecasts"]
                for telecast in telecasts_list:
                    title = html.unescape(telecast['title']).replace("<br />", "").encode('UTF-8')
                    description = html.unescape(telecast['desc']).replace("<br />", "").encode('UTF-8')

                    start_time = datetime.datetime.fromtimestamp(
                        mktime(time.strptime(timezone_regex.sub("", telecast["time"]), "%m/%d/%Y %H:%M:%S")))
                    end_time = datetime.datetime.fromtimestamp(
                        mktime(time.strptime(timezone_regex.sub("", telecast["ends"]), "%m/%d/%Y %H:%M:%S")))
                    title_time = "%02d:%02d - %02d:%02d" % (
                        start_time.hour, start_time.minute, end_time.hour, end_time.minute)

                    img = "" if "image" not in telecast else telecast["image"]

                    if end_time > datetime.datetime.now() > start_time:
                        colored_title = '  [COLOR FFFE2E2E]%s[/COLOR]' % title
                        filesurl = liveurl
                    elif datetime.datetime.now() > end_time:
                        files = telecast["files"]
                        filesurl = files[0]["movie"] if files else None
                        colored_title = '  [COLOR FF0000FF]%s[/COLOR]' % title
                    else:
                        colored_title = '  [COLOR FFBDBDBD]%s[/COLOR]' % title
                        filesurl = liveurl

                    if filesurl:
                        info = {"title": title, 'plot': description}
                        uri = '%s?%s' % (
                            sys.argv[0],
                            urllib.urlencode({'mode': 'play', 'title': description + ': ' + title, 'playurl': filesurl}))
                        item = xbmcgui.ListItem('    ' + title_time + colored_title)
                        item.setArt({'thumb': img, 'banner': img, 'fanart': img})
                        item.setInfo(type="Video", infoLabels=info)
                        xbmcplugin.addDirectoryItem(plugin_handle, uri, item, isFolder=False,
                                                    totalItems=len(telecasts_list))

    xbmcplugin.endOfDirectory(plugin_handle, updateListing=update_list)


def get_channel_territory_id():
    territory_id = 483  # default Germany
    js = json.loads(get("http://api.peers.tv/registry/2/whereami.json").content)
    if js and js["territories"]:
        territory_id = js["territories"][0]["territoryId"]
    return territory_id


def play(params):
    if 'playurl' not in params:
        return None

    title = urllib.unquote_plus(params['title'])
    url = urllib.unquote_plus(params['playurl']) + '|User-Agent=%s' % Player_User_Agent

    playList = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    playList.clear()

    item = xbmcgui.ListItem(title, iconImage='', thumbnailImage='')
    item.setInfo(type="Video", infoLabels={"Title": title})

    playList.add(url, item)
    xbmc.Player().play(playList)
