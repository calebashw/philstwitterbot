import tweepy
import statsapi
import time
import bot_keys
import pybaseball
import pandas
from datetime import date
#from schedule_tweet import *
from tweet_funcs import *
from pybaseball import *
import random
import re

client = tweepy.Client(consumer_key=bot_keys.CONSUMER_KEY, consumer_secret=bot_keys.CONSUMER_SECRET, 
                       access_token=bot_keys.ACCESS_TOKEN, access_token_secret=bot_keys.ACCESS_SECRET, bearer_token=bot_keys.BEARER_TOKEN)

auth = tweepy.OAuthHandler(consumer_key=bot_keys.CONSUMER_KEY, consumer_secret=bot_keys.CONSUMER_SECRET)
auth.set_access_token(bot_keys.ACCESS_TOKEN, bot_keys.ACCESS_SECRET)
api = tweepy.API(auth)

tweeter = TwitterClient()

scoring_plays = statsapi.game_scoring_plays(statsapi.last_game(143))
each_play = scoring_plays.split('\n\n')
i = 1

# To Tweet all game scoring plays
for each in each_play:
    tweeter.tweet(message=each)

# To Tweet most recent scoring play
#tweeter.tweet(message=each_play[-1])