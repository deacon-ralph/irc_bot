"""Dictionary API plugin"""
import requests

import colors
import logger
import plugin_api

_logger = logger.LOGGER


class Plugin(plugin_api.LocalPlugin):
    """Dictionary plugin"""

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

    def help_msg(self):
        return {
            '.define': 'define <word>'
        }
