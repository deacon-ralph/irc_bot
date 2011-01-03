"""Module containing the bot(s)"""
import dataclasses

import pydle


class FamilyFriendlyChatBot(pydle.Client):
    """chat bot with command processing and all the standard IRC things"""

    def __init__(self, channels):
        """Initialize bot

        :param list[_ChannelModel] channels: channel list to join on connect
        """
        self._channels = channels

    async def on_connect(self):
        for chan in self._channels:
            await self.join(chan.name, chan.passwd)
