# Author: Caleb Ash
# Created June 2023, refactored 2026
# Tweets Phillies highlights from the most recently finished game.
# Staleness-capped + dedup'd via .state/last_highlight_game_id so the same
# game isn't posted twice across multiple cron fires.

import os
import re
import sys
import time
from datetime import date, timedelta
from pathlib import Path

import statsapi

from tweet_funcs import TwitterClient

PHILLIES_TEAM_ID = 143
MAX_TWEETS_PER_RUN = int(os.environ.get("HIGHLIGHTS_MAX_TWEETS", "8"))
DRY_RUN = os.environ.get("DRY_RUN", "").lower() in ("1", "true", "yes")
TWEET_LIMIT = 280
SLEEP_BETWEEN_TWEETS_SEC = 3
MAX_STALENESS_DAYS = int(os.environ.get("HIGHLIGHTS_MAX_AGE_DAYS", "2"))
STATE_FILE = Path(os.environ.get("HIGHLIGHTS_STATE_FILE", ".state/last_highlight_game_id"))


def split_lines(blob: str) -> list[str]:
    return [s for s in re.split(r"\n+", blob) if s.strip()]


def first_two_words(text: str) -> str:
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


def most_recent_finished_game() -> dict | None:
    """Return the most recently finished Phillies game in the last MAX_STALENESS_DAYS, or None."""
    today = date.today()
    earliest = today - timedelta(days=MAX_STALENESS_DAYS)
    games = statsapi.schedule(
        start_date=earliest.isoformat(),
        end_date=today.isoformat(),
        team=PHILLIES_TEAM_ID,
    )
    finished = [g for g in games if g.get("status") == "Final"]
    if not finished:
        return None
    # game_id is monotonically assigned, so this picks the most recent including doubleheaders.
    finished.sort(key=lambda g: g.get("game_id", 0), reverse=True)
    return finished[0]


def read_last_posted() -> int | None:
    if not STATE_FILE.exists():
        return None
    text = STATE_FILE.read_text().strip()
    if not text:
        return None
    try:
        return int(text)
    except ValueError:
        print(f"  state file {STATE_FILE} contains non-int {text!r}; ignoring.")
        return None


def write_last_posted(game_id: int) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(f"{game_id}\n")


def collect_highlight_tweets(game_id: int) -> list[str]:
    try:
        blob = statsapi.game_highlights(game_id)
    except Exception as e:
        print(f"  game_highlights failed for game_id={game_id}: {e}")
        return []

    lines = split_lines(blob)
    tweets: list[str] = []
    pending = ""
    skip_next = False

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
    game = most_recent_finished_game()
    if game is None:
        print(f"No finished Phillies game in the last {MAX_STALENESS_DAYS} day(s); nothing to tweet.")
        return 0

    game_id = game["game_id"]
    summary = game.get("summary", "")
    last_posted = read_last_posted()
    if last_posted == game_id:
        print(f"Highlights for game {game_id} ({summary}) already posted; skipping.")
        return 0

    tweets = collect_highlight_tweets(game_id)
    if not tweets:
        # Don't write state — highlights may simply not be uploaded yet; let the next fire retry.
        print(f"No Phillies highlights matched for game {game_id} ({summary}); will retry next run.")
        return 0

    capped = tweets[:MAX_TWEETS_PER_RUN]
    print(f"Game {game_id} ({summary}): found {len(tweets)} highlights, posting {len(capped)} (cap={MAX_TWEETS_PER_RUN}).")

    twitter = TwitterClient()
    failures = 0
    for i, msg in enumerate(capped, start=1):
        print(f"[{i}/{len(capped)}] {msg}")
        if DRY_RUN:
            print("  (DRY_RUN: skipped)")
        else:
            if twitter.tweet(msg) is None:
                failures += 1
            time.sleep(SLEEP_BETWEEN_TWEETS_SEC)

    if failures == 0 and not DRY_RUN:
        write_last_posted(game_id)
        print(f"Recorded game {game_id} as posted in {STATE_FILE}.")

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
