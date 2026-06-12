# Michigan Electrical Code 2023 (NEC / NFPA 70-2023) — Quick Reference

> ## ⚠️ READ THIS FIRST — provenance, editions & trust
>
> Three sources back this file:
>
> 1. **Michigan amendments (Part 8)** — quoted from the **official LARA PDF**
>    `2023-Michigan-Electrical-Code-Part8-Final-Rules-eff-2024-03-12.pdf` (this folder). **Authoritative, current (2023).**
> 2. **Verbatim NEC base text — `NEC-2017-fulltext-public-resource-org.txt`** (this folder): the full
>    **NEC 2017** as posted by Public.Resource.org / Internet Archive (a code incorporated-by-reference
>    into law). The base-code numbers below have been **cross-checked against this verbatim text**
>    (confirmed: 110.26 working space, 240.4(D) conductor caps, 240.6 ratings, 250.52/53 ground rod &
>    25 Ω rule, 250.66, 314.16 box fill, 334.30 NM support, 210.8(A) GFCI list, pool 680.x). `grep` it
>    for exact wording.
> 3. **Edition reconciliation** — **Michigan adopts NEC *2023* (2nd printing)**; the verbatim file is
>    **2017**. The overwhelming majority of provisions (ampacity, box fill, grounding, conductor sizing,
>    raceway fill, clearances) are **unchanged 2017→2023**. The handful of dwelling items that *did*
>    change are flagged **[2023 Δ]** below and sourced from the official MI Part 8 PDF (and noted where
>    the 2017 verbatim text differs). For anything not yet confirmed against 2023, a **VERIFY** tag
>    remains — check NFPA LiNK (free login) or UpCodes (free login) for the current text.
>
> **Scope caveat for this project:** detached 1- & 2-family dwellings are built under the **Michigan
> Residential Code (MRC)**, whose electrical chapters (E34xx–E43xx) mirror the NEC and are openly
> readable on UpCodes — see `Michigan-Residential-Code-2021-reference.md`. The MEC/NEC governs
> everything else and is the technical backbone. Items most relevant to a private home are flagged **🏠**.
>
> Units in US customary as the NEC uses them. `A`=amps, `V`=volts, `VA`=volt-amps, `AWG`=wire gauge,
> `OCPD`=overcurrent protective device, `GEC`=grounding-electrode conductor, `EGC`=equipment-grounding
> conductor, `GFCI`/`AFCI` as usual.

---

## Michigan adoption & key state amendments (Part 8 — authoritative)

**R 408.30801** — Adopts the **NEC 2023, second printing** (incl. TIAs 70-23-1…13, Errata 70-23-1…6,
and **Annex H**), *except* §§ 80.2, 80.5, 80.15, 80.23, 80.27, 80.29, 80.31, 80.33, 80.35, 90.6.
Also adopts **NFPA 110 (2019)** and **NFPA 111 (2019)** for emergency/standby power.
Effective **March 12, 2024**. Renamed the "Michigan electrical code" (R 408.30807, §80.7).

**Substantive Michigan amendments that change dwelling wiring:**

- **🏠 §230.85 Emergency disconnects (R 408.30870)** — For **1- & 2-family dwellings**, an emergency
  disconnecting means **shall be installed in a readily accessible *outdoor* location on or within sight
  of the dwelling**. Each disconnect is a *service* disconnect; SCCR ≥ available fault current; group if
  >1. Marked **"EMERGENCY DISCONNECT, SERVICE DISCONNECT."** (Exception: where §225.41 met.) Applies on
  service-equipment replacement (except meter-socket/SE-conductor-only swaps).
- **🏠 §250.104(B) Bonding metal piping incl. gas / CSST (R 408.30871)** — Metal piping (incl. gas)
  that can become energized must be bonded; size per **Table 250.122** on the circuit likely to energize
  it. **CSST gas piping** must be bonded to the service grounding-electrode system with a jumper
  **≥ 6 AWG copper**, connected between the point of delivery and the first downstream CSST fitting
  (unless the listed CSST is approved without additional bonding).
