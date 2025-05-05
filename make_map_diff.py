#!/usr/bin/env python3

import csv
from collections import defaultdict
from io import StringIO
from math import log10
import os
import subprocess
from xml.etree import ElementTree

import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from matplotlib import cm


SVG_IN = os.getenv("SVG_IN", "harti/romania-uat.svg")
CSV_FILE_FINAL = os.getenv("CSV_FILE_FINAL", "info-voturi/pv_part_cntry_prsd.csv")
CSV_FILE_EARLY = os.getenv("CSV_FILE_EARLY", "info-voturi/presence_2025-05-04_21-00.csv")
OUT_FILE = os.getenv("OUT_FILE", "harti/prezentatarzie-uat-XXXX-YYYY.svg")

SIRUTA_FIELD_FINAL = os.getenv("SIRUTA_FIELD_FINAL", "uat_siruta")
VOTED_FIELD_FINAL = os.getenv("VOTED_FIELD_FINAL", "b")
SIRUTA_FIELD_EARLY = os.getenv("SIRUTA_FIELD_EARLY", "Siruta")
VOTED_FIELD_EARLY = os.getenv("VOTED_FIELD_EARLY", "LT")

TICKS_MIN_DISTANCE = float(os.getenv("TICKS_MIN_DISTANCE", "0.5"))

COLOR_SCHEME = os.getenv("COLOR_SCHEME", "cool")
FONT_FAMILY = os.getenv("FONT_FAMILY", '"DejaVu Sans", sans-serif')

MAP_TITLE_X = int(os.getenv("MAP_TITLE_X", "2580"))
MAP_TITLE_Y = int(os.getenv("MAP_TITLE_Y", "20"))
MAP_TITLE = os.getenv("MAP_TITLE", "Numărul de voturi exprimate\ndupă ora 21 (închiderea\nnormală a urnelor) per UAT\nla alegerile prezidențiale\ndin 2025, turul 1").splitlines()

LEGEND_X = int(os.getenv("LEGEND_X", "750"))
LEGEND_Y = int(os.getenv("LEGEND_Y", "90"))
LEGEND_SCALE = float(os.getenv("LEGEND_SCALE", "3.5"))


def color_to_rgb(color):
    return f"rgb({int(color[0] * 255)}, {int(color[1] * 255)}, {int(color[2] * 255)})"


def get_ticks(data_max, ticks_end_min_distance=TICKS_MIN_DISTANCE):
    ticks = []
    power10 = 1
    while power10 < data_max:
        for sub_elem in [1, 2, 5]:
            tick = sub_elem * power10
            if tick > data_max:
                break
            ticks.append(tick)
        power10 *= 10
    ticks.append(data_max)

    delta = ticks[-1] - ticks[-2]
    if delta / (10 ** log10(delta)) < ticks_end_min_distance:
        ticks.pop(-2)
    return ticks


data = defaultdict(lambda: [0, 0])

with open(CSV_FILE_FINAL, "r", encoding="utf-8-sig") as final_file, open(CSV_FILE_EARLY, "r", encoding="utf-8-sig") as early_file:
    final_data = csv.DictReader(final_file)
    early_data = csv.DictReader(early_file)

    for row in final_data:
        siruta = row[SIRUTA_FIELD_FINAL]
        if int(siruta) == 9999:
            continue

        data[siruta][0] += int(row[VOTED_FIELD_FINAL])

    for row in early_data:
        siruta = row[SIRUTA_FIELD_EARLY]
        if int(siruta) == 9999:
            continue

        data[siruta][1] += int(row[VOTED_FIELD_EARLY])

data = {d: data[d][0] - data[d][1] for d in data}
data_arr = list(data.values())
data_max = max(data_arr)
data_min = min(data_arr)

with open(SVG_IN, "r") as file:
    svg_base = file.read()

color_mapping = cm.ScalarMappable(norm=LogNorm(1, data_max), cmap=plt.get_cmap(COLOR_SCHEME))
new_styles = ""
for siruta in data:
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
svg_defs += f'<text font-family=\'{FONT_FAMILY}\' font-weight="bold" dominant-baseline="hanging" text-anchor="middle" x="{MAP_TITLE_X}" y="{MAP_TITLE_Y}" font-size="50">'
first_line = True
for title_line in MAP_TITLE:
    svg_defs += f'<tspan x="{MAP_TITLE_X}" dy="{"0em" if first_line else "1.2em"}">{title_line}</tspan>'
    first_line = False
svg_defs += '</text>'

im = plt.pcolor([[1, data_max]], cmap=COLOR_SCHEME, norm=LogNorm(1, data_max))
plt.gca().set_visible(False)
colorbar = plt.colorbar(im)
ticks = get_ticks(data_max)
colorbar.set_ticks(ticks)
colorbar.set_ticklabels(ticks)

svg_content = StringIO()
plt.savefig(svg_content, format="svg", bbox_inches="tight", pad_inches=0)
svg_content.seek(0)

svg_data = svg_content.read()
svg_content.close()

svg_xml = ElementTree.fromstring(svg_data)
graph = svg_xml.find(".//*[@id='axes_1']")
graph.set("transform", f"scale({LEGEND_SCALE} {LEGEND_SCALE}) translate({LEGEND_X} {LEGEND_Y})")
svg_defs += ElementTree.tostring(graph, encoding="unicode")

final_svg = svg_base.replace("</style>", new_styles + "</style>" + svg_defs)
with open(OUT_FILE, "w") as file:
    print(final_svg, file=file)
subprocess.run(["./text-to-path.sh", OUT_FILE])
