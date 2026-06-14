import FreeCAD as App, Part
R="/home/joee/github/alieniron/home-cad"
rep=open(R+"/Drain/_align_fix.txt","w",buffering=1)
def L(*a): rep.write(" ".join(str(x) for x in a)+"\n")
d=App.openDocument(R+"/Drain/DrainLaundry.FCStd")
p=d.getObject("Pad035")
L("expr before:",p.ExpressionEngine,"len=",p.Length.Value)
p.setExpression('Length','250 "')
d.recompute()
L("expr after :",p.ExpressionEngine,"len=",p.Length.Value)
# verify in House world
h=App.openDocument(R+"/House/House.FCStd"); h.recompute()
link=h.getObject("DrainLaundry"); m=link.LinkPlacement.Matrix
dl=App.getDocument("DrainLaundry"); pt=dl.getObject("PTrap")
s=pt.Shape.copy(); s.transformShape(m)
b=s.BoundBox
L("PTrap world bbox X[%.1f,%.1f] Y[%.1f,%.1f] Z[%.1f,%.1f]"%(b.XMin,b.XMax,b.YMin,b.YMax,b.ZMin,b.ZMax))
# vertical (Z-axis) circular openings near top -> candidate trap inlet
L("vertical circular openings (axis~Z):")
for e in s.Edges:
    if isinstance(e.Curve,Part.Circle):
        ax=e.Curve.Axis
        if abs(abs(ax.z)-1)<0.1:   # axis vertical
            c=e.Curve.Center
            L("   center=(%.1f,%.1f,%.1f) r=%.1f"%(c.x,c.y,c.z,e.Curve.Radius))
L("TUB stub world=(14977.3,7473.9, Z541-611)")
if App.GuiUp: d.save(); L("SAVED GuiUp=1")
rep.close()
