# -*- coding: utf-8 -*-
"""ViWinTech ThruBlack Single Glider windows (XO, brick-mould, 2 7/8" frame).
Left sash operable (X), right sash stationary (O), viewed from outside. Builds
common callouts from the glider grid (widths 24-72", heights 24-48"); each is
written to its own sub-folder. Callout = rough opening, inches.
Change SIZES to add more from the grid. Run headless:  freecadcmd build_window.py
"""
import os
import sys

OUT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(OUT))  # Library/ViWinTech/ThruBlack on path
import thrublack_lib as tb

STYLE = "glider"
SIZES = [               # (RO_W, RO_H, model)
    (36, 24, "SG3624"),
    (48, 36, "SG4836"),
    (60, 36, "SG6036"),
    (60, 48, "SG6048"),
    (72, 48, "SG7248"),
]

for w, h, name in SIZES:
    d = os.path.join(OUT, name)
    if not os.path.isdir(d):
        os.makedirs(d)
    tb.build(STYLE, w, h, d, "ThruBlack_" + name)
