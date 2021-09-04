"""Module containing the bot(s)"""
import dataclasses

import pydle

import common

channels = [common.ChannelModel('#channel')]

class FamilyFriendlyChatBot(pydle.Client):
    """chat bot with command processing and all the standard IRC things"""

    async def on_connect(self):
        for chan in channels:
            await self.join(chan.name, chan.passwd)
