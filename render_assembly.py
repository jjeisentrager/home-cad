# -*- coding: utf-8 -*-
"""Offscreen-GUI software render of the kitchen assembly using each object's
REAL ShapeColor (read via ViewObject), so we see what actually displays."""
import os, math
import numpy as np
from PIL import Image
import FreeCAD as App
import FreeCADGui as Gui  # noqa

H = "/home/joee/github/alieniron/home-cad/"
KIT = H + "Kitchen/"
adoc = App.openDocument(KIT + "Kitchen_Assembly.FCStd")
adoc.recompute()

def col_of(o):
    vo = getattr(o, "ViewObject", None)
    if vo is None:
        return np.array([180, 185, 190], float)
    c = vo.ShapeColor
    return np.array([c[0] * 255, c[1] * 255, c[2] * 255], float)

tris = []
for link in adoc.Objects:
    if link.TypeId != "App::Link":
        continue
    lp = link.LinkedObject
    lm = link.Placement.Matrix
    if not hasattr(lp, "Group"):
        continue
    for ch in lp.Group:
        sh = getattr(ch, "Shape", None)
        if sh is None or not getattr(ch, "Visibility", True):
            continue
        if sh.Faces == []:
            continue
        col = col_of(ch)
        try:
            vs, fs = sh.tessellate(2.0)
        except Exception:
            continue
        P = []
        for v in vs:
            w = lm.multiply(App.Vector(v.x, v.y, v.z))
            P.append([w.x, w.y, w.z])
        P = np.array(P, float)
        for f in fs:
            tris.append((P[list(f)], col))

print("TRIS", len(tris))

def n(v): return v / np.linalg.norm(v)
view = n(np.array([0.55, 0.85, -0.5]))   # look toward -X,-Y from above-ish
up = np.array([0, 0, 1.0])
right = n(np.cross(view, up))
tup = n(np.cross(right, view))
allp = np.vstack([t[0] for t in tris])
center = (allp.max(0) + allp.min(0)) / 2.0
def project(p):
    d = p - center
    return np.array([d @ right, d @ tup, d @ view])

W, Hh = 1400, 1000
proj = [(np.array([project(v) for v in tri]), col) for tri, col in tris]
sx = np.array([p[:, 0] for p, _ in proj]).ravel()
sy = np.array([p[:, 1] for p, _ in proj]).ravel()
margin = 40
scale = min((W - 2*margin)/(sx.max()-sx.min()), (Hh - 2*margin)/(sy.max()-sy.min()))
ox = W/2 - scale*(sx.max()+sx.min())/2
oy = Hh/2 + scale*(sy.max()+sy.min())/2
img = np.full((Hh, W, 3), 245, float)
zbuf = np.full((Hh, W), 1e18, float)
for p, col in proj:
    a, b, c = p
    nz = np.cross(b-a, c-a); nn = np.linalg.norm(nz)
    if nn == 0: continue
    nz = nz/nn
    if nz[2] < 0: nz = -nz
    inten = min(1.0, 0.35 + 0.7*max(0.12, nz[2]))
    shade = np.clip(col*inten, 0, 255)
    xs = ox + scale*p[:,0]; ys = oy - scale*p[:,1]; zs = p[:,2]
    x0 = int(max(0, math.floor(xs.min()))); x1 = int(min(W-1, math.ceil(xs.max())))
    y0 = int(max(0, math.floor(ys.min()))); y1 = int(min(Hh-1, math.ceil(ys.max())))
    if x1 < x0 or y1 < y0: continue
    ax, ay = xs[0], ys[0]; bx, by = xs[1], ys[1]; cx, cy = xs[2], ys[2]
    det = (by-cy)*(ax-cx) + (cx-bx)*(ay-cy)
    if abs(det) < 1e-9: continue
    yy, xx = np.mgrid[y0:y1+1, x0:x1+1]
    l1 = ((by-cy)*(xx-cx)+(cx-bx)*(yy-cy))/det
    l2 = ((cy-ay)*(xx-cx)+(ax-cx)*(yy-cy))/det
    l3 = 1-l1-l2
    inside = (l1>=-0.001)&(l2>=-0.001)&(l3>=-0.001)
    if not inside.any(): continue
    z = l1*zs[0]+l2*zs[1]+l3*zs[2]
    sub_z = zbuf[y0:y1+1, x0:x1+1]
    closer = inside & (z < sub_z)
    sub_z[closer] = z[closer]
    sub_img = img[y0:y1+1, x0:x1+1]
    sub_img[closer] = shade
Image.fromarray(img.astype(np.uint8)).save(H + "assembly_shot.png")
print("SW_RENDER_DONE")
