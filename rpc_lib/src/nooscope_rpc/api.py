"""python api"""

import abc
import asyncio
import json
import os
import pathlib
import ssl
import sys

import loguru

try:
    import constants as constants  # work around
except ModuleNotFoundError:
    import nooscope_rpc.constants as constants


_LOGGER = loguru.logger

_LOGGER.add(
    sys.stderr,
    format="{time} {level} {message}",
    filter="my_module",
    level="INFO"
)
_LOGGER.add(
    sys.stdout,
    format="{time} {level} {message}",
    filter="my_module",
    level="INFO"
)
_LOGGER.add(
    sys.stdin,
    format="{time} {level} {message}",
    filter="my_module",
    level="INFO"
)


class ServerRestartError(Exception):
    """Raised when server restarting msg received"""


class IrcImpl(abc.ABC):
    """Abstract bot impl"""

    _rpc = None

    @property
    def rpc(self):
        return self._rpc

    @rpc.setter
    def rpc(self, rpc):
        self._rpc = rpc

    @abc.abstractmethod
    async def on_message(self, target, by, message):
        """called on message"""


class Rpc:
    """RPC implementation"""

    def __init__(self, writer):
        self._writer = writer

    async def send_message(self, target, message):
        """send message cmd

        :param str target: target; can be #channel, or user
        :param str message: message to send
        """
        json_data = json.dumps(
            {
                'target': target,
                'message': message
            }
        )
        data = f'{constants.SEND_MESSAGE}{json_data}{constants.SEPARATOR_S}'
        self._writer.write(data.encode('utf8'))
        await self._writer.drain()

    async def disconnect(self):
        dc_msg = f'{constants.CLIENT_END}{constants.SEPARATOR_S}'
        self._writer.write(dc_msg.encode('utf'))
        await self._writer.drain()


class TcpClient:

    def __init__(self, host, port, impl):
        """Initialize tcp client

        :param str host: host/ip
        :param int port: port
        :param IrcImpl impl: bot implementation
        """
        self.reader = None
        self.writer = None
        self._host = host
        self._port = port
        self._impl = impl
        self._ssl_context = self._create_ssl_conext()

    @classmethod
    def _create_ssl_conext(cls):
        cafile = f'{pathlib.Path(__file__).parent.resolve()}' \
                 f'{os.path.sep}' \
                 f'selfsigned.cert'
        context = ssl.create_default_context(
            ssl.Purpose.SERVER_AUTH,
            cafile=cafile
        )
        context.check_hostname = False
        return context

    async def connect(self):
        """Connects to socket and returns a

        :returns: Rpc implementation
        :rtype: Rpc
        """
        await asyncio.sleep(5)  # wait for server to be back up
        self.reader, self.writer = await asyncio.open_connection(
            self._host,
            self._port,
            ssl=self._ssl_context
        )
        self._impl.rpc = Rpc(self.writer)
        return self._impl.rpc

    async def msg_process(self, data):
        """Process message

        :param str data:
        """
        if data.startswith(constants.ON_MESSAGE):
            _LOGGER.info(
                data
            )
            on_msg_data = json.loads(
                data.split(constants.ON_MESSAGE)[1]
            )
            target = on_msg_data.get('target')
            by = on_msg_data.get('by')
            msg = on_msg_data.get('message')
            await self._impl.on_message(target, by, msg)
        elif data.startswith(constants.RESTARTING):
            raise ServerRestartError
        else:
            _LOGGER.error(f'Unkonwn message: {data}')

    async def read(self):
        data = 'START'
        while not data.startswith(constants.SERVER_END):
            try:
                data = (
                    await self.reader.readuntil(constants.SEPARATOR_B)
                ).decode('utf8').replace(constants.SEPARATOR_S, '')
                if data.startswith(constants.SERVER_END):
                    _LOGGER.info(
                        f'client received END notice, {data}'
                    )
                else:
                    await self.msg_process(data)
            except ServerRestartError:
                _LOGGER.info('Got server restart message')
                break
            except BrokenPipeError:
                _LOGGER.error('BrokenPipeError, client closed?')
                data = None
                break
            except asyncio.exceptions.IncompleteReadError:
                _LOGGER.error('IncompleteReadError, client closed?')
                data = None
                break

        _LOGGER.info(f'LOOP WAS BROKEN: {data}')
        self.writer.close()
        await self.writer.wait_closed()
