#!/usr/bin/env sh

inkscape "$1" --export-text-to-path --export-plain-svg="$1"
