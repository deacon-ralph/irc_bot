"""Module containing the bot(s)"""
import pydle


class FamilyFriendlyChatBot(pydle.Client):
    """chat bot with command processing and all the standard IRC things"""

    async def on_connect(self):
        """called on connection to server"""
        for chan in self._channels:
            await self.join(chan.name, chan.password)

    async def on_message(self, target, by, message):
        """called on message

        :param str target: target for the msg. can be channel or the bot nick
        :param str by: who msg is from
        :param str message: the message
        """
        print(target, by, message)


