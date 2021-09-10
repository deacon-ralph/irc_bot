"""simple markov chaining for shitposting"""
import asyncio
import random

import colors
import logger
import plugin_api


_logger = logger.LOGGER

# End of Sentence for Markov chaining
EOS = ('.', '?', '!')


def _should_log(msg):
    """Returns bool to log or not

    will return False if:
        - msg starts with a . (period)
        - has color control char (0x03) in it

    :param str msg: message

    :returns: bool value weather to log or not
    :rtype: bool
    """
    if msg.startswith('.'):
        return False
    if colors.CONTROL_COLOR in msg:
        return False

    return True


def _maybe_log(msg):
    """Maybe write message to disk. see _should_log method

    :param str msg: the message
    """
    if not _should_log(msg):
        return
    if not msg.endswith(EOS):
        msg += '.'
    with open('/irc_bot/chatter.log', 'a') as f:
        f.write(f'\n{msg}')


def _shitpost(seed_word=None):
    with open('/irc_bot/chatter.log', "r") as log:
        text = log.read()
    words = text.split()
    model = _build_dict(words)
    sentence = _generate_sentence(model, seed_word)
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


def _generate_sentence(d, seed_word):
    """Generate sentence

    :param dict d: dict of words

    :returns: a sentence based off of the words
    :rtype: str
    """
    words_set = [key for key in d.keys() if key[0][0].isupper()]
    if seed_word:
        key_tuples = [i for i in words_set if seed_word in i[0] or seed_word in i[1]]
        try:
            key = random.choice(key_tuples)
        except IndexError:
            _logger.error('IndexError, using random')
            key = random.choice(words_set)
    else:
        key = random.choice(words_set)
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

    async def on_message(self, target, by, message):
        await super().on_message(target, by, message)
        if not self.enabled:
            return
        await self.exec_thread(_maybe_log, message)
        if message.startswith('.markov'):
            parts = message.split(' ')
            if len(parts) == 1:
                args = None
            elif len(parts) > 1:
                args = parts[1]
            else:
                return
            sentence = await asyncio.ensure_future(
                self.exec_proc(_shitpost, args)
            )
            await self.client.message(target, sentence)
