"""Module containing the bot(s)"""
import pydle

import common
import logger

_logger = logger.LOGGER


class FamilyFriendlyChatBot(pydle.Client):
    """chat bot with command processing and all the standard IRC things"""

    _plugins = None
    _chatnet = None
    _channel_list = None

    @property
    def plugins(self):
        return self._plugins

    @plugins.setter
    def plugins(self, plugins):
        self._plugins = plugins
        for _, plugin in plugins.items():
            plugin.on_loaded(self)

    @property
    def chatnet(self):
        """Returns the chatnet"""
        return self._chatnet

    @property
    def channel_list(self):
        """Returns list of ChannelModels

        :returns: list of ChannelModel instances
        :rtype: list of common.ChannelModel
        """
        return self._channels

    async def on_connect(self):
        """Called on connection to server

        will do initial loading of enabled plugins
        """
        self.plugins = common.load_py_plugins()
        for _, plugin in self.plugins.items():
            plugin.on_loaded(self)

        for chan in self._channels:
            await self.join(chan.name, chan.password)

    async def on_message(self, target, by, message):
        """Called on message

        :param str target: target for the msg. can be channel or the bot nick
        :param str by: who msg is from
        :param str message: the message
        """
        _logger.info(f'{target} {by} {message}')
        if by == self.nickname:
            return  # dont respond to ourself
        for _, plugin in self.plugins.items():
            await plugin.on_message(target, by, message)
