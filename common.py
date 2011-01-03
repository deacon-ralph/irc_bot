"""Shared classes and functions"""
import dataclasses


@dataclasses.dataclass
class ChannelModel:
    name: str
    passwd: str = None
