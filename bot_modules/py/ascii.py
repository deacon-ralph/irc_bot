"""IRC art module"""
import glob
import os
import pathlib

import logger
import plugin_api


_logger = logger.LOGGER


class Plugin(plugin_api.LocalPlugin):
    """irc art plugin"""

    def help_msg(self):
        return {
            'ascii': '.ascii <art name>',
            'list': '.ascii list will display available asciis'
        }

    @classmethod
    def _get_available_asciis(cls):
        """Returns a dict of ascii_name: path

        :returns: dict of name: path
        :rtype: dict
        """
        root_folder = pathlib.Path(__file__).parent.parent.parent.resolve()
        path = root_folder.joinpath('ascii_art', '*.txt').resolve()
        filenames = glob.glob(str(path))
        ascii_art_paths = {}
        for filename in filenames:
            key = filename.split(os.sep)[-1]
            ascii_art_paths[os.path.splitext(key)[0]] = filename
        return ascii_art_paths

    def _get_ascii(self, art_name):
        """Returns ascii art as a list

        :param str art_name: file name of the art

        :raises: FileNotFoundError or TypeError if file not found
        :returns: list of lines to send to channel
        :rtype: [str]
        """
        ascii_art_paths = self._get_available_asciis()
        art_file = ascii_art_paths.get(art_name)
        if not art_file:
            _logger.info(f'Found ascii\'s {ascii_art_paths}')
            raise FileNotFoundError
        with open(art_file, 'r') as f:
            lines = f.readlines()
            fixed_lines = []
            for line in lines:
                fixed = line.replace("\n", "\n")
                fixed_lines.append(fixed)
            return fixed_lines

    async def on_message(self, target, by, message):
        await super().on_message(target, by, message)
        if not self.enabled:
            return
        if message == '.ascii list':
            await self.client.message(
                target,
                ','.join(list(sorted(self._get_available_asciis().keys())))
            )
        elif message.startswith('.ascii'):
            art = message.replace('.ascii', '').strip()

            try:
                lines = self._get_ascii(art)
            except (FileNotFoundError, TypeError):
                _logger.error(f'{art} not found')
                return
            if lines:
                await self.client.message(target, ''.join(lines))
            else:
                _logger.info('no lines found, was the file empty?')
