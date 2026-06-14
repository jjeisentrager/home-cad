# -*- coding: utf-8 -*-
"""Rework the AddOn kitchen drain (DrainAddOn.FCStd) to an S-TRAP layout:

  sink strainer -> tailpiece -> DW-branch WYE (45 deg branch for the dishwasher
  high-rise-loop flex hose) -> S-TRAP -> straight DROP through the subfloor ->
  LARGE-SWEEP 90 (long radius) -> west run -> 90 down -> basement drop.

The S-trap goes straight DOWN (no horizontal trap arm), so the whole horizontal
run + basement drop shift in +X to sit directly under the sink (X 13188.8 ->
13366.8). Replaces the old P-trap + below-trap wye + standard corner elbow.

Reused links (repositioned/resized): Wye (now DW branch above trap),
Straight001 (vertical drop), StraightDropB (tailpiece), Straight002 (west run),
Elbow001 (run->down), Straight (basement drop).
Baked Part::Features (custom geometry): STrap (lib shape), Sweep90 (long radius),
DWHose (looping flex hose).
Hidden (superseded): PTrap, Elbow002, StraightDW, Elbow (old corner).

Run OFFSCREEN GUI so GuiDocument survives.  SAVE=1 to persist.
"""
import os, math, FreeCAD as App, Part
R="/home/joee/github/alieniron/home-cad"
SAVE=os.environ.get("SAVE","0")=="1"
V=App.Vector
M3=App.Matrix(0,-1,0,13722.4, 0,0,1,7187.0, -1,0,0,2984.9, 0,0,0,1)
M3i=M3.inverse()
def W2L(world_mat): return App.Placement(M3i.multiply(world_mat))
def unit(v): v=V(v); v.normalize(); return v
def toW(p): return M3.multVec(V(p))

d=App.openDocument(os.path.join(R,"Drain/DrainAddOn.FCStd"))
lib=App.openDocument(os.path.join(R,"Library/PVC-SCH40/PVC-SCH40.FCStd"))
asm=d.getObject("Assembly")

# ---------------- helpers ----------------
def straight_world(start, dirv):
    return App.Placement(V(start), App.Rotation(V(1,0,0), unit(dirv))).Matrix

def elbow_world(corner, din, dout):
    dout=unit(dout); din=unit(din); n=din.cross(dout)
    m=App.Matrix(dout.x,n.x,din.x,0, dout.y,n.y,din.y,0, dout.z,n.z,din.z,0, 0,0,0,1)
    cl=V(0,0,76.2); rc=m.multVec(cl); base=V(corner)-rc
    wm=App.Matrix(m); wm.A14=base.x; wm.A24=base.y; wm.A34=base.z
    return wm

def setpl(name, world_mat):
    d.getObject(name).Placement = App.Placement(M3i.multiply(world_mat))

def setlen(padname, L):
    pad=d.getObject(padname)
    body=next((o for o in pad.InList if o.TypeId=="PartDesign::Body"), pad.InList[0])
    pad.setExpression('Length', None); pad.Length=float(L)
    pad.touch(); body.touch(); d.recompute([pad,body], True, True)

def bake(name, world_shape, color=None):
    """add world_shape (in WORLD coords) as a Part::Feature in DrainAddOn-local."""
    sh=world_shape.copy(); sh.transformShape(M3i)
    old=d.getObject(name)
    if old is not None: d.removeObject(name)
    f=d.addObject("Part::Feature", name); f.Shape=sh
    if asm is not None: asm.addObject(f)
    f.Visibility=True
    if App.GuiUp and f.ViewObject is not None:
        f.ViewObject.Visibility=True
        if color is not None: f.ViewObject.ShapeColor=color
    return f

def hide(name):
    o=d.getObject(name)
    if o is None: return
    o.Visibility=False
    if App.GuiUp and getattr(o,'ViewObject',None) is not None: o.ViewObject.Visibility=False
    lo=getattr(o,'LinkedObject',None)
    if lo is not None and lo.Document is d:
        try:
            lo.Visibility=False
            if App.GuiUp and lo.ViewObject is not None: lo.ViewObject.Visibility=False
        except Exception: pass

# suppress every joint so manual placements hold
for o in d.Objects:
    if 'Joint' in o.TypeId or getattr(o,'Label','').startswith(('Fixed','Grounded')):
        try: o.Suppressed=True
        except Exception: pass

# ============== WORLD GEOMETRY ==============
SINK_X, SINK_Y = 13570.0, 13688.0          # sink drain (trap inlet column)
RUN_X   = 13366.8                            # = SINK_X - 203.2  (S-trap inlet->outlet offset)
RUN_Z   = 2440.0                             # joist band 2337..2591
R_SWEEP = 140.0                              # long-radius sweep centerline radius
DROP_Y  = 7300.0                             # west run -> down corner
BASE_Z  = 500.0
ROD     = 30.48                              # pipe radius (OD 60.96)

