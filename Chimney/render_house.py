"""Render the whole House with the Chimney highlighted, to check placement.
freecadcmd render_house.py -> house_chimney_iso.png"""
import os, math
import numpy as np
from PIL import Image
import FreeCAD as App

R = "/home/joee/github/alieniron/home-cad"
doc = App.openDocument(os.path.join(R, "House/House.FCStd"))

CHIM = np.array([190, 70, 50], float)
HEARTH = np.array([200, 200, 192], float)
WOOD = np.array([205, 178, 130], float)
GREY = np.array([176, 180, 185], float)

# top-level object names to skip (origins/datums/joints + roof/ground for clarity)
SKIP = ("Origin", "Axis", "Plane", "Joint", "Assembly", "Ground", "Deck",
        "MainRoof", "RoofFrame", "RoofConnector", "DeckPosts")

tris = []
for o in doc.Objects:
    nm = o.Name
    if any(s in nm for s in SKIP):
        continue
    sh = getattr(o, "Shape", None)
    if sh is None or sh.isNull() or not sh.Faces:
        continue
    if nm == "Chimney":
        col = CHIM
    elif "Framing" in nm or nm.startswith(("SubFloor", "Body")):
        col = WOOD
    else:
        col = GREY
    try:
        vs, fs = sh.tessellate(6.0)
    except Exception:
        continue
    Pn = np.array([[v.x, v.y, v.z] for v in vs], float)
    for f in fs:
        tris.append((Pn[list(f)], col))


def n(v):
    return v / np.linalg.norm(v)

allp = np.vstack([t[0] for t in tris])
center = (allp.max(0) + allp.min(0)) / 2.0


def render(view, up, fname, W=1700, H=1200):
    view = n(view); right = n(np.cross(view, up)); tup = n(np.cross(right, view))

    def proj(p):
        d = p - center
        return np.array([d @ right, d @ tup, d @ view])

    pr = [(np.array([proj(v) for v in tri]), c) for tri, c in tris]
    sx = np.array([p[:, 0] for p, _ in pr]).ravel()
    sy = np.array([p[:, 1] for p, _ in pr]).ravel()
    m = 60
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
        inten = min(1.0, 0.34 + 0.7*max(0.12, abs(nz[2])))
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
    Image.fromarray(img.astype(np.uint8)).save(os.path.join(R, fname))


# SE-above view (south=+X, east=+Y): sees the great-room end + the chimney/roof
render(np.array([-0.5, -0.55, -0.45]), np.array([0, 0, 1.0]),
       "Chimney/house_chimney_iso.png")
# top-down plan: +Y (east) up, +X (south) right
render(np.array([0, 0, -1.0]), np.array([0, 1.0, 0]),
       "Chimney/house_chimney_plan.png", W=1900, H=1000)
print("HOUSE_RENDER_DONE", len(tris))
