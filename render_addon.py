# -*- coding: utf-8 -*-
"""Render AddOn_Assembly in consistent WORLD coords: top-level links use their
own obj.Shape; Assembly001's children (the kitchen) get A1.Placement applied."""
import os, math
import numpy as np
from PIL import Image
import FreeCAD as App
import FreeCADGui as Gui  # noqa

ROOT = "/home/joee/github/alieniron/home-cad"
rep = open(os.path.join(ROOT, "addon_report.txt"), "w")
def L(*a): rep.write(" ".join(str(x) for x in a) + "\n")

ad = App.openDocument(os.path.join(ROOT, "AddOn/AddOn_Assembly.FCStd"))
ad.recompute()
A1 = ad.getObject("Assembly001").Placement

TAN = np.array([196, 170, 120], float)
GRAY = np.array([200, 200, 205], float)
BLUE = np.array([120, 150, 200], float)
BLACK=np.array([35,35,40],float); FABRIC=np.array([150,143,132],float)
STEEL=np.array([110,113,120],float); STEELY=np.array([120,150,200],float)
def color_for(name):
    n = name.lower()
    if any(k in n for k in ("fram", "joist", "subfloor", "roof", "body")): return TAN
    if "beam" in n: return STEEL
    if "slider" in n: return BLACK
    if n.startswith("tv"): return BLACK
    if "couch" in n: return FABRIC
    if any(k in n for k in ("island", "counter", "kitchen")): return GRAY
    return STEELY

a1_children = set()
a1 = ad.getObject("Assembly001")
if hasattr(a1, "Group"):
    a1_children = {o.Name for o in a1.Group}

tris = []
for o in ad.Objects:
    if o.TypeId != "App::Link": continue
    sh = getattr(o, "Shape", None)
    if sh is None or not sh.Faces: continue
    c = sh.copy()
    A1inv = A1.inverse()
    if o.Name not in a1_children:
        c.Placement = A1inv.multiply(c.Placement)   # world -> native frame
    b = c.BoundBox
    L("%-16s X[%.0f,%.0f] Y[%.0f,%.0f] Z[%.0f,%.0f]" %
      (o.Name, b.XMin, b.XMax, b.YMin, b.YMax, b.ZMin, b.ZMax))
    col = color_for(o.Name)
    try: vs, fs = c.tessellate(4.0)
    except Exception: continue
    P = np.array([[v.x, v.y, v.z] for v in vs], float)
    for f in fs: tris.append((P[list(f)], col))
L("tris %d" % len(tris))

def n(v): return v/np.linalg.norm(v)
def render(view, up, fname, W=1500, Hh=1100):
    view=n(view); up=np.array(up,float); right=n(np.cross(view,up)); tup=n(np.cross(right,view))
    allp=np.vstack([t[0] for t in tris]); ctr=(allp.max(0)+allp.min(0))/2
    def pr(p): d=p-ctr; return np.array([d@right,d@tup,d@view])
    pj=[(np.array([pr(v) for v in t]),c) for t,c in tris]
    sx=np.array([p[:,0] for p,_ in pj]).ravel(); sy=np.array([p[:,1] for p,_ in pj]).ravel()
    m=40; sc=min((W-2*m)/(sx.max()-sx.min()),(Hh-2*m)/(sy.max()-sy.min()))
    ox=W/2-sc*(sx.max()+sx.min())/2; oy=Hh/2+sc*(sy.max()+sy.min())/2
    img=np.full((Hh,W,3),247,float); zb=np.full((Hh,W),1e18,float)
    for p,col in pj:
        a,b2,c2=p; nz=np.cross(b2-a,c2-a); nn=np.linalg.norm(nz)
        if nn==0: continue
        nz=nz/nn
        if nz[2]<0: nz=-nz
        sh=np.clip(col*min(1.0,0.35+0.7*max(0.12,abs(nz[2]))),0,255)
        xs=ox+sc*p[:,0]; ys=oy-sc*p[:,1]; zs=p[:,2]
        x0=int(max(0,math.floor(xs.min()))); x1=int(min(W-1,math.ceil(xs.max())))
        y0=int(max(0,math.floor(ys.min()))); y1=int(min(Hh-1,math.ceil(ys.max())))
        if x1<x0 or y1<y0: continue
        ax,ay=xs[0],ys[0]; bx,by=xs[1],ys[1]; cx,cy=xs[2],ys[2]
        det=(by-cy)*(ax-cx)+(cx-bx)*(ay-cy)
        if abs(det)<1e-9: continue
        yy,xx=np.mgrid[y0:y1+1,x0:x1+1]
        l1=((by-cy)*(xx-cx)+(cx-bx)*(yy-cy))/det; l2=((cy-ay)*(xx-cx)+(ax-cx)*(yy-cy))/det; l3=1-l1-l2
        ins=(l1>=-0.001)&(l2>=-0.001)&(l3>=-0.001)
        if not ins.any(): continue
        z=l1*zs[0]+l2*zs[1]+l3*zs[2]; sz=zb[y0:y1+1,x0:x1+1]; cl=ins&(z<sz)
        sz[cl]=z[cl]; si=img[y0:y1+1,x0:x1+1]; si[cl]=sh
    img=img[:,::-1]; Image.fromarray(img.astype(np.uint8)).save(os.path.join(ROOT,fname))

render(np.array([0.0001,0.0001,-1.0]),[0,1.0,0],"addon_plan.png")
render(np.array([0.55,0.6,-0.55]),[0,0,1.0],"addon_iso.png")
rep.close(); print("ADDON_RENDER_DONE")
