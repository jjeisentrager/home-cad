# Home CAD

FreeCAD models for a home design: appliances/furniture component library plus
room assemblies (kitchen, add-on). **FreeCAD 1.1**, all geometry in **millimetres**
(`IN = 25.4`).

## Running FreeCAD

FreeCAD is installed as a **flatpak** (no native binary on PATH):

```bash
# Headless scripting (preferred for automation):
flatpak run --command=freecadcmd org.freecad.FreeCAD /abs/path/to/script.py

# GUI (needed only for colors / interactive work):
flatpak run org.freecad.FreeCAD /abs/path/to/file.FCStd
```

Gotchas learned the hard way:
- The flatpak has `host` filesystem access, so scripts can read/write anywhere
  under `$HOME` using normal absolute paths. **But the sandbox `/tmp` is private**
  — write scratch/report files into the repo (under `$HOME`), not `/tmp`.
- `print()` from a script is swallowed/interleaved with `freecadcmd`'s progress-bar
  spam. To inspect anything, **write results to a file** (e.g.
  `open(".../report.txt","w")`) and `cat` it afterward, rather than relying on stdout.
- Scripts run with a relative path argument do execute, but write outputs with
  absolute paths to be safe.

### ⚠️ `freecadcmd` destroys GuiDocument.xml — never use it to *save* a file you'll open in the GUI

`freecadcmd` runs without the Gui layer, so on **save it drops `GuiDocument.xml`
entirely** (verify with `unzip -l file.FCStd | grep GuiDocument`). When the user
then opens that file, FreeCAD regenerates view providers and **defaults every
object to hidden** — which looks like "I have to click the eye on everything down
the hierarchy." `obj.Visibility` set headlessly does *not* fix this.

**To save anything the user will open in the GUI, run with the Gui layer up via
the offscreen Qt platform** (there is an active `DISPLAY=:0`, but offscreen avoids
popping a window):

```bash
flatpak run --env=QT_QPA_PLATFORM=offscreen org.freecad.FreeCAD /abs/script.py
```

In that mode `App.GuiUp == 1`, `obj.ViewObject` exists, and saving writes a proper
`GuiDocument.xml`. Set visibility with a helper that touches both:
`obj.Visibility = True; obj.ViewObject.Visibility = True`. Use `freecadcmd` only
for read-only inspection / geometry queries, never to save user-facing files.

Visibility pattern to preserve when re-saving: show `App::Link`, `App::Part`,
`PartDesign::Body` **and its tip Pad**, loose `Part::Feature`s, and `Part::Cut`
results; keep `App::Origin` axes/planes, sketches, and intermediate PartDesign
features hidden.

## Repository layout

```
Library/<MODEL>/        one component each (appliances, furniture)
  build_<thing>.py      generator: builds the solids, saves FCStd/step/stl
  <MODEL>.FCStd         the model      <MODEL>.step / .stl   exports
  color_save.py         GUI helper: apply ShapeColors, re-save
  render_sw.py          headless software renderer -> preview_iso.png (numpy+PIL)
  preview_iso.png       iso preview thumbnail
Library/_reference/     vendor PDFs / spec sources
Kitchen/                kitchen assemblies + Kitchen_Counter (L-shaped counter+island)
AddOn/                  add-on room: framing, floor joists, subfloor, roof
*.FCBak                 FreeCAD backups (git-ignored)
```

### Components in the Library
| Dir | Model | What |
|-----|-------|------|
| `LG_LRMXS2806S` | LG LRMXS2806S | 4-door French-door **refrigerator** |
| `LRGL5823S` | LG LRGL5823S | gas **range / stove** |
| `KWT310-33` | Kraus KWT310-33 | undermount **sink** |
| `WDP540HAMZ` | Whirlpool WDP540HAMZ | **dishwasher** |
| `VIKIO-IKP02-30` | VIKIO IKP02-30 | range **hood** |
| `Edenfield-29004S1` | Ashley Edenfield | **sofa** |
| `ViWinTech/…` | ViWinTech ThruBlack | **windows** (3-Lite Glider, multiple sizes) |

