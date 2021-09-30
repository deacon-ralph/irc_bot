"""Remote socket plugin"""

import asyncio
import json
import os
import pathlib
import ssl

import rpc_lib.src.nooscope_rpc.constants as constants
import logger
import plugin_api


_logger = logger.LOGGER


class Plugin(plugin_api.LocalPlugin):
    """Remote socket handler"""

    client = None
    stop = False
    server = None
    ssl_ctx = None
    writers = set()

    def help_msg(self):
        return "Remote socket plugin"

    def on_reload(self):
        super().on_reload()
        if self.server:
            for writer in self.writers:
                asyncio.ensure_future(
                    self.write_to_client(
                        writer,
                        f'{constants.RESTARTING}'
                    )
                )
                writer.close()
                asyncio.ensure_future(writer.wait_closed())
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

    async def cmd_processor(self, data):
        """Process cmd from client

        :param str data: the data recv over socket
        """
        if data.startswith(constants.SEND_MESSAGE):
            msg_data = json.loads(
                data.split(constants.SEND_MESSAGE)[1]
            )
            await self.client.message(
                msg_data.get('target'),
                msg_data.get('message')
            )

    async def write_to_client(self, writer, data):
        """Writes data to socket and drains writer

        :param asyncio.StreamWriter writer:
        :param str data: data to write
        """
        data = f'{data}{constants.SEPARATOR_S}'
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
        self.writers.add(writer)
        data = constants.CLIENT_CMD
        while not data.startswith(constants.CLIENT_END):
            try:
                data = (
                    await reader.readuntil(constants.SEPARATOR_B)
                ).decode('utf8').replace(constants.SEPARATOR_S, '')
                if data.startswith(constants.CLIENT_END):
                    _logger.info(f'CLIENT ENDED: {data}')
                    await self.write_to_client(
                        writer,
                        f'{constants.SERVER_END} got close command'
                    )
                    break
                elif not data.startswith(constants.CLIENT_CMD):
                    _logger.error(
                        f'socket recv: {data} did not '
                        f'start with {constants.CLIENT_CMD}'
                    )
                    break
                else:
                    _logger.info(data)
                    await self.cmd_processor(data)
            except BrokenPipeError:
                _logger.error('BrokenPipeError, client closed?')
                data = None
                break
            except asyncio.exceptions.IncompleteReadError:
                _logger.error('IncompleteReadError, client closed?')
                data = None
                break

        _logger.info(f'LOOP WAS BROKEN: {data}')
        self.writers.remove(writer)
        writer.close()
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

    async def on_message(self, target, by, message):
        await super().on_message(target, by, message)
        if not self.enabled:
            return
        for writer in self.writers:
            json_data = json.dumps(
                {"target": target, "by": by, "message": message}
            )
            data = f'{constants.ON_MESSAGE}{json_data}'
            await self.write_to_client(writer, data)





