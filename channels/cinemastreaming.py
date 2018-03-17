# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# streamondemand.- XBMC Plugin
# Canale cinemastreaming
# http://www.mimediacenter.info/foro/viewforum.php?f=36
# Version: 201802030900
# ------------------------------------------------------------
import re  
import urlparse

from core import config, httptools
from platformcode import logger
from core import scrapertools
from core import servertools
from core.item import Item
from core.tmdb import infoSod

__channel__ = "cinemastreaming"

host = "https://www.cinemastreaming.pw"

headers = [['Referer', host]]

def mainlist(item):
    logger.info("[cinemastreaming.py] mainlist")

    # Main options
    itemlist = [Item(channel=__channel__,
                     action="peliculas",
                     title="[COLOR azure]Film[/COLOR]",
                     url="%s/film/" % host,
                     extra="movie",
                     thumbnail="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png"),
                Item(channel=__channel__,
                     action="categorie",
                     title="[COLOR azure]Categorie[/COLOR]",
                     url=host,
                     extra="movie",
                     thumbnail="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png"),
                Item(channel=__channel__,
                     action="paesi",
                     title="[COLOR azure]Paesi[/COLOR]",
                     url=host,
                     extra="movie",
                     thumbnail="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png"),
                Item(channel=__channel__,
                     action="search",
                     title="[COLOR yellow]Cerca Film[/COLOR]",
                     extra="movie",
                     thumbnail="http://dc467.4shared.com/img/fEbJqOum/s7/13feaf0c8c0/Search")]

    return itemlist


def peliculas(item):
    logger.info("[cinemastreaming.py] peliculas")
    itemlist = []

    if item.url == "":
        item.url = host

    # Carica la pagina 
    data = httptools.downloadpage(item.url, headers=headers).data
    #logger.info("*****************************")
    #logger.info(data)

    # Estrae i contenuti 
    patronvideos = '<li class="TPostMv">.*?<a href="([^"]+)">.*?<img width="215" height="320" src="([^"]+)".*?<h2 class="Title">([^"]+)</h2>.*?<span class="Year">([^"]+)</span>.*?<p>([^"]+)</p>'
    matches = re.compile(patronvideos, re.DOTALL).finditer(data)
    
    for match in matches:
        scrapedurl = urlparse.urljoin(item.url, match.group(1))
        scrapedthumbnail = urlparse.urljoin(item.url, match.group(2))
        scrapedthumbnail = scrapedthumbnail.replace(" ", "%20")
        scrapedtitle = scrapertools.unescape(match.group(3))
        year = scrapertools.unescape(match.group(4))
        scrapedplot = scrapertools.unescape("[COLOR orange]" + match.group(5) + "[/COLOR]\n")
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="findvideos",
                 contentType="movie",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title=scrapedtitle,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 extra=item.extra,
                 viewmode="movie_with_plot"), tipo='movie'))

    next_page = scrapertools.find_single_match(data, '<a class="next page-numbers" href="(.*?)">')

    if next_page != "":
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR orange]Successivo >>[/COLOR]",
                 url=next_page,
                 extra=item.extra,
                 thumbnail="http://2.bp.blogspot.com/-fE9tzwmjaeQ/UcM2apxDtjI/AAAAAAAAeeg/WKSGM2TADLM/s1600/pager+old.png"))
				 
    return itemlist

def categorie(item):
    logger.info("[cinemastreaming.py] categorie")
    itemlist = []

    if item.url == "":
        item.url = host

    # Carica la pagina 
    data = httptools.downloadpage(item.url, headers=headers).data

    # Estrae i contenuti 
    patronvideos = '<li id="menu-item-.*?category.*?<a href="([^"]+)">([^"]+)</a></li>'
    matches = re.compile(patronvideos, re.DOTALL).finditer(data)
    
    for match in matches:
        scrapedurl = urlparse.urljoin(item.url, match.group(1))
        scrapedtitle = urlparse.urljoin(item.url, match.group(2))
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title=match.group(2),
                 url=match.group(1),
                 thumbnail="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png",
                 folder=True))

    return itemlist

def paesi(item):
    logger.info("[cinemastreaming.py] paesi")
    itemlist = []

    if item.url == "":
        item.url = host

    # Carica la pagina 
    data = httptools.downloadpage(item.url, headers=headers).data

    # Estrae i contenuti 
    patronvideos = '<li id="menu-item-.*?country.*?<a href="([^"]+)">([^"]+)</a></li>'
    matches = re.compile(patronvideos, re.DOTALL).finditer(data)
    
    for match in matches:
        scrapedurl = urlparse.urljoin(item.url, match.group(1))
        scrapedtitle = urlparse.urljoin(item.url, match.group(2))
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title=match.group(2),
                 url=match.group(1),
                 thumbnail="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png",
                 folder=True))

    return itemlist

# Al llamarse "search" la función, el launcher pide un texto a buscar y lo añade como parámetro
def search(item, texto):
    logger.info("[cinemastreaming.py] " + item.url + " search " + texto)
    try:
        if item.extra == "movie":
            item.url = host + "/?s=" + texto
            return peliculas(item)
        if item.extra == "serie":
            item.url = host + "/serietv/?s=" + texto
            return listserie(item)

    # Continua la ricerca in caso di errore 
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

def listserie(item):
    # da implementare
    return None

def findvideos(item):
    logger.info("[cinemastreaming.py] findvideos")

    # Carica la pagina 
    data = httptools.downloadpage(item.url, headers=headers).data

    itemlist = servertools.find_video_items(data=data)

    for videoitem in itemlist:
        videoitem.title = "".join([item.title, '[COLOR green][B]' + videoitem.title + '[/B][/COLOR]'])
        videoitem.fulltitle = item.fulltitle
        videoitem.show = item.show
        videoitem.thumbnail = item.thumbnail
        videoitem.channel = __channel__

    return itemlist

