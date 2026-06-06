# -*- coding: utf-8 -*-
"""ViWinTech ThruBlack 3-Lite Glider windows (XOX, brick-mould, 2 7/8" frame).
25-50-25 split: operable left/right sashes (X) flank a fixed centre lite (O).
Builds common wide callouts; each is written to its own sub-folder.
Callout = rough opening, inches. These wide units are representative common
sizes (custom widths available). Run headless:  freecadcmd build_window.py
"""
import os
import sys

OUT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(OUT))  # Library/ViWinTech/ThruBlack on path
import thrublack_lib as tb

STYLE = "glider3"
SIZES = [               # (RO_W, RO_H, model)
    (72, 48, "3LG7248"),
    (84, 48, "3LG8448"),
    (96, 48, "3LG9648"),
    (96, 60, "3LG9660"),
    (108, 48, "3LG10848"),
]

for w, h, name in SIZES:
    d = os.path.join(OUT, name)
    if not os.path.isdir(d):
        os.makedirs(d)
    tb.build(STYLE, w, h, d, "ThruBlack_" + name)
