# -*- coding: utf-8 -*-
"""ViWinTech ThruBlack Single Hung window (brick-mould, 2 7/8" frame).
Callout SH3252 = 32" x 52" rough opening (top sash fixed, bottom operable).
Run headless:  freecadcmd build_window.py
"""
import os
import sys

OUT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(OUT))  # Library/ on path
import thrublack_lib as tb

RO_W, RO_H = 32, 52          # callout = rough opening, inches
DOCNAME = "ThruBlack_SH3252"

tb.build("single_hung", RO_W, RO_H, OUT, DOCNAME)
