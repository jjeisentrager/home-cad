# -*- coding: utf-8 -*-
"""ViWinTech ThruBlack Single Glider window (XO, brick-mould, 2 7/8" frame).
Callout SG4836 = 48" x 36" rough opening. XO as viewed from outside:
left sash operable (X), right sash stationary (O).
Run headless:  freecadcmd build_window.py
"""
import os
import sys

OUT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(OUT))  # Library/ on path
import thrublack_lib as tb

RO_W, RO_H = 48, 36          # callout = rough opening, inches
DOCNAME = "ThruBlack_SG4836"

tb.build("glider", RO_W, RO_H, OUT, DOCNAME)
