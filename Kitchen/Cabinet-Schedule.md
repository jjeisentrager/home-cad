# Kitchen Cabinet Schedule

Real cabinet units (carcass + doors) in `Kitchen/Kitchen_Cabinets.FCStd`. Standard sizes: widths in 3" increments, base 34½"×24", wall 36"×12". Dimensions are **W × H × D in inches**.

| # | Cabinet | Type | W × H × D | Doors | Location |
|---|---------|------|-----------|-------|----------|
| 1 | B-Cnr-F | BASE | 24 × 34.5 × 24 | 1 door | Corner — 24" door on the FRONT wall |
| 2 | B-Cnr-E | BASE | 24 × 34.5 × 24 | 1 door | Corner — 24" door on the STOVE wall |
| 3 | B-F-21 | BASE | 21 × 34.5 × 24 | drawer + 1 door | Front wall — corner→sink |
| 4 | B-F-sink | BASE | 36 × 34.5 × 24 | 2 doors (no drawer) | Front wall — under sink window |
| 5 | B-F-15 | BASE | 15 × 34.5 × 24 | drawer + 1 door | Front wall — end, next to slider |
| 6 | B-E-36 | BASE | 36 × 34.5 × 24 | drawer + 2 doors | Stove wall — corner→range |
| 7 | B-E-36c | BASE | 36 × 34.5 × 24 | drawer + 2 doors | Stove wall — corner→range |
| 8 | B-E-36b | BASE | 36 × 34.5 × 24 | drawer + 2 doors | Stove wall — range→fridge |
| 9 | B-E-30 | BASE | 30 × 34.5 × 24 | drawer + 2 doors | Stove wall — range→fridge |
| 10 | U-F-12 | WALL | 12 × 36 × 12 | 1 door | Front wall — flanks diagonal (corner side) |
| 11 | U-F-30 | WALL | 30 × 36 × 12 | 2 doors | Front wall — end, next to slider |
| 12 | U-E-12 | WALL | 12 × 36 × 12 | 1 door | Stove wall — flanks diagonal (corner side) |
| 13 | U-E-36 | WALL | 36 × 36 × 12 | 2 doors | Stove wall — range→fridge |
| 14 | U-E-30 | WALL | 30 × 36 × 12 | 2 doors | Stove wall — range→fridge |
| 15 | U-CNR (diagonal corner) | WALL | 24×24 × 36 × 12 | 1 angled door | Inside corner (diagonal) |
| 16 | U-E-OF | WALL | 36 × 24 × 24 | 2 doors | Stove wall — over the refrigerator |

### Notes
- **Lower corner:** 24" square corner base cabinet with an equal 24" door on each wall (`B-Cnr-F`/`B-Cnr-E`).
- **Upper corner:** 24×24" diagonal cabinet (`U-CNR`) flanked by a 12" cabinet on each wall.
- **Slider end:** the front run was shortened 15" at the patio door — base end cabinet 30"→**15"** (`B-F-15`), and the two end uppers (24"+21") became a single **30"** (`U-F-30`). The **slider was moved 15" (381 mm) toward the counter** (rough opening + door) so the ~50 mm gap to the counter end is unchanged.
- **Sink base** has doors only (no drawer). **Over-fridge** is 24" deep. Countertop top at 940 mm (37").
- **Fillers:** small (≤ ~2") filler strips take up slack — standard trim, not cabinets.
