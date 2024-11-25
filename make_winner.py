#!/usr/bin/env python3

import csv
from collections import defaultdict
import json
from math import ceil
import os


INPUT_GEOJSON = os.getenv("INPUT_FILE", "ro-comune-simplificate.geojson")
OUTPUT_GEOJSON = os.getenv("OUTPUT_FILE", "comune-WIN.geojson")

CSV_FILE = os.getenv("CSV_FILE", "pv_part_cntry_prsd.csv")

SIRUTA_FIELD = os.getenv("SIRUTA_FIELD", "uat_siruta")
REGISTERED_FIELD = os.getenv("REGISTERED_FIELD", "Înscriși pe liste permanente")
VOTED_FIELD = os.getenv("VOTED_FIELD", "LT")

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

with open(INPUT_GEOJSON, "r") as file:
    geojson = json.load(file)

for feature in geojson["features"]:
    max_votes = -1
    winner = "eq"
    for c in candidates:
        if data[feature["properties"]["natCode"]][c] == max_votes:
            winner = "eq"
        if data[feature["properties"]["natCode"]][c] > max_votes:
            max_votes = data[feature["properties"]["natCode"]][c]
            winner = c.removesuffix("-voturi")
    feature["properties"]["WIN"] = winner

with open(OUTPUT_GEOJSON, "w") as file:
    json.dump(geojson, file)