## Component modelling convention

Every `build_*.py` builds **loose `Part::Feature` solids** (no container) in a
consistent local frame:

- Origin at the **back-left-bottom corner**.
- **+X = width**, **+Y = depth with the FRONT face at +Y**, **+Z = height (up)**.
- Bottom on `Z=0` (the sink is the exception: its deck rim is at `Z=0` and the
  bowl hangs to negative Z).

Colors are not baked into geometry — they're applied by name (`color_save.py`,
GUI) or at render time (`render_sw.py`), keying on substrings like
`handle/knob/window/burner/grate/display` → dark, everything else → steel.

## Assemblies

Assemblies use the **Assembly workbench** (`Assembly::AssemblyObject` with an
`App::Origin` and a `Joints` group). Components are brought in as **`App::Link`**
objects whose `LinkedObject` is an **`App::Part`** inside an external `.FCStd`,
positioned via the link's `Placement`. One part is fixed with a `GroundedJoint`;
others are simply placed (no joint needed for static layout — the solver leaves
un-jointed links where you put them). Add a link into the scene by appending it
to the `Assembly` object's group (`assembly.addObject(link)`).

**Important:** the raw Library components are loose `Part::Feature`s and are *not*
directly linkable. To use one in an assembly it must first be **wrapped in an
`App::Part` named `Part`** inside its `.FCStd` (see `Kitchen/place_appliances.py`,
which does this idempotently and then creates+places the links).

### Kitchen counter reference frame
`Kitchen/Kitchen_Counter.FCStd` holds two `App::Part`s — `Part` (label
*Kitchen_Counter*, the L-shaped run) and `Part001` (*Kitchen_Island*). In
`Kitchen_Assembly.FCStd` the counter is grounded at the origin, so **counter-local
coords == assembly/world coords**. The L-shape (base `Z 0→914.4`, countertop top
`Z=939.8`, floor `Z=0`):

- **Long side**: runs along **−Y** (Y from 0 → −6959.6), back wall at **X=0**,
  front faces **−X**, 609.6 mm (24") deep.
- **Short side**: runs along **−X** (X from 0 → −3302), back wall at **Y=0**,
  front faces **−Y**, 609.6 mm deep.
- Inner (concave) corner at (−609.6, −609.6); both walls meet at the room corner
  near (0, 0).

To make a component face the counter front, rotate about **Z** (its front is
local +Y): **+90°** makes the front point −X (long-side appliances: fridge, range);
**180°** makes it point −Y (short-side: sink, dishwasher). `Kitchen/place_appliances.py`
is the worked example — fridge at the long-side end, range mid-long-side, sink
mid-short-side (rim at Z=939.8), dishwasher under the short-side end.

**Countertop cut-outs** (`Kitchen/finish_kitchen.py`): the sink and stove read
*through* the countertop because the L-top (`Body001` / CounterTop) is boolean-cut
by a `Part::Cut` (`CounterTop_Cut`) whose tool is a compound of two boxes — the
sink bowl opening and a full-depth stove slot (the slot splits the long run into
two solids, which is correct). The cut lives inside the `Part` App::Part; the
original `Body001`/`Pad002` are hidden and `CounterTop_Cut` is shown, so the
external link renders the holed top.

## Workflow tips
- After scripting changes, verify by reopening the saved file in a fresh
  `freecadcmd` session and reporting global bounding boxes. Note: `Part.getShape()`
  on an `App::Link`-to-`App::Part` returns an empty shape in a cold session — to
  get a real bbox, compound the linked `Part.Group`'s feature shapes and apply the
  link's `Placement.Matrix`.
- Regenerate a component's exports/preview by re-running its `build_*.py` (+
  `render_sw.py` for the thumbnail).
