#!/usr/bin/env python3
"""Makes a date's day file final (round 14): the paper the day's run is built from, which never changes after.

The news task finalises tomorrow's file at 06:10 UTC (a catch-up at 08:10); this is the site's own safety net, run at
08:30 and 09:15 UTC, before 10:00 UTC, when the first time zone reaches tomorrow. A file already final is left alone; a
draft becomes final with the news it has; with no file at all, a quiet day's file is written (no real news: the game
makes the day's headlines from the date, the same on every phone). Usage: days-final.py <days folder> [YYYY-MM-DD]
(default: tomorrow in UTC). Prints what it did; the workflow commits a changed file.
"""
import datetime
import json
import os
import re
import sys


def main(folder, date=None):
    today = datetime.datetime.now(datetime.timezone.utc).date()
    date = date or (today + datetime.timedelta(days=1)).isoformat()
    if not re.fullmatch(r'20\d\d-[01]\d-[0-3]\d', date):
        print('REFUSED: not a date: ' + date)
        sys.exit(1)
    path = os.path.join(folder, date + '.json')
    if os.path.exists(path):
        with open(path, encoding='utf-8') as fh:
            day = json.load(fh)
        if day.get('final') is True:
            print('Already final: ' + date)
            return
        day['final'] = True
        what = 'Final with its %d real news: %s' % (len(day.get('events', [])), date)
    else:
        day = {'date': date, 'v': 1, 'seed': date, 'made': today.isoformat(), 'events': [], 'final': True}
        what = 'A quiet day, final: ' + date
    with open(path, 'w', encoding='utf-8') as fh:
        fh.write(json.dumps(day, ensure_ascii=False, indent=1) + '\n')
    print(what)


if __name__ == '__main__':
    if len(sys.argv) not in (2, 3):
        print('usage: days-final.py <days folder> [YYYY-MM-DD]')
        sys.exit(2)
    main(sys.argv[1], sys.argv[2] if len(sys.argv) == 3 and sys.argv[2] else None)
