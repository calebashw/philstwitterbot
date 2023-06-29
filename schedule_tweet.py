#Author: Caleb Ash
#Created in June, 2023
#Maintained by Caleb Ash

import tweepy
import statsapi
import time
import bot_keys
import pybaseball
import pandas
from tweet_funcs import *
from pybaseball import *
from datetime import date



client = tweepy.Client(consumer_key=bot_keys.CONSUMER_KEY, consumer_secret=bot_keys.CONSUMER_SECRET, 
                       access_token=bot_keys.ACCESS_TOKEN, access_token_secret=bot_keys.ACCESS_SECRET, bearer_token=bot_keys.BEARER_TOKEN)

auth = tweepy.OAuthHandler(consumer_key=bot_keys.CONSUMER_KEY, consumer_secret=bot_keys.CONSUMER_SECRET)
auth.set_access_token(bot_keys.ACCESS_TOKEN, bot_keys.ACCESS_SECRET)
api = tweepy.API(auth)

    

# Delete a tweet with ID as parameter
def delete(id: id):
    client.delete_tweet(id)
    print("Tweet deleted:", id)

# Update with tweet to be deleted
reply_id = 1673753226531708947

#client.create_tweet(text='Marsh walks for an RBI', media_ids='https://bdata-producedclips.mlb.com/1dd0caae-441e-40af-b689-90131c902ab2.mp4')
phils_sched = statsapi.schedule(start_date='2023-06-27', end_date='2023-07-01', team='143')
first_game_date = phils_sched[0]['game_date']

game_dates = []
i = 0
while i < 5:
    curr_date = phils_sched[i]['game_date']
    game_dates.append(curr_date)
    i += 1

away_teams=[]
i = 0
while i < 5:
    away_team = phils_sched[i]['away_name']
    away_teams.append(away_team)
    i += 1

home_teams=[]
i = 0
while i < 5:
    home_team = phils_sched[i]['home_name']
    home_teams.append(home_team)
    i += 1

away_pitchers = []
i = 0
while i < 5:
    pitcher = phils_sched[i]['away_probable_pitcher']
    away_pitchers.append(pitcher)
    i += 1

home_pitchers = []
i = 0
while i < 5:
    pitcher = phils_sched[i]['home_probable_pitcher']
    home_pitchers.append(pitcher)
    i += 1

venues = []
i = 0
while i < 5:
    stadium = phils_sched[i]['venue_name']
    venues.append(stadium)
    i += 1

content = 'Phillies Schedule for the next 5 days as of ' + date.today() + ' (in replies):'
twitter_client = TwitterClient()
day = ''
home = ''
away = ''
home_pitch = ''
away_pitch = ''
stad = ''
final_tweet = ''
i = 0

while i < 5:
    content = ''
    day = game_dates[i]
    home = home_teams[i]
    away = away_teams[i]
    if home_pitchers[i] != '':
        home_pitch = home_pitchers[i]
    else:
        home_pitch = 'Pitcher TBD'
    
    if away_pitchers[i] != '':
        away_pitch = away_pitchers[i]
    else:
        away_pitch = 'Pitcher TBD'
    
    stad = venues[i]
    content = content + day + '\n'
    content = content + home + ' (' + home_pitch + ') vs ' + away + ' (' + away_pitch + ')\n'
    content = content + "Game will be played at " + stad
    if i != 4:
        content += "\n"
    print(content)
    twitter_client.tweet(content, replyid=reply_id)
    content = ''
    time.sleep(5)
    i += 1

#twitter_client.tweet(final_tweet)