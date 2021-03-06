# -*- coding: utf-8 -*-

from core import httptools, scrapertools
from core import servertools
from core.item import Item
from core.tmdb import infoSod
from platformcode import logger
import re

__channel__ = "filmhd"

host = "http://filmhd.me"

headers = [['Referer', host]]

def mainlist(item):
    logger.info(" mainlist")

    itemlist = [
        Item(
            channel=__channel__,
            title="[COLOR azure]Film - Novita'[/COLOR]",
            action="movies",
            url=host,
            thumbnail=
            "http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png"
        ),
        Item(
            channel=__channel__,
            title="[COLOR azure]Film - 3D[/COLOR]",
            action="movies",
            url="%s/genere/3d/" % host,
            thumbnail=
            "http://files.softicons.com/download/computer-icons/disks-icons-by-wil-nichols/png/256x256/Blu-Ray.png"
        ),
        Item(
            channel=__channel__,
            title="[COLOR azure]Film - Per Genere[/COLOR]",
            action="genre",
            url=host,
            thumbnail=
            "https://farm8.staticflickr.com/7562/15516589868_13689936d0_o.png"
        ),
        Item(
            channel=__channel__,
            title="[COLOR azure]Film - Per anno[/COLOR]",
            action="genre_years",
            url=host,
            thumbnail=
            "http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png"
        ),
        Item(
            channel=__channel__,
            title="[COLOR azure]Film - Per Paese[/COLOR]",
            action="genre_country",
            url=host,
            thumbnail=
            "http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png"
        ),
        Item(
            channel=__channel__,
            title="[COLOR azure]Film - A-Z[/COLOR]",
            action="genre_az",
            url=host,
            thumbnail=
            "http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png"
        ),
        Item(
            channel=__channel__,
            title="[COLOR yellow]Cerca...[/COLOR]",
            action="search",
            extra="movie",
            thumbnail=
            "http://dc467.4shared.com/img/fEbJqOum/s7/13feaf0c8c0/Search"
        ),
        Item(
            channel=__channel__,
            title="[COLOR azure]SerieTV[/COLOR]",
            action="movies_tv",
            url="%s/genere/serie-tv/" % host,
            extra="serie",
            thumbnail=
            "http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png"
        ),
        Item(
            channel=__channel__,
            title="[COLOR yellow]Cerca SerieTV...[/COLOR]",
            action="search",
            extra="serie",
            thumbnail=
            "http://dc467.4shared.com/img/fEbJqOum/s7/13feaf0c8c0/Search")
    ]

    return itemlist


def search(item, texto):
    logger.info(" " + item.url + " search " + texto)

    item.url = host + "/?s=" + texto

    try:
        if item.extra == "movie":
            return movies(item)
        if item.extra == "serie":
            return movies_tv(item)

    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

def genre(item):
    logger.info(" genre")
    itemlist = []

    data = httptools.downloadpage(item.url, headers=headers).data

    bloque = scrapertools.get_match(data, '<ul class="dropdown-menu dropdown-menu-large">(.*?)</ul>')

    patron = '<li><a href="([^"]+)">([^<]+)</a></li>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for scrapedurl, scrapedtitle in matches:
        itemlist.append(
            Item(
                channel=__channel__,
                action="movies",
                title=scrapedtitle,
                url=scrapedurl,
                thumbnail=
                "https://farm8.staticflickr.com/7562/15516589868_13689936d0_o.png",
                folder=True))

    return itemlist


def genre_years(item):
    logger.info(" genre_years")
    itemlist = []

    data = httptools.downloadpage(item.url, headers=headers).data

    bloque = scrapertools.get_match(data, 'Anno<i class="icon-chevron-down"></i></div>(.*?)</ul>')

    patron = '<li><a href="([^"]+)">([^<]+)</a></li>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for scrapedurl, scrapedtitle in matches:
        itemlist.append(
            Item(
                channel=__channel__,
                action="movies",
                title=scrapedtitle,
                url=scrapedurl,
                thumbnail=
                "http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png",
                folder=True))

    return itemlist


def genre_country(item):
    logger.info(" genre_country")
    itemlist = []

    data = httptools.downloadpage(item.url, headers=headers).data

    bloque = scrapertools.get_match(data, 'Nazione<i class="icon-chevron-down"></i></div>(.*?)</ul>')

    patron = '<li><a href="([^"]+)">([^<]+)</a></li>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for scrapedurl, scrapedtitle in matches:
        itemlist.append(
            Item(
                channel=__channel__,
                action="movies",
                title=scrapedtitle,
                url=scrapedurl,
                thumbnail=
                "http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png",
                folder=True))

    return itemlist


