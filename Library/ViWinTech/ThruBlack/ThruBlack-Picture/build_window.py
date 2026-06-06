# -*- coding: utf-8 -*-
"""ViWinTech ThruBlack Picture windows (fixed, brick-mould, 2 7/8" frame).
Direct-glazed fixed lite. Builds common callouts from the picture-window grid;
each is written to its own sub-folder. Callout = rough opening, inches.
Change SIZES to add more from the grid. Run headless:  freecadcmd build_window.py
"""
import os
import sys

OUT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(OUT))  # Library/ViWinTech/ThruBlack on path
import thrublack_lib as tb

STYLE = "picture"
SIZES = [               # (RO_W, RO_H, model)
    (24, 24, "PW2424"),
    (36, 36, "PW3636"),
    (48, 48, "PW4848"),
    (60, 48, "PW6048"),
    (60, 60, "PW6060"),
]

for w, h, name in SIZES:
    d = os.path.join(OUT, name)
    if not os.path.isdir(d):
        os.makedirs(d)
    tb.build(STYLE, w, h, d, "ThruBlack_" + name)