- **🏠 §334.10 / §334.12(A) NM cable "Romex" (R 408.30873)** — Type NM/NMC **permitted** in 1- & 2-family
  dwellings + attached/detached garages & storage buildings, and multifamily dwellings + detached garages;
  in structures >1 floor above grade it must be concealed behind a **15-minute thermal/finish barrier**.
  **Not permitted**: as service-entrance cable; embedded in concrete/aggregate; in hazardous locations;
  hoistways; battery rooms; exposed in suspended ceilings of other than 1-/2-/multifamily dwellings.
- **Permits (R 408.30818, §80.19)** — expire **180 days** after issuance; extended 180 days from last
  inspection; one 180-day extension allowed. No permit for lamp/cord swaps or minor repair (switch/fuse/
  socket/receptacle replacement).
- **Plans required (R 408.30819, §80.21)** — detailed plans/specs required when service or feeder
  equipment ampacity is **> 400 A** (≤ 1000 V) **and** calculated floor area **> 3,500 ft²**. All
  conductors assumed copper unless stated.
- **§§700.9 / 701.9 (R 408.30838)** — emergency & legally-required standby systems install per NFPA 110/111 (2019).

---

## 🏠 The 30-second home cheat-sheet (verify against NEC 2023 / MRC)

| Thing | Value | Cite |
|---|---|---|
| Min service for a one-family dwelling | **100 A** | 230.79(C) |
| Std breaker/fuse ratings | 15, 20, 25, 30, 35, 40, 45, 50, 60, 70, 80, 90, 100… | 240.6 |
| Copper conductor OCPD cap | 14 AWG→**15 A**, 12 AWG→**20 A**, 10 AWG→**30 A** | 240.4(D) |
| EGC (ground) size | 15 A→14 AWG, 20 A→12, 30–60 A→10, 100 A→8, 200 A→6 (Cu) | T.250.122 |
| Receptacle spacing along walls | no point >**6 ft** from a receptacle (outlets ≤ **12 ft** apart); any wall ≥ **2 ft** wide needs one | 210.52(A) |
| Kitchen countertop receptacles | within **24 in** of any point; spaced ≤ **4 ft**; any counter ≥ 12 in wide | 210.52(C) |
| Small-appliance circuits (kitchen/dining) | **two 20 A** | 210.11(C)(1) |
| Laundry / bathroom circuits | **20 A** each, dedicated | 210.11(C)(2)(3) |
| GFCI (dwelling) | bathrooms, garages, outdoors, crawlspaces, **all basements**, kitchens, laundry, within **6 ft** of any sink/tub/shower | 210.8(A) |
| AFCI (dwelling) | nearly all 120 V 15/20 A outlets in living areas (bedrooms, living, kitchen, halls, laundry…) | 210.12 |
| Tamper-resistant receptacles | required in dwellings | 406.12 |
| Working space in front of panels | depth **≥ 36 in**, width **≥ 30 in** (or equip. width), headroom **≥ 6.5 ft** | 110.26 |
| Panel not allowed in | clothes closets, bathrooms (dwelling); not over steps | 240.24 / 110.26 |
| Ground rod | **≥ 8 ft**, two rods **6 ft** apart unless single ≤ 25 Ω | 250.52 / 250.53 |
| General lighting load | **3 VA/ft²** | 220.12 |
| Box fill per conductor | 14 AWG **2.0 in³**, 12 AWG **2.25**, 10 AWG **2.5** | 314.16(B) |
| NM cable support | within **12 in** of box, every **4.5 ft** | 334.30 |
| Outdoor receptacles | front & back of dwelling, ≤ **6.5 ft** above grade, GFCI, in-use cover | 210.52(E)/406.9 |
| Overhead service drop clearance | **10 ft** (grade/walk), **12 ft** (residential drive), **18 ft** (public road) | 230.24 |

---

# CHAPTER 1 — General

## Article 90 — Introduction
- 90.2 Scope — covers electrical installations; **not** under exclusive utility control, nor ships/aircraft/autos/mines.
- 90.3 Arrangement — Ch. 1–4 apply generally; Ch. 5–7 supplement/modify; Ch. 8 (communications) is *independent* unless referenced; Ch. 9 tables are mandatory where referenced.
- 90.5 "Shall" = mandatory; *Informational Notes* are non-enforceable; *Exceptions* modify the rule.

