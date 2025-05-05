#!/usr/bin/env python3

import csv
from collections import defaultdict
from functools import reduce
import os
import subprocess

SVG_IN = os.getenv("SVG_IN", "harti/romania-uat.svg")
CSV_FILE = os.getenv("CSV_FILE", "info-voturi/pv_part_cntry_prsd.csv")
OUT_FILE = os.getenv("OUT_FILE", "harti/voturi-uat-XXXX-YYYY.svg")

SIRUTA_FIELD = os.getenv("SIRUTA_FIELD", "uat_siruta")

FONT_FAMILY = os.getenv("FONT_FAMILY", '"DejaVu Sans", sans-serif')
STRIPE_SIZE = int(os.getenv("VOTED_FIELD", "10"))
LEGEND_Y_START = int(os.getenv("LEGEND_Y_START", "220"))
MAP_TITLE_X = int(os.getenv("MAP_TITLE_X", "2580"))
MAP_TITLE_Y = int(os.getenv("MAP_TITLE_Y", "20"))
MAP_TITLE = os.getenv("MAP_TITLE", "Candidații cu cele mai multe\nvoturi dintr-un UAT la alegerile\nprezidențiale 2025, turul 1").splitlines()

NORMAL_SIZE = int(os.getenv("SQUEEZE_SIZE", "30"))
SQUEEZE_THRESH = int(os.getenv("SQUEEZE_THRESH", "10"))
SQUEEZE_SIZE = int(os.getenv("SQUEEZE_SIZE", "20"))

CANDIDATE_SPEC_FILE = os.getenv("CANDIDATE_SPEC_FILE", "info-candidati/prez1-2025.csv")

with open(CANDIDATE_SPEC_FILE, "r") as file:
    csv_data = csv.reader(file)
    candidate_spec = {line[0]: line[1:] for line in csv_data}
#candidate_spec = {
#    "CĂLIN GEORGESCU": ["#bb00ff", "#8800cc", "Călin Georgescu (Indep.)"],
#    "ELENA-VALERICA LASCONI": ["#00ccff", "#0099cc", "Elena Lasconi (USR)"],
#    "ION-MARCEL CIOLACU": ["#ff0000", "#aa0000", "Marcel Ciolacu (PSD)"],
#    "GEORGE-NICOLAE SIMION": ["#ffdd00", "#999900", "George Simion (AUR)"],
#    "NICOLAE-IONEL CIUCĂ": ["#0055ff", "#0000ee", "Nicolae Ciucă (PNL)"],
#    "HUNOR KELEMEN": ["#00aa00", "#006600", "Kelemen Hunor (UDMR)"],
#}

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
votes_of = defaultdict(lambda: 0)
for siruta in data:
    max_votes = -1
    for c in candidates:
        votes_of[c.removesuffix("-voturi")] += data[siruta][c]
        if data[siruta][c] == max_votes:
            winners[siruta][0].append(c.removesuffix("-voturi"))
        if data[siruta][c] > max_votes:
            max_votes = data[siruta][c]
            winners[siruta] = [[c.removesuffix("-voturi")], max_votes / (data[siruta]["total"] or 1) * 100]

with open(SVG_IN, "r") as file:
    svg_base = file.read()

to_consider = sorted(reduce(lambda a, b: a | b, {frozenset(w[0]) for w in winners.values()}), key=lambda c: votes_of[c], reverse=True)
for c in to_consider:
    extra = ""
    if len([w for w in winners if winners[w][0][0] == c and winners[w][1] > 50]) > 0:
        extra += "M"
    if len([w for w in winners if c in winners[w][0] and winners[w][1] <= 50]) > 0:
        extra += "m"
    print(f'"{c.replace('"', '""')}","#ffffff","#dddddd","Abrev.{extra}"')

classes = {frozenset(w[0]) for w in winners.values() if len(w[0]) > 1}
representative_eq = next(filter(lambda c: len(c) > 1, classes), None)
svg_defs = "<defs>"
for c in classes:
    svg_defs += f'<pattern id="p{hash(c)}" patternUnits="userSpaceOnUse" width="{STRIPE_SIZE}" height="{STRIPE_SIZE}">'
    x = 0
    for cand in c:
        svg_defs += f'<rect x="{x}" height="{STRIPE_SIZE}" width="{STRIPE_SIZE / len(c)}" fill="{candidate_spec[cand][0]}"/>'
        x += STRIPE_SIZE / len(c)
    svg_defs += "</pattern>"
svg_defs += "</defs>"

svg_defs += f'<rect x="0" y="0" fill="white" width="100%" height="100%"/>'
svg_defs += f'<text font-family=\'{FONT_FAMILY}\' font-weight="bold" dominant-baseline="hanging" text-anchor="middle" x="{MAP_TITLE_X}" y="{MAP_TITLE_Y}" font-size="50">'
first_line = True
for title_line in MAP_TITLE:
    svg_defs += f'<tspan x="{MAP_TITLE_X}" dy="{"0em" if first_line else "1.2em"}">{title_line}</tspan>'
    first_line = False
svg_defs += '</text>'

y = LEGEND_Y_START
svg_defs += f'<text font-family=\'{FONT_FAMILY}\' font-size="22" y="{y - 10}" x="2850" fill="black" text-anchor="middle">≤50%</text>'
svg_defs += f'<text font-family=\'{FONT_FAMILY}\' font-size="22" y="{y - 10}" x="2950" fill="black" text-anchor="middle">&gt;50%</text>'
for cand in candidate_spec:
    if not [w for w in winners if cand in winners[w][0]]:
        continue
    if len([w for w in winners if cand in winners[w][0] and winners[w][1] <= 50]) > 0:
        svg_defs += f'<rect width="100" height="50" fill="{candidate_spec[cand][0]}" x="2800" y="{y}" class="rect-candidat"/>'
    if len([w for w in winners if winners[w][0][0] == cand and winners[w][1] > 50]) > 0:
        svg_defs += f'<rect width="100" height="50" fill="{candidate_spec[cand][1]}" x="2900" y="{y}" class="rect-candidat"/>'
    svg_defs += f'<text font-family=\'{FONT_FAMILY}\' dominant-baseline="central" text-anchor="end" x="2795" y="{y + 25}" font-size="{NORMAL_SIZE if len(candidate_spec[cand][2]) < SQUEEZE_THRESH else SQUEEZE_SIZE}">{candidate_spec[cand][2]}</text>'
    y += 50

y += 25
if representative_eq:
    svg_defs += f'<rect width="200" height="50" fill="url(#p{hash(representative_eq)})" x="2800" y="{y}" class="rect-candidat"/>'
    svg_defs += f'<text font-family=\'{FONT_FAMILY}\' dominant-baseline="central" text-anchor="end" x="2795" y="{y + 25}" font-size="{NORMAL_SIZE}">Egalitate</text>'

new_styles = """
    .rect-candidat {
        stroke: black;
        stroke-width: 2px;
    }
"""
for siruta in winners:
    if len(winners[siruta][0]) > 1:
        fill = f"url(#p{hash(frozenset(winners[siruta][0]))})"
    elif winners[siruta][1] > 50:
        fill = candidate_spec[winners[siruta][0][0]][1]
    else:
        fill = candidate_spec[winners[siruta][0][0]][0]

    new_styles += """
        #uat-%d {
            fill: %s;
        }
    """ % (int(siruta), fill)

final_svg = svg_base.replace("</style>", new_styles + "</style>" + svg_defs)

with open(OUT_FILE, "w") as file:
    file.write(final_svg)
subprocess.run(["./text-to-path.sh", OUT_FILE])
