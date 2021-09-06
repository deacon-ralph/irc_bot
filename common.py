"""Shared classes and functions"""
import glob
import importlib
import logger
import os
import pathlib

import dataclasses

import toml

_logger = logger.LOGGER


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


def load_py_plugins():
    """Returns dict of initialized plugin objects

    :returns: dict of plugins as {key: instance}
    :rtype: dict
    """

    instances = {}
    plugins = _get_plugin_names()
    for plugin in plugins:
        module = importlib.import_module(f'bot_modules.py.{plugin}')
        klass = getattr(module, 'Plugin')
        instance = klass()
        instance._name = plugin
        instances[instance.name] = instance
    return instances


def reload_py_plugins():
    """Reloads plugin by name, or all of em

    :returns: dict of plugins as {key: instance}
    :rtype: dict
    """
    instances = {}
    plugins = _get_plugin_names()
    for plugin in plugins:
        module = importlib.import_module(f'bot_modules.py.{plugin}')
        importlib.reload(module)
        klass = getattr(module, 'Plugin')
        instance = klass()
        instance._name = plugin
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
