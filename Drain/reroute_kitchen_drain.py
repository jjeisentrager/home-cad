# -*- coding: utf-8 -*-
"""Re-route the AddOn kitchen drain (DrainAddOn.FCStd), Stage A:
 - lower the long horizontal run into the floor-joist bay (Z~2500, joists Z[2362,2591])
 - remove the unnecessary south jog: the run now turns straight DOWN at its west end
Reuses the existing 7 PVC parts via direct link.Placement edits + pad-length edits
(no assembly solver). World route is computed, then mapped to DrainAddOn-local via
M3^-1 (M3 = the House 'DrainAddOn' link placement). Set SAVE=1 env to persist.
"""
import os, FreeCAD as App
R="/home/joee/github/alieniron/home-cad"
SAVE = os.environ.get("SAVE","0")=="1"
d=App.openDocument(os.path.join(R,"Drain/DrainAddOn.FCStd"))

# ---- M3 : DrainAddOn-local -> world (the House link placement) ----
M3 = App.Matrix(0,-1,0,13722.4, 0,0,1,7187.0, -1,0,0,2984.9, 0,0,0,1)
M3i = M3.inverse()
def W2Lmat(world_mat):   # world placement matrix -> local placement matrix
    return M3i.multiply(world_mat)

V=App.Vector
def unit(v):
    v=V(v); return v.normalize()

# ---- placement builders (return WORLD placement matrix) ----
def straight_world(start, dirv):
    """local +X (port A at 0) -> world 'dirv', port A at world 'start'."""
    rot=App.Rotation(V(1,0,0), unit(dirv))
    return App.Placement(V(start), rot).Matrix

def elbow_world(corner, din, dout):
    """Elbow: P1(incoming,(0,0,0) face -Z, leg76.2) outward=-din;
              P2(outgoing,(101.6,0,76.2) face +X, leg101.6) outward=+dout.
       corner_local=(0,0,76.2). Map X_l->dout, Z_l->din, Y_l->din x dout."""
    dout=unit(dout); din=unit(din)
    n=din.cross(dout)
    m=App.Matrix(dout.x, n.x, din.x, 0,
                 dout.y, n.y, din.y, 0,
                 dout.z, n.z, din.z, 0,
                 0,0,0,1)
    # base = corner_world - m*corner_local
    cl=V(0,0,76.2)
    rc=m.multVec(cl)
    base=V(corner)-rc
    wm=App.Matrix(m); wm.A14=base.x; wm.A24=base.y; wm.A34=base.z
    return wm

def setpl(link, world_mat):
    link.Placement = App.Placement(W2Lmat(world_mat))

def setlen(padname, L):
    pad=d.getObject(padname)
    body=next((o for o in pad.InList if o.TypeId=="PartDesign::Body"), pad.InList[0])
    pad.setExpression('Length', None)
    pad.Length=float(L)
    pad.touch(); body.touch()
    d.recompute([pad,body], True, True)

# ---- suppress all Fixed/Grounded joints so placements are static ----
for jn in ("GroundedJoint","Joint","Joint001","Joint002","Joint003","Joint004","Joint005"):
    o=d.getObject(jn)
    if o is not None:
        try: o.Suppressed=True
        except Exception: pass

# ===================== WORLD ROUTE (Stage A) =====================
TRAP_OUT = V(13265.2, 13688.4, 3174.6)   # fixed (PTrap outlet), arm faces -X
RUN_X    = 13188.8                         # joist bay X[13030,13360]
RUN_Z    = 2500.0                          # joist band Z[2362,2591]
DROP_Y   = 7300.0                          # basement-drop Y (over basement, in joist span)
BASE_Z   = 500.0                           # land here, no tie-in

# Elbow002: trap(-X) -> down(-Z); P1 mates trap outlet
e002_corner = V(RUN_X, 13688.4, 3174.6)
setpl(d.getObject("Elbow002"), elbow_world(e002_corner, din=V(-1,0,0), dout=V(0,0,-1)))
# its P2 (drop-to-joist start):
dropA_top = V(RUN_X, 13688.4, 3174.6-101.6)         # = corner + 101.6*(-Z)

# Elbow (down->west): din -Z, dout -Y ; corner at run level
ew_corner = V(RUN_X, 13688.4, RUN_Z)
setpl(d.getObject("Elbow"), elbow_world(ew_corner, din=V(0,0,-1), dout=V(0,-1,0)))
dropA_bot = V(RUN_X, 13688.4, RUN_Z+76.2)           # Elbow P1 (top of run-elbow)
runA_start = V(RUN_X, 13688.4-101.6, RUN_Z)         # Elbow P2 (run start), -Y

