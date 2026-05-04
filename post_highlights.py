# Author: Caleb Ash
# Created June 2023, refactored 2026
# Tweets Phillies highlights from the most recently finished game.
# Staleness-capped + dedup'd via .state/last_highlight_game_id so the same
# game isn't posted twice across multiple cron fires.

import os
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


def first_two_words(text: str) -> str:
    """Player-name extractor: grab everything before the second whitespace/apostrophe."""
    out = []
    k = 0
    for ch in text:
        if ch in (" ", "'"):
            k += 1
        if k == 2:
            break
        out.append(ch)
    return "".join(out).strip()


def parse_highlight_blocks(blob: str) -> list[tuple[str, str, str]]:
    """Parse the MLB highlights blob into (title, description, url) tuples.
    Block layout is variable: some have title+description+URL, some skip the
    description (title, blank line, URL). The URL line always terminates a
    block, so we use that as the delimiter rather than splitting on blank lines.
    """
    results = []
    current: list[str] = []
    for raw_line in blob.split("\n"):
        line = raw_line.strip()
        if not line:
            continue
        current.append(line)
        if line.startswith("http"):
            url = current[-1]
            non_url = current[:-1]
            if non_url:
                title = non_url[0]
                description = non_url[1] if len(non_url) > 1 else ""
                results.append((title, description, url))
            current = []
    return results


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
    # Sort by start time (most recent first); game_id is a tiebreaker for doubleheaders.
    # NOTE: game_id is NOT monotonic by date in MLB-StatsAPI -- e.g., 5/1=823877,
    # 5/2=823876, 5/3=823875 (descending). Sorting by game_id picks the wrong game.
    def sort_key(g):
        return (g.get("game_datetime") or g.get("game_date") or "", g.get("game_id", 0))
    finished.sort(key=sort_key, reverse=True)
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

    tweets: list[str] = []
    for title, description, url in parse_highlight_blocks(blob):
        # Skip the "Condensed Game" reel — not a player highlight, and doesn't pass the player filter.
        if title.lower().startswith("condensed game"):
            continue
        # Filter to Phillies players via the title (more reliable than description).
        if not is_phillie(first_two_words(title)):
            continue
        # Prefer description (richer); fall back to title if too long or absent.
        body = description or title
        tweet = f"{body} {url}".strip()
        if len(tweet) > TWEET_LIMIT:
            tweet = f"{title} {url}".strip()
            if len(tweet) > TWEET_LIMIT:
                continue
        tweets.append(tweet)
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
