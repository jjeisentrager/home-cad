"""Top-down plan of ONLY the main-floor framing (walls) + chimney, with a world
1000 mm grid, oriented to match chimney-location.png (X->left=South, Y->down=East).
freecadcmd render_walls_plan.py -> walls_plan.png"""
import os, math
import numpy as np
from PIL import Image, ImageDraw
import FreeCAD as App

R = "/home/joee/github/alieniron/home-cad"
doc = App.openDocument(os.path.join(R, "House/House.FCStd"))

X0, X1 = -1500.0, 18500.0
Y0, Y1 = -1500.0, 9500.0
SC = 0.11
Wd = int((X1 - X0) * SC)
Hh = int((Y1 - Y0) * SC)


def sx(x):
    return (X1 - x) * SC


def sy(y):
    return (y - Y0) * SC


img = np.full((Hh, Wd, 3), 255, float)
zb = np.full((Hh, Wd), -1e18, float)

for o in doc.Objects:
    nm = o.Name
    keep = ("Framing" in nm) or nm == "Chimney"
    if not keep:
        continue
    sh = getattr(o, "Shape", None)
    if sh is None or sh.isNull() or not sh.Faces:
        continue
    col = np.array((210, 40, 40) if nm == "Chimney" else (70, 70, 78), float)
    try:
        vs, fs = sh.tessellate(5.0)
    except Exception:
        continue
    Pn = np.array([[v.x, v.y, v.z] for v in vs], float)
    for f in fs:
        tri = Pn[list(f)]
        xs = np.array([sx(p[0]) for p in tri])
        ys = np.array([sy(p[1]) for p in tri])
        zs = np.array([p[2] for p in tri])
        x0 = int(max(0, math.floor(xs.min()))); x1 = int(min(Wd-1, math.ceil(xs.max())))
        y0 = int(max(0, math.floor(ys.min()))); y1 = int(min(Hh-1, math.ceil(ys.max())))
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
        ins = (l1 >= -0.02) & (l2 >= -0.02) & (l3 >= -0.02)
        if not ins.any():
            continue
        z = l1*zs[0] + l2*zs[1] + l3*zs[2]
        sub = zb[y0:y1+1, x0:x1+1]
        cl = ins & (z > sub)
        sub[cl] = z[cl]
        img[y0:y1+1, x0:x1+1][cl] = col

pim = Image.fromarray(img.astype(np.uint8))
dr = ImageDraw.Draw(pim)
for gx in range(0, 18000, 1000):
    px = int(sx(gx))
    if 0 <= px < Wd:
        dr.line([(px, 0), (px, Hh)], fill=(200, 200, 230), width=1)
        dr.text((px + 2, 2), str(gx), fill=(60, 60, 140))
for gy in range(0, 9000, 1000):
    py = int(sy(gy))
    if 0 <= py < Hh:
        dr.line([(0, py), (Wd, py)], fill=(200, 200, 230), width=1)
        dr.text((2, py + 1), str(gy), fill=(60, 60, 140))
pim.save(os.path.join(R, "Chimney/walls_plan.png"))
print("WALLS_PLAN_DONE")
