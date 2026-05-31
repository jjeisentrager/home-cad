# -*- coding: utf-8 -*-
"""ViWinTech ThruBlack Picture window (fixed, brick-mould, 2 7/8" frame).
Callout PW4848 = 48" x 48" rough opening. Direct-glazed fixed lite.
Run headless:  freecadcmd build_window.py
"""
import os
import sys

OUT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(OUT))  # Library/ on path
import thrublack_lib as tb

RO_W, RO_H = 48, 48          # callout = rough opening, inches
DOCNAME = "ThruBlack_PW4848"

tb.build("picture", RO_W, RO_H, OUT, DOCNAME)
