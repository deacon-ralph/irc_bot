import asyncio

import pendulum
import tweepy

import common
import logger
import plugin_api


_logger = logger.LOGGER


class Plugin(plugin_api.LocalPlugin):
    """Plugin to send fishtankdotlive tweets to irc"""

    def __init__(self):
        super().__init__()
        self.tweet_scraper_task = None
        self.last_scraped = pendulum.now(tz='UTC')
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

    async def _read_tweets(self):
        """Reads fishtank tweets from @fishtankdotlive account"""
        while self.enabled:
            auth = tweepy.OAuthHandler(self.api_key, self.api_key_secret)
            auth.set_access_token(self.access_token, self.access_token_secret)
            api = tweepy.API(auth)
            _logger.info('fetching tweets from fishtankdotlive')
            tweets = api.user_timeline(
                screen_name='fishtankdotlive',
                exclude_replies=True
            )
            tweets.reverse()
            _logger.info(f'Found {len(tweets)} tweets')
            for tweet in tweets:
                if tweet.created_at > self.last_scraped:
                    _logger.info(
                        f'found tweet newer then '
                        f'{self.last_scraped.isoformat()}'
                    )
                    await self.client.message(
                        '#fishtanklive',
                        f'🐠 {tweet.text}'
                    )
            self.last_scraped = pendulum.now(tz='UTC')
            await asyncio.sleep(300)
