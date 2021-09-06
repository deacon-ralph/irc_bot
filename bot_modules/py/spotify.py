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

        soup = bs4.BeautifulSoup(html)
        title = soup.find('title')
        return title.string.replace(' | Spotify', '')

    async def on_message(self, target, by, message):
        if 'spotify' in message:
            try:
                url = re.search(
                    "(?P<url>https?://[^\s]+)",
                    message
                ).group("url")
                if 'spotify' in url:
                    title = await self._parse_spotify(url)
                    song_btn = colors.colorize(' ♪ ', fg=colors.BLACK, bg=colors.LIME)
                    title = colors.colorize(title, fg=colors.BLACK, bg=colors.SILVER)
                    await self.client.message(
                        target,
                        f'{song_btn} {title}'
                    )
            except Exception:
                _logger.error('Failed to parse spotify link')

    def help_msg(self):
        return 'displays spotify artist + track title'
