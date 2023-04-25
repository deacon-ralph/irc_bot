import asyncio
import dataclasses

import pendulum
import tweepy

import common
import colors
import logger
import plugin_api


_logger = logger.LOGGER


@dataclasses.dataclass
class _UserQuery:
    username : str
    since_id: int


class Plugin(plugin_api.LocalPlugin):
    """Plugin to send fishtankdotlive tweets to irc"""

    def __init__(self):
        super().__init__()
        self.tweet_scraper_task = None
        self.last_ftdl_id = _UserQuery('fishtankdotlive', None)
        self.last_cfd_id = _UserQuery('DoctorCumFart', None)
        self.twitter_config = common.parse_config().get('twitter')
        self.bearer_token = self.twitter_config.get('bearer_token')
        self.api_key = self.twitter_config.get('api_key')
        self.api_key_secret = self.twitter_config.get('api_key_secret')
        self.access_token = self.twitter_config.get('access_token')
        self.access_token_secret = self.twitter_config.get('access_token_secret')
        self.client_id = self.twitter_config.get('client_id')
        self.client_secret = self.twitter_config.get('client_secret')

    def help_msg(self):
        return {
            'tweets': 'outputs fishtankdotlive tweets to irc'
        }

    def on_loaded(self, client):
        super().on_loaded(client)
        self.tweet_scraper_task = asyncio.create_task(self._read_tweets())

    def on_reload(self):
        super().on_reload()
        self.tweet_scraper_task.cancel()

    def _get_tweets(self, api, username_query):
        """Get tweets for username

        :param tweepy.API api: twitter api
        :param _UserQuery username_query: twitter username

        :returns: list of status
        :rtype: list
        """
        if username_query.since_id is None:
            count = 1
        else:
            count = 20
        tweets = api.user_timeline(
            screen_name=username_query.username,
            since_id=username_query.since_id,
            count=count,
            exclude_replies=False,
            tweet_mode='extended'
        )
        tweets.reverse()
        username_query.since_id = tweets[-1].id
        _logger.info(
            f'Found {len(tweets)} tweets for {username_query.username}'
        )
        return tweets

    async def _read_tweets(self):
        """Reads fishtank tweets from @fishtankdotlive account"""
        while self.enabled:
            auth = tweepy.OAuthHandler(self.api_key, self.api_key_secret)
            auth.set_access_token(self.access_token, self.access_token_secret)
            api = tweepy.API(auth, wait_on_rate_limit=True)
            username_queries = [self.last_ftdl_id, self.last_cfd_id]
            for username_query in username_queries:
                _logger.info(f'fetching tweets from {username_query.username}')
                tweets = self._get_tweets(api, username_query)
                for tweet in tweets:
                    username = username_query.username
                    text = tweet.full_text
                    await self.client.message(
                        '#fishtanklive',
                        f'{colors.colorize(text="🐠 @"+ username, fg=colors.WHITE, bg=colors.BLUE_TWITTER)} {text}'
                    )
                await asyncio.sleep(320)
