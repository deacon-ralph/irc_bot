"""Plugin api for python"""
import abc
import concurrent.futures as concurrent_futures

import pydle

import colors
import common


_PROC_EXECUTOR = concurrent_futures.ProcessPoolExecutor()
_THREAD_EXECUTOR = concurrent_futures.ThreadPoolExecutor()


class _Plugin(abc.ABC):
    """Abstract base plugin defining api contract"""

    client = None
    _name = None
    _enabled = None

    def on_loaded(self, client):
        """Called when bot is connected. will set client here to handle IRC

        :param pydle.Client client: irc client impl
        """
        self.client = client

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
        return await loop.run_in_executor(_PROC_EXECUTOR, target, *args)


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
            self._enabled = True
            common.update_enabled_py_conf(self.name, self.enabled)
            await self.client.message(
                target,
                f'🔌 {self.name} '
                f'{colors.colorize("E N A B L E D", fg=colors.GREEN)}'
            )
        elif message == f'.{self.name} disable':
            self._enabled = False
            common.update_enabled_py_conf(self.name, self.enabled)
            await self.client.message(
                target,
                f'🔌 {self.name} '
                f'{colors.colorize("D I S A B L E D", fg=colors.RED)}'
            )


class RemotePlugin:
    """Remote plugin, do comms over ???"""
