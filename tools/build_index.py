#!/usr/bin/env python3
"""Regenera data/decks/index.json e data/news/index.json.
Rode sempre depois de criar ou alterar arquivos em data/decks ou data/news:
    python3 tools/build_index.py
"""
import hashlib, json, os, glob
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def h(p): return hashlib.sha1(open(p, 'rb').read()).hexdigest()[:10]
decks = {}
for p in sorted(glob.glob(os.path.join(ROOT, 'data/decks/*.json'))):
    name = os.path.basename(p)[:-5]
    if name == 'index': continue
    json.load(open(p))  # falha se o JSON estiver quebrado
    decks[name] = h(p)
json.dump({'decks': decks}, open(os.path.join(ROOT, 'data/decks/index.json'), 'w'), indent=0)
days = []
for p in sorted(glob.glob(os.path.join(ROOT, 'data/news/*.json')), reverse=True):
    name = os.path.basename(p)[:-5]
    if name == 'index': continue
    json.load(open(p))
    days.append({'date': name, 'v': h(p)})
json.dump({'days': days}, open(os.path.join(ROOT, 'data/news/index.json'), 'w'), indent=0)
print(f'{len(decks)} decks, {len(days)} dias de clipping')
