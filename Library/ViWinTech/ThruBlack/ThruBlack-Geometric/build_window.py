# -*- coding: utf-8 -*-
"""ViWinTech ThruBlack Geometric window (half-round, brick-mould frame).
Callout HR48 = 48" wide x 24" tall half-round (flat bottom, round top), fixed.
The geometric style covers special shapes; this builds the common half-round.
Run headless:  freecadcmd build_window.py
"""
import os
import sys

OUT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(OUT))  # Library/ on path
import thrublack_lib as tb

RO_W, RO_H = 48, 24          # half-round: height = width / 2
DOCNAME = "ThruBlack_HR48"

tb.build("geometric", RO_W, RO_H, OUT, DOCNAME)
