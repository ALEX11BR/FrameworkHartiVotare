#!/usr/bin/env python3

import json
from math import ceil


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


with open("ro-comune-simplificate.geojson", "r") as file:
    geojson = json.load(file)
with open("ro-judete-simplificate.geojson", "r") as file:
    geojson_judete = json.load(file)

geojson_range = CoordRange(min([p[0] for f in geojson["features"]
                               for pp in f["geometry"]["coordinates"] for p in pp[0]]),
                           min([p[1] for f in geojson["features"]
                               for pp in f["geometry"]["coordinates"] for p in pp[0]]),
                           max([p[0] for f in geojson["features"]
                               for pp in f["geometry"]["coordinates"] for p in pp[0]]),
                           max([p[1] for f in geojson["features"]
                               for pp in f["geometry"]["coordinates"] for p in pp[0]]))
MAP_BUFFER = 10
map_range = CoordRange(MAP_BUFFER, MAP_BUFFER, MAP_BUFFER + 6000, MAP_BUFFER + 6000 / (
    geojson_range.end_x - geojson_range.start_x) * (geojson_range.end_y - geojson_range.start_y))

print(f'<svg width="{map_range.end_x + MAP_BUFFER}" height="{
      ceil(map_range.end_y) + MAP_BUFFER}" xmlns="http://www.w3.org/2000/svg">')
print("""<style>
    .judet {
        fill: none;
        stroke: black;
        stroke-width: 5px;
    }
    .uat {
        fill: grey;
        stroke: black;
        stroke-width: 3px;
    }
</style>""")

for feature in filter(lambda f: True, geojson["features"]):
    print(
        f'<path class="uat" id="uat-{feature["properties"]["natCode"]}" d="', end="")
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
    print(f'"><title>{feature["properties"]["name"]}</title></path>')

for feature in geojson_judete["features"]:
    print(
        f'<path class="judet" id="judet-{feature["properties"]["judet"]}" d="', end="")
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
