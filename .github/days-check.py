#!/usr/bin/env python3
"""Checks the game's day files before the "Publish the day files" workflow puts them on the site.

Each file is days/<YYYY-MM-DD>.json: a JSON object of at most 20 KB with only the game's fields, dated as its name says;
its real news at most 8 items, each with its source named, an https link if any, and a headline of 12 words or fewer;
nothing that looks like markup or a script. Usage: days-check.py <folder of day files>
"""
import json
import os
import re
import sys

FIELDS = {'date', 'v', 'seed', 'made', 'events', 'gen'}


def refuse(msg):
    print('REFUSED: ' + msg)
    sys.exit(1)


def main(folder):
    names = sorted(os.listdir(folder))
    if not names:
        refuse('no day files')
    if len(names) > 60:
        refuse('%d files: at most 60 at a time' % len(names))
    for name in names:
        path = os.path.join(folder, name)
        if not re.fullmatch(r'20\d\d-[01]\d-[0-3]\d\.json', name):
            refuse('not a day file: ' + name)
        if os.path.getsize(path) > 20000:
            refuse(name + ' is over 20 KB')
        try:
            with open(path, encoding='utf-8') as fh:
                day = json.load(fh)
        except Exception as err:  # noqa: BLE001 (any parse error refuses the file)
            refuse('%s is not JSON (%s)' % (name, err))
        if not isinstance(day, dict):
            refuse(name + ' is not an object')
        extra = set(day) - FIELDS
        if extra:
            refuse('%s has fields the game does not read: %s' % (name, ', '.join(sorted(extra))))
        if day.get('date') != name[:-5]:
            refuse('%s says its date is %s' % (name, day.get('date')))
        real, gen = day.get('events', []), day.get('gen', [])
        if not isinstance(real, list) or len(real) > 8:
            refuse(name + ': real news must be a list of at most 8')
        if not isinstance(gen, list) or len(gen) > 30:
            refuse(name + ': game events must be a list of at most 30')
        for ev in real + gen:
            if not isinstance(ev, dict):
                refuse(name + ': an event is not an object')
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
    print('OK: %d day files' % len(names))


if __name__ == '__main__':
    if len(sys.argv) != 2:
        refuse('usage: days-check.py <folder>')
    main(sys.argv[1])
