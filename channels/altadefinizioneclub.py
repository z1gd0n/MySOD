# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# streamondemand.- XBMC Plugin
# Canale altadefinizione01
# http://www.mimediacenter.info/foro/viewforum.php?f=36
# ------------------------------------------------------------
import re

import xbmc

from core import httptools
from platformcode import logger
from core import scrapertools
from core.item import Item
from core.tmdb import infoSod

__channel__ = "altadefinizioneclub"

host = "http://altadefinizione.bid"


def mainlist(item):
    logger.info("streamondemand.altadefinizione01 mainlist")
    itemlist = [Item(channel=__channel__,
                     title="[COLOR azure]Prime visioni[/COLOR]",
                     action="peliculas",
                     url="%s/prime-visioni/" % host,
                     thumbnail=ThumbPrimavisione,
                     fanart=fanart),
                Item(channel=__channel__,
                     title="[COLOR azure]Film in HD[/COLOR]",
                     action="peliculas",
                     url="%s/?s=[HD]" % host,
                     thumbnail=ThumbPrimavisione,
                     fanart=fanart),
                Item(channel=__channel__,
                     title="[COLOR azure]Genere[/COLOR]",
                     action="categorias",
                     url=host,
                     thumbnail=ThumbPrimavisione,
                     fanart=fanart),
                Item(channel=__channel__,
                     title="[COLOR yellow]Cerca...[/COLOR]",
                     extra="movie",
                     action="search",
                     thumbnail=ThumbPrimavisione,
                     fanart=fanart)]

    return itemlist


def peliculas(item):
    logger.info("streamondemand.altadefinizioneclub peliculas")
    itemlist = []

    patron = '<li><a href="([^"]+)" data-thumbnail="([^"]+)"><div>\s*<div class="title">(.*?)</div>'
    for scrapedurl, scrapedthumbnail, scrapedtitle in scrapedAll(item.url, patron):
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        scrapedtitle = scrapedtitle.replace("[HD]", "")
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="findvideos",
                 contentType="movie",
                 title=scrapedtitle,
                 fulltitle=scrapedtitle,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 viewmode="movie"),
            tipo="movie", ))

    # Paginazione
    # ===========================================================================================================================
    matches = scrapedSingle(item.url, '<span class=\'pages\'>(.*?)class="clearfix"',
                            "class='current'>.*?</span>.*?href=\"(.*?)\">.*?</a>")
    if len(matches) > 0:
        paginaurl = scrapertools.decodeHtmlentities(matches[0])
        itemlist.append(
            Item(channel=__channel__, action="peliculas", title=AvantiTxt, url=paginaurl, thumbnail=AvantiImg))
        itemlist.append(
            Item(channel=__channel__, action="HomePage", title=HomeTxt, thumbnail=ThumbnailHome, folder=True))
    else:
        itemlist.append(
            Item(channel=__channel__, action="mainlist", title=ListTxt, thumbnail=ThumbnailHome, folder=True))
    # ===========================================================================================================================
    return itemlist


def search(item, texto):
    logger.info("[altadefinizioneclub.py] " + item.url + " search " + texto)
    item.url = host + "/?s=%s" % texto

    return peliculas(item)

def categorias(item):
    logger.info("streamondemand.altadefinizioneclub categorias")
    itemlist = []

    # data = scrapertools.cache_page(item.url)
    data = httptools.downloadpage(item.url).data

    # Narrow search by selecting only the combo
    bloque = scrapertools.get_match(data, '<h3 class="widget-title">Categorie</h3>(.*?)</ul>')

    # The categories are the options for the combo
    patron = '<li><a href="([^"]+)">(.*?)</a></li>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for scrapedurl, scrapedtitle in matches:
        scrapedurl = host + scrapedurl
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png",
                 folder=True))

    return itemlist

def HomePage(item):
    xbmc.executebuiltin("ReplaceWindow(10024,plugin://plugin.video.streamondemand)")


# =================================================================
# Funzioni di servizio
# -----------------------------------------------------------------
def scrapedAll(url="", patron=""):
    data = httptools.downloadpage(url).data
    data = data.replace('<span class="hdbox">HD</span>', "")
    MyPatron = patron
    matches = re.compile(MyPatron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)
    return matches


# =================================================================

# -----------------------------------------------------------------
def scrapedSingle(url="", single="", patron=""):
    data = httptools.downloadpage(url).data
    elemento = scrapertools.find_single_match(data, single)
    logger.info("elemento ->" + elemento)
    matches = re.compile(patron, re.DOTALL).findall(elemento)
    scrapertools.printMatches(matches)
    return matches


# =================================================================

HomeTxt = "[COLOR yellow]Torna Home[/COLOR]"
ThumbnailHome = "https://upload.wikimedia.org/wikipedia/commons/thumb/8/81/Dynamic-blue-up.svg/580px-Dynamic-blue-up.svg.png"
ListTxt = "[COLOR orange]Torna a elenco principale [/COLOR]"
AvantiTxt = "[COLOR orange]Successivo>>[/COLOR]"
AvantiImg = "http://2.bp.blogspot.com/-fE9tzwmjaeQ/UcM2apxDtjI/AAAAAAAAeeg/WKSGM2TADLM/s1600/pager+old.png"
ThumbPrimavisione = "http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png"
FilmFanart = "https://superrepo.org/static/images/fanart/original/script.artwork.downloader.jpg"
fanart = "http://www.virgilioweb.it/wp-content/uploads/2015/06/film-streaming.jpg"
