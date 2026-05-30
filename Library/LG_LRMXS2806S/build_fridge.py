# -*- coding: utf-8 -*-
"""
Build a simplified CAD model of the:
  LG Standard-Depth Craft Ice 27.8 cu ft 4-Door French Door Refrigerator
  with Dual Ice Maker  (model LRMXS2806S)

General representation only - no moving parts. Captures:
  - 2 top French doors (each with a vertical bar handle)
  - 2 bottom freezer drawers (each with a horizontal bar handle)
  - Ice / water dispenser recess on the left door
  - Correct overall outside dimensions

Run headless:  freecadcmd build_fridge.py
or with GUI:   freecad     build_fridge.py   (adds stainless-steel colors)

Units: millimetres.
"""

import os
import FreeCAD as App
import Part

# Optional GUI (for colors). Present only when launched via the GUI binary.
try:
    import FreeCADGui as Gui
    HAVE_GUI = Gui.getMainWindow() is not None
except Exception:
    HAVE_GUI = False

IN = 25.4  # mm per inch

# --- Overall outside dimensions (LRMXS2806S) -------------------------------
W = 35.75 * IN   # width   = 908.05 mm
H = 69.75 * IN   # height  = 1771.65 mm
D = 36.25 * IN   # depth   = 920.75 mm

# --- Design parameters ------------------------------------------------------
PANEL_T = 40.0   # how far doors/drawers stand out from the cabinet front
REVEAL  = 7.0    # gap (reveal line) between adjacent doors/drawers
MARGIN  = 7.0    # gap from cabinet outer edge to a panel
BASE_H  = 70.0   # recessed toe-kick height at the bottom front

BODY_D  = D - PANEL_T          # cabinet box depth; panels make up the rest
FRONT   = BODY_D               # Y of the cabinet front face
PFRONT  = D                    # Y of the door/drawer front face

# --- Vertical layout (Z) ----------------------------------------------------
DOOR_REGION_H = 1000.0
z_div = H - MARGIN - DOOR_REGION_H          # boundary doors <-> drawers
z_mid = BASE_H + (z_div - BASE_H) / 2.0     # boundary between the two drawers

CX = W / 2.0                                # cabinet centerline (X)

OUT = os.path.dirname(os.path.abspath(__file__))
DOCNAME = "LG_LRMXS2806S"


# --- helpers ----------------------------------------------------------------
def box(l, w, h, x, y, z):
    return Part.makeBox(l, w, h, App.Vector(x, y, z))


def add(name, shape):
    o = doc.addObject("Part::Feature", name)
    o.Shape = shape
    return o


def vbar(xc, z1, z2):
    """Vertical bar handle, standing off the front face on two posts."""
    r = 12.0
    off = 38.0                       # bar distance from panel face
    yb = PFRONT + off
    bar = Part.makeCylinder(r, z2 - z1, App.Vector(xc, yb, z1),
                            App.Vector(0, 0, 1))
    post = box(24, off, 24, xc - 12, PFRONT, 0)
    p1 = post.copy(); p1.translate(App.Vector(0, 0, z1 + 30))
    p2 = post.copy(); p2.translate(App.Vector(0, 0, z2 - 54))
    return bar.fuse(p1).fuse(p2)


def hbar(zc, x1, x2):
    """Horizontal bar handle, standing off the front face on two posts."""
    r = 12.0
    off = 38.0
    yb = PFRONT + off
    bar = Part.makeCylinder(r, x2 - x1, App.Vector(x1, yb, zc),
                            App.Vector(1, 0, 0))
    post = box(24, off, 24, 0, PFRONT, zc - 12)
    p1 = post.copy(); p1.translate(App.Vector(x1 + 30, 0, 0))
    p2 = post.copy(); p2.translate(App.Vector(x2 - 54, 0, 0))
    return bar.fuse(p1).fuse(p2)


# --- build ------------------------------------------------------------------
doc = App.newDocument(DOCNAME)

# Cabinet body
cabinet = add("Cabinet", box(W, BODY_D, H, 0, 0, 0))

# Door / drawer panel extents (with reveal gaps)
ld_x1, ld_x2 = MARGIN, CX - REVEAL / 2.0
rd_x1, rd_x2 = CX + REVEAL / 2.0, W - MARGIN
door_z1, door_z2 = z_div + REVEAL / 2.0, H - MARGIN

