# -*- coding: utf-8 -*-
"""ViWinTech ThruBlack Grand Vista Traditional Sliding Door (2-panel XO bypass,
brick-mould, 3/4" insulated glass). Left panel operable (X), right fixed (O) as
viewed from outside. Builds common patio-door callouts; each is written to its
own sub-folder. Callout = rough opening, inches (WWHH).
Change SIZES to add more. Run headless:  freecadcmd build_door.py
"""
import os
import sys

OUT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(OUT))   # Library/ViWinTech/ThruBlack on path
import thrublack_door_lib as td

STYLE = "traditional_sliding"
SIZES = [                  # (RO_W, RO_H, panels, model)
    (60, 80, 2, "GVTS6080"),
    (72, 80, 2, "GVTS7280"),
    (96, 80, 2, "GVTS9680"),
    (72, 96, 2, "GVTS7296"),
    (96, 96, 2, "GVTS9696"),
]

for w, h, p, name in SIZES:
    d = os.path.join(OUT, name)
    if not os.path.isdir(d):
        os.makedirs(d)
    td.build(STYLE, w, h, p, d, "ThruBlack_" + name)
