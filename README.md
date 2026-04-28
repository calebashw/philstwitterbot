# philstwitterbot

A Twitter/X bot that posts Philadelphia Phillies content using the X API and [MLB-StatsAPI](https://github.com/toddrob99/MLB-StatsAPI). Originally built June 2023; refactored April 2026 for the current X API and to run on GitHub Actions.

Account: [@philstweetbot](https://twitter.com/philstweetbot).

## What it posts

| Script | When | What |
|---|---|---|
| `gameday_post.py` | Daily, 14:00 UTC (~10am ET) | Preview tweet for today's game (off-days no-op) |
| `game_summary.py` | Daily, 12:00 UTC (~8am ET) | Summary tweet for yesterday's finished game |
| `post_highlights.py` | Daily, 13:00 UTC (~9am ET) | Up to `HIGHLIGHTS_MAX_TWEETS` (default 8) Phillies highlights from yesterday |

Each workflow can also be triggered manually from the Actions tab.

`scoring_plays.py` and `schedule_tweet.py` are present but **not scheduled** — they need design decisions (cadence, rate-limit headroom) before re-enabling.

## Setup

### 1. Get X API credentials

As of February 2026 X removed the free API tier for new developers. New apps go on the **pay-per-use** plan. You will need:

1. Apply at <https://developer.x.com/> for a developer account.
2. Create an **app** under a project, with **Read and Write** permissions.
3. Generate the five credentials this bot uses:
   - `CONSUMER_KEY` (a.k.a. API Key)
   - `CONSUMER_SECRET` (a.k.a. API Key Secret)
   - `ACCESS_TOKEN`
   - `ACCESS_SECRET` (a.k.a. Access Token Secret)
   - `BEARER_TOKEN`

> **Cost note.** On pay-per-use you're billed per write. The highlights workflow is hard-capped at 8 tweets per run to bound spend; raise it via `HIGHLIGHTS_MAX_TWEETS` only after you've watched a few real runs.

### 2. Add credentials as GitHub Secrets

In the GitHub repo: **Settings → Secrets and variables → Actions → New repository secret**. Add one secret per credential, named exactly:

```
CONSUMER_KEY
CONSUMER_SECRET
ACCESS_TOKEN
ACCESS_SECRET
BEARER_TOKEN
```

### 3. Push the branch and enable workflows

```bash
git push -u origin refactor-2026
```

Open a PR (or merge to `main`). The schedules in `.github/workflows/*.yml` activate once the workflow files are on the default branch. Check **Actions → Gameday preview / Game summary / Game highlights** to see runs.

## Running locally

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

export CONSUMER_KEY=...
export CONSUMER_SECRET=...
export ACCESS_TOKEN=...
export ACCESS_SECRET=...
export BEARER_TOKEN=...

# Dry-run highlights without tweeting:
DRY_RUN=1 python post_highlights.py

# Actually tweet:
python gameday_post.py
python game_summary.py
python post_highlights.py
```

## Scheduling notes

- GitHub Actions cron is **UTC-only**. Phillies are on Eastern Time, so the listed run times shift by an hour between EST and EDT — acceptable for morning posts.
- All three scripts no-op on off-days, so leaving them scheduled year-round is safe.
- GitHub may delay scheduled workflows by several minutes during peak load; the start times above are best-effort, not exact.

## Notice

This repository is meant to display my work. If you want to make a similar bot for another team, feel free — please don't make a copycat for the Phillies.
