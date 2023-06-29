import tweepy
import time
import bot_keys


client = tweepy.Client(consumer_key=bot_keys.CONSUMER_KEY, consumer_secret=bot_keys.CONSUMER_SECRET, 
                       access_token=bot_keys.ACCESS_TOKEN, access_token_secret=bot_keys.ACCESS_SECRET, bearer_token=bot_keys.BEARER_TOKEN)

class TwitterClient():
    def tweet(self, message: str, replyid: id = None):
        if replyid is None:
            client.create_tweet(text=message)
            print("Successful Tweet!")
        else:
            client.create_tweet(text=message, in_reply_to_tweet_id=replyid)
            print("Successful Tweet Reply!")

    def thread_creator(self, message: str, replyid: id, length: int):
        i = 0
        while i < length:
            t = client.create_tweet(text=message, in_reply_to_tweet_id=replyid)
            url_split = t.url.split('/')
            replyid = url_split[-1]
            i += 1

    def delete(self, id: id):
        client.delete_tweet(id)
        print("Tweet deleted:", id)