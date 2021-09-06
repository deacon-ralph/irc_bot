"""simple markov chaining for shitposting"""
import asyncio
import random

import plugin_api

# End of Sentence for Markov chaining
EOS = ('.', '?', '!')


def _shitpost():
    with open('/irc_bot/chatter.log', "r") as log:
        text = log.read()
    words = text.split()
    model = _build_dict(words)
    sentence = _generate_sentence(model)
    return sentence


def _build_dict(words):
    """Builds a dictionary of words

    :param list[str] words: words

    :returns: dictionary of words
    :rtype: dict
    """
    d = {}
    for i, word in enumerate(words):
        try:
            first, second, third = words[i], words[i + 1], words[i + 2]
        except IndexError:
            break
        key = (first, second)
        if key not in d:
            d[key] = []
        d[key].append(third)
    return d


def _generate_sentence(d):
    """Generate sentence

    :param dict d: dict of words

    :returns: a sentence based off of the words
    :rtype: str
    """
    li = [key for key in d.keys() if key[0][0].isupper()]
    key = random.choice(li)
    li = []
    first, second = key
    li.append(first)
    li.append(second)
    while True:
        try:
            third = random.choice(d[key])
        except KeyError:
            break
        li.append(third)
        if third[-1] in EOS:
            break
        else:
            key = (second, third)
            first, second = key
    return ' '.join(li)


class Plugin(plugin_api.LocalPlugin):
    """Markov plugin"""

    def help_msg(self):
        return ".markov to generate random sentence"

    def _maybe_log(self, msg):
        if msg.startswith('.'):
            return
        if not msg.endswith(EOS):
            msg += '.'
        with open('/irc_bot/chatter.log', 'a') as f:
            f.write(f'\n{msg}')

    async def on_message(self, target, by, message):
        await super().on_message(target, by, message)
        if not self.enabled:
            return
        self._maybe_log(message)
        if message == '.markov':
            sentence = await asyncio.ensure_future(
                self.exec_proc(_shitpost)
            )
            await self.client.message(target, sentence)

