# -*- coding: utf-8 -*-
from base64 import b64decode

from core import httptools, scrapertools
from platformcode import logger


def get_long_url(short_url):
    logger.info("short_url = '%s'" % short_url)

    data = httptools.downloadpage(short_url, cookies=False).data
    ysmm = scrapertools.find_single_match(data, "var ysmm = '([^']+)';")

    b64 = []
    for i in reversed(range(len(ysmm))):
        if i & 1:
            b64.append(ysmm[i])
        else:
            b64.insert(0, ysmm[i])

    i = 0
    ln = len(b64)
    while i < ln:
        if b64[i].isdigit():
            j = i + 1
            while j < ln:
                if b64[j].isdigit():
                    b = int(b64[i]) ^ int(b64[j])
                    if b < 10:
                        b64[i] = str(b)
                    i = j
                    break
                j += 1
        i += 1

    decoded_uri = b64decode(''.join(b64))[16:][:-16]

    if "adf.ly/redirecting" in decoded_uri:
        data = scrapertools.downloadpage(decoded_uri)
        decoded_uri = scrapertools.find_single_match(data, "window.location = '([^']+)'")

    return decoded_uri
