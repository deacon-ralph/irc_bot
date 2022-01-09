"""ghetto service"""

import logger

import common
import plugin_api


_logger = logger.LOGGER


class Plugin(plugin_api.LocalPlugin):
    """irc art plugin"""

    @property
    def enabled(self):
        """ALWAYS ENABLED!"""
        return True

    def help_msg(self):
        return {
            'HUH': 'whats going on'
        }

    async def on_join(self, channel, user):
        whois_info = await self.client.whois(user)
        _logger.info(
            '%s joined %s with hostname %s',
            user, channel, whois_info['hostname']
        )
        admin_conf = common.parse_admin_config()
        for dj in admin_conf.get('admins'):
            if dj['nick'] == user:
                for hostname in dj['hostnames']:
                    if hostname == whois_info['hostname']:
                        _logger.info('setting mode to +o for %s', user)
                        await self.client.set_mode(channel, "-b", user)
                        await self.client.set_mode(channel, "+o", user)

        await super().on_join(channel, user)
