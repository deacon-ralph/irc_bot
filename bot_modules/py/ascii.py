"""IRC art module"""
import glob
import os
import pathlib
import re

import colors
import logger
import plugin_api


_logger = logger.LOGGER


class Plugin(plugin_api.LocalPlugin):
    """irc art plugin"""

    def help_msg(self):
        return {
            'ascii': '.ascii <art name>',
            'list': '.ascii list will display available asciis',
            'search': '.ascii search <text> will list matching asciis'
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

    def _search_ascii(self, search_word):
        """Returns a string of ascii arts containing the searchg word

        :param str search_word: search word

        :returns: list of matched asciis
        :rtype: str
        """
        matched = []
        ascii_names = self._get_available_asciis().keys()
        for name in ascii_names:
            match = re.search(search_word, name, re.IGNORECASE)
            if match:
                insensitive_name = re.compile(
                    re.escape(search_word),
                    re.IGNORECASE
                )
                hl_name = insensitive_name.sub(
                    colors.colorize(match.group(), fg=colors.RED),
                    match.string
                )
                matched.append(hl_name)
        return sorted(matched)

    async def _display_99_colors(self, target):
        """Displays 99 color palette"""
        c = 0
        msg = ''
        ctrl = colors.CONTROL_COLOR

        for i in range(0, 16):
            code = str(i).zfill(2)
            msg += f'{ctrl}{code},{code}{code}{ctrl}'

        await self.client.message(target, msg)

        msg = ''
        for i in range(16, 99):
            code = str(i).zfill(2)
            msg += f'{ctrl}{code},{code}{code}{ctrl}'
            c += 1
            if c == 12 or i == 98:
                await self.client.message(target, msg)
                msg = ''
                c = 0

    async def on_message(self, target, by, message):
        await super().on_message(target, by, message)
        if not self.enabled:
            return
        if message == '.ascii list':
            await self.client.message(
                target,
                ', '.join(list(sorted(self._get_available_asciis().keys())))
            )
        elif message.startswith('.ascii search '):
            search_word = message.replace('.ascii search ', '').strip()
            matched = self._search_ascii(search_word)
            if matched:
                await self.client.message(
                    target,
                    f"{colors.colorize('found:', fg=colors.GREEN)} "
                    f"{', '.join(matched)}"
                )
            else:
                await self.client.message(
                    target,
                    f'no asciis found for '
                    f'{colors.colorize(search_word, fg=colors.RED)}'
                )
        elif message == '.ascii 99':
            await self._display_99_colors(target)
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
