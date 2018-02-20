# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# streamondemand.- XBMC Plugin
# Canale ilgiramondo
# http://www.mimediacenter.info/foro/viewforum.php?f=36
# ------------------------------------------------------------
import re
import urlparse

from core import httptools
from platformcode import logger
from core import scrapertools
from core.item import Item

__channel__ = "ilgiramondo"

host = "http://www.ilgiramondo.net"


def mainlist(item):
    logger.info("streamondemand.ilgiramondo mainlist")
    itemlist = [Item(channel=__channel__, title="[COLOR azure]Video di Viaggi[/COLOR]", action="peliculas",
                     url=host + "/video-vacanze-viaggi/",
                     thumbnail="http://hotelsjaisalmer.com/wp-content/uploads/2016/10/Travel1.jpg")]

    return itemlist


def peliculas(item):
    logger.info("streamondemand.ilgiramondo peliculas")
    itemlist = []

    # Carica la pagina 
    data = httptools.downloadpage(item.url).data

    # Estrae i contenuti 
    patron = '<article id=[^>]+><div class="space">\s*<a href="([^"]+)"><img[^s]+src="(.*?)"[^>]+><\/a>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl, scrapedthumbnail in matches:
        html = httptools.downloadpage(scrapedurl).data
        start = html.find("</script></div>")
        end = html.find("</p>", start)
        scrapedplot = html[start:end]
        scrapedplot = re.sub(r'<[^>]*>', '', scrapedplot)
        scrapedplot = scrapertools.decodeHtmlentities(scrapedplot)
        html = httptools.downloadpage(scrapedurl).data
        start = html.find("<title>")
        end = html.find("</title>", start)
        scrapedtitle = html[start:end]
        scrapedtitle = re.sub(r'<[^>]*>', '', scrapedtitle)
        scrapedtitle = scrapedtitle.replace(" | Video Di Viaggi E Vacanze", "")
        # scrapedplot = ""
        itemlist.append(Item(channel=__channel__, action="findvideos", fulltitle=scrapedtitle, show=scrapedtitle,
                             title=scrapedtitle, url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot,
                             folder=True))

    # Paginazione 
    patronvideos = '<a class="next page-numbers" href="(.*?)">Successivo'
    matches = re.compile(patronvideos, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    if len(matches) > 0:
        scrapedurl = urlparse.urljoin(item.url, matches[0])
        itemlist.append(
            Item(channel=__channel__, action="HomePage", title="[COLOR yellow]Torna Home[/COLOR]", folder=True))
        itemlist.append(
            Item(channel=__channel__, action="peliculas", title="[COLOR orange]Avanti >>[/COLOR]", url=scrapedurl,
                 folder=True))

    return itemlist


def HomePage(item):
    import xbmc
    xbmc.executebuiltin("ReplaceWindow(10024,plugin://plugin.video.streamondemand)")
