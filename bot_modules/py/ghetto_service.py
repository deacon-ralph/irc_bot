"""ghetto service"""

import logger
import plugin_api

_logger = logger.LOGGER

APPROVED_DJS = [
    {
        'nick': 'ralph',
        'hostnames': [
            'a3c01d64.irc.notgay.men',
            'run.data.UnixMaster.org',
            '164bc6a9.irc.notgay.men',
            '206.41.117.46',
            '206.41.117.47'
        ]
    },
    {
        'nick': 'ralph_',
        'hostnames': [
            'a3c01d64.irc.notgay.men',
            'run.data.UnixMaster.org',
            '164bc6a9.irc.notgay.men',
            '206.41.117.46',
            '206.41.117.47'
        ]
    },
    {
        'nick': 'cumdata',
        'hostnames': [
            'a3c01d64.irc.notgay.men',
            'run.data.UnixMaster.org',
            '164bc6a9.irc.notgay.men',
            '206.41.117.46',
            '206.41.117.47'
        ]
    },
    {
        'nick': 'cumdata_',
        'hostnames': [
            'a3c01d64.irc.notgay.men',
            'run.data.UnixMaster.org',
            '164bc6a9.irc.notgay.men',
            '206.41.117.46',
            '206.41.117.47'
        ]
    },
    {
        'nick': 'Lions',
        'hostnames': [
            'id-228252.hampstead.irccloud.com',
            'e43a9c7a.irc.notgay.men'
        ]
    }
]


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
        for dj in APPROVED_DJS:
            if dj['nick'] == user:
                for hostname in dj['hostnames']:
                    if hostname == whois_info['hostname']:
                        _logger.info('setting mode to +o for %s', user)
                        await self.client.set_mode(channel, "-b", user)
                        await self.client.set_mode(channel, "+o", user)

        await super().on_join(channel, user)
