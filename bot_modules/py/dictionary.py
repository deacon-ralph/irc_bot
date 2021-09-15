"""Dictionary API plugin"""
import requests

import colors
import logger
import plugin_api

_logger = logger.LOGGER


class Plugin(plugin_api.LocalPlugin):
    """Dictionary plugin"""

    @classmethod
    def _get_urban(cls, word):
        """Returns urban dict definition

        :param str word: the word

        :returns: urban dict definition
        :rtype: [str]
        """
        url = f'https://api.urbandictionary.com/v0/define?term={word}'
        try:
            resp = requests.get(url, timeout=5.0)
            resp.raise_for_status()
        except requests.exceptions.RequestException:
            _logger.exception(f'request failed', exc_info=True)
            return ['request failed :(']

        try:
            json_resp = resp.json()
            def_list = json_resp['list']
            first_two = def_list[:2]
            if not first_two:
                return ['I AINT FIND THAT WORD ON UD CUZ!']
            definitions = []
            for definition in first_two:
                the_definition = f'{colors.colorize(definition["word"], fg=colors.RED)}: ' \
                                 f'{definition["definition"]}\r\n' \
                                 f'{colors.colorize("example", fg=colors.PINK)}: {definition["example"]}'
                definitions.append(the_definition)
            return definitions
        except Exception:
            _logger.exception('Failed to parse response', exc_info=True)
            return ['couldnt parse the response :( im dumb']

    @classmethod
    def _get_definitions(cls, word):
        """Returns definitions of a word

        :param str word: the word to define

        :returns: definition
        :rtype: [str]
        """
        url = f'https://api.dictionaryapi.dev/api/v2/entries/en/{word}'
        try:
            resp = requests.get(url, timeout=5.0)
        except requests.exceptions.RequestException:
            _logger.exception(f'request failed', exc_info=True)
            return ['request failed :(']

        try:
            json_resp = resp.json()

            if resp.status_code == 404:
                if 'title' in json_resp and 'message' in json_resp:
                    return [json_resp['message']]

            definitions = []
            for word in json_resp:
                for meaning in word["meanings"]:
                    for definition in meaning['definitions']:
                        the_definition = f'{word["word"]} ' \
                                     f'{colors.BOLD}{meaning["partOfSpeech"]}{colors.BOLD}: ' \
                                     f'{definition["definition"]}'
                        definitions.append(the_definition)
            return definitions

        except Exception:
            _logger.exception('Failed to parse response', exc_info=True)
            return ['couldnt parse the response :( im dumb']

    async def on_message(self, target, by, message):
        await super().on_message(target, by, message)
        if not self.enabled:
            return
        if message.startswith('.define'):
            word = message.replace('.define', '')
            definitions = self._get_definitions(word)
            for definition in definitions:
                await self.client.message(target, definition)
        elif message.startswith('.ud'):
            word = message.replace('.ud', '')
            definitions = self._get_urban(word)
            for definition in definitions:
                await self.client.message(target, definition)

    def help_msg(self):
        return {
            'define': '.define <word> - wil show all definitions[FUCK CAN-SPAM]',
            'urban': '.ud <word> - will show first 2 urban definitions'
        }
