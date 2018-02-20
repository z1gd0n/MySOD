# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# StreamOnDemand / XBMC Plugin
# Canale altadefinizione01_video
# http://www.mimediacenter.info/foro/viewtopic.php?f=36&t=7808
# ------------------------------------------------------------

import base64
import re
import urlparse

from core import httptools
from platformcode import logger
from core import scrapertools
from core import servertools
from core.item import Item
from core.tmdb import infoSod

__channel__ = "altadefinizione01_video"


host = "http://altadefinizione01.video/"

headers = [
    ['User-Agent', 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:44.0) Gecko/20100101 Firefox/44.0'],
    ['Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'],
    ['Accept-Encoding', 'gzip, deflate'],
    ['Referer', host],
    ['Cache-Control', 'max-age=0']
]


def isGeneric():
    return True

# ==============================================================================================================================================

def mainlist(item):
    logger.info("[altadefinizione01_video] mainlist")

    itemlist = [
        Item(channel=__channel__,
             title="[COLOR azure]Film - [COLOR orange]Novita'[/COLOR]",
             action="peliculas_new",
             url=host + "/category/nuove-uscite/",
             thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/popcorn_cinema_P.png"),
        Item(channel=__channel__,
             title="[COLOR azure]Film - [COLOR orange]Per Genere[/COLOR]",
             action="genere",
             url=host,
             thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/genres_P.png"),
        Item(channel=__channel__,
             title="[COLOR azure]Film - [COLOR orange]Nelle Sale[/COLOR]",
             action="peliculas_new",
             url=host + "/category/in-sala/",
             thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/movies_P.png"),
        Item(channel=__channel__,
             title="[COLOR azure]Film - [COLOR orange]Sottotitolati[/COLOR]",
             action="peliculas_new",
             url=host + "/category/sub-ita/",
             thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/movie_sub_P.png"),
        Item(channel=__channel__,
             title="[COLOR azure]Film - [COLOR orange]Animazione[/COLOR]",
             action="peliculas_new",
             url=host + "/category/film/animazione/",
             thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/animation2_P.png"),
        Item(channel=__channel__,
             title="[COLOR orange]Cerca...[/COLOR]",
             action="search",
             extra="movie",
             thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/search_P.png")]

    return itemlist

# ==============================================================================================================================================

def genere(item):
    logger.info("[altadefinizione01_video] genere")
    itemlist = []

    data = scrapertools.anti_cloudflare(item.url, headers)

    patron = '<a href="[^"]+">Film</a>(.*?)</div>'
    data = scrapertools.find_single_match(data, patron)

    patron = '<li class=".*?"><a href="([^"]+).*?">([^<]+)</a>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl, scrapedtitle in matches:
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas_new",
                 title=scrapedtitle,
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/genre_P.png",
                 folder=True))

    return itemlist

# ==============================================================================================================================================

def fichas(item):
    logger.info("[altadefinizione01_video] fichas")

    itemlist = []

    # Descarga la pagina 
    data = httptools.downloadpage(item.url, headers=headers).data
	

    patron = '<a href="([^"]+)" title="[^>]+">\s*<div class="poster">\s*<span class="rating">\s*'
    patron += '<i class="glyphicon glyphicon-star"></i><span class="rating-number">([^"]+)</span>\s*</span>\s*<div class="poster-image-container">\s*'
    patron += '<img src="([^"]+)" title="([^<]+)" /> </div>'


    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedpuntuacion, scrapedthumbnail, scrapedtitle in matches:
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        scrapedtitle += " (" + scrapedpuntuacion + ")"

        # ------------------------------------------------
        scrapedthumbnail = httptools.get_url_headers(scrapedthumbnail)
        # ------------------------------------------------
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="findvideos",
                 title=scrapedtitle,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 fulltitle=scrapedtitle,
                 show=scrapedtitle), tipo='movie'))

    # Paginación
    next_page = scrapertools.find_single_match(data, '<a href="([^"]+)"><i class="glyphicon glyphicon-chevron-right" aria-hidden="true"></i></a></div>')
    if next_page != "":
        itemlist.append(
            Item(channel=__channel__,
                 action="fichas",
                 title="[COLOR orange]Successivo >>[/COLOR]",
                 url=next_page,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/next_1.png"))

    return itemlist

# ==============================================================================================================================================================================

def peliculas_new(item):
    logger.info("[altadefinizione01_video] fichas")

    itemlist = []

    # Descarga la pagina 
    data = httptools.downloadpage(item.url, headers=headers).data
	
    # Narrow search by selecting only the combo
    bloque = scrapertools.get_match(data, '<h1>Genere:.*?</h1>(.*?)<aside id="sidebar" class="col-mt-2">')

    patron = '<a href="([^"]+)" title="[^>]+">\s*<div class="poster">\s*<span class="rating">\s*'
    patron += '<i class="glyphicon glyphicon-star"></i><span class="rating-number">([^"]+)</span>\s*</span>\s*<div class="poster-image-container">\s*'
    patron += '<img src="([^"]+)" title="([^<]+)" /> </div>'


    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for scrapedurl, scrapedpuntuacion, scrapedthumbnail, scrapedtitle in matches:
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        scrapedtitle += " (" + scrapedpuntuacion + ")"

        # ------------------------------------------------
        scrapedthumbnail = httptools.get_url_headers(scrapedthumbnail)
        # ------------------------------------------------
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="findvideos",
                 title=scrapedtitle,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 fulltitle=scrapedtitle,
                 show=scrapedtitle), tipo='movie'))

    # Paginación
    next_page = scrapertools.find_single_match(data, '<a href="([^"]+)"><i class="glyphicon glyphicon-chevron-right" aria-hidden="true"></i></a></div>')
    if next_page != "":
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas_new",
                 title="[COLOR orange]Successivo >>[/COLOR]",
                 url=next_page,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/next_1.png"))

    return itemlist

# ==============================================================================================================================================================================

def search(item, texto):
    logger.info("[altadefinizione01_video] " + item.url + " search " + texto)

    item.url = host + "/?s=" + texto

    try:
        return peliculas_search(item)

    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

# ==============================================================================================================================================================================

def peliculas_search(item):
    logger.info("[altadefinizione01_video] peliculas_search")

    itemlist = []

    # Descarga la pagina 
    data = httptools.downloadpage(item.url, headers=headers).data

    patron = '<div class="row">\s*<a href="([^"]+)" title="[^>]+">\s*'
    patron += '<img src="([^"]+)" title="([^<]+)" /> </a>'


    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedthumbnail, scrapedtitle in matches:
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)

        # ------------------------------------------------
        scrapedthumbnail = httptools.get_url_headers(scrapedthumbnail)
        # ------------------------------------------------
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="findvideos",
                 title=scrapedtitle,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 fulltitle=scrapedtitle,
                 show=scrapedtitle), tipo='movie'))

    # Paginación
    next_page = scrapertools.find_single_match(data, '</a><a href="(.*?)"><i class="glyphicon glyphicon-chevron-right" aria-hidden="true"></i></a></div>')
    if next_page != "":
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas_search",
                 title="[COLOR orange]Successivo >>[/COLOR]",
                 url=next_page,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/next_1.png"))

    return itemlist		
	