## Article 100 — Definitions (the ones that matter) 🏠
- **Dwelling unit** — one or more rooms with permanent provisions for living, sleeping, cooking, sanitation.
- **Branch circuit** — conductors between the final OCPD and the outlet(s). **Feeder** — between service equipment (or source) and the final branch-circuit OCPD.
- **Service** — conductors/equipment delivering utility power to the premises wiring. **Service point** = utility/premises boundary.
- **Grounded (neutral) conductor** vs **Grounding conductor (EGC)** vs **Grounding-electrode conductor (GEC)** — distinct; neutral carries current, EGC/GEC do not in normal operation.
- **GFCI** — trips on ~4–6 mA ground-fault (people protection). **AFCI** — detects arcing faults (fire protection).
- **Accessible / Readily accessible** — reachable without removing obstacles / without tools, climbing, or removing panels.
- **Ampacity** — current a conductor can carry continuously without exceeding its temp rating.
- **Continuous load** — max current ≥ 3 hours (size at **125%**).
- **Outlet** — point where current is taken to supply utilization equipment. **Receptacle** — the contact device itself.
- **Bonding** — connecting metal parts to form an electrically conductive path. **Qualified person** — trained on the hazards.

## Article 110 — Requirements for Electrical Installations 🏠
- **110.3** — listing/labeling & installation per instructions.
- **110.12** — neat & workmanlike; unused openings closed.
- **110.14** — terminations; **110.14(C) temperature limitations**: use the **60 °C** column for circuits ≤ 100 A / ≤ 14–1 AWG unless equipment & conductors are listed for higher; **75 °C** common for larger/feeder terminations. Copper-to-aluminum terminals must be listed (CO/ALR devices for 15/20 A).
- **110.26 Working space** — clear space about equipment likely to be serviced energized:
  - **Depth** (Table 110.26(A)(1), 0–150 V to ground): Condition 1 = **3 ft**, Cond. 2 = 3½ ft, Cond. 3 = 4 ft.
  - **Width** ≥ **30 in** or width of equipment, whichever greater; door must open ≥ 90°.
  - **Headroom** ≥ **6.5 ft** (or height of equipment if taller).
  - Dedicated equipment space above panel to structural ceiling / 6 ft; no foreign piping/ducts in it.
  - Equipment ≥ 1200 A & > 6 ft wide → an entrance at each end.
- **110.27** — guard live parts ≥ 50 V.

---

# CHAPTER 2 — Wiring and Protection

## Article 200 — Grounded (Neutral) Conductors
- Identify by **white or gray** (or 3 white stripes). Neutral never used as an EGC except limited legacy cases. Larger than 6 AWG may be re-identified white at terminations.

## Article 210 — Branch Circuits 🏠 (the heart of dwelling wiring)
- **210.8(A) GFCI, dwellings** — **[2023 Δ]** GFCI-protect receptacles in these areas.
  - *Verbatim 2017 list (10):* (1) bathrooms, (2) garages & accessory buildings, (3) outdoors, (4) crawl spaces at/below grade, (5) **unfinished** basement areas, (6) kitchens — **countertop-serving** receptacles, (7) within **6 ft** of a sink, (8) boathouses, (9) within **6 ft** of bathtub/shower, (10) laundry areas.
  - *2023 changes (what MI adopts):* basement coverage → **all areas of basements** (not just unfinished); kitchens → **all** receptacles; range expanded to **125 V–250 V, ≤ 50 A** so it now catches some 240 V appliance receptacles (e.g., ranges/dryers near the listed areas); **dishwashers** (210.8(D)) added; outdoor dwelling outlets (210.8(F)) added in 2020. Confirm the exact 2023 wording on NFPA LiNK / UpCodes for a permit.
