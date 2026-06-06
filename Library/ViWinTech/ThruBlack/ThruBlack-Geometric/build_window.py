# -*- coding: utf-8 -*-
"""ViWinTech ThruBlack Geometric windows (half-round, brick-mould frame).
Flat bottom, round top, fixed. The geometric style covers special shapes; this
builds the common half-round in several widths (height = width / 2). Each is
written to its own sub-folder. Run headless:  freecadcmd build_window.py
"""
import os
import sys

OUT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(OUT))  # Library/ViWinTech/ThruBlack on path
import thrublack_lib as tb

STYLE = "geometric"
SIZES = [               # (RO_W, RO_H, model)  half-round: H = W / 2
    (24, 12, "HR24"),
    (36, 18, "HR36"),
    (48, 24, "HR48"),
    (60, 30, "HR60"),
    (72, 36, "HR72"),
]

for w, h, name in SIZES:
    d = os.path.join(OUT, name)
    if not os.path.isdir(d):
        os.makedirs(d)
    tb.build(STYLE, w, h, d, "ThruBlack_" + name)
