"""ghetto service"""
import asyncio

import logger

import common
import plugin_api


_logger = logger.LOGGER


class Plugin(plugin_api.LocalPlugin):
    """irc art plugin"""

    @property
    def enabled(self):
        """ALWAYS ENABLED!"""
        return True

    def help_msg(self):
        return {
            'HUH': 'whats going on',
            'defcon': 'set the defcon level 1-4'
        }

    async def _defcon_1(self, target):
        """Sets the channel to +m so only voiced users can chat

        :param str target: the channel
        """
        await self.client.set_mode(target, '+m')
        await self.client.message(
            target,
            '🚨 SETTING DEFCON LEVEL 1: Something smells rotten 🚨'
        )
        await self.client.message(
            target,
            ' '.join(self.client.channels[target]['users'])
        )

    async def _defcon_2(self, target):
        """Sets the channel to invite only and only voiced users can chat

        :param str target: the channel
        """
        await self.client.set_mode(target, '+mi')
        await self.client.message(
            target,
            '🚨 SETTING DEFCON LEVEL 2: Shits going south 🚨'
        )

    async def _defcon_3(self, target):
        """Sets channel to invite, only voiced users, and devoices users

        :param str target: the channel
        """
        users = self.client.channels[target]['users']
        mode = f'+mi-{"v" * len(users)}'
        await self.client.set_mode(target, mode, *users)
        await self.client.message(
            target,
            '🚨 SETTING DEFCON LEVEL 3: Prepare for battle 🚨'
        )

    async def _defcon_4(self, target):
        """Sets channel to invite only, devoices voiced users, and kicks

        :param str target: the channel
        :return:
        """
        users = self.client.channels[target]['users']
        mode = f'+mi-{"v" * len(users)}'
        await self.client.set_mode(target, mode, *users)
        await asyncio.sleep(5)
        users_with_modes = []
        for k, v in self.client.channels[target]['modes'].items():
            if isinstance(v, list) or isinstance(v, set):
                users_with_modes.extend(v)
        users_without_modes = users - set(users_with_modes)
        await self.client.message(
            target,
            '🚨 SETTING DEFCON LEVEL 4: THIS IS NOT A TEST 🚨'
        )
        for user in users_without_modes:
            await self.client.kick(
                target,
                user,
                reason='Terminal Lost'
            )

    async def on_message(self, target, by, message):
        if message.startswith('.defcon '):
            if await common.is_user_admin(self.client, by):
                level = message.replace('.defcon ', '').strip()
                try:
                    level = int(level)
                except (ValueError, TypeError):
                    _logger.warning('Invalid defcon level')
                    return
                if level == 1:
                    await self._defcon_1(target)
                elif level == 2:
                    await self._defcon_2(target)
                elif level == 3:
                    await self._defcon_3(target)
                elif level == 4:
                    await self._defcon_4(target)

    async def on_join(self, channel, user):
        whois_info = await self.client.whois(user)
        _logger.info(
            '%s joined %s with hostname %s',
            user, channel, whois_info['hostname']
        )
        if await common.is_user_admin(self.client, user):
            _logger.info('setting mode to +o for %s', user)
            await self.client.set_mode(channel, '-b', user)
            await self.client.set_mode(channel, '+o', user)

        await super().on_join(channel, user)

    async def on_kick(self, channel, target, by, reason=None):
        await super().on_kick(channel, target, by, reason)
        if await common.is_user_admin(self.client, target):
            await self.client.kick(channel, by, reason='Lost Terminal')
            await self._defcon_1(channel)


