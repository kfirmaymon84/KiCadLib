# Fab Layers Toolbox — KiCad Action Plugin

A small PCB Editor toolbar tool for tidying up `${REFERENCE}` text on the
**F.Fab** and **B.Fab** layers. It adds a dialog with two one-click actions:

- **Auto Orient F.Fab / B.Fab** — normalizes text rotation so fab labels read
  the right way up.
- **Fit Text to Fab Outline** — automatically scales each footprint's
  `${REFERENCE}` fab text to fill its component outline, without touching the
  rectangle or overlapping any interior circle.

![toolbar icon](icon.png)

## Installation

1. Open your KiCad scripting plugins folder. The easiest way is from the
   PCB Editor: **Tools → External Plugins → Open Plugin Directory**.

   The default locations are:
   - **Windows:** `%APPDATA%\kicad\<version>\scripting\plugins\`
     (some setups use `Documents\KiCad\<version>\scripting\plugins\`)
   - **macOS:** `~/Library/Application Support/kicad/<version>/scripting/plugins/`
   - **Linux:** `~/.local/share/kicad/<version>/scripting/plugins/`

2. Copy the entire `fab_layers_toolbox` folder into that `plugins`
   directory so you end up with:
   ```
   .../scripting/plugins/fab_layers_toolbox/
       __init__.py
       fab_layers_toolbox.py
       icon.png
       README.md
   ```

3. In the PCB Editor, run **Tools → External Plugins → Refresh Plugins**
   (or just restart KiCad).

4. The plugin appears as a toolbar icon and under
   **Tools → External Plugins → Fab Layers Toolbox**.

> Requires KiCad 7 or newer (uses the `EDA_ANGLE` / `VECTOR2I` / `BOX2I`
> Python API). Developed and tested on KiCad 10.

## Usage

Click the toolbar icon (or the Tools-menu entry) to open the toolbox, then:

### Auto Orient F.Fab / B.Fab
Scans every footprint's fab-layer text (graphical text plus the Reference and
Value fields) and:
- Remaps rotation **180° → 0°** and **90° → 270°** so text isn't upside-down
  or facing the wrong way.
- Disables **Keep Upright** on those items so the rotation sticks.

### Fit Text to Fab Outline
For every footprint, finds the `${REFERENCE}` text item on **F.Fab** / **B.Fab**
and resizes it (and its stroke thickness) to fill the component's fab outline:
- **Only `${REFERENCE}` fab text is touched** — the silkscreen Reference,
  Value, and other text are left alone.
- **Outlines drawn as separate line segments are reconstructed** into full
  rectangles, so the text is measured against the real body outline.
- **Nested outlines** (an inner + outer rectangle) constrain the text to the
  smallest rectangle that encloses it.
- **Interior circles are treated as obstacles** — the text shrinks so it stays
  clear of them instead of overlapping.
- A fixed **clearance gap** is kept on all sides so the text never touches the
  outline.
- Text height snaps to 0.1 mm steps; stroke thickness snaps to 0.05 mm steps to
  keep a small, consistent set of sizes across the board.

Both actions apply immediately to the open board (use **Ctrl+Z** to undo).

## Tuning

The behavior is controlled by a few constants near the top of
`_on_fit_text` in `fab_layers_toolbox.py`:

| Constant | Default | Effect |
|----------|---------|--------|
| `CLEARANCE_MM` | `0.15` | Gap (mm, per side) kept between text and the outline / circles. Smaller = larger text, closer to the border. |
| `_snap_size(... step=0.1, lo=0.3, hi=3.0)` | — | Text-height rounding step and min/max height (mm). |
| thickness `step=0.05` | `0.05` | Stroke-thickness rounding step (mm). |

The auto-orient angle remap lives in the `REMAP` dictionary in
`_on_auto_orient` if you need different rotation rules.

## Notes

- Angle checks use a small tolerance to absorb floating-point rounding
  (e.g. 180.0 vs 179.999999 won't be missed).
