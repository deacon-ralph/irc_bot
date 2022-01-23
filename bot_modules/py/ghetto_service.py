"""ghetto service

This service handles
    1. joining channels on invite by bot admin
    2. defcon mode
    3. auto opping bot admins
"""
import asyncio
import copy

import logger

import common
import plugin_api


_logger = logger.LOGGER


class Plugin(plugin_api.LocalPlugin):
    """Ghetto service plugin"""

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
        await self.client.message(
            target,
            ' '.join(self.client.channels[target]['users'])
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
        await self.client.message(
            target,
            ' '.join(self.client.channels[target]['users'])
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
        await self.client.message(
            target,
            ' '.join(self.client.channels[target]['users'])
        )

    async def on_message(self, target, by, message):
        await super().on_message(target, by, message)
        if message.startswith('.defcon '):
            if not await common.is_user_admin(self.client, by):
                return

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
        await super().on_join(channel, user)
        if await common.is_user_admin(self.client, user):
            _logger.info('setting mode to +o for %s', user)
            await self.client.set_mode(channel, '-b', user)
            await self.client.set_mode(channel, '+o', user)

        await super().on_join(channel, user)

    async def on_kick(self, channel, target, by, reason=None):
        await super().on_kick(channel, target, by, reason)
        if await common.is_user_admin(self.client, target):
            await self._defcon_2(channel)
            # make sure we dont kick a bot admin who kicked another admin
            if not await common.is_user_admin(self.client, by):
                # wasnt a bot admin, give em the boot
                await self._kick_all_with_same_host(channel, by)
            await self.client.rawmsg('INVITE', target, channel)

    async def on_invite(self, channel, by):
        await super().on_invite(channel, by)
        if await common.is_user_admin(self.client, by):
            await self.client.join(channel)

    async def on_mode_change(self, channel, modes, by):
        await super().on_mode_change(channel, modes, by)
        if await common.is_user_admin(self.client, by):
            _logger.info('mode changed by bot admin')
            return

        users = copy.deepcopy(self.client.channels[channel]['users'])
        users.remove(self.client.nickname)
        mode = f'+mi-{"o" * len(users)}'
        await self.client.set_mode(channel, mode, *users)
        users = copy.deepcopy(self.client.users)
        for nick, whois_info in users.items():
            if nick != self.client.nickname \
                    and not await common.is_user_admin(self.client, nick):
                await self.client.kick(
                    channel,
                    nick,
                    reason='Lost Terminal'
                )
        await self.client.unban(channel, 'run.data.UnixMaster.org')
        await self.client.rawmsg('INVITE', 'ralph', channel)

    async def _check_admin_not_deoped(self, channel, modes, by):
        """Checks bot admin wasnt deoped, and if they were, kick the user(s)

        :param str channel: the channel
        :param list modes: list of modes and nicks
            ex: ['-oo', 'user1', 'user2']
        :param str by: user who initiated the kick
        """
        current_modes = self.client.channels[channel]['modes']
        print(self.client.users)
        o = current_modes.get('o', [])
        a = current_modes.get('a', [])
        q = current_modes.get('q', [])

        affected_users = modes[1:]
        for user in affected_users:
            if await common.is_user_admin(self.client, user):
                if not any(user in mode for mode in [o, a, q]):
                    await self._defcon_2(channel)
                    await self._kick_all_with_same_host(channel, by)

    async def _kick_all_with_same_host(self, channel, target):
        """Kicks all users with the same host; excludes this bot, and bot admins

        :param str channel: the channel
        :param str target: the user to kick
        """
        users = copy.deepcopy(self.client.users)
        hostname = users.get(target).get('hostname')
        for nick, whois_info in users.items():
            if whois_info.get('hostname') == hostname:
                # dont kick this bot or bot admins
                if nick != self.client.nickname \
                        and not await common.is_user_admin(self.client, nick):
                    await self.client.kick(
                        channel,
                        nick,
                        reason='Lost Terminal'
                    )
