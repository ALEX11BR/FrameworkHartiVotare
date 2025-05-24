#!/usr/bin/env python3

import json
from math import ceil
import os


UNITS_GEOJSON = os.getenv("UNITS_GEOJSON", "ro-comune-simplificate-2025.geojson")
COUNTIES_GEOJSON = os.getenv("COUNTIES_GEOJSON", "ro-judete-simplificate-2025.geojson")
MAP_WIDTH = int(os.getenv("MAP_WIDTH", "3000"))
MAP_BUFFER = int(os.getenv("MAP_BUFFER", "10"))


class CoordRange:
    def __init__(self, start_x, start_y, end_x, end_y):
        self.start_x = start_x
        self.start_y = start_y
        self.end_x = end_x
        self.end_y = end_y


def convert_between_ranges(point, from_range: CoordRange, to_range: CoordRange):
    x = (point[0] - from_range.start_x) / (from_range.end_x -
                                           from_range.start_x) * (to_range.end_x - to_range.start_x) + to_range.start_x
    y = (point[1] - from_range.start_y) / (from_range.end_y -
                                           from_range.start_y) * (to_range.end_y - to_range.start_y) + to_range.start_y

    return [x, y]


def feature_title(feature):
    ans = feature["properties"]["name"]
    if feature["properties"]["natLevName"] not in ["Sectoarele municipiului Bucuresti"]:
        ans += f' ({feature["properties"]["countyName"]})'
    return ans


with open(UNITS_GEOJSON, "r") as file:
    geojson = json.load(file)
with open(COUNTIES_GEOJSON, "r") as file:
    geojson_judete = json.load(file)

geojson_range = CoordRange(min([p[0] for f in geojson["features"]
                               for pp in f["geometry"]["coordinates"] for p in pp[0]]),
                           min([p[1] for f in geojson["features"]
                               for pp in f["geometry"]["coordinates"] for p in pp[0]]),
                           max([p[0] for f in geojson["features"]
                               for pp in f["geometry"]["coordinates"] for p in pp[0]]),
                           max([p[1] for f in geojson["features"]
                               for pp in f["geometry"]["coordinates"] for p in pp[0]]))
map_range = CoordRange(MAP_BUFFER, MAP_BUFFER, MAP_BUFFER + MAP_WIDTH, MAP_BUFFER + MAP_WIDTH / (
    geojson_range.end_x - geojson_range.start_x) * (geojson_range.end_y - geojson_range.start_y))

print(f'<svg width="{map_range.end_x + MAP_BUFFER}" height="{
      ceil(map_range.end_y) + MAP_BUFFER}" xmlns="http://www.w3.org/2000/svg">')
print("""<style>
    .judet {
        fill: none;
        stroke: black;
        stroke-width: 2.5px;
        stroke-linejoin: round;
    }
    .uat {
        fill: grey;
        stroke: black;
        stroke-width: 1.5px;
        stroke-linejoin: round;
    }
</style>""")

print(f'<rect x="0" y="0" fill="white" width="{map_range.end_x + MAP_BUFFER}" height="{
    ceil(map_range.end_y) + MAP_BUFFER}"/>')
for feature in geojson["features"]:
    print(
        f'<path id="uat-{feature["properties"]["natCode"]}" class="uat" d="', end="")
    # c1 = poligoanele distincte ce alcătuiesc un UAT
    for c1 in feature["geometry"]["coordinates"]:
        for c2 in c1:  # c2 = [poligon extern, eventuale găuri...]
            c = "M"
            for c3 in c2:  # c3 = [puncte din poligon]
                point = convert_between_ranges(c3, geojson_range, map_range)
                point[1] = map_range.end_y - point[1] + MAP_BUFFER
                print(f"{c}{point[0]:.2f},{point[1]:.2f} ", end="")
                c = "L"
            print("Z ", end="")
    print(f'"><title>{feature_title(feature)}</title></path>')

for feature in geojson_judete["features"]:
    print(f'<path class="judet" d="', end="")
    # c1 = poligoanele distincte ce alcătuiesc un UAT
    for c1 in feature["geometry"]["coordinates"]:
        for c2 in c1:  # c2 = [poligon extern, eventuale găuri...]
            c = "M"
            for c3 in c2:  # c3 = [puncte din poligon]
                point = convert_between_ranges(c3, geojson_range, map_range)
                point[1] = map_range.end_y - point[1] + MAP_BUFFER
                print(f"{c}{point[0]:.2f},{point[1]:.2f} ", end="")
                c = "L"
            print("Z ", end="")
    print(f'"/>')

print("</svg>")
