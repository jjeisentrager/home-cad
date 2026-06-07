# -*- coding: utf-8 -*-
"""ViWinTech ThruBlack Grand Vista French Sliding Door (wide-stile "French" look
on a bypass slider, brick-mould, 3/4" insulated glass). Up to 8 ft tall and up
to 4 panels wide; 2-panel XO, 3-panel XOX, 4-panel OXXO. Operable panels (X)
ride the interior track. Each callout is written to its own sub-folder.
Callout = rough opening, inches; multi-panel models carry a _#P suffix.
Change SIZES to add more. Run headless:  freecadcmd build_door.py
"""
import os
import sys

OUT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(OUT))   # Library/ViWinTech/ThruBlack on path
import thrublack_door_lib as td

STYLE = "french_sliding"
SIZES = [                  # (RO_W, RO_H, panels, model)
    (72, 80, 2, "GVFS7280"),
    (96, 96, 2, "GVFS9696"),
    (108, 96, 3, "GVFS10896_3P"),
    (144, 96, 4, "GVFS14496_4P"),
    (192, 96, 4, "GVFS19296_4P"),
]

for w, h, p, name in SIZES:
    d = os.path.join(OUT, name)
    if not os.path.isdir(d):
        os.makedirs(d)
    td.build(STYLE, w, h, p, d, "ThruBlack_" + name)
