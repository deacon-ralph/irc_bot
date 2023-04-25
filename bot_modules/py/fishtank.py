import asyncio

import pendulum
import tweepy

import common
import colors
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

    def _get_tweets(self, api, username):
        """Get tweets for username

        :param tweepy.API api: twitter api
        :param str username: twitter username

        :returns: list of status
        :rtype: list
        """
        tweets = api.user_timeline(
            screen_name=username,
            exclude_replies=True
        )
        tweets.reverse()
        _logger.info(f'Found {len(tweets)} tweets')
        return tweets

    async def _read_tweets(self):
        """Reads fishtank tweets from @fishtankdotlive account"""
        while self.enabled:
            auth = tweepy.OAuthHandler(self.api_key, self.api_key_secret)
            auth.set_access_token(self.access_token, self.access_token_secret)
            api = tweepy.API(auth, wait_on_rate_limit=True)
            _logger.info('fetching tweets from fishtankdotlive')
            usernames = ['fishtankdotlive', 'DoctorCumFart']
            for username in usernames:
                tweets = self._get_tweets(api, username)
                for tweet in tweets:
                    if tweet.created_at > self.last_scraped:
                        _logger.info(
                            f'found tweet newer then '
                            f'{self.last_scraped.isoformat()}'
                        )
                        await self.client.message(
                            '#fishtanklive',
                            f'{colors.colorize(text="🐠 @"+ username, fg=colors.WHITE, bg=colors.BLUE_TWITTER)} {tweet.text}'
                        )
            self.last_scraped = pendulum.now(tz='UTC')
            await asyncio.sleep(390)
