import tweepy
import statsapi
import time
import bot_keys
import pybaseball
import pandas
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

def split_string_by_newlines(long_string):
    # Split the long string using the regular expression pattern for one or more consecutive newline characters
    substrings = re.split(r'\n+', long_string)
    return substrings

tweets = split_string_by_newlines(statsapi.game_highlights(statsapi.last_game(143)))

final_tweet = ''
print(len(tweets))
# Algorithm to accurately chop up and post highlights with link, one at a time. Only posts if they're on the Phillies
i = 0
skip_next = False
# Skips the first few highlights since they are just starting lineups, etc.
for tweet in range(8, len(tweets) - 1):
    # Taking first string and assigning to a temp
    temp_tweet = tweets[tweet]

    # Check to see if this string should be skipped
    if temp_tweet[:5] != 'https' and skip_next:
        skip_next = False
        continue

    # Updating final_tweet with temp, stripping of extra spaces
    final_tweet = (final_tweet + " " + temp_tweet).strip()

    #If I've done too many tweets, stop
    if i > 45:
        break

    # If the temp just added on is a URL
    elif temp_tweet[:5] == 'https':
        # If the length of the tweet is within the character limit
        if len(final_tweet) <= 280:
            k = 0
            final_check = ''
            # Splitting up final tweet and grabbing the first two words
            for char in final_tweet:
                if k == 2:
                    break

                if char == "'" or char == ' ':
                    k += 1
                
                if k == 2:
                    break

                final_check += char
             
            #If it's Nick Castellanos
            if final_check == "Nick Castellanos":
                final_check = "Nicholas Castellanos"
            
            # Look up the player to see if they are a Phillie
            player = statsapi.lookup_player(final_check)

            # Skip Tweet if it's just a link
            if final_tweet[:5] == 'https':
                print("Only came with link")
                continue

            # If the player couldn't be found
            if player == []:
                print("Player could not be found")
                continue

            # If the player is not on the Phillies
            if player[0]['currentTeam']['id'] != 143:
                print("player is not on Phillies")
                continue

            # Tweet out the Tweet!, then increment, pause
            #client.create_tweet(text=final_tweet)
            print(final_tweet)
            i += 1
            print("Tweeting out highlights")
            time.sleep(3)
        else:
            print("Tweet is too many characters, sorry")
        final_tweet = ''
    elif temp_tweet == '':
        break
    else:
        print("Skipping next")
        skip_next = True
        continue

# client.create_tweet(text="Josh Harrison crushes a ball over the left field wall for a solo home run, giving the Phillies their eighth run of the game in the top of the 5th https://mlb-cuts-diamond.mlb.com/FORGE/2023/2023-06/28/b22434aa-1141ff0d-60f43bf6-csvm-diamondx64-asset_1280x720_59_4000K.mp4")