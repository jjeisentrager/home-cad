# Kitchen Cabinet Schedule

Real cabinet units (carcass + doors) modelled in `Kitchen/Kitchen_Cabinets.FCStd`. All dimensions are **standard**: widths in 3" increments, base 34½"×24", wall 36"×12". Dimensions are **W × H × D in inches**.

| # | Cabinet | Type | W × H × D | Doors | Location |
|---|---------|------|-----------|-------|----------|
| 1 | B-F-9 | BASE | 9 × 34.5 × 24 | drawer + 1 door | Front wall — corner→sink |
| 2 | B-F-sink | BASE | 36 × 34.5 × 24 | 2 doors (no drawer) | Front wall — under sink window |
| 3 | B-F-30 | BASE | 30 × 34.5 × 24 | drawer + 2 doors | Front wall — DW→slider |
| 4 | B-E-36 | BASE | 36 × 34.5 × 24 | drawer + 2 doors | Stove wall — corner→range |
| 5 | B-E-24 | BASE | 24 × 34.5 × 24 | drawer + 2 doors | Stove wall — corner→range |
| 6 | B-E-36b | BASE | 36 × 34.5 × 24 | drawer + 2 doors | Stove wall — range→fridge |
| 7 | B-E-30 | BASE | 30 × 34.5 × 24 | drawer + 2 doors | Stove wall — range→fridge |
| 8 | B-CNR (diagonal corner) | BASE | 36×36 × 34.5 × 24 | 1 angled door | Inside corner (lazy-Susan) |
| 9 | U-F-12 | WALL | 12 × 36 × 12 | 1 door | Front wall — flanks diagonal (corner side) |
| 10 | U-F-24 | WALL | 24 × 36 × 12 | 2 doors | Front wall — west of sink window |
| 11 | U-F-21 | WALL | 21 × 36 × 12 | 1 door | Front wall — west of sink window |
| 12 | U-E-12 | WALL | 12 × 36 × 12 | 1 door | Stove wall — flanks diagonal (corner side) |
| 13 | U-E-36 | WALL | 36 × 36 × 12 | 2 doors | Stove wall — range→fridge |
| 14 | U-E-30 | WALL | 30 × 36 × 12 | 2 doors | Stove wall — range→fridge |
| 15 | U-CNR (diagonal corner) | WALL | 24×24 × 36 × 12 | 1 angled door | Inside corner (diagonal) |
| 16 | U-E-OF | WALL | 36 × 24 × 24 | 2 doors | Stove wall — over the refrigerator |

### Notes
- **Diagonal corners:** base = 36×36" lazy-Susan; wall = 24×24" diagonal. The wall diagonal is flanked by a **12" cabinet on each wall** (rows U-F-12 & U-E-12).
- **Sink base** (B-F-sink) has doors only (no drawer) to clear the bowl.
- **Over-fridge** (U-E-OF) is 24" deep to sit flush with the refrigerator.
- **Countertop:** continuous slab, top at 940 mm (37") to keep the existing sink/range datum (base box is standard 34½"; the counter makes up the balance).
- **Window moved:** the stove-wall window (`WindowWall`) was slid **127 mm (5") toward the range** so a 12" upper could flank the diagonal corner on that wall too. `Outlet_E2` was relocated to the range→fridge run since the window now covers its old spot.
- **Fillers:** small filler strips (≤ ~2") take up slack between runs and appliances/windows — these are standard trim, not cabinets. No cabinet required a non-standard size.
