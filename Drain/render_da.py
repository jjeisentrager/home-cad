import os, math
import numpy as np
from PIL import Image
import FreeCAD as App, Part
R="/home/joee/github/alieniron/home-cad"
d=App.openDocument(os.path.join(R,"Drain/DrainAssembly.FCStd"))

C4=np.array([200,70,70],float)   # 4" red
C3=np.array([70,170,90],float)   # 3" green
C2=np.array([80,120,210],float)  # 2" blue
CF=np.array([150,150,160],float) # fitting gray
CV=np.array([230,180,60],float)  # vertical stack yellow

tris=[]
def add(shape,col):
    try: vs,fs=shape.tessellate(3.0)
    except Exception: return
    P=np.array([[v.x,v.y,v.z] for v in vs],float)
    for f in fs: tris.append((P[list(f)],col))

def gshape(o):
    # return global shape
    if o.TypeId=="App::Link" and o.LinkedObject is not None and hasattr(o.LinkedObject,'Shape'):
        s=o.LinkedObject.Shape
        if s is None or s.isNull(): return None
        s=s.copy()
        try: s.transformShape(o.getGlobalPlacement().Matrix)
        except Exception: s.transformShape(o.Placement.Matrix)
        return s
    if hasattr(o,'Shape') and o.Shape and not o.Shape.isNull():
        return o.Shape
    return None

def classify(o,s):
    bb=s.BoundBox
    L=o.Label
    if "Wye" in L or "Tee" in L or "Trap" in L or "Flare" in L: return CF
    # vertical?
    dims=sorted([bb.XLength,bb.YLength,bb.ZLength])
    od=dims[1] # middle ~ diameter
    if bb.ZLength>600 and bb.ZLength>3*max(bb.XLength,bb.YLength): return CV
    if od>100: return C4
    if od>75: return C3
    return C2

for o in d.Objects:
    if not getattr(o,"Visibility",False): continue
    if o.TypeId in ("App::Part","Assembly::AssemblyObject","App::Origin","App::LinkGroup"): continue
    s=gshape(o)
    if s is None: continue
    add(s, classify(o,s))

if not tris:
    open(os.path.join(R,"Drain/_da_status.txt"),"w").write("NO TRIS\n"); raise SystemExit
allp=np.vstack([t[0] for t in tris]); center=(allp.max(0)+allp.min(0))/2.0
def n(v): return v/np.linalg.norm(v)
def render(view,up,fname,W=1500,Hh=1000):
    view=n(view);right=n(np.cross(view,up));tup=n(np.cross(right,view))
    def proj(p):
        dd=p-center;return np.array([dd@right,dd@tup,dd@view])
    pr=[(np.array([proj(v) for v in tri]),col) for tri,col in tris]
    sx=np.array([p[:,0] for p,_ in pr]).ravel();sy=np.array([p[:,1] for p,_ in pr]).ravel()
    m=60;scale=min((W-2*m)/(sx.max()-sx.min()),(Hh-2*m)/(sy.max()-sy.min()))
    ox=W/2-scale*(sx.max()+sx.min())/2;oy=Hh/2+scale*(sy.max()+sy.min())/2
    img=np.full((Hh,W,3),255,float);zb=np.full((Hh,W),1e18,float)
    for p,col in pr:
        a,b,c=p;nz=np.cross(b-a,c-a);nn=np.linalg.norm(nz)
        if nn==0:continue
        nz=nz/nn
        if nz[2]<0:nz=-nz
        inten=min(1.0,0.34+0.7*max(0.12,abs(nz[2])));shade=np.clip(col*inten,0,255)
        xs=ox+scale*p[:,0];ys=oy-scale*p[:,1];zs=p[:,2]
        x0=int(max(0,math.floor(xs.min())));x1=int(min(W-1,math.ceil(xs.max())))
        y0=int(max(0,math.floor(ys.min())));y1=int(min(Hh-1,math.ceil(ys.max())))
        if x1<x0 or y1<y0:continue
        ax,ay=xs[0],ys[0];bx,by=xs[1],ys[1];cx,cy=xs[2],ys[2]
        det=(by-cy)*(ax-cx)+(cx-bx)*(ay-cy)
        if abs(det)<1e-9:continue
        yy,xx=np.mgrid[y0:y1+1,x0:x1+1]
        l1=((by-cy)*(xx-cx)+(cx-bx)*(yy-cy))/det;l2=((cy-ay)*(xx-cx)+(ax-cx)*(yy-cy))/det;l3=1-l1-l2
        ins=(l1>=-0.002)&(l2>=-0.002)&(l3>=-0.002)
        if not ins.any():continue
        z=l1*zs[0]+l2*zs[1]+l3*zs[2]
        sz=zb[y0:y1+1,x0:x1+1];cl=ins&(z<sz);sz[cl]=z[cl]
        si=img[y0:y1+1,x0:x1+1];si[cl]=shade
    Image.fromarray(img.astype(np.uint8)).save(os.path.join(R,fname))
# Plan: top-down. +X south is down, +Y east is right. view -Z, up = -X (so south=down)
render(np.array([0,0,-1.0]),np.array([-1.0,0,0]),"Drain/da_plan.png",1500,1100)
# Iso
render(n(np.array([0.6,0.6,-0.5])),np.array([0,0,1.0]),"Drain/da_iso.png",1400,1100)
# Elevation looking West (-Y): project X(south)-Z. up=+Z, view=+Y? to see south slope
render(np.array([0,1.0,0]),np.array([0,0,1.0]),"Drain/da_elevX.png",1600,800)
open(os.path.join(R,"Drain/_da_status.txt"),"w").write("DONE tris=%d center=%s\n"%(len(tris),center))
