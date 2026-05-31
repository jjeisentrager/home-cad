# -*- coding: utf-8 -*-
"""ViWinTech ThruBlack 3-Lite Glider window (XOX, brick-mould, 2 7/8" frame).
Callout 3LG9648 = 96" x 48" rough opening. 25-50-25 split: operable left and
right sashes (X) flanking a fixed centre lite (O).
Run headless:  freecadcmd build_window.py
"""
import os
import sys

OUT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(OUT))  # Library/ on path
import thrublack_lib as tb

RO_W, RO_H = 96, 48          # callout = rough opening, inches
DOCNAME = "ThruBlack_3LG9648"

tb.build("glider3", RO_W, RO_H, OUT, DOCNAME)
