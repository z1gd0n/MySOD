# -*- coding: utf-8 -*-
# By MrTruth

from core import httptools
from core import scrapertools
from platformcode import logger


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)
    data = httptools.downloadpage(page_url).data
    if "borrado" in data:
        return False, "[vidlox] Video non trovato"

    return True, ""


def get_video_url(page_url, user="", password="", video_password=""):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []
    data = httptools.downloadpage(page_url).data
    bloque = scrapertools.find_single_match(data, 'sources:.\[.*?]')
    matches = scrapertools.find_multiple_matches(bloque, '(http.*?)"')
    for videourl in matches:
        extension = scrapertools.get_filename_from_url(videourl)[-4:]
        video_urls.append(["%s [vidlox]" %extension, videourl])

    return video_urls
