# Author: Caleb Ash
# Created June 2023, refactored 2026
# Centralized X (Twitter) client + thin wrapper used by every script.

import os
import tweepy

REQUIRED_ENV = (
    "CONSUMER_KEY",
    "CONSUMER_SECRET",
    "ACCESS_TOKEN",
    "ACCESS_SECRET",
    "BEARER_TOKEN",
)


def _load_credentials():
    missing = [name for name in REQUIRED_ENV if not os.environ.get(name)]
    if missing:
        raise RuntimeError(
            "Missing required environment variables: "
            + ", ".join(missing)
            + ". Set them locally (export VAR=...) or via GitHub Actions secrets."
        )
    return {name: os.environ[name] for name in REQUIRED_ENV}


_creds = _load_credentials()

client = tweepy.Client(
    consumer_key=_creds["CONSUMER_KEY"],
    consumer_secret=_creds["CONSUMER_SECRET"],
    access_token=_creds["ACCESS_TOKEN"],
    access_token_secret=_creds["ACCESS_SECRET"],
    bearer_token=_creds["BEARER_TOKEN"],
)


class TwitterClient:
    def tweet(self, message: str, replyid: int | None = None) -> int | None:
        """Post a tweet; if replyid is set, post as a reply. Returns the new tweet id, or None on failure."""
        try:
            if replyid is None:
                resp = client.create_tweet(text=message)
            else:
                resp = client.create_tweet(text=message, in_reply_to_tweet_id=replyid)
            new_id = resp.data["id"]
            print(f"Tweet posted: id={new_id}")
            return new_id
        except tweepy.TweepyException as e:
            print(f"Tweet failed: {e}")
            return None

    def delete(self, tweet_id: int) -> None:
        try:
            client.delete_tweet(tweet_id)
            print(f"Tweet deleted: {tweet_id}")
        except tweepy.TweepyException as e:
            print(f"Delete failed for {tweet_id}: {e}")