- **210.8(F)** — outdoor outlets for dwellings (e.g., A/C units) GFCI-protected.
- **210.11(C)** — required dwelling circuits: **(1)** two 20 A small-appliance (kitchen/dining/pantry); **(2)** one 20 A laundry; **(3)** one 20 A bathroom (serves only bathroom receptacles, or one bathroom's full load).
- **210.12 AFCI** — all 120 V, 15/20 A branch circuits supplying outlets/devices in dwelling kitchens, family/living/dining rooms, parlors, libraries, dens, bedrooms, sunrooms, rec rooms, closets, hallways, laundry areas (essentially everywhere except bath/garage/outdoor). Combination-type AFCI.
- **210.52 Receptacle placement (dwellings):**
  - **(A) General** — no point along the floor line of any wall > **6 ft** from a receptacle (so spacing ≤ **12 ft**); any wall space ≥ **2 ft** wide gets one; counts wall, fixed glass, railings; floor receptacles within **18 in** of wall count.
  - **(B)** small-appliance circuits serve countertop & wall receptacles in kitchen/pantry/dining.
  - **(C) Countertops** — a receptacle within **24 in** of any point along the counter (so ≤ **4 ft** spacing); any counter ≥ **12 in** wide needs one; islands/peninsulas have specific 2023 rules (at least one if ≥ 9 ft²; receptacle may be on/above counter, not face-up unless listed).
  - **(D)** bathroom — receptacle within **3 ft** of each basin's outside edge, on a 20 A circuit.
  - **(E)** outdoors — at least one at front and one at back, ≤ **6.5 ft** above grade.
  - **(F)** laundry receptacle; **(G)** at least one in basement, garage (each car space in 2023), and attached/detached garage with power; **(H)** hallways ≥ **10 ft** get a receptacle.
- **210.70 Lighting outlets** — wall-switch-controlled lighting outlet in every habitable room & bathroom; at least one at stairs, hallways, attached garages, outdoor entrances/exits; switch at each floor level of stairs with ≥ 6 risers.
- **210.19 / 210.20** — conductors sized for ≥ **125%** of continuous + 100% noncontinuous; OCPD likewise.
- **210.21(B)** — receptacle ratings vs circuit; **210.23** permissible loads (15/20 A circuits serve lighting + receptacles; a single fixed appliance ≤ 50% of circuit if shared).
- **210.24** summary table of conductor/OCPD/receptacle per circuit rating.

## Article 215 — Feeders
- Sized for the calculated load, ≥ 125% continuous; EGC per 250.122; min size that carries load & not less than service for single-dwelling feeder. **215.2** ampacity; **83% rule** allowed for a dwelling feeder that's the main power feeder (see 310.12).

## Article 220 — Branch-Circuit, Feeder & Service Calculations 🏠
- **220.12** General lighting: **3 VA/ft²** (dwellings), area from outside dimensions.
- **220.52** Two small-appliance + one laundry = **1500 VA each** added before demand factors.
- **220.42 / Table 220.45** Lighting demand factors: first **3000 VA @ 100%**, 3001–120,000 @ **35%**, remainder @ 25%.
- **220.53** Fixed appliances (≥ 4) — **75%** demand factor (not range/dryer/HVAC).
- **220.54** Electric clothes dryer — **5000 VA** or nameplate, whichever larger; demand factors for many units.
- **220.55 / Table 220.55** Electric ranges/ovens — demand for one 8–12 kW range = **8 kW**; table for multiple.
- **220.82 Optional dwelling method** 🏠 — for a dwelling served by single 120/240 V set: total of general loads (3 VA/ft² + 1500 VA each circuit + appliance nameplates) taken at **first 10 kVA @ 100% + remainder @ 40%**, then add the **larger** of A/C or heat at its demand %. Usually yields the service size.
- **220.83** Optional calc for existing dwelling adding load.

## Article 225 — Outside Branch Circuits & Feeders
- Clearances mirror 230.24; **225.18** overhead spans; detached-structure feeder needs disconnect (225.31) and a grounding electrode at the building (250.32). **225.41** emergency disconnect option referenced by MI §230.85.

## Article 230 — Services 🏠
- **230.9** — service conductors **3 ft** from windows/doors/porches (that can be opened); 3 ft from openings.
- **230.24 Overhead clearances**: **10 ft** above grade/walk/platform (≤ 150 V to ground); **12 ft** over residential property & driveways; **18 ft** over public streets/roads/parking. 8 ft above roof (with exceptions for low-slope/limited overhang).
- **230.26** point of attachment ≥ 10 ft above grade.
- **230.43** wiring methods for service conductors.
- **230.70** service disconnect — readily accessible, outside or nearest the point of entry; **not** in bathrooms.
- **230.71** number — **one to six** disconnects per service; **2020+: each in a separate enclosure** (or a listed single assembly / single panel with a main). *(VERIFY current MI/2023 wording.)*
- **230.79(C)** — one-family dwelling service disconnect rating **≥ 100 A**, 3-wire.
- **230.82** what may be connected on the supply side (meter, surge devices, etc.).
- **🏠 230.85 Emergency disconnect** — *(see Michigan amendment above; 2023 NEC + MI both require an outdoor, readily accessible emergency/service disconnect on 1- & 2-family dwellings, marked "EMERGENCY DISCONNECT, SERVICE DISCONNECT").*

## Article 240 — Overcurrent Protection 🏠
- **240.4(B)** next-standard-size-up rule allowed for OCPD ≤ **800 A** where conductor ampacity doesn't match a standard size.
- **240.4(D)** small-conductor cap (copper): 14 AWG → 15 A, 12 AWG → 20 A, 10 AWG → 30 A. (Aluminum: 12 → 15 A, 10 → 25 A.)
- **240.6** standard ratings: 15, 20, 25, 30, 35, 40, 45, 50, 60, 70, 80, 90, 100, 110, 125, 150, 175, 200…
- **240.21** tap rules (10-ft, 25-ft taps).
- **240.24** OCPDs **readily accessible**, 6.5 ft max to operating handle; **not in bathrooms or clothes closets** of dwellings; not over steps; protected from physical damage.
- Breakers used as switches must be listed **SWD/HID** where switching luminaires.

## Article 242 — Overvoltage Protection (SPDs / surge arresters)
- Type 1 (line side) / Type 2 (load side) SPDs; **230.67 (2020+) requires a surge-protective device for dwelling-unit services** — VERIFY (often cited 230.67, enforced with 242).

## Article 250 — Grounding & Bonding 🏠
- **250.24** — at service: bond grounded (neutral) to enclosure via **main bonding jumper**; neutral-to-ground bond made **only at the service** (or first means of disconnect), never downstream / in subpanels.
- **250.50 / 250.52 Grounding-electrode system** — bond ALL present: (1) metal underground water pipe in contact ≥ **10 ft**, (2) metal building frame, (3) **concrete-encased electrode (Ufer)** ≥ 20 ft of ½″ rebar or 20 ft #4 bare Cu, (4) **ground ring** ≥ 20 ft #2 bare Cu, (5) **rod/pipe** (≥ 8 ft, ⅝″ rod or ¾″ pipe), (6) plate electrodes.
- **250.53(A)(2)** — a made electrode (rod/pipe/plate) needs a **supplemental** electrode unless a single rod tests **≤ 25 Ω**; two rods **≥ 6 ft apart** satisfies this by default. Water-pipe electrode always needs supplementing.
- **250.66 / Table 250.66 GEC sizing** — by largest service conductor; **GEC to a rod need not exceed 6 AWG Cu**; to a concrete-encased electrode **need not exceed 4 AWG Cu**; to a ground ring not larger than the ring.
- **250.122 / Table 250.122 EGC sizing** — by OCPD: 15 A → 14 AWG, 20 A → 12, 30/40/60 A → 10, 100 A → 8, 200 A → 6, 300 A → 4, 400 A → 3, 500 A → 2 (Cu). Upsize proportionally if conductors upsized for voltage drop.
- **250.104 Bonding piping** — metal water pipe bonded (sized per 250.66); *(MI amends §250.104(B) for gas/CSST — see top: CSST jumper ≥ 6 AWG Cu).*
- **250.118** lists acceptable EGC types (wire, EMT, RMC, IMC, FMC w/ limits, MC, etc.).
- **250.32** detached building/structure fed by a feeder — install a grounding electrode there; keep neutral & EGC separate (4-wire feeder).

---

# CHAPTER 3 — Wiring Methods and Materials

## Article 300 — General Wiring Methods 🏠
- **300.4 Protection from physical damage** — bored holes ≥ **1¼ in** from nearest edge of stud/joist, else a **1/16 in steel plate**; notches need the steel plate too; cables in metal-framed walls use bushings/grommets.
- **300.5 Underground (direct burial) min cover (Table 300.5):** direct-burial conductors **24 in**; in PVC/rigid nonmetallic **18 in**; RMC/IMC **6 in**; **residential 120 V ≤ 20 A GFCI-protected branch circuit 12 in**; under a 4-in concrete slab in a building add cover.
- **300.11** secure & support; **300.15** boxes required at splices/outlets/pulls; **300.22** wiring in ducts/plenums limited.

## Article 310 — Conductors for General Wiring 🏠
- **Table 310.16 ampacities (75 °C copper, common):** 14 AWG **20 A** (limited to 15 by 240.4D), 12 AWG **25 A** (→20), 10 AWG **35 A** (→30), 8 AWG **50 A**, 6 AWG **65 A**, 4 AWG **85 A**, 3 AWG **100 A**, 2 AWG **115 A**, 1 AWG **130 A**, 1/0 **150 A**, 2/0 **175 A**, 3/0 **200 A**, 4/0 **230 A**.
- **Temperature correction** & **conductor-bundling derating** (more than 3 current-carrying conductors) per 310.15(B)/(C).
- **🏠 310.12 / Table 310.12 Dwelling services & feeders (83% / "main power feeder" rule):** 100 A → **4 AWG Cu / 2 AWG Al**; 125 A → 2 Cu / 1/0 Al; 150 A → 1 Cu / 2/0 Al; 200 A → **2/0 Cu / 4/0 Al**; 400 A → 400 kcmil Cu / 600 kcmil Al. (Applies to the ungrounded service/feeder conductors carrying the dwelling's total load.)

## Article 312 / 314 — Enclosures, Boxes & Box Fill 🏠
- **314.16 Box fill** — each conductor counts by **Table 314.16(B)**: 14 AWG **2.0 in³**, 12 AWG **2.25**, 10 AWG **2.5**, 8 AWG **3.0**, 6 AWG **5.0**. Counting: each *unbroken* hot/neutral = 1; all EGCs together = **1** (largest); each yoke/device = **2** (largest conductor on it); internal clamps = **1** (largest). Conductors entering & leaving without splice = 1.
- **314.16(A)** standard box volumes (e.g., 3×2×3½ device box = 18 in³).
- **314.23** box support; **314.27** outlet boxes for luminaires/ceiling fans must be **listed for the weight** (fan-rated boxes for paddle fans).
- **314.28** pull/junction box sizing (8× / 6× raceway trade size for straight/angle pulls).

## Articles 320–340 — Cable assemblies
- **320 AC cable (BX)**; **330 MC cable**; **🏠 334 NM cable (Romex)** — *(MI amends 334.10/334.12 — see top).* 334.80 ampacity uses the **60 °C** column; 334.30 secure within **12 in** of boxes (8 in for single-gang nonmetallic) and every **4.5 ft**; 334.15 exposed work follows surface or running boards; no NM in wet/damp.
- **338 SE/USE cable** — service entrance; interior use as feeder/branch must use insulated neutral & follow 334 ampacity (60 °C) for interior.

## Articles 342–362 — Raceways
- **342 IMC / 344 RMC** (threaded rigid); **348 FMC** (flex "Greenfield"); **350 LFMC** (liquidtight flex metal); **352 PVC** (rigid nonmetallic) — expansion fittings, 360° bends max between pulls; **356 LFNC**; **358 EMT** (thinwall) — most common interior raceway; **362 ENT** (flexible nonmetallic). Fill per **Chapter 9 Table 1** (1 wire 53%, 2 wires 31%, 3+ wires 40%). Max **360° total bend** between pull points.

## Article 392 — Cable Trays (commercial/industrial).

---

# CHAPTER 4 — Equipment for General Use

## Article 400 / 402 — Flexible Cords & Fixture Wires
- Cords not a substitute for fixed wiring; not through walls/ceilings/floors; ampacity per Table 400.5.

## Article 404 — Switches 🏠
- **404.2(C)** — a grounded (neutral) conductor required at most switch locations (for electronic/smart switches).
- Snap switch mounting; **404.8** accessible, ≤ 6.7 ft to handle; **404.9(B)** grounding of metal faceplates.

## Article 406 — Receptacles 🏠
- **406.4** grounding-type receptacles, EGC connected.
- **406.12 Tamper-resistant** receptacles required in dwellings (most 125 V 15/20 A locations).
- **406.9 Damp/wet locations** — weather-resistant + **in-use ("bubble") cover** outdoors; cover that keeps the cord plugged in protected.
- Receptacle face not installed face-up in countertops/work surfaces unless listed.

## Article 408 — Switchboards & Panelboards 🏠
- **408.4** every circuit legibly identified (directory); **408.36** panelboard protected by an OCPD ≤ its rating (main breaker or feeder OCPD); **408.41** grounded-conductor terminations — one neutral per terminal.

## Article 410 — Luminaires 🏠
- **410.16 Closet storage-space clearances:** surface incandescent/LED **12 in** from storage; surface fluorescent **6 in**; **recessed** incandescent/LED **6 in**; recessed fluorescent **6 in**; open/partly-enclosed lamps prohibited near storage.
- **410.116** recessed luminaire clearances (Type IC vs non-IC for insulation contact); **410.10(D)** wet-location & shower-zone listing.

## Article 411 — Low-Voltage Lighting (≤ 30 V).

## Article 422 — Appliances 🏠
- **422.11** OCP per appliance rating; **422.16(B)** cord-and-plug lengths: **dishwasher 3–4 ft**, disposal **18–36 in**, trash compactor **3–4 ft** (to a receptacle in the adjacent cabinet).
- **422.31/422.33** disconnecting means (unit switch or plug as disconnect); **422.51** vending/drinking GFCI.

## Article 424 — Fixed Electric Space Heating 🏠
- **424.9** permanently installed baseboard heaters may include receptacle outlets (but **a wall receptacle above a baseboard heater is not counted** as the required 210.52 receptacle, and cords must not lie on the heater).
- **424.3(B)** heating sized as **continuous load (125%)**; **424.19** disconnects.

## Article 430 — Motors / 440 — A/C & Refrigeration Equipment 🏠
- **440** — use nameplate **MCA** (minimum circuit ampacity) and **MOCP** (max OCPD) for HVAC; disconnect **within sight** of the A/C unit (440.14); GFCI for the outdoor service receptacle (210.8(F)).

## Articles 445 / 450 / 460 / 480
- **445 Generators** (incl. portable/standby — see 702 for optional standby & interlock); **450 Transformers** (working space, OCP, ventilation); **460 Capacitors**; **480 Stationary storage batteries**.

---

# CHAPTER 5 — Special Occupancies (overview)
- **500–516** Hazardous (classified) locations — Class I/II/III, Div/Zone; gas stations (514), spray (516).
- **517** Health-care facilities; **518** Assembly; **520** Theaters; **525** Carnivals/fairs; **530** Motion picture.
- **547 Agricultural buildings** (equipotential planes in livestock areas).
- **🏠 550 Manufactured/Mobile homes & lots**; **551 RVs & RV parks** (50 A/30 A pedestals); **552 Park trailers**.
- **555 Marinas, boatyards, docks** (shore power, leakage-current/GFPE, equipotential).
- **🏠 590 Temporary installations** (construction power, GFCI for personnel 590.6, 90-day/seasonal limits).

# CHAPTER 6 — Special Equipment
- **600 Electric signs / outline lighting**; **610 Cranes/hoists**; **620 Elevators**.
- **🏠 625 EV charging (EVSE)** — load is **continuous** (size 125%); branch ratings; disconnect for ≥ 60 A or > 150 V to ground; ventilation if required; EVSE listed; energy-management (625.42) may limit demand.
- **630 Welders**; **640 Audio**; **645 IT equipment rooms**; **646 modular data centers**.
- **🏠 680 Swimming Pools, Spas, Hot Tubs, Fountains** — major dwelling rules:
  - **680.8** overhead conductor clearances (e.g., **22.5 ft** above pool for service drops).
  - **680.22** receptacles: a **GFCI 125 V receptacle 6–20 ft** from inside pool wall (at least one for a dwelling); all pool-area receptacles GFCI; no receptacle within **6 ft** unless allowed.
  - **680.23/680.24** underwater luminaires (low-voltage, GFCI, bonding); **680.26 equipotential bonding grid** — **#8 AWG solid copper** bonding all metal within **5 ft** of the pool, the deck reinforcing, ladders, pumps, etc.
  - Pool pump motors GFCI-protected (680.21).
- **🏠 690 Solar PV** — max voltage, rapid shutdown (690.12), conductor/OCP sizing at **156%** (1.25×1.25) of Isc, dc disconnects, labeling; **705** governs interconnection.
- **694 Wind**; **695 Fire pumps**.

# CHAPTER 7 — Special Conditions
- **700 Emergency systems** (life-safety; power restored ≤ **10 s**; install per NFPA 110/111 — MI §700.9).
- **701 Legally-required standby** (≤ **60 s**; MI §701.9 per NFPA 110/111); **702 Optional standby** (home generators/transfer switches; **interlock or transfer switch** required, no backfeed).
- **🏠 705 Interconnected power sources (PV/battery/generator)** — **120% busbar rule** (705.12): sum of main OCPD + inverter backfeed OCPD ≤ **120%** of busbar rating; backfed breaker at opposite end; labeling of all power sources.
- **🏠 706 Energy Storage Systems (ESS / home batteries)**; **708 COPS**; **710 Stand-alone**; **712 DC microgrids**.
- **722/724/725 Class 1/2/3 (power-limited) circuits** (2023 renumbered; **725** = Class 2/3, e.g., thermostats, doorbells, low-voltage controls); **760 Fire alarm**; **770 Optical fiber**.

# CHAPTER 8 — Communications Systems (stands alone, Ch. 1–4 apply only where referenced)
- **800** general (cabling, bonding, listing); **805** communications (telephone/data) circuits; **810** radio/TV antennas & masts (bonding, lead-in clearances); **820 CATV/coaxial** (bond shield to GES at building entrance, ≤ 20 ft); **830** network-powered broadband; **840** premises-powered broadband (PON/ONT).

# CHAPTER 9 — Tables (mandatory where referenced)
- **Table 1** — raceway fill %: **1 conductor 53%, 2 conductors 31%, over 2 → 40%.**
- **Table 4** — dimensions/% area of each conduit type; **Table 5** — dimensions of insulated conductors; **Table 8** — conductor properties (circular mils, dc resistance) for voltage-drop calcs; **Table 9** — AC resistance/reactance.

# Informative Annexes
- **A** product safety standards; **B** ampacity calc background; **C conduit/tubing fill tables** (number of same-size conductors per conduit — very handy); **D worked examples** (incl. dwelling load-calc examples); **E** construction types; **H Administration & Enforcement (adopted by Michigan)**; **I** UL tightening-torque tables; **J** ADA. (Annex **K** medical equipment in dwellings.)

---

### How to extend / correct this file
- **NEC verbatim wording (2017)** — `grep` the full text already in this folder, e.g.
  `grep -n -A6 "314.16(B)" code/NEC-2017-fulltext-public-resource-org.txt`. It's OCR'd & metric-first
  (`762 mm (30 in.)`), with hyphenation breaks across lines — read a few lines of context. Source:
  Public.Resource.org / Internet Archive item `gov.law.nfpa.nec.2017` (incorporated-by-reference, no login).
- **Michigan amendments (2023)** — re-extract from `2023-Michigan-Electrical-Code-Part8-Final-Rules-eff-2024-03-12.pdf`
  (`pdftotext`), or the LARA "strike & bold" version for context.
- **Current 2023 base text** — for items tagged **[2023 Δ]** or **VERIFY**, the 2017 file won't have the
  current wording; check **NFPA LiNK** (`link.nfpa.org`, free login) or **UpCodes** (`up.codes/viewer/michigan/nfpa-70-2023`,
  free login) — both gate NFPA 70 behind a login I can't pass, but you can read them. The **Michigan
  Residential Code** electrical chapters (ungated on UpCodes) are the closest openly-readable proxy for
  one-/two-family dwellings. Replace a "VERIFY" item with the confirmed value and drop the flag.
