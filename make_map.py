#!/usr/bin/env python3

import csv
from collections import defaultdict
from math import floor
import os

import matplotlib.pyplot as plt

CSV_FILE = os.getenv("CSV_FILE", "presence_2024-11-25_07-00.csv")
OUT_FILE = os.getenv("OUT_FILE", "prezenta-uat.svg")

SIRUTA_FIELD = os.getenv("SIRUTA_FIELD", "Siruta")
REGISTERED_FIELD = os.getenv("REGISTERED_FIELD", "Înscriși pe liste permanente")
VOTED_FIELD = os.getenv("VOTED_FIELD", "LT")


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

with open("romania-uat.svg", "r") as file:
    svg_base = file.read()

new_styles = ""
for siruta in data:
    cmap = plt.get_cmap("gist_rainbow")

    color = cmap((data[siruta] - data_min) / (data_max - data_min) * 1)

    new_styles += """
        #uat-%d {
            fill: %s;
        }
    """ % (int(siruta), color_to_rgb(color))

final_svg = svg_base.replace("</style>", new_styles + "</style>")
with open(OUT_FILE, "w") as file:
    print(final_svg, file=file)

im = plt.imshow([list(data.values())] * len(data), cmap="gist_rainbow")
colorbar = plt.colorbar(im)
ticks = [data_min] + list(range((int(data_min) // 10 + 1) * 10, int(data_max), 10)) + [data_max]
colorbar.set_ticks(ticks)
colorbar.set_ticklabels([f"{i:.1f}%" for i in ticks])
plt.show()