def genre_az(item):
    logger.info(" genre_az")
    itemlist = []

    data = httptools.downloadpage(item.url, headers=headers).data

    bloque = scrapertools.get_match(data, '<li class="dropdown abc-filter">(.*?)</ul>')

    patron = '<li class="abc"><a href="([^"]+)">([^<]+)</a></li>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for scrapedurl, scrapedtitle in matches:
        itemlist.append(
            Item(
                channel=__channel__,
                action="movies",
                title=scrapedtitle,
                url=scrapedurl,
                thumbnail=
                "http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png",
                folder=True))

    return itemlist


def movies(item):
    logger.info(" movies")

    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url, headers=headers).data

    patron = '<div class="item">\s*<a href="([^"]+)">\s*<div class="item-flip">\s*<div class="item-inner">\s*<img src=[^=]+="(.*?)">'

    matches = scrapertools.find_multiple_matches(data, patron)

    for scrapedurl, scrapedtitle in matches:
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)

        scrapedthumbnail = ""
        itemlist.append(
            infoSod(
                Item(
                    channel=__channel__,
                    action="findvideos",
                    title=scrapedtitle,
                    url=scrapedurl,
                    thumbnail=scrapedthumbnail,
                    fulltitle=scrapedtitle,
                    show=scrapedtitle),
                tipo='movie'))

    # Paginación
    next_page = scrapertools.find_single_match(data, '<span class="current">[^<]+</span><a href=\'(.*?)\' class="inactive">')
    if next_page:
        itemlist.append(
            Item(
                channel=__channel__,
                action="movies",
                title="[COLOR orange]Successivo >>[/COLOR]",
                url=next_page,
                thumbnail=
                "http://2.bp.blogspot.com/-fE9tzwmjaeQ/UcM2apxDtjI/AAAAAAAAeeg/WKSGM2TADLM/s1600/pager+old.png"
            ))

    return itemlist

def movies_tv(item):
    logger.info(" tv")

    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url, headers=headers).data

    patron = '<div class="item">\s*<a href="([^"]+)">\s*<div class="item-flip">\s*<div class="item-inner">\s*<span[^\/]+\/i><\/span><img src=[^=]+="(.*?)">'

    matches = scrapertools.find_multiple_matches(data, patron)

    for scrapedurl, scrapedtitle in matches:
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)

        scrapedthumbnail = ""
        itemlist.append(
            infoSod(
                Item(
                    channel=__channel__,
                    action="findvideos",
                    title=scrapedtitle,
                    url=scrapedurl,
                    thumbnail=scrapedthumbnail,
                    fulltitle=scrapedtitle,
                    show=scrapedtitle),
                tipo='tv'))

    # Paginación
    next_page = scrapertools.find_single_match(data, '<span class="current">[^<]+</span><a href=\'(.*?)\' class="inactive">')
    if next_page:
        itemlist.append(
            Item(
                channel=__channel__,
                action="movies",
                title="[COLOR orange]Successivo >>[/COLOR]",
                url=next_page,
                thumbnail=
                "http://2.bp.blogspot.com/-fE9tzwmjaeQ/UcM2apxDtjI/AAAAAAAAeeg/WKSGM2TADLM/s1600/pager+old.png"
            ))

    return itemlist

def episodios(item):
    logger.info("streamondemand.channels.filmhd episodios")

    itemlist = []

    data = httptools.downloadpage(item.url, headers=headers).data
    bloque = scrapertools.get_match(data, '</footer>(.*?)</script>')

    patron = '([^"]+)"[^a]+append[^w]+w[^=]+=[^=]+=[^=]+=(.*?)frame'
    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for scrapedtitle, scrapedurl in matches:
        scrapedplot = ""
        scrapedurl = scrapedurl.replace("'", "")
        scrapedurl = scrapedurl.replace(" ", "")
        if "span" not in scrapedtitle: continue
        scrapedtitle = scrapedtitle.replace("span", "")
        scrapedtitle = scrapedtitle.replace("openload", "")

        itemlist.append(
            Item(channel=__channel__,
                 action="findvideos",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=item.thumbnail,
                 plot=scrapedplot,
                 folder=True))

    return itemlist


def findvideos(item):
    logger.info("[filmhd.py] findvideos")

    # Carica la pagina 
    data = httptools.downloadpage(item.url, headers=headers).data
    data = data.rpartition('/')
    data = data[0]

    itemlist = servertools.find_video_items(data=data)

    for videoitem in itemlist:
        videoitem.title = "".join([item.title, '[COLOR green][B]' + videoitem.title + '[/B][/COLOR]'])
        videoitem.fulltitle = item.fulltitle
        videoitem.show = item.show
        videoitem.thumbnail = item.thumbnail
        videoitem.channel = __channel__

    return itemlist

