"""Seed four murals with sample wall photos from data/.

Usage:
    python seed.py            # seeds the local `murals` catalog directory
    python seed.py my_dir     # or another directory you passed to `pxt schema update`
"""
import sys
from pathlib import Path

import pixeltable as pxt

target = sys.argv[1] if len(sys.argv) > 1 else 'murals'
HERE = Path(__file__).resolve().parent

SEED = {
    'murals': [
        {'title': 'Harbor Wave', 'artist': 'L. Ortega', 'neighborhood': 'waterfront', 'wall_photo': 'data/harbor-wave.png'},
        {'title': 'Sunflower Wall', 'artist': 'M. Adeyemi', 'neighborhood': 'mission', 'wall_photo': 'data/sunflower-wall.png'},
        {'title': 'Canopy', 'artist': 'K. Tan', 'neighborhood': 'mission', 'wall_photo': 'data/canopy.png'},
        {'title': 'The Long Mile', 'artist': 'R. Novak', 'neighborhood': 'eastside', 'wall_photo': 'data/long-mile.png'},
    ],
}

for table_name, rows in SEED.items():
    t = pxt.get_table(f'{target}/{table_name}')
    if t.count() > 0:
        print(f'{target}/{table_name} already has {t.count()} rows; skipping')
        continue
    for row in rows:
        for k, v in row.items():
            if isinstance(v, str) and v.startswith('data/'):
                row[k] = str(HERE / v)   # local sample media file
    t.insert(rows)
    print(f'inserted {len(rows)} rows into {target}/{table_name}')
