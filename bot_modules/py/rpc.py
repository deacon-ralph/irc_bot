"""Remote socket plugin"""

import asyncio
import os
import pathlib
import ssl

import colors
import logger
import plugin_api


_logger = logger.LOGGER


CLIENT_CMD = 'CLIENT_CMD:'
CLIENT_END = 'CLIENT_END:'
SERVER_END = 'SERVER_END:'

class Plugin(plugin_api.LocalPlugin):
    """Remote socket handler"""

    client = None
    stop = False
    server = None
    ssl_ctx = None

    def help_msg(self):
        return "Remote socket plugin"

    def on_reload(self):
        super().on_reload()
        if self.server:
            self.server.close()

    def on_loaded(self, client):
        super().on_loaded(client)
        if self.enabled:
            self._load_ssl()
            asyncio.ensure_future(self.socket_listen())

    @property
    def cert_folder(self):
        """Returns cert folder abs path

        :returns: returns cert folder path
        """
        root_folder = pathlib.Path(__file__).parent.parent.parent.resolve()
        cert_folder = root_folder.joinpath('certs').resolve()
        return cert_folder

    @property
    def cert(self):
        """Returns cert file from disk

        :returns: cert file
        """
        cert_folder = self.cert_folder
        return f'{cert_folder}{os.path.sep}selfsigned.cert'

    @property
    def key(self):
        """Returns key file from disks

        :returns: key file
        """
        cert_folder = self.cert_folder
        return f'{cert_folder}{os.path.sep}selfsigned.key'

    def _load_ssl(self):
        """Loads ssl cert chain"""
        self.ssl_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        self.ssl_ctx.load_cert_chain(self.cert, self.key)

    async def write_to_client(self, writer, data):
        writer.write(data.encode('utf8'))
        try:
            await writer.drain()
        except (ConnectionResetError, ConnectionError):
            _logger.error('connection closed')

    async def socket_recv(self, reader, writer):
        """Acts as a callback to handle tcp connections

        :param asyncio.StreamReader reader: socket reader
        :param asyncio.StreamWriter writer: socket writer
        """
        data = CLIENT_CMD
        while not data.startswith(CLIENT_END):
            try:
                data = (await reader.read(4096)).decode('utf8')
                if data.startswith(CLIENT_END):
                    _logger.info(f'CLIENT ENDED: {data}')
                    await self.write_to_client(
                        writer,
                        f'{SERVER_END} got close command'
                    )
                    break
                if not data.startswith(CLIENT_CMD):
                    _logger.error(
                        f'socket recv: {data} did not start with {CLIENT_CMD}'
                    )
                    break
            except BrokenPipeError:
                _logger.error('broken pipe')
                break

            _logger.info(f'socket recv: {data}')
            response = 'here is a response!\n'
            await self.write_to_client(writer, response)

        await writer.wait_closed()

    async def socket_listen(self):
        """Starts a socket server"""
        self.server = await asyncio.start_server(
            self.socket_recv, '0.0.0.0',
            12345,
            ssl=self.ssl_ctx
        )
        async with self.server:
            await self.server.serve_forever()


