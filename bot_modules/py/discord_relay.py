"""Discord relay module"""

import asyncio

import discord

import colors
import common
import logger
import plugin_api


_logger = logger.LOGGER

# _MEMBER_CHANNEL_ID = 880514005410652200
# _PUBLIC_CHANNEL_ID = 881456369025290251


def _get_relay_settings(irc_client):
    """Returns discord relay settings if available

    :param irc_client: the irc client

    :returns: list of dicts of channel mappings
    :rtype: dict
    """
    for server in common.CONFIG['servers']:
        for chatnet, settings in server.items():
            if chatnet == irc_client.chatnet:
                return settings.get('discord_relay')


class _DiscordClient(discord.Client):

    def __init__(self, *, irc_client, loop=None, **options):
        self.irc_client = irc_client
        super().__init__(loop=loop, **options)

    async def on_ready(self):
        _logger.info('Logged into discord as {0.user}'.format(self))

    async def on_message(self, message):
        if message.author == self.user:
            return

        elif message.content == 'ping':
            await message.channel.send('pong')

        else:
            formatted_name = f'{colors.BOLD}{message.author.display_name}{colors.BOLD}'
            relay_settings = _get_relay_settings(self.irc_client)

            if not relay_settings:
                _logger.info(
                    f'no discord_relay settings for {self.irc_client.chatnet}'
                )
                return

            for relay in relay_settings:
                if message.channel.id == relay['discord_channel']:
                    await self.irc_client.message(
                        relay['irc_channel'], f'<{formatted_name}>: {message.content}'
                    )


class Plugin(plugin_api.LocalPlugin):
    """Discord relay plugin"""

    discord_client = None

    def __del__(self):
        asyncio.ensure_future(self.discord_client.close())
        self.discord_client = None

    def on_loaded(self, client):
        super().on_loaded(client)
        self.discord_client = _DiscordClient(irc_client=self.client)
        asyncio.ensure_future(
            self.discord_client.start(
                common.CONFIG['discord_token'])
        )

    async def on_nick_change(self, old, new):
        await super().on_nick_change(old, new)
        relay_settings = _get_relay_settings(self.client)

        if not relay_settings:
            _logger.info(
                f'no discord_relay settings for {self.client.chatnet}'
            )
            return

        for relay in relay_settings:
            discord_chan = self.discord_client.get_channel(
                relay['discord_channel']
            )
            if discord_chan:
                await discord_chan.send(
                    f'**{old}** *is now known as*  **{new}**'
                )

    def help_msg(self):
        return 'discord relay bot'

    async def on_message(self, target, by, message):
        await super().on_message(target, by, message)
        if not self.enabled:
            return
        if message.startswith('.'):
            return
        else:
            relay_settings = _get_relay_settings(self.client)

            if not relay_settings:
                _logger.info(
                    f'no discord_relay settings for {self.client.chatnet}'
                )
                return

            for relay in relay_settings:
                if target == relay['irc_channel']:
                    discord_chan = self.discord_client.get_channel(
                        relay['discord_channel']
                    )
                    if discord_chan:
                        await discord_chan.send(f'**<{by}>**: {message}')

            # logging stuff
            print('channels', self.discord_client.get_all_channels())
            for guild in self.discord_client.guilds:
                _logger.info(guild.name)
                for channel in guild.text_channels:
                    _logger.info(f'{channel}, {channel.name}, {channel.id}')
