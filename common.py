"""Shared classes and functions"""
import glob
import importlib
import logger
import os
import pathlib

import dataclasses

import toml

_logger = logger.LOGGER


def _get_enabled_py_conf(chatnet):
    """Returns enabled conf as dict

    :rtype: dict
    """
    proj_folder = pathlib.Path(__file__).parent.resolve()
    py_modules = proj_folder.joinpath('bot_modules', 'py')
    enable_conf = f'{py_modules}{os.path.sep}{chatnet}{os.path.sep}enabled.toml'
    try:
        return toml.load(
            f'{py_modules}{os.path.sep}{chatnet}{os.path.sep}enabled.toml'
        )
    except FileNotFoundError:
        directory = os.path.dirname(enable_conf)
        if not os.path.exists(directory):
            os.makedirs(directory)
        pathlib.Path(enable_conf).touch()
        return {}


def update_enabled_py_conf(chatnet, name, enabled):
    """Updates enabled conf and writes to disk

    :param str chatnet: the clients chatnet
    :param str name: name of the plugin
    :param bool enabled: is enabled?
    """
    proj_folder = pathlib.Path(__file__).parent.resolve()
    py_modules = proj_folder.joinpath('bot_modules', 'py')
    conf_path = f'{py_modules}{os.path.sep}{chatnet}{os.path.sep}enabled.toml'
    enabled_conf = toml.load(
        conf_path
    )
    enabled_conf[name] = enabled
    with open(conf_path, 'w+') as f:
        toml.dump(enabled_conf, f)


def _get_plugin_names():
    """Returns list of module names

    :returns: plugin names as a list
    :rtype: list[str]
    """
    # this could be better...
    proj_folder = pathlib.Path(__file__).parent.resolve()
    py_modules = proj_folder.joinpath('bot_modules', 'py')
    plugins = glob.glob(f'{py_modules}{os.path.sep}*.py')
    plugins.remove(f'{py_modules}{os.path.sep}__init__.py')
    _logger.info(f'found plugins: {plugins}')
    return [p.split(f'{py_modules}{os.path.sep}')[1].replace('.py', '') for p in plugins]


def load_py_plugins(chatnet, name=None, reload=False):
    """Returns dict of initialized plugin objects

    If name is supplied, only that plugin will be reloaded
    If reload is Ture, plugins will be reloaded

    :param str chatnet: clients chatnet
    :param str name: name of the plugin
    :param bool reload: should reload?

    :returns: dict of plugins as {key: instance}
    :rtype: dict
    """
    instances = {}
    plugins = _get_plugin_names()
    if name:
        plugins = [name]
    enabled_conf = _get_enabled_py_conf(chatnet)
    for plugin in plugins:
        module = importlib.import_module(f'bot_modules.py.{plugin}')
        if reload:
            importlib.reload(module)
            _logger.info(f'{module} reloaded...')
        klass = getattr(module, 'Plugin')
        instance = klass()
        instance._name = plugin
        instance._enabled = enabled_conf.get(plugin, False)
        instances[instance.name] = instance
    return instances


@dataclasses.dataclass
class ChannelModel:
    name: str
    password: str = None


def parse_config():
    """Returns config as dict

    :returns: dict representation of the config
    :rtype: dict
    """
    directory = pathlib.Path(__file__).parent.resolve()
    try:
        return toml.load(directory.joinpath('config.toml'))
    except FileNotFoundError:
        _logger.error(
            'create config.toml in irc_bot/ directory. see example_conf.toml',
            exc_info=False
        )
        exit(1)


def parse_admin_config():
    """Returns admin config as a dict

    :returns: admin config
    :rtype: dict
    """
    directory = pathlib.Path(__file__).parent.resolve()
    try:
        return toml.load(directory.joinpath('admins.toml'))
    except FileNotFoundError:
        _logger.error('Missing admins.toml file in project dir')
        return {'admins': []}


async def is_user_admin_whois(client, user):
    """Returns if user is listed as admin in settings and does whois lookup

    :param FamilyFriendlyChatBot client: irc client
    :param str user: users nick

    :returns: True if user is admin
    :rtype: bool
    """
    whois_info = await client.whois(user)
    admin_conf = parse_admin_config()
    for dj in admin_conf.get('admins'):
        if dj['nick'] == user:
            for hostname in dj['hostnames']:
                if hostname == whois_info['hostname']:
                    return True
    return False


async def is_user_admin(client, user):
    """Returns if user is listed as admin in settings

    :param FamilyFriendlyChatBot client: irc client
    :param str user: users nick

    :returns: True if user is admin
    :rtype: bool
    """
    whois_info = client.users.get(user)
    admin_conf = parse_admin_config()
    for dj in admin_conf.get('admins'):
        if dj['nick'] == user:
            for hostname in dj['hostnames']:
                if hostname == whois_info['hostname']:
                    return True
    return False


CONFIG = parse_config()
