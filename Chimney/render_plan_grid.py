"""Top-down orthographic plan of the House in TRUE world coords with a labelled
1000 mm grid, so locations can be read directly. freecadcmd render_plan_grid.py
-> plan_grid.png.  World X -> screen X (right), world Y -> screen Y (down)."""
import os, math
import numpy as np
from PIL import Image, ImageDraw
import FreeCAD as App

R = "/home/joee/github/alieniron/home-cad"
doc = App.openDocument(os.path.join(R, "House/House.FCStd"))

SKIP = ("Origin", "Axis", "Plane", "Joint", "Assembly", "Ground",
        "MainRoof", "RoofFrame", "RoofConnector",
        "SubFloor", "Body001", "Body002")   # hide floor slabs so joists/walls show


def colof(nm):
    if nm == "Chimney":
        return (220, 40, 40)
    if nm in ("Tub_InteriorBath", "Toilet_NorthBath", "Toilet_InteriorBath",
              "Sink", "LaundrySink", "Washer", "Dryer", "Dishwasher"):
        return (40, 160, 210)
    if nm.startswith("Deck") or nm == "Deck":
        return (150, 110, 70)
    if "Framing" in nm or nm.startswith(("SubFloor", "Body", "Beams", "Floor")):
        return (90, 90, 95)
    return (170, 175, 180)


# world view window
X0, X1 = -1500.0, 18500.0
Y0, Y1 = -1500.0, 19000.0
SC = 0.09          # px per mm
Wd = int((X1 - X0) * SC)
Hh = int((Y1 - Y0) * SC)


def sx(x):
    return (X1 - x) * SC          # FLIP X: high world-X (South) -> screen left


def sy(y):
    return (y - Y0) * SC


img = np.full((Hh, Wd, 3), 255, float)
zb = np.full((Hh, Wd), -1e18, float)   # keep HIGHEST z (top-down)

for o in doc.Objects:
    nm = o.Name
    if any(s in nm for s in SKIP):
        continue
    sh = getattr(o, "Shape", None)
    if sh is None or sh.isNull() or not sh.Faces:
        continue
    col = np.array(colof(nm), float)
    try:
        vs, fs = sh.tessellate(8.0)
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
# grid every 1000 mm
for gx in range(-1000, 19000, 1000):
    px = int(sx(gx))
    if 0 <= px < Wd:
        dr.line([(px, 0), (px, Hh)], fill=(210, 210, 235), width=1)
        dr.text((px + 2, 2), str(gx), fill=(60, 60, 140))
for gy in range(-1000, 19000, 1000):
    py = int(sy(gy))
    if 0 <= py < Hh:
        dr.line([(0, py), (Wd, py)], fill=(210, 210, 235), width=1)
        dr.text((2, py + 1), str(gy), fill=(60, 60, 140))
dr.text((Wd - 200, Hh - 20), "X->left(South) Y->down(East)  [matches screenshot]", fill=(0, 0, 0))
pim.save(os.path.join(R, "Chimney/plan_grid.png"))
print("PLAN_GRID_DONE")
