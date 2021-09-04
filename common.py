"""Shared classes and functions"""
import pathlib

import dataclasses

import toml


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
    return toml.load(directory.joinpath('config.toml'))


CONFIG = parse_config()
