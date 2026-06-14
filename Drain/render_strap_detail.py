import os, math, numpy as np
from PIL import Image
import FreeCAD as App, Part
R="/home/joee/github/alieniron/home-cad"
M3=App.Matrix(0,-1,0,13722.4,0,0,1,7187.0,-1,0,0,2984.9,0,0,0,1)
SINK=np.array([70,120,200],float); DW=np.array([225,90,45],float)
STR=np.array([150,160,175],float); JOI=np.array([205,180,140],float)
tris=[]
def add(shape,col):
    vs,fs=shape.tessellate(1.2)
    P=np.array([[v.x,v.y,v.z] for v in vs],float)
    for f in fs: tris.append((P[list(f)],col))
d=App.openDocument(os.path.join(R,"Drain/DrainAddOn.FCStd"))
baked={"STrap":STR,"Sweep90":STR,"DWHose":DW}
# clip to sink-end region (world)
def inreg(bb): return bb.XMax>12700 and bb.XMin<13750 and bb.YMax>13350 and bb.ZMax>2350
for o in d.Objects:
    if not getattr(o,"Visibility",False): continue
    if o.Name in baked and hasattr(o,'Shape') and o.Shape and not o.Shape.isNull():
        s=o.Shape.copy(); s.transformShape(M3)
        if inreg(s.BoundBox): add(s, baked[o.Name])
    elif o.TypeId=="App::Link" and o.LinkedObject is not None and hasattr(o.LinkedObject,'Shape'):
        s=o.LinkedObject.Shape
        if s is None or s.isNull(): continue
        s=s.copy(); s.transformShape(o.Placement.Matrix); s.transformShape(M3)
        if inreg(s.BoundBox): add(s, SINK)
# subfloor plane indicator? add joists near region
b=App.openDocument(os.path.join(R,"Basement/Basement.FCStd"))
try:
    for sol in b.getObject("Floor_Joists").Shape.Solids:
        bb=sol.BoundBox
        if 12700<bb.Center.x<13800 and bb.YMax>13300 and bb.ZMin<2600: add(sol,JOI)
except Exception: pass
def n(v): return v/np.linalg.norm(v)
allp=np.vstack([t[0] for t in tris]); center=(allp.max(0)+allp.min(0))/2.0
def render(view,up,fname,W=1300,Hh=1100):
    view=n(view); right=n(np.cross(view,up)); tup=n(np.cross(right,view))
    def proj(p):
        dd=p-center; return np.array([dd@right,dd@tup,dd@view])
    pr=[(np.array([proj(v) for v in tri]),col) for tri,col in tris]
    sx=np.array([p[:,0] for p,_ in pr]).ravel(); sy=np.array([p[:,1] for p,_ in pr]).ravel()
    m=60; scale=min((W-2*m)/(sx.max()-sx.min()),(Hh-2*m)/(sy.max()-sy.min()))
    ox=W/2-scale*(sx.max()+sx.min())/2; oy=Hh/2+scale*(sy.max()+sy.min())/2
    img=np.full((Hh,W,3),255,float); zb=np.full((Hh,W),1e18,float)
    for p,col in pr:
        a,bb,c=p; nz=np.cross(bb-a,c-a); nn=np.linalg.norm(nz)
        if nn==0: continue
        nz=nz/nn
        inten=min(1.0,0.34+0.7*max(0.12,abs(nz[2]))); shade=np.clip(col*inten,0,255)
        xs=ox+scale*p[:,0]; ys=oy-scale*p[:,1]; zs=p[:,2]
        x0=int(max(0,math.floor(xs.min())));x1=int(min(W-1,math.ceil(xs.max())))
        y0=int(max(0,math.floor(ys.min())));y1=int(min(Hh-1,math.ceil(ys.max())))
        if x1<x0 or y1<y0: continue
        ax,ay=xs[0],ys[0];bx,by=xs[1],ys[1];cx,cy=xs[2],ys[2]
        det=(by-cy)*(ax-cx)+(cx-bx)*(ay-cy)
        if abs(det)<1e-9: continue
        yy,xx=np.mgrid[y0:y1+1,x0:x1+1]
        l1=((by-cy)*(xx-cx)+(cx-bx)*(yy-cy))/det; l2=((cy-ay)*(xx-cx)+(ax-cx)*(yy-cy))/det; l3=1-l1-l2
        ins=(l1>=-0.002)&(l2>=-0.002)&(l3>=-0.002)
        if not ins.any(): continue
        z=l1*zs[0]+l2*zs[1]+l3*zs[2]
        sz=zb[y0:y1+1,x0:x1+1]; cl=ins&(z<sz); sz[cl]=z[cl]
        si=img[y0:y1+1,x0:x1+1]; si[cl]=shade
    Image.fromarray(img.astype(np.uint8)).save(os.path.join(R,fname))
# elevation looking -Y (X-Z plane): clearest S-trap + loop view
render(np.array([0,-1.0,0]),np.array([0,0,1.0]),"Drain/strap_detail_elev.png")
render(n(np.array([0.5,0.6,-0.4])),np.array([0,0,1.0]),"Drain/strap_detail_iso.png")
open(os.path.join(R,"Drain/strap_detail_status.txt"),"w").write("OK tris=%d\n"%len(tris))
