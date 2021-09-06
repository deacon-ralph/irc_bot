"""Shared classes and functions"""
import glob
import importlib
import logger
import os
import pathlib

import dataclasses

import toml

_logger = logger.LOGGER


def _get_enabled_py_conf():
    """Returns enabled conf as dict

    :rtype: dict
    """
    proj_folder = pathlib.Path(__file__).parent.resolve()
    py_modules = proj_folder.joinpath('bot_modules', 'py')
    enabled_conf = toml.load(f'{py_modules}{os.path.sep}enabled.toml')
    return enabled_conf


def update_enabled_py_conf(name, enabled):
    """Updates enabled conf and writes to disk

    :param str name: name of the plugin
    :param bool enabled: is enabled?
    """
    proj_folder = pathlib.Path(__file__).parent.resolve()
    py_modules = proj_folder.joinpath('bot_modules', 'py')
    enabled_conf = toml.load(f'{py_modules}{os.path.sep}enabled.toml')
    enabled_conf[name] = enabled
    with open(f'{py_modules}{os.path.sep}enabled.toml', 'w+') as f:
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
    plugins.remove('/irc_bot/bot_modules/py/__init__.py')
    _logger.info(f'found plugins: {plugins}')
    return [p.split('/irc_bot/bot_modules/py/')[1].replace('.py', '') for p in plugins]


def load_py_plugins(name=None, reload=False):
    """Returns dict of initialized plugin objects

    If name is supplied, only that plugin will be reloaded
    If reload is Ture, plugins will be reloaded

    :param str|None name: name of plugin
    :param bool reload: should reload?

    :returns: dict of plugins as {key: instance}
    :rtype: dict
    """
    instances = {}
    plugins = _get_plugin_names()
    if name:
        plugins = [name]
    enabled_conf = _get_enabled_py_conf()
    for plugin in plugins:
        module = importlib.import_module(f'bot_modules.py.{plugin}')
        if reload:
            importlib.reload(module)
            _logger.info(f'{name} reloaded...')
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


CONFIG = parse_config()
