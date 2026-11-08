# Portbound

The public site of Portbound, the trading game for iPhone: https://cloudbite-eu.github.io/portbound/

- `docs/index.html`, `docs/support.html`, `docs/privacy.html`: the game's page, its support page and its privacy
  policy (the addresses App Store Connect asks for).
- `docs/days/<date>.json`: the day files. Every player on a date trades the same world, moved by that date's real news;
  the iPhone app reads the day's file from https://cloudbite-eu.github.io/portbound/days/ and plays the copies bundled
  with it when it cannot.
- `.github/workflows/days.yml`: the scheduled news task pushes each day's files to a branch `claude/days-<date>`; this
  workflow checks them (`.github/days-check.py`), publishes them here on `main` and removes the branch.

GitHub Pages serves the `docs` folder of `main`. The game's code is not here.
