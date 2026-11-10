#!/usr/bin/env python3
"""Checks the game's day files before the "Publish the day files" workflow puts them on the site.

Each file is days/<YYYY-MM-DD>.json: a JSON object of at most 20 KB with only the game's fields, dated as its name says;
its real news at most 8 items, each with its source named, an https link if any, and a headline of 12 words or fewer,
at most one of them the day's lead; nothing that looks like markup or a script. A file the site already has as final
never changes (round 14): with --site, a file that would change one is set aside and named, and the rest go on.
Usage: days-check.py <folder of day files> [--site <the site's days folder>]
"""
import json
import os
import re
import sys

FIELDS = {'date', 'v', 'seed', 'made', 'events', 'gen', 'final', 'foundersUntil'}
DATE = r'20\d\d-[01]\d-[0-3]\d'


def refuse(msg):
    print('REFUSED: ' + msg)
    sys.exit(1)


def load(path, name):
    try:
        with open(path, encoding='utf-8') as fh:
            return json.load(fh)
    except Exception as err:  # noqa: BLE001 (any parse error refuses the file)
        refuse('%s is not JSON (%s)' % (name, err))


def check(name, day):
    if not isinstance(day, dict):
        refuse(name + ' is not an object')
    extra = set(day) - FIELDS
    if extra:
        refuse('%s has fields the game does not read: %s' % (name, ', '.join(sorted(extra))))
    if day.get('date') != name[:-5]:
        refuse('%s says its date is %s' % (name, day.get('date')))
    if 'final' in day and day['final'] is not True:
        refuse(name + ': final is true or not there at all')
    if 'foundersUntil' in day and not re.fullmatch(DATE, str(day['foundersUntil'])):
        refuse(name + ': foundersUntil is not a date')
    real, gen = day.get('events', []), day.get('gen', [])
    if not isinstance(real, list) or len(real) > 8:
        refuse(name + ': real news must be a list of at most 8')
    if not isinstance(gen, list) or len(gen) > 30:
        refuse(name + ': game events must be a list of at most 30')
    for ev in real + gen:
        if not isinstance(ev, dict):
            refuse(name + ': an event is not an object')
    leads = [ev for ev in real if 'lead' in ev]
    if any(ev['lead'] is not True for ev in leads) or any('lead' in ev for ev in gen):
        refuse(name + ': lead is true, on real news only, or not there at all')
    if len(leads) > 1:
        refuse(name + ': more than one lead')
    for ev in real:
        head = str(ev.get('h', ''))
        if len(head.split()) > 12:
            refuse('%s: a headline of more than 12 words: %s' % (name, head))
        if not ev.get('src'):
            refuse(name + ': real news without its source')
        if ev.get('url') and not str(ev['url']).startswith('https://'):
            refuse(name + ': a source link that is not https')
    text = json.dumps(day, ensure_ascii=False)
    if re.search(r'[<>]|javascript:', text, re.I):
        refuse(name + ': something that looks like markup')


def main(folder, site=None):
    names = sorted(os.listdir(folder))
    if not names:
        refuse('no day files')
    if len(names) > 60:
        refuse('%d files: at most 60 at a time' % len(names))
    kept = 0
    for name in names:
        path = os.path.join(folder, name)
        if not re.fullmatch(DATE + r'\.json', name):
            refuse('not a day file: ' + name)
        if os.path.getsize(path) > 20000:
            refuse(name + ' is over 20 KB')
        day = load(path, name)
        check(name, day)
        if site and os.path.exists(os.path.join(site, name)):
            old = load(os.path.join(site, name), name)
            if isinstance(old, dict) and old.get('final') is True and old != day:
                print('KEPT: %s is final on the site; the new copy is set aside' % name)
                os.remove(path)
                kept += 1
    print('OK: %d day files%s' % (len(names) - kept, ' (%d final ones kept as they were)' % kept if kept else ''))


if __name__ == '__main__':
    args = sys.argv[1:]
    site = None
    if len(args) == 3 and args[1] == '--site':
        site = args[2]
        args = args[:1]
    if len(args) != 1:
        refuse('usage: days-check.py <folder> [--site <folder>]')
    main(args[0], site)
