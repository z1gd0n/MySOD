# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# streamondemand - XBMC Plugin
# http://www.mimediacenter.info/foro/viewforum.php?f=36
# ------------------------------------------------------------
import Queue
import glob
import os
import re
import threading
import time
import urllib
from threading import Thread

from core import channeltools
from core import config
from platformcode import logger
from core.item import Item
from lib.fuzzywuzzy import fuzz
from platformcode import platformtools

TIMEOUT_TOTAL = config.get_setting("timeout")
MAX_THREADS = config.get_setting("maxthreads")


def mainlist(item, preferred_thumbnail="squares"):
    logger.info("streamondemand.channels.buscador mainlist")

    context = [{"title": "Scegli i canali da includere",
                "action": "settingCanal",
                "channel": item.channel}]
    itemlist = [
        Item(channel=item.channel,
             context=context,
             action="search",
             extra="movie",
             thumbnail="http://i.imgur.com/pE5WSZp.png",
             title="[COLOR yellow]Nuova ricerca film...[/COLOR]"),
        Item(channel=item.channel,
             context=context,
             action="search",
             extra="serie",
             thumbnail="http://i.imgur.com/pE5WSZp.png",
             title="[COLOR yellow]Nuova ricerca serie tv...[/COLOR]"),
        Item(channel=item.channel,
             thumbnail="http://i.imgur.com/pE5WSZp.png",
             action="settings",
             title="[COLOR green]Altre impostazioni[/COLOR]")
    ]

    saved_searches_list = get_saved_searches()

    context2 = context[:]
    context2.append({"title": "Cancella ricerche salvate",
                     "action": "clear_saved_searches",
                     "channel": item.channel})
    for saved_search_text in saved_searches_list:
        itemlist.append(
            Item(channel=item.channel, action="do_search", title=' "' + saved_search_text.split('{}')[0] + '"',
                 extra=saved_search_text, context=context2, category=saved_search_text))

    if len(saved_searches_list) > 0:
        itemlist.append(
            Item(channel=item.channel,
                 action="clear_saved_searches",
                 thumbnail="http://i.imgur.com/pE5WSZp.png",
                 title="[COLOR red]Elimina cronologia ricerche[/COLOR]"))

    return itemlist


def opciones(item):
    itemlist = [Item(channel=item.channel, action="settingCanal", title="Scegli i canali da includere nella ricerca"),
                Item(channel=item.channel, action="clear_saved_searches", title="Cancella ricerche salvate"),
                Item(channel=item.channel, action="settings", title="Altre opzioni")]
    return itemlist


def settings(item):
    return platformtools.show_channel_settings()


def settingCanal(item):
    channels_path = os.path.join(config.get_runtime_path(), "channels", '*.xml')
    channel_language = config.get_setting("channel_language")

    if channel_language == "":
        channel_language = "all"

    list_controls = []
    for infile in sorted(glob.glob(channels_path)):
        channel_name = os.path.basename(infile)[:-4]
        channel_parameters = channeltools.get_channel_parameters(channel_name)

        # Do not include inactive channel
        if channel_parameters["active"] != True:
            continue

        # Do not include adult channel if adult section is not selected
        if channel_parameters["adult"] == True and config.get_setting("adult_mode") == False:
            continue

        # Do not include channel if filtered by language
        if channel_language != "all" and channel_parameters["language"] != channel_language:
            continue

        # Do not include channel if not "include_in_global_search"
        include = channel_parameters["include_in_global_search"]
        if include not in ["", True]:
            continue
        else:
            # The stored value is searched in the channel configuration
            include_in_global_search = config.get_setting("include_in_global_search", channel_name)

        # Set the channel True if the configuration is missed 
        if include_in_global_search == "":
            include_in_global_search = True

        control = {'id': channel_name,
                   'type': "bool",
                   'label': channel_parameters["title"],
                   'default': include_in_global_search,
                   'enabled': True,
                   'visible': True}

        list_controls.append(control)

    return platformtools.show_channel_settings(list_controls=list_controls,
                                               caption="Canali inclusi nella ricerca globale",
                                               callback="save_settings", item=item)


def save_settings(item, dict_values):
    for v in dict_values:
        config.set_setting("include_in_global_search", dict_values[v], v)


def search(item, tecleado):
    logger.info("streamondemand.channels.buscador search")

    item.extra = tecleado + '{}' + item.extra

    if tecleado != "":
        save_search(item.extra)

    return do_search(item)


