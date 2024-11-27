#!/usr/bin/env python3

import csv
from collections import defaultdict
import os
import re

SVG_IN = os.getenv("SVG_IN", "romania-uat.svg")
CSV_FILE = os.getenv("CSV_FILE", "pv_part_cntry_prsd.csv")
OUT_FILE = os.getenv("OUT_FILE", "voturi-uat.svg")

SIRUTA_FIELD = os.getenv("SIRUTA_FIELD", "uat_siruta")
REGISTERED_FIELD = os.getenv("REGISTERED_FIELD", "Înscriși pe liste permanente")
VOTED_FIELD = os.getenv("VOTED_FIELD", "LT")

STRIPE_SIZE = 7

colors = {
    "CĂLIN GEORGESCU": ["#bb00ff", "#8800cc", "Călin Georgescu (Indep.)"],
    "ELENA-VALERICA LASCONI": ["#00ccff", "#0099cc", "Elena Lasconi (USR)"],
    "ION-MARCEL CIOLACU": ["#ff0000", "#aa0000", "Marcel Ciolacu (PSD)"],
    "GEORGE-NICOLAE SIMION": ["#ffdd00", "#999900", "George Simion (AUR)"],
    "NICOLAE-IONEL CIUCĂ": ["#0055ff", "#0000ee", "Nicolae Ciucă (PNL)"],
    "HUNOR KELEMEN": ["#00aa00", "#006600", "Kelemen Hunor (UDMR)"],
}

data = defaultdict(lambda: defaultdict(lambda: 0))

with open(CSV_FILE, "r", encoding="utf-8-sig") as csv_file:
    csv_data = csv.DictReader(csv_file)

    candidates = [c for c in csv_data.fieldnames if c.endswith("-voturi")]

    for row in csv_data:
        siruta = row[SIRUTA_FIELD]
        if int(siruta) == 9999:
            continue

        for c in candidates:
            data[siruta][c] += int(row[c])
            data[siruta]["total"] += int(row[c])

winners = defaultdict(lambda: [[], 0])
for siruta in data:
    max_votes = -1
    for c in candidates:
        if data[siruta][c] == max_votes:
            winners[siruta][0].append(c.removesuffix("-voturi"))
        if data[siruta][c] > max_votes:
            max_votes = data[siruta][c]
            winners[siruta] = [[c.removesuffix("-voturi")], max_votes / (data[siruta]["total"] or 1) * 100]

with open(SVG_IN, "r") as file:
    svg_base = file.read()

classes = {frozenset(w[0]) for w in winners.values()}
svg_defs = "<defs>"
for c in classes:
    svg_defs += f'<pattern id="p{hash(c)}" patternUnits="userSpaceOnUse" width="{STRIPE_SIZE}" height="{STRIPE_SIZE}">'
    x = 0
    for cand in c:
        svg_defs += f'<rect x="{x}" height="{STRIPE_SIZE}" width="{STRIPE_SIZE / len(c)}" fill="{colors[cand][0]}"/>'
        x += STRIPE_SIZE / len(c)
    svg_defs += "</pattern>"
svg_defs += "</defs>"

y = 200
svg_defs += f'<text font-family="sans-serif" font-size="22" y="{y - 10}" x="2850" fill="black" text-anchor="middle">≤50%</text>'
svg_defs += f'<text font-family="sans-serif" font-size="22" y="{y - 10}" x="2950" fill="black" text-anchor="middle">&gt;50%</text>'
for cand, color in colors.items():
    svg_defs += f'<rect width="100" height="50" fill="{color[0]}" x="2800" y="{y}" class="rect-candidat"/>'
    if len([w for w in winners if winners[w][0][0] == cand and winners[w][1] > 50]) > 0:
        svg_defs += f'<rect width="100" height="50" fill="{color[1]}" x="2900" y="{y}" class="rect-candidat"/>'
    svg_defs += f'<text font-family="sans-serif" dominant-baseline="central" text-anchor="end" x="2795" y="{y + 25}" font-size="30">{colors[cand][2]}</text>'
    y += 50

new_styles = """
    .rect-candidat {
        stroke: black;
        stroke-width: 2px;
    }
"""
for siruta in winners:
    new_styles += """
        #uat-%d {
            fill: %s;
        }
    """ % (int(siruta), colors[winners[siruta][0][0]][1] if winners[siruta][1] > 50 else "url(#p%d)" % hash(frozenset(winners[siruta][0])))

final_svg = svg_base.replace("</style>", new_styles + "</style>" + svg_defs)

with open(OUT_FILE, "w") as file:
    file.write(final_svg)
