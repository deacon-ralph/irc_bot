"""Main module"""
import asyncio

import bots
import common

import pydle
import pydle.client as client


Channel = common.ChannelModel


if __name__ == '__main__':
    brain = bots.FamilyFriendlyChatBot(
        'thing1',  username='thing1',
        realname='thing1', fallback_nicknames=['thing2']
    )
    brain.run('serv', tls=True, tls_verify=False)

