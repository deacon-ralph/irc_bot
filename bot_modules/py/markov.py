"""simple markov chaining for shitposting"""
import asyncio
import random

import plugin_api

# End of Sentence for Markov chaining
EOS = ['.', '?', '!']


class Plugin(plugin_api.LocalPlugin):
    """Markov plugin"""

    def help_msg(self):
        return "markov shitposting"

    async def on_message(self, target, by, message):
        if 1 == 2:
            sentence = await asyncio.ensure_future(
                self.exec_proc(self._shitpost())
            )
            await self.client.message(target, sentence)

    def _shitpost(self):
        with open("chatter.log", "r") as log:
            text = log.read()
        words = text.split()
        model = self.build_dict(words)
        sentence = self.generate_sentence(model)
        return sentence

    @classmethod
    def build_dict(cls, words):
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

    @classmethod
    def generate_sentence(cls, d):
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
