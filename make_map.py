#!/usr/bin/env python3

import csv
from collections import defaultdict
import os

import matplotlib.pyplot as plt


SVG_IN = os.getenv("SVG_IN", "romania-uat.svg")
CSV_FILE = os.getenv("CSV_FILE", "presence_2024-11-25_07-00.csv")
OUT_FILE = os.getenv("OUT_FILE", "prezenta-uat.svg")

SIRUTA_FIELD = os.getenv("SIRUTA_FIELD", "Siruta")
REGISTERED_FIELD = os.getenv("REGISTERED_FIELD", "Înscriși pe liste permanente")
VOTED_FIELD = os.getenv("VOTED_FIELD", "LT")

COLOR_SCHEME = os.getenv("COLOR_SCHEME", "gist_rainbow")
DECIMAL_SEP = os.getenv("DECIMAL_SEP", ",")

MAP_TITLE_X = int(os.getenv("MAP_TITLE_X", "2580"))
MAP_TITLE_Y = int(os.getenv("MAP_TITLE_Y", "20"))
MAP_TITLE = os.getenv("MAP_TITLE", "Prezența per UAT la alegerile\nparlamentare 2024").splitlines()


def color_to_rgb(color):
    return f"rgb({int(color[0] * 255)}, {int(color[1] * 255)}, {int(color[2] * 255)})"


data = defaultdict(lambda: [0, 0])

with open(CSV_FILE, "r", encoding="utf-8-sig") as csv_file:
    csv_data = csv.DictReader(csv_file)

    for row in csv_data:
        siruta = row[SIRUTA_FIELD]
        if int(siruta) == 9999:
            continue

        data[siruta][0] += int(row[VOTED_FIELD])
        data[siruta][1] += int(row[REGISTERED_FIELD])

data = {d: data[d][0] / data[d][1] * 100 for d in data}
data_arr = list(data.values())
data_max = max(data_arr)
data_min = min(data_arr)

with open(SVG_IN, "r") as file:
    svg_base = file.read()

new_styles = ""
for siruta in data:
    cmap = plt.get_cmap(COLOR_SCHEME)

    color = cmap((data[siruta] - data_min) / (data_max - data_min) * 1)

    new_styles += """
        #uat-%d {
            fill: %s;
        }
    """ % (int(siruta), color_to_rgb(color))

svg_defs = '<rect x="0" y="0" fill="white" width="100%" height="100%"/>'
svg_defs += f'<text font-family="sans-serif" font-weight="bold" dominant-baseline="hanging" text-anchor="middle" x="{MAP_TITLE_X}" y="{MAP_TITLE_Y}" font-size="50">'
first_line = True
for title_line in MAP_TITLE:
    svg_defs += f'<tspan x="{MAP_TITLE_X}" dy="{"0em" if first_line else "1.2em"}">{title_line}</tspan>'
    first_line = False
svg_defs += '</text>'

final_svg = svg_base.replace("</style>", new_styles + "</style>" + svg_defs)
with open(OUT_FILE, "w") as file:
    print(final_svg, file=file)

im = plt.pcolor([list(data.values())], cmap=COLOR_SCHEME)
colorbar = plt.colorbar(im)
ticks = [data_min] + list(range((int(data_min) // 10 + 1) * 10, int(data_max), 10)) + [data_max]
if len(ticks) > 2:
    if abs(ticks[1] - ticks[0]) < 5:
        ticks.pop(1)
    if abs(ticks[-1] - ticks[-2]) < 5:
        ticks.pop(-2)
colorbar.set_ticks(ticks)
colorbar.set_ticklabels([f"{i:.1f}%".replace(".", DECIMAL_SEP) for i in ticks])
plt.show()
