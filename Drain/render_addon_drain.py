import os, math, numpy as np
from PIL import Image
import FreeCAD as App, Part
R="/home/joee/github/alieniron/home-cad"
M3=App.Matrix(0,-1,0,13722.4,0,0,1,7187.0,-1,0,0,2984.9,0,0,0,1)
d=App.openDocument(os.path.join(R,"Drain/DrainAddOn.FCStd"))
tris=[]
C=np.array([90,140,200],float); CF=np.array([150,150,160],float); CW=np.array([210,120,90],float)
def add(s,col):
    try: vs,fs=s.tessellate(4.0)
    except Exception: return
    P=np.array([[v.x,v.y,v.z] for v in vs],float)
    for f in fs: tris.append((P[list(f)],col))
for o in d.Objects:
    if not getattr(o,"Visibility",False): continue
    if o.TypeId in ("App::Part","Assembly::AssemblyObject","App::Origin","App::LinkGroup"): continue
    s=None
    if o.TypeId=="App::Link" and o.LinkedObject is not None and hasattr(o.LinkedObject,'Shape'):
        s=o.LinkedObject.Shape
        if s and not s.isNull(): s=s.copy(); s.transformShape(o.Placement.Matrix)
    elif o.TypeId=="Part::Feature" and o.Shape and not o.Shape.isNull():
        s=o.Shape.copy()    # baked features: world = M3*Shape (placement inert)
    else: continue
    if s is None or s.isNull(): continue
    s.transformShape(M3)
    nm=o.Label
    col = CW if "Hose" in nm else (CF if any(k in nm for k in("Wye","Trap","Elbow","Sweep","Flare")) else C)
    add(s,col)
allp=np.vstack([t[0] for t in tris]); center=(allp.max(0)+allp.min(0))/2.0
def n(v): return v/np.linalg.norm(v)
def render(view,up,fname,W=1600,H=1000):
    view=n(view); right=n(np.cross(view,up)); tup=n(np.cross(right,view))
    def proj(p): dd=p-center; return np.array([dd@right,dd@tup,dd@view])
    pr=[(np.array([proj(v) for v in tri]),col) for tri,col in tris]
    sx=np.array([p[:,0] for p,_ in pr]).ravel(); sy=np.array([p[:,1] for p,_ in pr]).ravel()
    m=60; scale=min((W-2*m)/(sx.max()-sx.min()),(H-2*m)/(sy.max()-sy.min()))
    ox=W/2-scale*(sx.max()+sx.min())/2; oy=H/2+scale*(sy.max()+sy.min())/2
    img=np.full((H,W,3),255,float); zb=np.full((H,W),1e18,float)
    for p,col in pr:
        a,b,c=p; nz=np.cross(b-a,c-a); nn=np.linalg.norm(nz)
        if nn==0: continue
        nz=nz/nn
        if nz[2]<0: nz=-nz
        inten=min(1.0,0.35+0.7*max(0.12,abs(nz[2]))); shade=np.clip(col*inten,0,255)
        xs=ox+scale*p[:,0]; ys=oy-scale*p[:,1]; zs=p[:,2]
        x0=int(max(0,math.floor(xs.min()))); x1=int(min(W-1,math.ceil(xs.max())))
        y0=int(max(0,math.floor(ys.min()))); y1=int(min(H-1,math.ceil(ys.max())))
        if x1<x0 or y1<y0: continue
        ax,ay=xs[0],ys[0]; bx,by=xs[1],ys[1]; cx,cy=xs[2],ys[2]
        det=(by-cy)*(ax-cx)+(cx-bx)*(ay-cy)
        if abs(det)<1e-9: continue
        yy,xx=np.mgrid[y0:y1+1,x0:x1+1]
        l1=((by-cy)*(xx-cx)+(cx-bx)*(yy-cy))/det; l2=((cy-ay)*(xx-cx)+(ax-cx)*(yy-cy))/det; l3=1-l1-l2
        ins=(l1>=-0.003)&(l2>=-0.003)&(l3>=-0.003)
        if not ins.any(): continue
        z=l1*zs[0]+l2*zs[1]+l3*zs[2]
        sz=zb[y0:y1+1,x0:x1+1]; cl=ins&(z<sz); sz[cl]=z[cl]
        si=img[y0:y1+1,x0:x1+1]; si[cl]=shade
    Image.fromarray(img.astype(np.uint8)).save(os.path.join(R,fname))
# Elevation looking NORTH (+X): see Y(west<-) vs Z(up).  view=+X, up=+Z
render(np.array([1.0,0,0]),np.array([0,0,1.0]),"Drain/addon_west_elev.png",1700,900)
render(n(np.array([0.6,-0.6,-0.45])),np.array([0,0,1.0]),"Drain/addon_west_iso.png",1500,1000)
open(os.path.join(R,"Drain/_addrender.txt"),"w").write("DONE center=%s\n"%center)
