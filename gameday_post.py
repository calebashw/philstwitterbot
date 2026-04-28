# Author: Caleb Ash
# Created June 2023, refactored 2026
# Tweets a game-day preview for the Phillies' game today.
# Exits cleanly (no tweet) on off-days or when the schedule call returns nothing.

import sys
from datetime import date

import statsapi

from tweet_funcs import TwitterClient

PHILLIES_TEAM_ID = 143


def build_preview(today: date) -> str | None:
    games = statsapi.schedule(start_date=today.isoformat(), team=PHILLIES_TEAM_ID)
    if not games:
        return None

    game = games[0]
    away = game.get("away_name", "Away")
    home = game.get("home_name", "Home")
    away_pitch = game.get("away_probable_pitcher") or "TBD"
    home_pitch = game.get("home_probable_pitcher") or "TBD"
    stadium = game.get("venue_name", "the ballpark")
    game_time = game.get("game_datetime", "")

    weekday = today.strftime("%A")
    formatted_date = today.strftime("%m-%d-%Y")

    return (
        "Calling all Phillies fans, it's game day!\n"
        f"{weekday}, {formatted_date}: {away} @ {home}, "
        f"with {away_pitch} vs {home_pitch} at {stadium}. "
        "Let's play ball!"
    )


def main() -> int:
    today = date.today()
    message = build_preview(today)
    if message is None:
        print(f"No Phillies game on {today.isoformat()}; nothing to tweet.")
        return 0

    print(message)
    if TwitterClient().tweet(message) is None:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
