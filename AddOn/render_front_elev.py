"""Front-wall elevation (native frame) to verify the slider switch + the new
under-window outlet. freecadcmd render_front_elev.py -> front_elev.png
Looks at the room-facing side of Wall_Front (native Y~0), up = +Z."""
import os, math
import numpy as np
from PIL import Image
import FreeCAD as App

R = "/home/joee/github/alieniron/home-cad"
fd = App.openDocument(os.path.join(R, "AddOn/AddOn_Framing.FCStd"))
ed = App.openDocument(os.path.join(R, "AddOn/AddOn_Electrical.FCStd"))

TAN = np.array([200, 175, 130], float)
RED = np.array([210, 60, 50], float)
BLU = np.array([90, 140, 200], float)

tris = []


def add(shp, col):
    vs, fs = shp.tessellate(2.0)
    Pn = np.array([[v.x, v.y, v.z] for v in vs], float)
    for f in fs:
        tris.append((Pn[list(f)], col))


# front wall framing only
for o in fd.Objects:
    if o.Name == "Wall_Front":
        add(o.Shape, TAN)

# front-wall electrical devices (native Y near 0)
for o in ed.Objects:
    if o.TypeId != "App::Link":
        continue
    bb = o.Shape.BoundBox
    if -120 < bb.YMin < 120:
        col = BLU if o.Name.startswith("Switch") else RED
        add(o.Shape, col)

allp = np.vstack([t[0] for t in tris])
center = (allp.max(0) + allp.min(0)) / 2.0


def n(v):
    return v / np.linalg.norm(v)

# view the room-facing (-Y) side head-on, up = +Z
view = n(np.array([0.0, 1.0, 0.0]))
up = np.array([0, 0, 1.0])
right = n(np.cross(view, up))
tup = n(np.cross(right, view))

W, H = 2000, 700


def proj(p):
    d = p - center
    return np.array([d @ right, d @ tup, d @ view])

pr = [(np.array([proj(v) for v in tri]), c) for tri, c in tris]
sx = np.array([p[:, 0] for p, _ in pr]).ravel()
sy = np.array([p[:, 1] for p, _ in pr]).ravel()
m = 40
scale = min((W - 2*m)/(sx.max()-sx.min()), (H - 2*m)/(sy.max()-sy.min()))
ox = W/2 - scale*(sx.max()+sx.min())/2
oy = H/2 + scale*(sy.max()+sy.min())/2
img = np.full((H, W, 3), 255, float)
zb = np.full((H, W), 1e18, float)
for p, col in pr:
    a, b, c = p
    nz = np.cross(b-a, c-a); nn = np.linalg.norm(nz)
    if nn == 0:
        continue
    nz = nz/nn
    if nz[2] < 0:
        nz = -nz
    inten = min(1.0, 0.4 + 0.6*max(0.15, abs(nz[1])))
    shade = np.clip(col*inten, 0, 255)
    xs = ox + scale*p[:, 0]; ys = oy - scale*p[:, 1]; zs = p[:, 2]
    x0 = int(max(0, math.floor(xs.min()))); x1 = int(min(W-1, math.ceil(xs.max())))
    y0 = int(max(0, math.floor(ys.min()))); y1 = int(min(H-1, math.ceil(ys.max())))
    if x1 < x0 or y1 < y0:
        continue
    ax, ay = xs[0], ys[0]; bx, by = xs[1], ys[1]; cx, cy = xs[2], ys[2]
    det = (by-cy)*(ax-cx) + (cx-bx)*(ay-cy)
    if abs(det) < 1e-9:
        continue
    yy, xx = np.mgrid[y0:y1+1, x0:x1+1]
    l1 = ((by-cy)*(xx-cx)+(cx-bx)*(yy-cy))/det
    l2 = ((cy-ay)*(xx-cx)+(ax-cx)*(yy-cy))/det
    l3 = 1-l1-l2
    ins = (l1 >= -0.002) & (l2 >= -0.002) & (l3 >= -0.002)
    if not ins.any():
        continue
    z = l1*zs[0] + l2*zs[1] + l3*zs[2]
    sz = zb[y0:y1+1, x0:x1+1]; cl = ins & (z < sz); sz[cl] = z[cl]
    si = img[y0:y1+1, x0:x1+1]; si[cl] = shade
Image.fromarray(img.astype(np.uint8)).save(os.path.join(R, "AddOn/front_elev.png"))
print("FRONT_ELEV_DONE", len(tris))
