"""Rumble plugin"""
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
    async def _parse_rumble(cls, link):
        """Returns rumble title and author

        :param str link: url

        :returns: title, author
        :rtype: tuple
        """
        html = requests.get(link).text

        soup = bs4.BeautifulSoup(html, features='lxml')
        title = soup.find('title').string
        author = soup.find('div', {'class': 'media-heading-name'}).text
        return title, author

    async def on_message(self, target, by, message):
        await super().on_message(target, by, message)
        if not self.enabled:
            return
        if 'rumble' in message:
            try:
                url = re.search(
                    "(?P<url>https?://rumble.com/[^\s]+)",
                    message
                ).group("url")
                title, author = await self._parse_rumble(url)
                title_author = ' ' + title + ' | ' + author + ' '  # add padding
                rumble_logo = colors.colorize(' ▶ ', fg=colors.BLACK, bg=colors.LIME)
                msg = colors.colorize(title_author, fg=colors.BLACK, bg=colors.SILVER)
                await self.client.message(
                    target,
                    f'{rumble_logo} {msg}'
                )
            except AttributeError:
                pass
            except Exception:
                _logger.exception('Failed to parse spotify link', exc_info=True)

    def help_msg(self):
        return 'displays rumble video title + author'
