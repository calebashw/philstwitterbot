# Author: Caleb Ash
# Created June 2023
# NOT CURRENTLY SCHEDULED. Refactored only enough to import under the new credential setup.
# To re-enable: review rate-limit headroom, add yesterday-only filter, then add a workflow.

import sys

import statsapi

from tweet_funcs import TwitterClient

PHILLIES_TEAM_ID = 143


def main() -> int:
    last_id = statsapi.last_game(PHILLIES_TEAM_ID)
    blob = statsapi.game_scoring_plays(last_id)
    plays = [p for p in blob.split("\n\n") if p.strip()]
    if not plays:
        print("No scoring plays found.")
        return 0
    twitter = TwitterClient()
    for play in plays:
        twitter.tweet(play)
    return 0


if __name__ == "__main__":
    sys.exit(main())
