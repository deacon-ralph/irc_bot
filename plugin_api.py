"""Plugin api for python"""
import abc
import bots
import concurrent.futures as concurrent_futures

import pydle

import colors
import common
import logger


_PROC_EXECUTOR = concurrent_futures.ProcessPoolExecutor()
_THREAD_EXECUTOR = concurrent_futures.ThreadPoolExecutor()


_logger = logger.LOGGER


class _Plugin(abc.ABC):
    """Abstract base plugin defining api contract"""

    client = None
    _name = None
    _enabled = None

    def on_loaded(self, client):
        """Called when bot is connected. will set client here to handle IRC

        :param bots.FamilyFriendlyChatBot client: irc client impl
        """
        self.client = client

    def on_reload(self):
        """Called when reloading plugins"""

    def showhelp(self, key=None):
        """Shows help menu for given module

        :param str|None key: key corresponding to value in mapping

        :returns: string of available help or value for specific key
        :rtype: str
        """
        if not key:
            if isinstance(self.help_msg(), dict):
                return f'try one of ' \
                       f'{colors.colorize(".help "+self.name, fg=colors.YELLOW)} ' \
                       f'{colors.colorize("|", fg=colors.WHITE).join(list(self.help_msg().keys()))}'
            else:
                return self.help_msg()
        else:
            if isinstance(self.help_msg(), str):
                return self.help_msg()
            else:
                return self.help_msg()[key] if key in self.help_msg() \
                    else f'no help available for {key}'

    @abc.abstractmethod
    def help_msg(self):
        """Returns dict containing help info

        :returns: dict of help options or str as description
        :rtype: dict|str
        """

    @property
    def name(self):
        """Returns name of the plugin

        :returns: name of the plugin as a string
        :rtype: str
        """
        return self._name

    @property
    def enabled(self):
        """Returns if plugin is enabled

        :returns: True if plugin is enabled
        :rtype: bool
        """
        return self._enabled

    @classmethod
    async def exec_proc(cls, target, *args):
        """Executes in process

        :param func target: blocking function
        :param args: args to pass

        :returns: value from target function
        """
        loop = pydle.client.get_event_loop()
        return await loop.run_in_executor(_PROC_EXECUTOR, target, *args)

    @classmethod
    async def exec_thread(cls, target, *args):
        """Executes in a thread

        :param func target: blocking function
        :param args: args to pass

        :returns: value from target function
        """
        loop = pydle.client.get_event_loop()
        return await loop.run_in_executor(_THREAD_EXECUTOR, target, *args)


class LocalPlugin(_Plugin):
    """Local plugin, to be run and loaded where bot is running at"""

    @abc.abstractmethod
    def help_msg(self):
        """Returns dict containing help info

        :returns: dict of help options or str as description
        :rtype: dict|str
        """

    async def on_message(self, target, by, message):
        """called on message from user or channel"""
        if message == f'.{self.name} enable':
            if not await common.is_user_admin_whois(self.client, by):
                _logger.info('%s is not an admin, cant enable plugin')
                return
            self._enabled = True
            common.update_enabled_py_conf(
                self.client.chatnet,
                self.name,
                self.enabled
            )
            await self.client.message(
                target,
                f'🔌 {self.name} '
                f'{colors.colorize("E N A B L E D", fg=colors.GREEN)}'
            )
        elif message == f'.{self.name} disable':
            if not await common.is_user_admin_whois(self.client, by):
                _logger.info('%s is not an admin, cant disable plugin')
                return
            self._enabled = False
            common.update_enabled_py_conf(
                self.client.chatnet,
                self.name,
                self.enabled
            )
            await self.client.message(
                target,
                f'🔌 {self.name} '
                f'{colors.colorize("D I S A B L E D", fg=colors.RED)}'
            )
        elif message == f'.{self.name} reload':
            if not await common.is_user_admin_whois(self.client, by):
                _logger.info('%s is not an admin, cant reloade plugin')
                return
            self.client.plugins = common.load_py_plugins(
                self.client.chatnet,
                self.name,
                True
            )
            await self.client.message(
                target,
                f'🔌 {self.name} {colors.BOLD}R E L O A D E D{colors.BOLD}'
            )

    async def on_kick(self, channel, target, by, reason=None):
        """Called when a user, possibly the client, was kicked from a channel.

        :param str channel: the channel
        :param str target: the user being kicked
        :param str by: who done it
        :param str reason: reason
        """

    async def on_nick_change(self, old, new):
        """Called on nick change

        :param str old: old nick
        :param stre new: new nick
        """

    async def on_join(self, channel, user):
        """Called when user joins channel

        :param str channel: the channel that was joined
        :param str user: the user
        """

    async def on_invite(self, channel, by):
        """Callback called when client was invited into a channel by someone.

        :param str channel: the channel
        :param str by: the user who invited
        """

    async def on_mode_change(self, channel, modes, by):
        """Called when the mode on a channel was changed.

        :param str channel: channel
        :param list modes: list of modes and nicks
            ex: ['-oo', 'user1', 'user2']
        :param str by: user who set the mode
        """