# ==============================================================================================================================================================================

def findvideos(item):
    logger.info("[altadefinizione01_video] findvideos")

    itemlist = []

    # Descarga la página
    data = scrapertools.anti_cloudflare(item.url, headers).replace('\n', '')
    patron = r'</ul><br>\s*<p><iframe width=".*?" height=".*?" src="([^"]+)" allowfullscreen frameborder=".*?"></iframe></p>'
    url = scrapertools.find_single_match(data, patron).replace("?alta", "")
    url = url.replace("&download=1", "")

    if 'hdpass' in url:
        data = scrapertools.cache_page(url, headers=headers)

        start = data.find('<div class="row mobileRes">')
        end = data.find('<div id="playerFront">', start)
        data = data[start:end]

        patron_res = '<div class="row mobileRes">([^+]+)</select>.*?</div>'
        patron_mir = '<div class="row mobileMirrs">([^+]+)</select>\s*</div>'
        patron_media = r'<input type="hidden" name="urlEmbed" data-mirror="([^"]+)" id="urlEmbed" value="([^"]+)" />'

        res = scrapertools.find_single_match(data, patron_res)

        urls = []
        for res_url, res_video in scrapertools.find_multiple_matches(res, '<option.*?value="([^"]+?)">([^<]+?)</option>'):

            data = scrapertools.cache_page(urlparse.urljoin(url, res_url), headers=headers).replace('\n', '')

            mir = scrapertools.find_single_match(data, patron_mir)

            for mir_url in scrapertools.find_multiple_matches(mir, '<option.*?value="([^"]+?)">[^<]+?</value>'):

                data = scrapertools.cache_page(urlparse.urljoin(url, mir_url), headers=headers).replace('\n', '')

                for media_label, media_url in re.compile(patron_media).findall(data):
                    urls.append(url_decode(media_url))

        itemlist = servertools.find_video_items(data='\n'.join(urls))
        for videoitem in itemlist:
            videoitem.title = item.title + videoitem.title
            videoitem.fulltitle = item.fulltitle
            videoitem.thumbnail = item.thumbnail
            videoitem.show = item.show
            videoitem.plot = item.plot
            videoitem.channel = __channel__

    return itemlist

# ==============================================================================================================================================================================

def url_decode(url_enc):
    lenght = len(url_enc)
    if lenght % 2 == 0:
        len2 = lenght / 2
        first = url_enc[0:len2]
        last = url_enc[len2:lenght]
        url_enc = last + first
        reverse = url_enc[::-1]
        return base64.b64decode(reverse)

    last_car = url_enc[lenght - 1]
    url_enc[lenght - 1] = ' '
    url_enc = url_enc.strip()
    len1 = len(url_enc)
    len2 = len1 / 2
    first = url_enc[0:len2]
    last = url_enc[len2:len1]
    url_enc = last + first
    reverse = url_enc[::-1]
    reverse = reverse + last_car
    return base64.b64decode(reverse)


