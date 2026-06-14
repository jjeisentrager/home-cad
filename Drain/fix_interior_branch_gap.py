# -*- coding: utf-8 -*-
"""TASK 1: close the gap in the interior-toilet drain branch.

The interior closet drain straight (link 'Straight009' / label Straight022,
body Body027, Tip Pad087) was shifted +96.7mm toward the toilet to follow the
relocated 12"-rough closet bend, but its length is pinned by the expression
`Pad087.Length = 44 "` (=1117.6mm), so the raw length the prior move set never
took -> a 96.6mm gap opened at the STACK end (Straight022.Edge3 vs Elbow006 rim
at assembly X=577.6; the straight end sits at X=674.2).

Fix: clear the Length expression and set it to 1214.2mm so the stack end reaches
the Elbow006 socket rim (matching how the correct NORTH branch seats: straight
end exactly at the elbow rim). Then un-suppress Joint034 (Fixed, the toilet-end
joint Straight022<->Elbow011) to re-lock the connection. The earlier move shifted
the elbow AND the straight by the same +96.7, so their relative position is
unchanged and the Fixed joint is already satisfied (no part moves).

Run headless (freecadcmd); the assembly solver is NOT invoked (only Body027 is
recomputed). GuiDocument.xml is re-injected by the surrounding shell step.
"""
import os, FreeCAD as App
R = "/home/joee/github/alieniron/home-cad"
d = App.openDocument(os.path.join(R, "Drain/DrainAssembly.FCStd"))

pad = d.getObject("Pad087")
pad.setExpression('Length', None)         # drop the `44 "` pin
pad.Length = 1214.2                        # 96.6mm longer -> stack end at X=577.6
d.getObject("Body027").recompute()         # regenerate only this straight's solid

d.getObject("Joint034").Suppressed = False # restore toilet-end Fixed joint

d.save()

# verify
o = d.getObject("Straight009")
s = o.LinkedObject.Shape.copy(); s.transformShape(o.Placement.Matrix)
xs = [f.CenterOfMass.x for f in s.Faces
      if f.Surface.TypeId == "Part::GeomPlane" and f.Area > 1400]
rep = open(os.path.join(R, "Drain/gap_fix_report.txt"), "w")
rep.write("Pad087.Length now = %.2f (expr=%s)\n" % (pad.Length.Value, pad.ExpressionEngine))
rep.write("Straight022 end-face X centers = %s  (want a stack end ~577.6)\n" % sorted(xs))
rep.write("Joint034.Suppressed = %s\n" % d.getObject("Joint034").Suppressed)
rep.close()
print("GAPFIX_DONE")
