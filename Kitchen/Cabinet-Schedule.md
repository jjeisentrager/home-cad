# Kitchen Cabinet Schedule

Real cabinet units (carcass + doors) modelled in `Kitchen/Kitchen_Cabinets.FCStd`. All dimensions are **standard**: widths in 3" increments, base 34½"×24", wall 36"×12". Dimensions are **W × H × D in inches**.

| # | Cabinet | Type | W × H × D | Doors | Location |
|---|---------|------|-----------|-------|----------|
| 1 | B-Cnr-F | BASE | 24 × 34.5 × 24 | 1 door | Corner — 24" door on the FRONT wall |
| 2 | B-Cnr-E | BASE | 24 × 34.5 × 24 | 1 door | Corner — 24" door on the STOVE wall |
| 3 | B-F-21 | BASE | 21 × 34.5 × 24 | drawer + 1 door | Front wall — corner→sink |
| 4 | B-F-sink | BASE | 36 × 34.5 × 24 | 2 doors (no drawer) | Front wall — under sink window |
| 5 | B-F-30 | BASE | 30 × 34.5 × 24 | drawer + 2 doors | Front wall — DW→slider |
| 6 | B-E-36 | BASE | 36 × 34.5 × 24 | drawer + 2 doors | Stove wall — corner→range |
| 7 | B-E-36c | BASE | 36 × 34.5 × 24 | drawer + 2 doors | Stove wall — corner→range |
| 8 | B-E-36b | BASE | 36 × 34.5 × 24 | drawer + 2 doors | Stove wall — range→fridge |
| 9 | B-E-30 | BASE | 30 × 34.5 × 24 | drawer + 2 doors | Stove wall — range→fridge |
| 10 | U-F-12 | WALL | 12 × 36 × 12 | 1 door | Front wall — flanks diagonal (corner side) |
| 11 | U-F-24 | WALL | 24 × 36 × 12 | 2 doors | Front wall — west of sink window |
| 12 | U-F-21 | WALL | 21 × 36 × 12 | 1 door | Front wall — west of sink window |
| 13 | U-E-12 | WALL | 12 × 36 × 12 | 1 door | Stove wall — flanks diagonal (corner side) |
| 14 | U-E-36 | WALL | 36 × 36 × 12 | 2 doors | Stove wall — range→fridge |
| 15 | U-E-30 | WALL | 30 × 36 × 12 | 2 doors | Stove wall — range→fridge |
| 16 | U-CNR (diagonal corner) | WALL | 24×24 × 36 × 12 | 1 angled door | Inside corner (diagonal — unchanged) |
| 17 | U-E-OF | WALL | 36 × 24 × 24 | 2 doors | Stove wall — over the refrigerator |

### Notes
- **Lower corner:** a 24" square corner base cabinet with an **equal 24" door on each wall** (`B-Cnr-F` front, `B-Cnr-E` stove wall) — symmetric, a cabinet face on both sides. Two full-depth base cabinets can't both occupy an inside corner, so this shared-carcass corner is the symmetric way to get an equal-width cabinet on each wall (replaces the 36×36" lazy-Susan).
- **Upper corner:** still a 24×24" **diagonal** cabinet (`U-CNR`), flanked by a 12" cabinet on each wall.
- **Sink base** (B-F-sink) has doors only (no drawer) to clear the bowl.
- **Over-fridge** (U-E-OF) is 24" deep to sit flush with the refrigerator.
- **Countertop:** continuous slab, top at 940 mm (37") to keep the sink/range datum (base box is the standard 34½").
- **Window moved:** the stove-wall window was slid 127 mm toward the range so a 12" upper flanks the diagonal corner on that wall; `Outlet_E2` moved to the range→fridge run.
- **Fillers:** small filler strips (≤ ~2") take up slack between runs and appliances/windows — standard trim, not cabinets.
