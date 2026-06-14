# -*- coding: utf-8 -*-
"""Stage B: tie the dishwasher into the kitchen drain (DrainAddOn.FCStd).
A 2" WYE is inserted in the vertical drop just below the P-trap: the run stays
vertical (main sink line unchanged), and the wye's 45 deg branch rises NORTH
toward the dishwasher (world -X, +Z). A 2" straight forms the DW branch arm.
The existing vertical drop (Straight001/Pad032) is shortened to meet the wye top;
one new straight continues the drop from the wye bottom to the down->west elbow.

PVC parts are imported from the library by linking the Body, setting
LinkCopyOnChange='Owned', then toggling the 'Part' enum to spawn the owned copy
(verified working). Must run OFFSCREEN GUI. SAVE=1 to persist.
"""
import os, FreeCAD as App
R="/home/joee/github/alieniron/home-cad"
SAVE=os.environ.get("SAVE","0")=="1"
V=App.Vector
M3=App.Matrix(0,-1,0,13722.4,0,0,1,7187.0,-1,0,0,2984.9,0,0,0,1)
M3i=M3.inverse()
def W2L(world_mat): return App.Placement(M3i.multiply(world_mat))
def unit(v): v=V(v); return v.normalize()
def toW(p): return M3.multVec(V(p))

d=App.openDocument(os.path.join(R,"Drain/DrainAddOn.FCStd"))
lib=App.openDocument(os.path.join(R,"Library/PVC-SCH40/PVC-SCH40.FCStd"))
asm=d.getObject("Assembly")

def import_owned(bodyname, linkname, label):
    body=lib.getObject(bodyname)
    lk=d.addObject("App::Link", linkname); lk.Label=label
    lk.LinkedObject=body
    lk.LinkCopyOnChange='Owned'
    d.recompute()
    opts=list(lk.getEnumerationsOfProperty('Part'))
    other=[o for o in opts if o!='PVCE2'][0]
    lk.Part=other; d.recompute()
    lk.Part='PVCE2'; d.recompute()
    if asm is not None: asm.addObject(lk)
    return lk

def set_pad_len(lk, L):
    body=lk.LinkedObject
    pad=body.Tip
    pad.setExpression('Length', None); pad.Length=float(L)
    pad.touch(); body.touch(); d.recompute([pad,body],True,True)

def straight_world(start, dirv):
    return App.Placement(V(start), App.Rotation(V(1,0,0), unit(dirv))).Matrix

# ---------- geometry (WORLD) ----------
RUN_X, RUN_Y = 13188.8, 13688.4
E002_P2   = V(RUN_X, RUN_Y, 3073.4)     # bottom of Elbow002 (top of vertical drop)
ELBOW_P1  = V(RUN_X, RUN_Y, 2576.2)     # top of down->west Elbow (bottom of drop)
WYE_BASEZ = 2800.0                       # wye local origin world Z
# wye: local Z(run)->worldZ, local Y->world -X, local X->world +Y  (90deg about Z)
wm=App.Matrix(0,-1,0,RUN_X,  1,0,0,RUN_Y,  0,0,1,WYE_BASEZ,  0,0,0,1)
# wye ports (local): top run (0,0,127), bottom run (0,0,-57.1), branch (0,89.8,89.8)
def wlocal(p): return wm.multVec(V(p))
WYE_TOP    = wlocal((0,0,127.0))         # world
WYE_BOT    = wlocal((0,0,-57.1))
WYE_BRANCH = wlocal((0,89.8,89.8))
BR_DIR     = unit(V(-0.7071,0,0.7071))   # branch axis up-north (world)
BR_LEN     = 409.0
DW_END     = WYE_BRANCH + BR_DIR.multiply(BR_LEN)

# ---------- import + place ----------
wye=import_owned("Body009","Wye","WyeDW")
wye.Placement=W2L(wm)

dropB=import_owned("Body006","StraightDropB","StraightDropB")   # wye bottom -> elbow
dropB.Placement=W2L(straight_world(WYE_BOT, V(0,0,-1)))
set_pad_len(dropB, WYE_BOT.z-ELBOW_P1.z)

dwarm=import_owned("Body006","StraightDW","StraightDW")          # wye branch -> DW
dwarm.Placement=W2L(straight_world(WYE_BRANCH, BR_DIR))
set_pad_len(dwarm, BR_LEN)

# shorten existing vertical drop (Straight001/Pad032) to meet wye top
s1=d.getObject("Straight001")
# its A-port (start) stays at E002_P2 going -Z; new length = E002_P2.z - WYE_TOP.z
p032=d.getObject("Pad032")
p032.setExpression('Length',None); p032.Length=float(E002_P2.z-WYE_TOP.z)
p032.touch(); d.getObject("Body007").touch(); d.recompute([p032,d.getObject("Body007")],True,True)

# ---------- verify continuity ----------
rep=open(os.path.join(R,"Drain/_dwbranch_check.txt"),"w")
def w(s): rep.write(s+"\n")
def lp(name, *locs):
    lk=d.getObject(name); P=lk.Placement
    return [toW(P.multVec(V(p))) for p in locs]
a,b=lp("Straight001",(0,0,0),(p032.Length.Value,0,0))
w("Straight001(shortened) A=(%.0f,%.0f,%.0f) B=(%.0f,%.0f,%.0f)  [B should=WYE_TOP (%.0f,%.0f,%.0f)]"%(
   a.x,a.y,a.z,b.x,b.y,b.z, WYE_TOP.x,WYE_TOP.y,WYE_TOP.z))
wt,wb,wbr=lp("Wye",(0,0,127),(0,0,-57.1),(0,89.8,89.8))
w("Wye TOP=(%.0f,%.0f,%.0f) BOT=(%.0f,%.0f,%.0f) BRANCH=(%.0f,%.0f,%.0f)"%(wt.x,wt.y,wt.z,wb.x,wb.y,wb.z,wbr.x,wbr.y,wbr.z))
da,db=lp("StraightDropB",(0,0,0),(dropB.LinkedObject.Tip.Length.Value,0,0))
w("StraightDropB A=(%.0f,%.0f,%.0f) B=(%.0f,%.0f,%.0f)  [A=WYE_BOT, B=ELBOW_P1 (%.0f,%.0f,%.0f)]"%(
   da.x,da.y,da.z,db.x,db.y,db.z, ELBOW_P1.x,ELBOW_P1.y,ELBOW_P1.z))
xa,xb=lp("StraightDW",(0,0,0),(dwarm.LinkedObject.Tip.Length.Value,0,0))
w("StraightDW    A=(%.0f,%.0f,%.0f) B=(%.0f,%.0f,%.0f)  [A=WYE_BRANCH, B near DW(12810,13688,~)]"%(
   xa.x,xa.y,xa.z,xb.x,xb.y,xb.z))
rep.close()

if SAVE:
    for o in d.Objects:
        if o.TypeId=="App::Link":
            try:
                o.Visibility=True
                if App.GuiUp and o.ViewObject is not None: o.ViewObject.Visibility=True
            except Exception: pass
    d.save(); print("SAVED GuiUp=%s"%App.GuiUp)
else:
    print("DRYRUN_DONE")
