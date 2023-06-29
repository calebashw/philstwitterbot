# Author: Caleb Ash
# Date: Created June, 2023
# Maintained by Caleb Ash
# Program that uses Twitter bot to tweet out today's before it happens (game preview)

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

# Getting all access keys
client = tweepy.Client(consumer_key=bot_keys.CONSUMER_KEY, consumer_secret=bot_keys.CONSUMER_SECRET, 
                       access_token=bot_keys.ACCESS_TOKEN, access_token_secret=bot_keys.ACCESS_SECRET, bearer_token=bot_keys.BEARER_TOKEN)

auth = tweepy.OAuthHandler(consumer_key=bot_keys.CONSUMER_KEY, consumer_secret=bot_keys.CONSUMER_SECRET)
auth.set_access_token(bot_keys.ACCESS_TOKEN, bot_keys.ACCESS_SECRET)
api = tweepy.API(auth)

# Gets date in format: 'YYYY-MM-DD'
day = date.today()

# Function meant to see what day of the week it is
def calculate_weekday():
    weekday = day.weekday()
    if weekday == 0:
        weekday_str = "Monday"
    elif weekday == 1:
        weekday_str = "Tuesday"
    elif weekday == 2:
        weekday_str = "Wednesday"
    elif weekday == 3:
        weekday_str = "Thursday"
    elif weekday == 4:
        weekday_str = "Friday"
    elif weekday == 5:
        weekday_str = "Saturday"
    else:
        weekday_str = "Sunday"

    return weekday_str

# Creates TwitterClient object to call 'tweet'
funcs = TwitterClient()

# Gets weekday as String
weekday_string = calculate_weekday()

# Gets summary from statsapi for Phillies game that day
game = statsapi.schedule(start_date=day, team=143)
summary = game[0]['summary']
start = "Calling all Phillies fans, it's game day!\n"

# Formats date as 'MM-DD-YYYY'
formatted_date = day.strftime("%m-%d-%Y")

# Gets home and away probable pitcher, stadium, and combines them together.
home_pitch = game[0]['home_probable_pitcher']
away_pitch = game[0]['away_probable_pitcher']
stadium = game[0]['venue_name']
final_tweet = ''
final_tweet = final_tweet + summary + ', with ' + away_pitch + ' vs ' + home_pitch + " at " + stadium + ". Let's play ball!"

# Adds day of week and date to tweet
final_tweet = start + weekday_string + ', ' + formatted_date + final_tweet[10:] 

# Tweets out final Tweet
funcs.tweet(message=final_tweet)