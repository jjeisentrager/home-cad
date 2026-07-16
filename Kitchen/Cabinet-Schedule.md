# Kitchen Cabinet Schedule

Real cabinet units (carcass + doors) in `Kitchen/Kitchen_Cabinets.FCStd`. Standard sizes: widths in 3" increments, base 34½"×24", wall 36"×12". Dimensions are **W × H × D in inches**.

| # | Cabinet | Type | W × H × D | Doors | Location |
|---|---------|------|-----------|-------|----------|
| 1 | B-Cnr-F | BASE | 24 × 34.5 × 24 | 1 full-height door | Corner — 24" door on the FRONT wall |
| 2 | B-Cnr-E | BASE | 24 × 34.5 × 24 | 1 full-height door | Corner — 24" door on the STOVE wall |
| 3 | B-F-21 | BASE | 21 × 34.5 × 24 | drawer + 1 door | Front wall — corner→sink |
| 4 | B-F-sink | BASE | 36 × 34.5 × 24 | 2 doors (no drawer) | Front wall — under sink window |
| 5 | B-F-15 | BASE | 15 × 34.5 × 24 | drawer + 1 door | Front wall — end, next to slider |
| 6 | B-E-36 | BASE | 36 × 34.5 × 24 | drawer + 2 doors | Stove wall — corner→range |
| 7 | B-E-36c | BASE | 36 × 34.5 × 24 | drawer + 2 doors | Stove wall — corner→range |
| 8 | B-E-36b | BASE | 36 × 34.5 × 24 | drawer + 2 doors | Stove wall — range→fridge |
| 9 | B-E-30 | BASE | 30 × 34.5 × 24 | drawer + 2 doors | Stove wall — range→fridge |
| 10 | B-E-f36 | BASE | 36 × 34.5 × 24 | drawer + 2 doors | Stove wall — west of fridge |
| 11 | B-E-f30 | BASE | 30 × 34.5 × 24 | drawer + 2 doors | Stove wall — west of fridge |
| 12 | B-E-f15 | BASE | 15 × 34.5 × 24 | drawer + 1 door | Stove wall — west of fridge (wall end) |
| 13 | U-F-12 | WALL | 12 × 36 × 12 | 1 door | Front wall — flanks diagonal (corner side) |
| 14 | U-F-30 | WALL | 30 × 36 × 12 | 2 doors | Front wall — end, next to slider |
| 15 | U-E-12 | WALL | 12 × 36 × 12 | 1 door | Stove wall — flanks diagonal (corner side) |
| 16 | U-E-36 | WALL | 36 × 36 × 12 | 2 doors | Stove wall — range→fridge |
| 17 | U-E-30 | WALL | 30 × 36 × 12 | 2 doors | Stove wall — range→fridge |
| 18 | U-E-f36 | WALL | 36 × 36 × 12 | 2 doors | Stove wall — west of fridge |
| 19 | U-E-f30 | WALL | 30 × 36 × 12 | 2 doors | Stove wall — west of fridge |
| 20 | U-E-f15 | WALL | 15 × 36 × 12 | 1 door | Stove wall — west of fridge (wall end) |
| 21 | U-CNR (diagonal corner) | WALL | 24×24 × 36 × 12 | 1 angled door | Inside corner (diagonal) |
| 22 | U-E-OF | WALL | 36 × 24 × 24 | 2 doors | Stove wall — over the refrigerator |

### Notes
- **Lower corner:** 24" square corner base cabinet, an equal 24" **full-height door** on each wall (`B-Cnr-F`/`B-Cnr-E`) — no drawer.
- **West of the fridge:** the run continues to the end of the wall — base `B-E-f36`/`f30`/`f15` and matching uppers `U-E-f36`/`f30`/`f15`, with the countertop extended (into the Main-side V_p267 wall).
- **Upper corner:** 24×24" diagonal cabinet flanked by a 12" cabinet on each wall.
- **Sink base** has doors only (no drawer). **Over-fridge** is 24" deep. Countertop top at 940 mm.
- **Fillers:** small (≤ ~2") filler strips take up slack — standard trim, not cabinets.