dr_x1, dr_x2 = MARGIN, W - MARGIN
mid_z1, mid_z2 = z_mid + REVEAL / 2.0, z_div - REVEAL / 2.0
bot_z1, bot_z2 = BASE_H, z_mid - REVEAL / 2.0

# Left French door (with dispenser recess cut into it)
left = box(ld_x2 - ld_x1, PANEL_T, door_z2 - door_z1, ld_x1, FRONT, door_z1)
disp_w, disp_h, disp_d = 200.0, 330.0, 30.0
disp_cx = (ld_x1 + ld_x2) / 2.0 - 25.0
disp_cz = door_z1 + (door_z2 - door_z1) * 0.62
disp_pocket = box(disp_w, disp_d, disp_h,
                  disp_cx - disp_w / 2.0, PFRONT - disp_d,
                  disp_cz - disp_h / 2.0)
left = left.cut(disp_pocket)
door_left = add("Door_Left_FrenchDoor", left)

# A small dispenser tray/backing inside the recess so it reads as a dispenser
tray = box(disp_w - 30, 14, 60,
           disp_cx - (disp_w - 30) / 2.0, PFRONT - disp_d,
           disp_cz - disp_h / 2.0 + 30)
dispenser = add("Dispenser", tray)

# Right French door
right = box(rd_x2 - rd_x1, PANEL_T, door_z2 - door_z1, rd_x1, FRONT, door_z1)
door_right = add("Door_Right_FrenchDoor", right)

# Middle freezer drawer
mid = box(dr_x2 - dr_x1, PANEL_T, mid_z2 - mid_z1, dr_x1, FRONT, mid_z1)
drawer_mid = add("Drawer_Middle", mid)

# Bottom freezer drawer
bot = box(dr_x2 - dr_x1, PANEL_T, bot_z2 - bot_z1, dr_x1, FRONT, bot_z1)
drawer_bot = add("Drawer_Bottom", bot)

# Handles ---------------------------------------------------------------------
hL = add("Handle_DoorLeft",  vbar(CX - 110, door_z1 + 120, door_z2 - 120))
hR = add("Handle_DoorRight", vbar(CX + 110, door_z1 + 120, door_z2 - 120))
hM = add("Handle_DrawerMiddle", hbar(mid_z2 - 70, CX - 150, CX + 150))
hB = add("Handle_DrawerBottom", hbar(bot_z2 - 70, CX - 150, CX + 150))

doc.recompute()

# --- colors (only when run under the GUI) -----------------------------------
if HAVE_GUI:
    steel = (0.74, 0.76, 0.78)
    dark = (0.12, 0.12, 0.13)
    body = [cabinet, door_left, door_right, drawer_mid, drawer_bot]
    handles = [hL, hR, hM, hB, dispenser]
    for o in body:
        o.ViewObject.ShapeColor = steel
    for o in handles:
        o.ViewObject.ShapeColor = dark

# --- save / export ----------------------------------------------------------
fcstd = os.path.join(OUT, DOCNAME + ".FCStd")
step = os.path.join(OUT, DOCNAME + ".step")
stl = os.path.join(OUT, DOCNAME + ".stl")

doc.saveAs(fcstd)

solids = [cabinet, door_left, dispenser, door_right, drawer_mid,
          drawer_bot, hL, hR, hM, hB]
Part.export(solids, step)

# Mesh export (whole assembly as one STL)
import Mesh
compound = Part.makeCompound([o.Shape for o in solids])
Mesh.Mesh(compound.tessellate(1.0)).write(stl)

# Report
bb = compound.BoundBox
print("Saved: %s" % fcstd)
print("Saved: %s" % step)
print("Saved: %s" % stl)
print("Overall (mm)  W x H x D = %.1f x %.1f x %.1f"
      % (bb.XLength, bb.ZLength, bb.YLength))
print("Overall (in)  W x H x D = %.2f x %.2f x %.2f"
      % (bb.XLength / IN, bb.ZLength / IN, bb.YLength / IN))

if HAVE_GUI:
    doc.save()
    try:
        Gui.getMainWindow().close()
    except Exception:
        pass
