# -*- coding: utf-8 -*-
"""ViWinTech ThruBlack Single Hung windows (brick-mould, 2 7/8" frame).
Top sash fixed, bottom operable. Builds a handful of common callouts from the
brick-mould single-hung grid (widths 19/20-48", heights 36-60"); each callout
is written to its own sub-folder. Callout = rough opening, inches.
Change SIZES to add more from the grid. Run headless:  freecadcmd build_window.py
"""
import os
import sys

OUT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(OUT))  # Library/ViWinTech/ThruBlack on path
import thrublack_lib as tb

STYLE = "single_hung"
SIZES = [               # (RO_W, RO_H, model)
    (24, 36, "SH2436"),
    (28, 52, "SH2852"),
    (30, 48, "SH3048"),
    (32, 52, "SH3252"),
    (36, 60, "SH3660"),
]

for w, h, name in SIZES:
    d = os.path.join(OUT, name)
    if not os.path.isdir(d):
        os.makedirs(d)
    tb.build(STYLE, w, h, d, "ThruBlack_" + name)
