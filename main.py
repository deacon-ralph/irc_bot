"""Main module"""
import pydle
import pydle.client as pydle_client
import pydle.features.rfc1459.protocol as protocol
import pydle.features.isupport

import bots
import common
import logger

_logger = logger.LOGGER
_Channel = common.ChannelModel
_pool = pydle.ClientPool()

g_nick = common.CONFIG['nick']
g_username = common.CONFIG['username']
g_realname = common.CONFIG['realname']
g_fallback_nicknames = common.CONFIG['fallback_nicknames']


def _patched_parse_user(raw):
    """ Parse nick(!user(@host)?)? structure.
    patch to allow for nicks with @ or ! in them
    """
    nick = raw
    user = None
    host = None

    # Attempt to extract host.
    if protocol.HOST_SEPARATOR in raw:
        host_split = raw.split(protocol.HOST_SEPARATOR)
        raw = '@'.join(host_split[:-1])
        host = host_split[-1]

    # Attempt to extract user.
    if protocol.USER_SEPARATOR in raw:
        nick, user = raw.split(protocol.USER_SEPARATOR)

    return nick, user, host


def _patched_create_user(self, nickname):
    # patching to allow for . in nickname
    # previously it checked if . was in nickname to avoid adding servers
    # idk what the consequences of this will be...
    if not nickname:
        return

    self.users[nickname] = {
        'nickname': nickname,
        'username': None,
        'realname': None,
        'hostname': None
    }


async def _patch_on_raw_005(self, message):
    """ patched ISUPPORT indication. """

    FEATURE_DISABLED_PREFIX = '-'
    isupport = {}

    # Parse response.
    # Strip target (first argument) and 'are supported by this server' (last argument).
    for feature in message.params[1:-1]:
        if feature.startswith(FEATURE_DISABLED_PREFIX):
            value = False
        elif '=' in feature:
            feature, value = feature.split('=', 1)
        else:
            value = True
        isupport[feature.upper()] = value

    # Update internal dict first.
    self._isupport.update(isupport)

    # And have callbacks update other internals.
    for entry, value in isupport.items():
        if value is not False:
            # A value of True technically means there was no value supplied; correct this for callbacks.
            if value is True:
                value = None

            method = 'on_isupport_' + pydle.protocol.identifierify(entry)
            if hasattr(self, method):
                try:
                    await getattr(self, method)(value)
                except TypeError:
                    print('shit went south?')


# patch rfc1459 parsing
pydle.features.rfc1459.parsing.parse_user = _patched_parse_user
# patch for pdyle.client.BaseClient
pydle_client.BasicClient._create_user = _patched_create_user
#patch for isupport 005 raw handler
pydle.features.isupport.on_raw_005 = _patch_on_raw_005


def _make_client(chatnet, data):
    """Makes a client

    :param str chatnet: chatnet name. this is easily identifiable alias
    :param dict data: the actual settings data

    :returns: an irc client instance
    :rtype: bots.FamilyFriendlyChatBot
    """
    nick = data.get('nick', g_nick)
    username = data.get('username', g_username)
    realname = data.get('realname', g_realname)
    fallback_nicknames = data.get('fallback_nicknames', g_fallback_nicknames)
    bot = bots.FamilyFriendlyChatBot(
        nick,
        username=username,
        realname=realname,
        fallback_nicknames=fallback_nicknames
    )
    bot._chatnet = chatnet
    bot._channels = [_Channel(**chan) for chan in data['channels']]
    return bot


if __name__ == '__main__':
    for server in common.CONFIG['servers']:
        for chatnet, settings in server.items():
            if settings['auto_connect']:
                client = _make_client(chatnet, settings)
                _logger.info(
                    f'connecting to {settings["uri"]}:{settings["port"]}...'
                )
                try:
                    _pool.connect(
                        client,
                        settings['uri'],
                        settings['port'],
                        password=settings.get('password'),
                        tls=settings['use_tls'],
                        tls_verify=settings['tls_verify']
                    )
                except Exception:
                    _logger.exception(
                        'unable to connect to %s', settings['uri']
                    )

_pool.handle_forever()
