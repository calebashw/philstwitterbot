# Author: Caleb Ash
# Created June 2023, refactored 2026
# Tweets Phillies highlights from yesterday's finished game(s).
# Hard-capped on tweets/run so a parse bug can't blow up your API bill.

import os
import re
import sys
import time
from datetime import date, timedelta

import statsapi

from tweet_funcs import TwitterClient

PHILLIES_TEAM_ID = 143
MAX_TWEETS_PER_RUN = int(os.environ.get("HIGHLIGHTS_MAX_TWEETS", "8"))
DRY_RUN = os.environ.get("DRY_RUN", "").lower() in ("1", "true", "yes")
TWEET_LIMIT = 280
SLEEP_BETWEEN_TWEETS_SEC = 3


def split_lines(blob: str) -> list[str]:
    return [s for s in re.split(r"\n+", blob) if s.strip()]


def first_two_words(text: str) -> str:
    """Extract the first two whitespace/apostrophe-separated tokens — used to identify the player."""
    out = []
    k = 0
    for ch in text:
        if ch in (" ", "'"):
            k += 1
            if k == 2:
                break
        else:
            out.append(ch)
    return "".join(out).strip()


def is_phillie(name: str) -> bool:
    if not name:
        return False
    if name == "Nick Castellanos" or name.startswith("Castellanos"):
        name = "Nicholas Castellanos"
    try:
        matches = statsapi.lookup_player(name)
    except Exception as e:
        print(f"  player lookup failed for {name!r}: {e}")
        return False
    if not matches:
        return False
    return matches[0].get("currentTeam", {}).get("id") == PHILLIES_TEAM_ID


def yesterday_game_ids() -> list[int]:
    yesterday = date.today() - timedelta(days=1)
    games = statsapi.schedule(start_date=yesterday.isoformat(), team=PHILLIES_TEAM_ID)
    return [g["game_id"] for g in games if g.get("status") == "Final"]


def collect_highlight_tweets(game_id: int) -> list[str]:
    """Walk the human-readable highlights blob, pair each description with its URL,
    keep only Phillies-player highlights that fit in a tweet."""
    try:
        blob = statsapi.game_highlights(game_id)
    except Exception as e:
        print(f"  game_highlights failed for game_id={game_id}: {e}")
        return []

    lines = split_lines(blob)
    tweets: list[str] = []
    pending = ""
    skip_next = False

    # Skip the first chunk (lineups, weather, etc.) — same heuristic as the original script.
    for line in lines[8:]:
        if not line.startswith("https") and skip_next:
            skip_next = False
            continue

        pending = (pending + " " + line).strip()

        if line.startswith("https"):
            if pending.startswith("https"):
                pending = ""
                continue
            if len(pending) <= TWEET_LIMIT and is_phillie(first_two_words(pending)):
                tweets.append(pending)
            pending = ""
        else:
            skip_next = True

    return tweets


def main() -> int:
    game_ids = yesterday_game_ids()
    if not game_ids:
        print("No finished Phillies game yesterday; nothing to tweet.")
        return 0

    all_tweets: list[str] = []
    for gid in game_ids:
        all_tweets.extend(collect_highlight_tweets(gid))

    if not all_tweets:
        print("No Phillies highlights matched; nothing to tweet.")
        return 0

    capped = all_tweets[:MAX_TWEETS_PER_RUN]
    print(f"Found {len(all_tweets)} candidate highlights, posting {len(capped)} (cap={MAX_TWEETS_PER_RUN}).")

    twitter = TwitterClient()
    for i, msg in enumerate(capped, start=1):
        print(f"[{i}/{len(capped)}] {msg}")
        if DRY_RUN:
            print("  (DRY_RUN: skipped)")
        else:
            twitter.tweet(msg)
            time.sleep(SLEEP_BETWEEN_TWEETS_SEC)
    return 0


if __name__ == "__main__":
    sys.exit(main())
