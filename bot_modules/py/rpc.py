"""Remote socket plugin"""

import asyncio

import colors
import logger
import plugin_api


_logger = logger.LOGGER


class Plugin(plugin_api.LocalPlugin):
    """Remote socket handler"""

    client = None
    stop = False
    server = None

    def help_msg(self):
        return "Remote socket plugin"

    def on_reload(self):
        super().on_reload()
        if self.server:
            self.server.close()

    def on_loaded(self, client):
        super().on_loaded(client)
        if self.enabled:
            asyncio.ensure_future(self.socket_listen())

    async def socket_recv(self, reader, writer):
        data = (await reader.read(255)).decode('utf8')
        _logger.info(f'got data: {data}')
        response = 'here is a response!\n'
        writer.write(response.encode('utf8'))
        await writer.drain()
        await writer.wait_closed()

    async def socket_listen(self):
        self.server = await asyncio.start_server(
            self.socket_recv, '0.0.0.0',
            12345
        )
        async with self.server:
            await self.server.serve_forever()