def channel_search(queue, channel_parameters, category, tecleado):
    try:
        search_results = []

        title_search = urllib.unquote_plus(tecleado)

        exec "from channels import " + channel_parameters["channel"] + " as module"
        mainlist = module.mainlist(Item(channel=channel_parameters["channel"]))

        for item in mainlist:
            if item.action != "search" or category and item.extra != category:
                continue

            for res_item in module.search(item.clone(), tecleado):
                title = res_item.fulltitle

                # Clean up a bit the returned title to improve the fuzzy matching
                title = re.sub(r'\(.*\)', '', title)  # Anything within ()
                title = re.sub(r'\[.*\]', '', title)  # Anything within []

                # Check if the found title fuzzy matches the searched one
                if fuzz.WRatio(title_search, title) > 85:
                    res_item.title = "[COLOR azure]" + res_item.title + "[/COLOR][COLOR orange] su [/COLOR][COLOR green]" + channel_parameters["title"] + "[/COLOR]"
                    search_results.append(res_item)

        queue.put(search_results)

    except:
        logger.error("No se puede buscar en: " + channel_parameters["title"])
        import traceback
        logger.error(traceback.format_exc())


# This is the search function
def do_search(item):
    logger.info("streamondemand.channels.buscador do_search")

    if '{}' in item.extra:
        tecleado, category = item.extra.split('{}')
    else:
        tecleado = item.extra
        category = ""

    itemlist = []

    channels_path = os.path.join(config.get_runtime_path(), "channels", '*.xml')
    logger.info("streamondemand.channels.buscador channels_path=" + channels_path)

    channel_language = config.get_setting("channel_language")
    logger.info("streamondemand.channels.buscador channel_language=" + channel_language)
    if channel_language == "":
        channel_language = "all"
        logger.info("streamondemand.channels.buscador channel_language=" + channel_language)

    progreso = platformtools.dialog_progress_bg("Cercando " + urllib.unquote_plus(tecleado), "")
    channel_files = sorted(glob.glob(channels_path))

    number_of_channels = 0
    completed_channels = 0
    search_results = Queue.Queue()

    start_time = int(time.time())

    for infile in channel_files:

        basename_without_extension = os.path.basename(infile)[:-4]

        channel_parameters = channeltools.get_channel_parameters(basename_without_extension)

        # Ignore inactive channel
        if channel_parameters["active"] != True:
            continue

        # In case of search by categories
        if category and category not in channel_parameters["categories"]:
            continue

        # Ignore channel filtered by language
        if channel_language != "all" and channel_parameters["language"] != channel_language:
            continue

        # Ignore channel not configured in global search
        include_in_global_search = channel_parameters["include_in_global_search"]
        if include_in_global_search == True:
            # Search in the channel configuration
            include_in_global_search = config.get_setting("include_in_global_search", basename_without_extension)
        if include_in_global_search == False:
            continue

        t = Thread(target=channel_search, args=[search_results, channel_parameters, category, tecleado])
        t.setDaemon(True)
        t.start()
        number_of_channels += 1

        while threading.active_count() >= MAX_THREADS:
            delta_time = int(time.time()) - start_time
            if len(itemlist) <= 0:
                timeout = None  # No result so far,lets the thread to continue working until a result is returned
            elif delta_time >= TIMEOUT_TOTAL:
                progreso.close()
                itemlist = sorted(itemlist, key=lambda item: item.fulltitle)
                return itemlist
            else:
                timeout = TIMEOUT_TOTAL - delta_time  # Still time to gather other results

            progreso.update(completed_channels * 100 / number_of_channels)

            try:
                itemlist.extend(search_results.get(timeout=timeout))
                completed_channels += 1
            except:
                progreso.close()
                itemlist = sorted(itemlist, key=lambda item: item.fulltitle)
                return itemlist

    while completed_channels < number_of_channels:

        delta_time = int(time.time()) - start_time
        if len(itemlist) <= 0:
            timeout = None  # No result so far,lets the thread to continue working until a result is returned
        elif delta_time >= TIMEOUT_TOTAL:
            break  # At least a result matching the searched title has been found, lets stop the search
        else:
            timeout = TIMEOUT_TOTAL - delta_time  # Still time to gather other results

        progreso.update(completed_channels * 100 / number_of_channels)

        try:
            itemlist.extend(search_results.get(timeout=timeout))
            completed_channels += 1
        except:
            # Expired timeout raise an exception
            break

    progreso.close()

    itemlist = sorted(itemlist, key=lambda item: item.fulltitle)

    return itemlist


def save_search(text):

    saved_searches_limit = int((10, 20, 30, 40, )[int(config.get_setting("saved_searches_limit", "buscador"))])

    current_saved_searches_list = config.get_setting("saved_searches_list", "buscador")
    if current_saved_searches_list is None:
        saved_searches_list = []
    else:
        saved_searches_list = list(current_saved_searches_list)

    if text in saved_searches_list:
        saved_searches_list.remove(text)

    saved_searches_list.insert(0, text)

    config.set_setting("saved_searches_list", saved_searches_list[:saved_searches_limit], "buscador")


def clear_saved_searches(item):
    config.set_setting("saved_searches_list", list(), "buscador")
    platformtools.dialog_ok("Ricerca", "Ricerche cancellate correttamente")


def get_saved_searches():
    current_saved_searches_list = config.get_setting("saved_searches_list", "buscador")
    if current_saved_searches_list is None:
        saved_searches_list = []
    else:
        saved_searches_list = list(current_saved_searches_list)
    
    return saved_searches_list
