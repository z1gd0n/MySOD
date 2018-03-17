# -*- coding: utf-8 -*-
# by errmax
# Rel: 20180127

import urllib

from core import httptools
from core import scrapertools
from core import servertools
from platformcode import logger

headers = [
    ['User-Agent',
     'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:57.0) Gecko/20100101 Firefox/57.0'],
]


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("[vcrypt.py] url=" + page_url)
    video_urls = []

    url=page_url
    while 'vcrypt' in url:
        url = httptools.downloadpage(url, only_headers=True, follow_redirects=False).headers.get("location", "")

    if url:
        logger.info("vcrypt redirect: %s" % url)
        if 'bc.vc' in url:
            url=url.split('http')
            url='http'+url[-1]
            logger.info("bc.vc redirect: %s" % url)
        itemlist = servertools.find_video_items(data=url)  #Associate Url to Server
        for item in itemlist:
            try:
                server_module = __import__('servers.%s' % item.server, None, None, ["servers.%s" % item.server])
                video_urls=server_module.get_video_url(item.url)
            except:
                logger.error('VCrypt: Error while loading server or video_urls')
#                import traceback
#                logger.error(traceback.format_exc())

    return video_urls