# Straight001 = vertical drop trap->joist : from dropA_top down to dropA_bot
setpl(d.getObject("Straight001"), straight_world(dropA_top, V(0,0,-1)))
LEN_DROP2JOIST = dropA_top.z - dropA_bot.z
setlen("Pad032", LEN_DROP2JOIST)

# Elbow001 (west->down): din -Y, dout -Z ; corner at run level, DROP_Y
ed_corner = V(RUN_X, DROP_Y, RUN_Z)
setpl(d.getObject("Elbow001"), elbow_world(ed_corner, din=V(0,-1,0), dout=V(0,0,-1)))
runA_end = V(RUN_X, DROP_Y+76.2, RUN_Z)             # Elbow001 P1 (run end)
dropB_top = V(RUN_X, DROP_Y, RUN_Z-101.6)           # Elbow001 P2 (basement drop start)

# Straight002 = long run : runA_start -> runA_end  (-Y)
setpl(d.getObject("Straight002"), straight_world(runA_start, V(0,-1,0)))
LEN_RUN = runA_start.y - runA_end.y
setlen("Pad035", LEN_RUN)

# Straight (grounded) = basement drop : dropB_top down to BASE_Z
setpl(d.getObject("Straight"), straight_world(dropB_top, V(0,0,-1)))
LEN_DROP = dropB_top.z - BASE_Z
setlen("Pad031", LEN_DROP)

# ===================== VERIFY (world port continuity) =====================
def toW(p): return M3.multVec(V(p))
def linkports(name, *locals_):
    lk=d.getObject(name); P=lk.Placement
    return [toW(P.multVec(V(p))) for p in locals_]
rep=open(os.path.join(R,"Drain/_reroute_check.txt"),"w")
def w(s): rep.write(s+"\n")
w("LENGTHS: drop2joist=%.1f run=%.1f basementdrop=%.1f"%(LEN_DROP2JOIST,LEN_RUN,LEN_DROP))
# straight ports A(0,0,0) B(L,0,0)
for nm,L in (("Straight001",LEN_DROP2JOIST),("Straight002",LEN_RUN),("Straight",LEN_DROP)):
    a,b=linkports(nm,(0,0,0),(L,0,0))
    w("%-12s A=(%.0f,%.0f,%.0f) B=(%.0f,%.0f,%.0f)"%(nm,a.x,a.y,a.z,b.x,b.y,b.z))
for nm in ("Elbow002","Elbow","Elbow001"):
    p1,p2,c=linkports(nm,(0,0,0),(101.6,0,76.2),(0,0,76.2))
    w("%-12s P1=(%.0f,%.0f,%.0f) P2=(%.0f,%.0f,%.0f) corner=(%.0f,%.0f,%.0f)"%(nm,p1.x,p1.y,p1.z,p2.x,p2.y,p2.z,c.x,c.y,c.z))
pt=linkports("PTrap",(0,0,0),(-304.8,0,25.4))
w("PTrap        inlet=(%.0f,%.0f,%.0f) outlet=(%.0f,%.0f,%.0f)"%(pt[0].x,pt[0].y,pt[0].z,pt[1].x,pt[1].y,pt[1].z))
# overall world bbox of all link shapes
import Part
allsh=[]
for nm in ("PTrap","Elbow002","Straight001","Elbow","Straight002","Elbow001","Straight"):
    lk=d.getObject(nm); s=lk.LinkedObject.Shape.copy(); s.transformShape(lk.Placement.Matrix); s.transformShape(M3); allsh.append(s)
comp=Part.makeCompound(allsh); bb=comp.BoundBox
w("WORLD BBOX X[%.0f,%.0f] Y[%.0f,%.0f] Z[%.0f,%.0f]"%(bb.XMin,bb.XMax,bb.YMin,bb.YMax,bb.ZMin,bb.ZMax))
rep.close()

if SAVE:
    for nm in ("PTrap","Elbow002","Straight001","Elbow","Straight002","Elbow001","Straight"):
        o=d.getObject(nm)
        try:
            o.Visibility=True
            if App.GuiUp and o.ViewObject is not None:
                o.ViewObject.Visibility=True
        except Exception: pass
    d.save(); print("SAVED GuiUp=%s"%App.GuiUp)
else:
    print("DRYRUN_DONE")