Z_TRAPIN  = 3050.0                           # S-trap top opening (inlet)
Z_TRAPOUT = Z_TRAPIN - 228.6                 # 2821.4  (bottom opening)

# ---- S-TRAP (baked from lib Body011), Rz180 + translate so inlet=(SINK_X,SINK_Y,Z_TRAPIN)
T = V(SINK_X-203.2, SINK_Y, Z_TRAPIN-203.2)  # (13366.8,13688,2846.8)
M_trap=App.Matrix(-1,0,0,T.x, 0,-1,0,T.y, 0,0,1,T.z, 0,0,0,1)
strap=lib.getObject("Body011").Shape.copy(); strap.transformShape(M_trap)
bake("STrap", strap, color=(0.90,0.90,0.92))

# ---- DW WYE (reuse 'Wye'): Rz90 so branch points -X (toward DW), bottom run at trap inlet
Tw=V(SINK_X, SINK_Y, Z_TRAPIN+57.1)          # bottom run local (0,0,-57.1) -> Z_TRAPIN
M_wye=App.Matrix(0,-1,0,Tw.x, 1,0,0,Tw.y, 0,0,1,Tw.z, 0,0,0,1)
d.getObject("Wye").Placement = App.Placement(M3i.multiply(M_wye))
WYE_TOP    = V(SINK_X, SINK_Y, Tw.z+127.0)            # 3234.1  -> tailpiece
WYE_BRANCH = V(SINK_X-89.8, SINK_Y, Tw.z+89.8)        # 13480.2,13688,3196.9 -> hose

# ---- sink TAILPIECE (reuse StraightDropB): wye top -> up into strainer
setpl("StraightDropB", straight_world(WYE_TOP, V(0,0,1))); setlen("Pad054", 110.0)

# ---- vertical DROP (reuse Straight001): trap outlet -> sweep entry
SWEEP_TOP = V(RUN_X, SINK_Y, RUN_Z+R_SWEEP)          # 13366.8,13688,2580
setpl("Straight001", straight_world(V(RUN_X,SINK_Y,Z_TRAPOUT), V(0,0,-1)))
setlen("Pad032", Z_TRAPOUT-SWEEP_TOP.z)              # 241.4

# ---- LARGE SWEEP 90 (baked): down(-Z) -> west(-Y)
C  = V(RUN_X, SINK_Y-R_SWEEP, RUN_Z+R_SWEEP)         # arc center
E1 = V(RUN_X, SINK_Y,          RUN_Z+R_SWEEP)        # entry (top)  tangent -Z
E2 = V(RUN_X, SINK_Y-R_SWEEP,  RUN_Z)                # exit (bottom) tangent -Y
a45=R_SWEEP*math.sin(math.radians(45))
MidP=V(RUN_X, C.y+a45, C.z-a45)
arc=Part.Arc(E1,MidP,E2); spine=Part.Wire(arc.toShape())
prof=Part.Wire(Part.makeCircle(ROD, E1, V(0,0,1)))
sweep=spine.makePipeShell([prof], True, True)
bake("Sweep90", sweep, color=(0.82,0.82,0.85))
RUN_START=E2                                          # 13366.8, 13548, 2440

# ---- west RUN (reuse Straight002): sweep exit -> Elbow001 P1
ELB_P1=V(RUN_X, DROP_Y+76.2, RUN_Z)                  # 13366.8,7376.2,2440
setpl("Straight002", straight_world(RUN_START, V(0,-1,0)))
setlen("Pad035", RUN_START.y-ELB_P1.y)              # 6171.8

# ---- run -> DOWN elbow (reuse Elbow001)
setpl("Elbow001", elbow_world(V(RUN_X,DROP_Y,RUN_Z), din=V(0,-1,0), dout=V(0,0,-1)))
DROP2_TOP=V(RUN_X, DROP_Y, RUN_Z-101.6)             # 2338.4

# ---- basement DROP (reuse Straight, grounded)
setpl("Straight", straight_world(DROP2_TOP, V(0,0,-1)))
setlen("Pad031", DROP2_TOP.z-BASE_Z)               # 1838.4

# ---- DW HOSE (baked): branch tip -> high-rise loop -> dishwasher
H=[V(WYE_BRANCH.x,WYE_BRANCH.y,WYE_BRANCH.z),
   V(13440,SINK_Y,3300), V(13360,SINK_Y,3370),     # rise to loop peak
   V(13230,SINK_Y,3350), V(13080,SINK_Y,3170),
   V(12950,SINK_Y,3010), V(12830,SINK_Y,2960)]     # down to DW drain
