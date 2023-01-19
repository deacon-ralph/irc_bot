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
    RECONNECT_MAX_ATTEMPTS = 1000

    @property
    def plugins(self):
        return self._plugins

    @plugins.setter
    def plugins(self, plugins):
        """sets the _plugins value

        :param dict plugins: dict of name, plugin instance
        """
        if self._plugins:
            for name, plugin in self._plugins.items():
                if name in plugins:  # if the name is in the new plugin list...
                    plugin.on_reload()  # call on_reload to clean things up

        if self._plugins:
            # call update on the dict. this ensures we dont
            # lose the already loaded plugins that arent being reloaded
            self._plugins.update(plugins)
        else:
            self._plugins = plugins  # no plugins yet, set all of them

        for name, plugin in plugins.items():
            plugin.on_loaded(self)  # call on_loaded for the new instances

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
        self.plugins = common.load_py_plugins(self.chatnet)

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
        if not self.plugins:
            return
        for _, plugin in self.plugins.items():
            await plugin.on_message(target, by, message)

    async def on_nick_change(self, old, new):
        """Called on nick change

        :param str old: old nick
        :param stre new: new nick
        """
        _logger.info(f'{old} changed nick to {new}')
        if not self.plugins:
            return
        for _, plugin in self.plugins.items():
            await plugin.on_nick_change(old, new)

    async def on_join(self, channel, user):
        """Called when user joins a channel

        :param str channel: the channel
        :param str user: the user
        """
        _logger.info(f'{channel} {user}')
        if user == self.nickname:
            return  # dont respond to ourself
        for _, plugin in self.plugins.items():
            await plugin.on_join(channel, user)

    async def on_kick(self, channel, target, by, reason=None):
        """Called on kick; may be self or other user

        :param str channel: channel
        :param str target: who was kicked
        :param str by: who kicked the target
        :param str reason: reason for kick
        """
        _logger.info(f'{channel} {target} {by} {reason}')
        for _, plugin in self.plugins.items():
            await plugin.on_kick(channel, target, by, reason)

    async def on_invite(self, channel, by):
        """Callback called when client was invited into a channel by someone.

        :param str channel: the channel
        :param str by: the user who invited
        """
        _logger.info(f'{channel} {by}')
        for _, plugin in self.plugins.items():
            await plugin.on_invite(channel, by)

    async def on_mode_change(self, channel, modes, by):
        """Called when the mode on a channel was changed.

        :param str channel: channel
        :param list modes: list of modes and nicks
            ex: ['-oo', 'user1', 'user2']
        :param str by: user who set the mode
        """
        _logger.info(f'{channel} {modes} {by}')
        for _, plugin in self.plugins.items():
            await plugin.on_mode_change(channel, modes, by)
