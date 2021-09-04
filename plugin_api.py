"""Plugin api for python"""
import abc


class _Plugin(abc.ABC):
    """Abstract base plugin defining api contract"""

    async def on_message(self, target, by, message):
        """called on message from user or channel"""


class LocalPlugin:
    """Local plugin, to be run and loaded where bot is running at"""

    client = None

    @abc.abstractmethod
    def entry_point(self, client):
        """Entry point for plugin. do any required initialization here"""
        self.client = client


class RemotePlugin:
    """Remote plugin, do comms over ???"""