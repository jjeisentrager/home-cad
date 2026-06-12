#!/usr/bin/env bash
#
# open-freecad.sh — reliably launch the FreeCAD GUI (flatpak build).
#
# Why this exists: FreeCAD here is a flatpak with no binary on PATH, and the most
# common reason "it won't open" is a leftover hung instance from a previous
# headless/script run (e.g. `flatpak run ... some.py` that got stuck). The flatpak
# won't start a fresh GUI window while those zombies hold the instance/X locks.
# This script clears those automation leftovers first, then launches detached.
#
# Usage:
#   ./open-freecad.sh                 # just open FreeCAD
#   ./open-freecad.sh House/House.FCStd Drain/DrainAssembly.FCStd   # open file(s)
#   ./open-freecad.sh --fresh         # also kill ANY running FreeCAD (incl. GUIs)
#   ./open-freecad.sh --no-kill       # don't touch existing processes
#
set -u

APP="org.freecad.FreeCAD"
LOG="${TMPDIR:-/tmp}/freecad-launch.$(id -u).log"

# --- flags ------------------------------------------------------------------
KILL_MODE="auto"        # auto = kill only script/offscreen leftovers
files=()
for arg in "$@"; do
  case "$arg" in
    --fresh)   KILL_MODE="all" ;;
    --no-kill) KILL_MODE="none" ;;
    -h|--help) sed -n '2,20p' "$0"; exit 0 ;;
    *)         files+=("$arg") ;;
  esac
done

# --- preflight --------------------------------------------------------------
if ! command -v flatpak >/dev/null 2>&1; then
  echo "ERROR: flatpak is not installed." >&2; exit 1
fi
if ! flatpak info "$APP" >/dev/null 2>&1; then
  echo "ERROR: $APP is not installed. Try: flatpak install flathub $APP" >&2; exit 1
fi

# true if a FreeCAD instance (GUI or sandboxed run) is alive. The flatpak's child
# processes show up as "FreeCAD"/"bwrap … FreeCAD", NOT as the app-id string, so
# we check `flatpak ps` (canonical) with a pgrep fallback.
freecad_running() {
  flatpak ps --columns=application 2>/dev/null | grep -qx "$APP" && return 0
  pgrep -x FreeCAD >/dev/null 2>&1
}

# --- clear leftover instances ----------------------------------------------
case "$KILL_MODE" in
  auto)
    # only kill non-interactive leftovers: runs with a .py script or offscreen Qt.
    # never touches a real GUI session, so unsaved work in an open FreeCAD is safe.
    if ps -eo args= 2>/dev/null | grep -Eq '(freecadcmd|FreeCAD[^/]*\.py|QT_QPA_PLATFORM=offscreen.*FreeCAD)'; then
      echo "Clearing stale FreeCAD automation/script processes..."
      pkill -9 -f "QT_QPA_PLATFORM=offscreen.*FreeCAD" 2>/dev/null
      pkill -9 -f "FreeCAD .*\.py"                     2>/dev/null
      pkill -9 -f "freecadcmd"                         2>/dev/null
      pkill -9 -f "bwrap.*FreeCAD.*\.py"               2>/dev/null
      sleep 1
    fi
    ;;
  all)
    echo "Killing ALL FreeCAD processes (--fresh)..."
    flatpak kill "$APP" 2>/dev/null
    pkill -9 -f "$APP" 2>/dev/null
    pkill -9 -f "bwrap.*FreeCAD" 2>/dev/null
    sleep 1
    ;;
  none) : ;;
esac

# --- display env (Wayland session with XWayland fallback) -------------------
# Leaving QT_QPA_PLATFORM unset lets Qt auto-pick wayland, then xcb. We only make
# sure DISPLAY has a value so the XWayland fallback can work if wayland fails.
export DISPLAY="${DISPLAY:-:0}"

# --- resolve file args to absolute paths -----------------------------------
abs=()
for f in "${files[@]:-}"; do
  [ -z "$f" ] && continue
  if [ -e "$f" ]; then
    abs+=("$(readlink -f -- "$f")")
  else
    echo "WARNING: file not found, skipping: $f" >&2
  fi
done

# --- launch, detached so it survives this terminal -------------------------
echo "Launching FreeCAD${abs:+ with: ${abs[*]}}"
echo "(log: $LOG)"
setsid flatpak run "$APP" "${abs[@]}" >"$LOG" 2>&1 < /dev/null &

# --- confirm it actually came up -------------------------------------------
for i in $(seq 1 15); do
  sleep 1
  if freecad_running; then
    echo "FreeCAD is running. ✔"
    exit 0
  fi
done

echo "ERROR: FreeCAD did not stay running. Last log lines:" >&2
tail -n 20 "$LOG" >&2
exit 1