bs=Part.BSplineCurve(); bs.interpolate(H)
hpath=Part.Wire(bs.toShape())
hdir=H[1].sub(H[0])
hprof=Part.Wire(Part.makeCircle(11.0, H[0], unit(hdir)))
try:
    # parallel-transport frame (is_frenet=False) -> no profile flip at inflections
    hose=hpath.makePipeShell([hprof], True, False)
    hb=hose.BoundBox
    if (hb.YMax-hb.YMin) > 80:   # bulged -> fall back to robust polyline tube
        raise RuntimeError("pipeshell Y-bulge %.0f"%(hb.YMax-hb.YMin))
except Exception:
    # fallback: polyline of cylinders + spheres
    parts=[]
    for i in range(len(H)-1):
        a=H[i]; b=H[i+1]; dv=b.sub(a); L=dv.Length
        parts.append(Part.makeCylinder(11.0, L, a, unit(dv)))
        parts.append(Part.makeSphere(11.0, b))
    hose=Part.makeCompound(parts)
bake("DWHose", hose, color=(0.20,0.20,0.22))

# ---- hide superseded parts
for nm in ("PTrap","Elbow002","StraightDW","Elbow"):
    hide(nm)

# ============== VERIFY ==============
rep=open(os.path.join(R,"Drain/_strap_check.txt"),"w")
def w(s): rep.write(s+"\n")
def lp(name,*locs):
    lk=d.getObject(name); P=lk.Placement
    return [toW(P.multVec(V(p))) for p in locs]
w("S-trap inlet target (sink)  = (%.1f,%.1f,%.1f)"%(SINK_X,SINK_Y,Z_TRAPIN))
w("S-trap outlet (drop top)    = (%.1f,%.1f,%.1f)"%(RUN_X,SINK_Y,Z_TRAPOUT))
sb=d.getObject("STrap").Shape.copy(); sb.transformShape(M3); b=sb.BoundBox
w("STrap baked WORLD bbox X[%.0f,%.0f] Y[%.0f,%.0f] Z[%.0f,%.0f]"%(b.XMin,b.XMax,b.YMin,b.YMax,b.ZMin,b.ZMax))
wt,wb,wbr=lp("Wye",(0,0,127),(0,0,-57.1),(0,89.8,89.8))
w("Wye  TOP=(%.0f,%.0f,%.0f) BOT=(%.0f,%.0f,%.0f) BRANCH=(%.0f,%.0f,%.0f)"%(wt.x,wt.y,wt.z,wb.x,wb.y,wb.z,wbr.x,wbr.y,wbr.z))
a,b2=lp("Straight001",(0,0,0),(d.getObject("Pad032").Length.Value,0,0))
w("Drop      A=(%.0f,%.0f,%.0f) B=(%.0f,%.0f,%.0f)  [B=SWEEP_TOP %.0f,%.0f,%.0f]"%(a.x,a.y,a.z,b2.x,b2.y,b2.z,E1.x,E1.y,E1.z))
for nm in ("Sweep90","DWHose"):
    bb=d.getObject(nm).Shape.copy(); bb.transformShape(M3); bb=bb.BoundBox
    w("%-8s WORLD bbox X[%.0f,%.0f] Y[%.0f,%.0f] Z[%.0f,%.0f]"%(nm,bb.XMin,bb.XMax,bb.YMin,bb.YMax,bb.ZMin,bb.ZMax))
a,b2=lp("Straight002",(0,0,0),(d.getObject("Pad035").Length.Value,0,0))
w("Run       A=(%.0f,%.0f,%.0f) B=(%.0f,%.0f,%.0f)  [A=RUN_START %.0f,%.0f,%.0f]"%(a.x,a.y,a.z,b2.x,b2.y,b2.z,RUN_START.x,RUN_START.y,RUN_START.z))
a,b2=lp("Straight",(0,0,0),(d.getObject("Pad031").Length.Value,0,0))
w("BaseDrop  A=(%.0f,%.0f,%.0f) B=(%.0f,%.0f,%.0f)"%(a.x,a.y,a.z,b2.x,b2.y,b2.z))
# full visible world bbox
vis=[]
for o in d.Objects:
    if o.Name in ("STrap","Sweep90","DWHose"):
        s=o.Shape.copy(); s.transformShape(M3); vis.append(s)
    elif o.TypeId=="App::Link" and o.Visibility and o.LinkedObject is not None and hasattr(o.LinkedObject,'Shape'):
        s=o.LinkedObject.Shape
        if s and not s.isNull():
            s=s.copy(); s.transformShape(o.Placement.Matrix); s.transformShape(M3); vis.append(s)
if vis:
    comp=Part.makeCompound(vis); b=comp.BoundBox
    w("VISIBLE WORLD bbox X[%.0f,%.0f] Y[%.0f,%.0f] Z[%.0f,%.0f]"%(b.XMin,b.XMax,b.YMin,b.YMax,b.ZMin,b.ZMax))
rep.close()

if SAVE:
    d.recompute()
    d.save(); print("SAVED GuiUp=%s"%App.GuiUp)
else:
    print("DRYRUN_DONE GuiUp=%s"%App.GuiUp)
