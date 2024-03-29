"""Spotify plugin"""
import re

import aiohttp
import bs4
import requests

import colors
import logger
import plugin_api

_logger = logger.LOGGER


class Plugin(plugin_api.LocalPlugin):
    """Spotify plugin to display track titles"""

    @classmethod
    async def _parse_spotify(cls, link):
        """Returns spotify track title

        :param str link: url

        :returns: title
        :rtype: str
        """
        html = requests.get(link).text

        soup = bs4.BeautifulSoup(html, features='lxml')
        title = soup.find('title')
        return title.string\
            .replace(' | Spotify', '')\
            .replace('song by ', '')\
            .replace('song and lyrics by ', '')

    async def on_message(self, target, by, message):
        await super().on_message(target, by, message)
        if not self.enabled:
            return
        if 'spotify' in message:
            try:
                url = re.search(
                    "(?P<url>https?://open.spotify.com/[^\s]+)",
                    message
                ).group("url")
                title = await self._parse_spotify(url)
                title = ' ' + title + ' '  # add padding
                song_btn = colors.colorize(' ♪ ', fg=colors.BLACK, bg=colors.LIME)
                title = colors.colorize(title, fg=colors.BLACK, bg=colors.SILVER)
                await self.client.message(
                    target,
                    f'{song_btn} {title}'
                )
            except AttributeError:
                pass
            except Exception:
                _logger.exception('Failed to parse spotify link', exc_info=True)

    def help_msg(self):
        return 'displays spotify artist + track title'
