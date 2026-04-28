# Author: Caleb Ash
# Created June 2023
# NOT CURRENTLY SCHEDULED. Original logic was hardcoded to a 2023 date and to a
# parent-tweet ID that no longer exists. Skeleton kept for future re-enable.
# To re-enable: pick a cadence (e.g., weekly Monday morning), then add a workflow.

import sys
import time
from datetime import date, timedelta

import statsapi

from tweet_funcs import TwitterClient

PHILLIES_TEAM_ID = 143
LOOKAHEAD_DAYS = 5


def main() -> int:
    today = date.today()
    end = today + timedelta(days=LOOKAHEAD_DAYS - 1)
    games = statsapi.schedule(
        start_date=today.isoformat(),
        end_date=end.isoformat(),
        team=PHILLIES_TEAM_ID,
    )
    if not games:
        print(f"No Phillies games between {today.isoformat()} and {end.isoformat()}.")
        return 0

    twitter = TwitterClient()
    header = f"Phillies schedule for the next {LOOKAHEAD_DAYS} days as of {today.isoformat()} (in replies):"
    parent_id = twitter.tweet(header)
    if parent_id is None:
        return 1

    for game in games[:LOOKAHEAD_DAYS]:
        day = game.get("game_date", "")
        home = game.get("home_name", "Home")
        away = game.get("away_name", "Away")
        home_pitch = game.get("home_probable_pitcher") or "Pitcher TBD"
        away_pitch = game.get("away_probable_pitcher") or "Pitcher TBD"
        stadium = game.get("venue_name", "the ballpark")
        body = (
            f"{day}\n"
            f"{home} ({home_pitch}) vs {away} ({away_pitch})\n"
            f"Game will be played at {stadium}"
        )
        new_id = twitter.tweet(body, replyid=parent_id)
        if new_id is not None:
            parent_id = new_id
        time.sleep(5)
    return 0


if __name__ == "__main__":
    sys.exit(main())
