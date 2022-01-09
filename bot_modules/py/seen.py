"""Seen module will keep track of users in memory"""
import datetime

import colors
import logger
import plugin_api


_logger = logger.LOGGER


class Plugin(plugin_api.LocalPlugin):
    """Seen plugin"""

    userdata = {}

    def help_msg(self):
        return '.seen <name>'

    def _get_last_seen(self, nick):
        """Returns last seen data for nick

        :param str nick: user's nick

        :returns: data for nick as a string
        :rtype: message
        """
        lastseen = self.userdata.get(nick)
        if lastseen:
            msg = f'{colors.BOLD}{nick}{colors.BOLD} '
            msg += colors.colorize('last seen ', fg=colors.GREY)
            timedelta = datetime.datetime.utcnow() - \
                datetime.datetime.fromtimestamp(lastseen.get('datetime'))
            duration_str = ''
            days = timedelta.days
            hours, remainder = divmod(timedelta.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            if days > 0:
                duration_str += f'{days} days '
            if hours > 0:
                duration_str += f'{hours} hours '
            if minutes > 0:
                duration_str += f'{minutes} minutes '
            if seconds > 0:
                duration_str += f'{seconds} seconds'
            duration_str = f'{colors.BOLD}{duration_str}{colors.BOLD}'
            last_msg = colors.colorize(
                lastseen.get('message'),
                fg=colors.WHITE,
                bg=colors.BLACK
            )
            msg += f'{duration_str} ago: {last_msg}'
            return msg
        else:
            return 'I have not seen this user :('

    def _update_nicks(self, nick, message):
        """Updates nicks data

        :param str nick: user's nick
        :param str message: message
        """
        self.userdata[nick] = {
            'datetime': datetime.datetime.utcnow().timestamp(),
            'message': message
        }

    async def on_message(self, target, by, message):
        await super().on_message(target, by, message)
        if not self.enabled:
            return
        if message == '.seen reload':
            return
        elif message.startswith('.seen '):
            message = message.rstrip(' ')
            nick = message.split('.seen ')[1]
            last_seen = self._get_last_seen(nick)
            self._update_nicks(by, message)
            await self.client.message(target, last_seen)
        else:
            self._update_nicks(by, message)

    async def on_nick_change(self, old, new):
        await super().on_nick_change(old, new)
        self._update_nicks(old, f'changed nick to {new}')

