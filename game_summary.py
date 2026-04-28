# Author: Caleb Ash
# Created June 2023, refactored 2026
# Tweets a summary of yesterday's Phillies game(s). Run the morning after.
# Skips off-days and any game whose status isn't "Final" (postponed, suspended, in progress, etc.).

import sys
from datetime import date, timedelta

import statsapi

from tweet_funcs import TwitterClient

PHILLIES_TEAM_ID = 143


def fetch_finished_games(target_day: date):
    games = statsapi.schedule(start_date=target_day.isoformat(), team=PHILLIES_TEAM_ID)
    return [g for g in games if g.get("status") == "Final"]


def main() -> int:
    yesterday = date.today() - timedelta(days=1)
    finished = fetch_finished_games(yesterday)

    if not finished:
        print(f"No finished Phillies game on {yesterday.isoformat()}; nothing to tweet.")
        return 0

    twitter = TwitterClient()
    for game in finished:
        summary = game.get("summary", "")
        message = f"Yesterday's game summary:\n{summary}"
        print(message)
        twitter.tweet(message)
    return 0


if __name__ == "__main__":
    sys.exit(main())
