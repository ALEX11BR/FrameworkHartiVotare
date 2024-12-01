#!/usr/bin/env python3

import csv
from collections import defaultdict
import os

import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from matplotlib import cm

CSV_FILE_FINAL = os.getenv("CSV_FILE_FINAL", "presence_2024-11-25_07-00.csv")
CSV_FILE_EARLY = os.getenv("CSV_FILE_EARLY", "presence_2024-11-24_21-00.csv")
OUT_FILE = os.getenv("OUT_FILE", "prezenta-uat.svg")

SIRUTA_FIELD = os.getenv("SIRUTA_FIELD", "Siruta")
REGISTERED_FIELD = os.getenv("REGISTERED_FIELD", "Înscriși pe liste permanente")
VOTED_FIELD = os.getenv("VOTED_FIELD", "LT")

COLOR_SCHEME = os.getenv("COLOR_SCHEME", "cool")

MAP_TITLE_X = int(os.getenv("MAP_TITLE_X", "2580"))
MAP_TITLE_Y = int(os.getenv("MAP_TITLE_Y", "20"))
MAP_TITLE = os.getenv("MAP_TITLE", "Numărul de voturi exprimate după\nora 21 (închiderea normală a\nurnelor) per UAT la alegerile\nparlamentare din 2024").splitlines()


def color_to_rgb(color):
    return f"rgb({int(color[0] * 255)}, {int(color[1] * 255)}, {int(color[2] * 255)})"


data = defaultdict(lambda: [0, 0])

with open(CSV_FILE_FINAL, "r", encoding="utf-8-sig") as csv_file, open(CSV_FILE_EARLY, "r", encoding="utf-8-sig") as early_file:
    csv_data = csv.DictReader(csv_file)
    early_data = csv.DictReader(early_file)

    for row in csv_data:
        siruta = row[SIRUTA_FIELD]
        if int(siruta) == 9999:
            continue

        data[siruta][0] += int(row[VOTED_FIELD])

    for row in early_data:
        siruta = row[SIRUTA_FIELD]
        if int(siruta) == 9999:
            continue

        data[siruta][1] += int(row[VOTED_FIELD])

data = {d: data[d][0] - data[d][1] for d in data}
data_arr = list(data.values())
data_max = max(data_arr)
data_min = min(data_arr)

with open("romania-uat.svg", "r") as file:
    svg_base = file.read()

color_mapping = cm.ScalarMappable(norm=LogNorm(1, data_max), cmap=plt.get_cmap(COLOR_SCHEME))
new_styles = ""
for siruta in data:
    cmap = plt.get_cmap(COLOR_SCHEME)

    if data[siruta] == 0:
        color = "white"
    else:
        color = color_mapping.to_rgba([data[siruta]])
        color = color_to_rgb(color[0])

    new_styles += """
        #uat-%d {
            fill: %s;
        }
    """ % (int(siruta), color)

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

im = plt.pcolor([[1, data_max]], cmap=COLOR_SCHEME, norm=LogNorm(1, data_max))
colorbar = plt.colorbar(im)
ticks = [1, 2, 5, 10, 20, data_max]
colorbar.set_ticks(ticks)
colorbar.set_ticklabels(ticks)
plt.show()
