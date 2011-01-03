"""Main module"""
import asyncio

import bots
import common

import pydle
import pydle.client as client

Channel = common.ChannelModel

if __name__ == '__main__':
    brain = bots.FamilyFriendlyChatBot(
        [Channel('#chan')]
    )
    brain.run('server')

