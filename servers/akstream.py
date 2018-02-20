# -*- coding: utf-8 -*-
# by DrZ3r0

import urllib

from core import httptools
from core import scrapertools
from platformcode import logger

headers = [
    ['User-Agent',
     'Mozilla/5.0 (iPhone; CPU iPhone OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A5376e Safari/8536.25'],
]


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("[akstream.py] url=" + page_url)
    video_urls = []

    data = httptools.downloadpage(page_url, headers=headers).data

    data_pack = scrapertools.find_single_match(data, "(eval.function.p,a,c,k,e,.*?)\s*</script>")
    if data_pack != "":
        from lib import jsunpack
        data = jsunpack.unpack(data_pack)

    # URL
    matches = scrapertools.find_multiple_matches(data, 'file\s*:\s*"([^"]+)"\s*,\s*label\s*:\s*"([^"]+)"\s*\}')
    _headers = urllib.urlencode(dict(headers))

    for media_url, quality in matches:
        # URL del vídeo
        video_urls.append([scrapertools.get_filename_from_url(media_url)[-4:] + " %s [Akstream]" % quality, media_url + '|' + _headers])

    for video_url in video_urls:
        logger.info("[akstream.py] %s - %s" % (video_url[0], video_url[1]))

    return video_urls

