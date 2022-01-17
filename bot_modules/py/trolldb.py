"""Troll DB module"""

import base64
import pathlib
import random
import re

import logger
import plugin_api


_logger = logger.LOGGER


class Plugin(plugin_api.LocalPlugin):
    """troll db plugin"""

    def help_msg(self):
        return {
            'troll': '.troll <optional words>',
        }

    @classmethod
    def _open_trolldb(cls):
        """Returns list of trolls from trolldb.txt

        :returns: list of trolls
        :rtype: list[str]
        """
        root_folder = pathlib.Path(__file__).parent.parent.parent.resolve()
        trolldb_path = root_folder.joinpath('troll.b64').resolve()
        with open(trolldb_path, 'br') as f:
            trolls = f.read()
            trolls = base64.b64decode(trolls)
            trolls = trolls.decode('utf-8')
            trolls = trolls.split('%\n')
            return trolls

    @classmethod
    async def _search_troll_db(cls, phrase=None):
        """Search trolldb for matching text

        :param str phrase: phrase to match

        :returns: list of matched troll texts
        :rtype: list[str]
        """
        trolls = await cls.exec_thread(cls._open_trolldb)
        matched_trolls = []
        for troll in trolls:
            match = re.search(phrase, troll, re.IGNORECASE)
            if match:
                matched_trolls.append(troll)
        return matched_trolls

    async def _get_troll(self, phrase=None):
        """Returns a single troll from the db, matching words if found

        :param str phrase: phrase to search trolldb for

        :returns: single troll
        :rtype: str
        """
        trolls = await self._search_troll_db(phrase)
        troll = None
        if trolls:
            troll = random.choice(trolls)
        return troll

    async def on_message(self, target, by, message):
        await super().on_message(target, by, message)
        if not self.enabled:
            return
        if message.startswith('.troll'):
            phrase = message.replace('.troll', '').strip()
            troll = await self._get_troll(phrase)
            if troll:
                await self.client.message(
                    target,
                    troll.rstrip('\n')
                )
