"""Youtube plugin"""
import datetime
import re

import bs4
import aiohttp

import colors
import logger
import plugin_api


_logger = logger.LOGGER


class Plugin(plugin_api.LocalPlugin):
    """Youtube plugin"""

    def help_msg(self):
        return "displays youtube uri title"

    @classmethod
    async def _parse_youtube(cls, link):
        """Parses youtube data from link

        :param str link: the url

        :return: tuple of title, duration
        :rtype: (str, str)
        """
        async with aiohttp.ClientSession() as session:
            response = await session.get(link)
            html = await response.text()

        soup = bs4.BeautifulSoup(html, features='lxml')
        title = None
        duration = None
        for tag in soup.find_all("meta"):
            if tag.get("property", None) == "og:title":
                title = tag.get("content", None)
            if tag.get("itemprop", None) == "duration":
                duration = tag.get("content", None)
                dt = datetime.datetime.strptime(duration, 'PT%MM%SS')
                duration = dt.strftime('%H:%M:%S')

        return title, duration

    async def on_message(self, target, by, message):
        await super().on_message(target, by, message)
        if not self.enabled:
            return
        if 'youtube' in message or 'youtu.be' in message:
            try:
                url = re.search(
                    "(?P<url>https?://[^\s]+)",
                    message
                ).group("url")
                if 'youtube' in url or 'youtu.be' in url:
                    title, duration = await self._parse_youtube(url)
                    play_btn = colors.colorize(' ▶ ', fg=colors.SILVER, bg=colors.RED)
                    title = colors.colorize(title, fg=colors.BLACK, bg=colors.SILVER)
                    duration = colors.colorize(f'[{duration}]', fg=colors.BLACK, bg=colors.SILVER)
                    await self.client.message(
                        target,
                        f'{play_btn} {title} {duration}'
                    )
            except AttributeError:
                pass
            except Exception:
                _logger.error('Failed to parse youtube link')


