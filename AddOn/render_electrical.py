"""Render AddOn_Assembly walls + openings + electrical devices to check placement.
freecadcmd render_electrical.py"""
import os, math
import numpy as np
from PIL import Image
import FreeCAD as App
R = "/home/joee/github/alieniron/home-cad"
doc = App.openDocument(os.path.join(R, "AddOn/AddOn_Assembly.FCStd"))

RED = np.array([210, 60, 50], float)      # electrical
TAN = np.array([200, 175, 130], float)    # framing
BLUE = np.array([120, 160, 200], float)   # windows/slider

INCLUDE_PREFIX = ("AddOnFraming", "Electrical", "Window", "Slider")
tris = []
for o in doc.Objects:
    nm = o.Name
    lbl = o.Label
    if not any((nm.startswith(p) or lbl.startswith(p)) for p in INCLUDE_PREFIX):
        continue
    sh = getattr(o, "Shape", None)
    if sh is None or sh.isNull():
        continue
    if nm.startswith("Electrical") or lbl.startswith(("Electrical", "Outlet", "Switch")):
        col = RED
    elif nm.startswith("Window") or lbl.startswith(("Window", "Slider")):
        col = BLUE
    else:
        col = TAN
    try:
        vs, fs = sh.tessellate(3.0)
    except Exception:
        continue
    Pn = np.array([[v.x, v.y, v.z] for v in vs], float)
    for f in fs:
        tris.append((Pn[list(f)], col))

def n(v): return v / np.linalg.norm(v)
allp = np.vstack([t[0] for t in tris]); center = (allp.max(0) + allp.min(0)) / 2.0
def render(view, up, fname, W=1700, H=1100):
    view = n(view); right = n(np.cross(view, up)); tup = n(np.cross(right, view))
    def proj(p): d = p - center; return np.array([d @ right, d @ tup, d @ view])
    pr = [(np.array([proj(v) for v in tri]), c) for tri, c in tris]
    sx = np.array([p[:, 0] for p, _ in pr]).ravel(); sy = np.array([p[:, 1] for p, _ in pr]).ravel()
    m = 60; scale = min((W - 2*m)/(sx.max()-sx.min()), (H - 2*m)/(sy.max()-sy.min()))
    ox = W/2 - scale*(sx.max()+sx.min())/2; oy = H/2 + scale*(sy.max()+sy.min())/2
    img = np.full((H, W, 3), 255, float); zb = np.full((H, W), 1e18, float)
    for p, col in pr:
        a, b, c = p; nz = np.cross(b-a, c-a); nn = np.linalg.norm(nz)
        if nn == 0: continue
        nz = nz/nn
        if nz[2] < 0: nz = -nz
        inten = min(1.0, 0.34 + 0.7*max(0.12, abs(nz[2]))); shade = np.clip(col*inten, 0, 255)
        xs = ox + scale*p[:, 0]; ys = oy - scale*p[:, 1]; zs = p[:, 2]
        x0 = int(max(0, math.floor(xs.min()))); x1 = int(min(W-1, math.ceil(xs.max())))
        y0 = int(max(0, math.floor(ys.min()))); y1 = int(min(H-1, math.ceil(ys.max())))
        if x1 < x0 or y1 < y0: continue
        ax, ay = xs[0], ys[0]; bx, by = xs[1], ys[1]; cx, cy = xs[2], ys[2]
        det = (by-cy)*(ax-cx) + (cx-bx)*(ay-cy)
        if abs(det) < 1e-9: continue
        yy, xx = np.mgrid[y0:y1+1, x0:x1+1]
        l1 = ((by-cy)*(xx-cx)+(cx-bx)*(yy-cy))/det; l2 = ((cy-ay)*(xx-cx)+(ax-cx)*(yy-cy))/det; l3 = 1-l1-l2
        ins = (l1 >= -0.002) & (l2 >= -0.002) & (l3 >= -0.002)
        if not ins.any(): continue
        z = l1*zs[0] + l2*zs[1] + l3*zs[2]
        sz = zb[y0:y1+1, x0:x1+1]; cl = ins & (z < sz); sz[cl] = z[cl]
        si = img[y0:y1+1, x0:x1+1]; si[cl] = shade
    Image.fromarray(img.astype(np.uint8)).save(os.path.join(R, fname))

# AddOn_Assembly frame: vertical (room up) = +Y(assembly).  Up = +Y.
render(np.array([0.55, -0.55, 0.62]), np.array([0, 1.0, 0]), "AddOn/electrical_iso.png")
open(os.path.join(R, "AddOn/_elec_render.txt"), "w").write("DONE tris=%d\n" % len(tris))
print("RENDER_DONE", len(tris))
