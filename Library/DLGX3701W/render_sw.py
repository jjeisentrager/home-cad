"""Software render of the model (no OpenGL). freecadcmd render_sw.py
Renders the single .FCStd found in this script's folder to preview_iso.png."""
import os, math, glob
import numpy as np
from PIL import Image
import FreeCAD as App

OUT = os.path.dirname(os.path.abspath(__file__))
fc = glob.glob(os.path.join(OUT, "*.FCStd"))[0]
doc = App.openDocument(fc)

WHITE = np.array([238, 238, 240], float)
DARK = np.array([34, 34, 40], float)


def is_dark(nm):
    return any(k in nm for k in ("glass", "display", "handle", "foot", "window"))


tris = []
for o in doc.Objects:
    sh = getattr(o, "Shape", None)
    if sh is None:
        continue
    nm = o.Name.lower()
    col = DARK if is_dark(nm) else WHITE
    vs, fs = sh.tessellate(2.0)
    P = np.array([[v.x, v.y, v.z] for v in vs], float)
    for f in fs:
        tris.append((P[list(f)], col))


def n(v):
    return v / np.linalg.norm(v)

view = n(np.array([-0.55, -1.0, -0.42]))
up = np.array([0, 0, 1.0])
right = n(np.cross(view, up))
tup = n(np.cross(right, view))

allp = np.vstack([t[0] for t in tris])
center = (allp.max(0) + allp.min(0)) / 2.0


def project(p):
    d = p - center
    return np.array([d @ right, d @ tup, d @ view])

W, Hh = 1000, 1150
proj = [(np.array([project(v) for v in tri]), col) for tri, col in tris]
sx = np.array([p[:, 0] for p, _ in proj]).ravel()
sy = np.array([p[:, 1] for p, _ in proj]).ravel()
margin = 70
scale = min((W - 2 * margin) / (sx.max() - sx.min()),
            (Hh - 2 * margin) / (sy.max() - sy.min()))
ox = W / 2 - scale * (sx.max() + sx.min()) / 2
oy = Hh / 2 + scale * (sy.max() + sy.min()) / 2

img = np.full((Hh, W, 3), 255, float)
zbuf = np.full((Hh, W), 1e18, float)

for p, col in proj:
    a, b, c = p
    nz = np.cross(b - a, c - a)
    nn = np.linalg.norm(nz)
    if nn == 0:
        continue
    nz = nz / nn
    if nz[2] < 0:
        nz = -nz
    inten = min(1.0, 0.30 + 0.75 * max(0.15, nz[2]))
    shade = np.clip(col * inten, 0, 255)

    xs = ox + scale * p[:, 0]
    ys = oy - scale * p[:, 1]
    zs = p[:, 2]
    x0 = int(max(0, math.floor(xs.min()))); x1 = int(min(W - 1, math.ceil(xs.max())))
    y0 = int(max(0, math.floor(ys.min()))); y1 = int(min(Hh - 1, math.ceil(ys.max())))
    if x1 < x0 or y1 < y0:
        continue
    ax, ay = xs[0], ys[0]; bx, by = xs[1], ys[1]; cx, cy = xs[2], ys[2]
    det = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy)
    if abs(det) < 1e-9:
        continue
    yy, xx = np.mgrid[y0:y1 + 1, x0:x1 + 1]
    l1 = ((by - cy) * (xx - cx) + (cx - bx) * (yy - cy)) / det
    l2 = ((cy - ay) * (xx - cx) + (ax - cx) * (yy - cy)) / det
    l3 = 1 - l1 - l2
    inside = (l1 >= -0.001) & (l2 >= -0.001) & (l3 >= -0.001)
    if not inside.any():
        continue
    z = l1 * zs[0] + l2 * zs[1] + l3 * zs[2]
    sub_z = zbuf[y0:y1 + 1, x0:x1 + 1]
    closer = inside & (z < sub_z)
    sub_z[closer] = z[closer]
    sub_img = img[y0:y1 + 1, x0:x1 + 1]
    sub_img[closer] = shade

img = img[:, ::-1]  # natural orientation
Image.fromarray(img.astype(np.uint8)).save(os.path.join(OUT, "preview_iso.png"))
print("SW_RENDER_DONE", len(tris), "triangles")
