# Author: Caleb Ash
# Date: Created June, 2023
# Maintained by Caleb Ash
# Program that uses Twitter bot to tweet out today's game summary, when ran
import tweepy
import statsapi
import time
import bot_keys
from tweet_funcs import *
from pybaseball import *
from datetime import date

client = tweepy.Client(consumer_key=bot_keys.CONSUMER_KEY, consumer_secret=bot_keys.CONSUMER_SECRET, 
                       access_token=bot_keys.ACCESS_TOKEN, access_token_secret=bot_keys.ACCESS_SECRET, bearer_token=bot_keys.BEARER_TOKEN)

auth = tweepy.OAuthHandler(consumer_key=bot_keys.CONSUMER_KEY, consumer_secret=bot_keys.CONSUMER_SECRET)
auth.set_access_token(bot_keys.ACCESS_TOKEN, bot_keys.ACCESS_SECRET)
api = tweepy.API(auth)


# Make a check that checks if the game today is already completed, only then will it tweet out summary

day = date.today()
game = statsapi.schedule(start_date=day, team='143')

#Used to access tweeting functions
funcs = TwitterClient()

summary = game[0]['summary']
final_summary = "Today's game summary:\n" + summary
print(final_summary)
try:
    funcs.tweet(final_summary)
    print("Summary succesfully Tweeted!")
except:
    print("Summary could not be tweeted :(")