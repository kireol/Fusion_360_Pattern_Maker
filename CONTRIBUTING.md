# Contributing to Pattern Maker 2 (PM2)

This guide covers the development setup, code structure, and how to extend the add-in with new shapes or engines.

---

## Development Setup

### Prerequisites

- [Autodesk Fusion 360](https://www.autodesk.com/products/fusion-360/) (Windows or macOS)
- [Visual Studio Code](https://code.visualstudio.com/) (recommended)
- Python extension for VSCode (for syntax highlighting and remote attach debugging)

### Getting Started

1. **Clone or copy** this repository into Fusion 360's Add-Ins directory:
   - **Windows:** `%APPDATA%\Autodesk\Autodesk Fusion 360\API\AddIns\`
   - **macOS:** `~/Library/Application Support/Autodesk/Autodesk Fusion 360/API/AddIns/`

2. **Open the folder** in VSCode:
   ```
   code /path/to/PM2
   ```

3. **Start Fusion 360** and enable the add-in via **Utilities > Add-Ins > Scripts and Add-Ins**.

4. After making changes to `PatternMaker.py`, use the **Stop** and **Run** buttons in the Scripts and Add-Ins dialog to reload the add-in. There is no build step -- Fusion 360 loads Python source files directly.

### Debugging with VSCode

The project includes a pre-configured debug configuration at `.vscode/launch.json` that uses Python remote attach.

1. In Fusion 360, open the **Text Command** window (available under the main application menu or via `Ctrl+Alt+C` / `Cmd+Alt+C`).

2. In VSCode, open the **Run and Debug** panel (`Ctrl+Shift+D` / `Cmd+Shift+D`).

3. Select the **"Python: Attach"** configuration and click the green play button.

4. Set breakpoints in `PatternMaker.py` and trigger the relevant command in Fusion 360.

5. To enable verbose logging, set `DEBUG = True` in `config.py`. Log messages will appear in Fusion's Text Command window.

---

## Code Structure

### Production Code

All production logic lives in a single file:

```
PatternMaker.py
```

This file is organized into clearly labeled sections:

| Section | Lines | Purpose |
|---------|-------|---------|
| Universal Drawing Engine | `draw_shape()` | Renders any supported shape onto a Fusion sketch |
| Wall Module | `execute_wall_engine()` + Wall* classes | Flat/planar face patterning |
| Cylinder Module | `execute_cylinder_engine()` + Cyl* classes | Cylindrical surface patterning |
| Multi Module | `execute_multi_engine()` + Multi* classes | Multi-face patterning |
| UI Registration | `run()` / `stop()` | Add-in lifecycle and menu setup |

### Event Handler Pattern

Each engine has four handler classes that follow the Fusion 360 command lifecycle:

| Class Suffix | Event | Role |
|-------------|-------|------|
| `*Created` | `commandCreated` | Defines all UI inputs (dropdowns, sliders, value inputs, selection inputs) |
| `*Execute` | `execute` | Called when user clicks OK; runs the engine function |
| `*Preview` | `executePreview` | Called when preview is requested; runs the engine with a preview flag |
| `*InputChanged` | `inputChanged` | Called on any input change; toggles visibility of shape-specific inputs |

The global `_handlers` list retains references to all handler instances so Python's garbage collector does not release them prematurely.

### Template Commands (Not Used)

The `commands/` directory contains boilerplate from the Fusion 360 add-in template:

- `commandDialog/` -- Sample command with a dialog
- `paletteShow/` -- Sample HTML palette window
- `paletteSend/` -- Sample palette messaging

These are **not used** by the pattern engine. They exist as reference code for potential future expansion.

### Utility Library

`lib/fusionAddInUtils/` provides Autodesk-supplied helpers:

- `general_utils.py` -- `log()` for debug output, `handle_error()` for standardized error handling
- `event_utils.py` -- `add_handler()` for type-safe event handler registration (used by the template commands, not by PatternMaker.py directly)

---

## How to Add a New Shape

All shape rendering is handled by the `draw_shape()` function in `PatternMaker.py`. To add a new shape:

### Step 1: Add Drawing Logic to `draw_shape()`

Add a new `elif` branch for your shape type. The function receives:

| Parameter | Type | Description |
|-----------|------|-------------|
| `sketch` | `adsk.fusion.Sketch` | Target Fusion sketch |
| `shape_type` | `str` | Shape name (must match the dropdown label exactly) |
| `cx`, `cy` | `float` | Center coordinates in sketch space |
| `r` | `float` | Base radius |
| `slot_len` | `float` | Slot length (only relevant for Slot shapes) |
| `is_rotated` | `bool` | Whether the shape should be rotated 90 degrees |
| `slot_horizontal` | `bool` | Slot orientation flag |
| `rect_h_scale` | `int` | Rectangle height as a percentage of width |

Example for adding a triangle:

```python
elif shape_type == 'Triangle':
    h = r * math.sqrt(3)
    p1 = adsk.core.Point3D.create(x, y + r, 0)
    p2 = adsk.core.Point3D.create(x - h/2, y - r/2, 0)
    p3 = adsk.core.Point3D.create(x + h/2, y - r/2, 0)
    lines.addByTwoPoints(p1, p2)
    lines.addByTwoPoints(p2, p3)
    lines.addByTwoPoints(p3, p1)
```

### Step 2: Register the Shape in All `*Created` Handlers

Add the new shape name to the dropdown list in `WallCreated`, `CylCreated`, and `MultiCreated`:

```python
[shape.listItems.add(n, n=='Hexagon') for n in ['Hexagon', 'Circle', 'Rect / Square', 'Slot', 'Triangle']]
```

The shape name string must match exactly between the dropdown definition and the `draw_shape()` comparison.

### Step 3: Handle Shape-Specific Inputs (If Needed)

If your shape requires custom parameters (like Slot needs length and orientation, or Rect / Square needs height scale):

1. Add the input controls in each `*Created` handler.
2. Add visibility logic in each `*InputChanged` handler.
3. Read the input values in each `execute_*_engine()` function.
4. Pass them through to `draw_shape()`.

### Step 4: Adjust Spacing Calculations (If Needed)

If your shape's bounding dimensions differ from `r * 2` in either axis, update the spacing calculations in `execute_wall_engine()`, `execute_cylinder_engine()`, and `execute_multi_engine()`. Look for the section where `w_shape` and `h_shape` are computed based on `shape_type`.

---

## How to Add a New Engine

To add an engine for a new surface type (e.g., a conical or spherical surface):

### Step 1: Create the Engine Function

Write an `execute_*_engine(inputs)` function following the pattern of existing engines:

1. Read the selected face and UI inputs from the `inputs` parameter.
2. Compute geometry parameters (dimensions, coordinate system).
3. Create a construction plane and sketch.
4. Set `sketch.isComputeDeferred = True` before drawing.
5. Loop over rows and columns, calling `draw_shape()` for each position.
6. Set `sketch.isComputeDeferred = False` after drawing.

### Step 2: Create the Four Handler Classes

Create four classes following the naming convention:

```python
class NewEnginePreview(adsk.core.CommandEventHandler):
    # Check _preview_flags['new_engine'], call execute_new_engine()

class NewEngineExecute(adsk.core.CommandEventHandler):
    # Call execute_new_engine(), show traceback on error

class NewEngineInputChanged(adsk.core.InputChangedEventHandler):
    # Toggle visibility of shape-specific inputs, set preview flag

class NewEngineCreated(adsk.core.CommandCreatedEventHandler):
    # Define all UI inputs, wire up the three other handlers
```

### Step 3: Add a Preview Flag

Add an entry to the global `_preview_flags` dictionary:

```python
_preview_flags = {'wall': False, 'cyl': False, 'multi': False, 'new_engine': False}
```

### Step 4: Register the Command in `run()`

In the `run(context)` function:

1. Add icon resources for the new command.
2. Create a button definition with `_ui.commandDefinitions.addButtonDefinition()`.
3. Wire the `commandCreated` handler.
4. Add it to the dropdown with `dropControl.controls.addCommand()`.

Remember to also clean up the command in the `stop(context)` function and at the start of `run()`.

### Step 5: Add Icons

Create icon PNGs in a new subdirectory under `resources/`:

```
resources/
  new_engine/
    16x16-normal.png
    32x32-normal.png
    tooltip.png        (optional, displayed in the Fusion tooltip)
```

---

## Important Conventions

### String-Based Dispatch

UI dropdown label strings serve double duty as both display text and comparison keys:

```python
# In *Created handler:
grid.listItems.add('Staggered (Brick)', True)

# In execute_*_engine():
is_staggered_grid = ('Staggered' in grid_type)
```

If you rename a label in one place, you must update it everywhere. Search for the exact string across all handlers and engine functions.

### Minimum Radius Guard

`draw_shape()` enforces a minimum radius of `0.01` cm to prevent degenerate geometry:

```python
if r < 0.01: r = 0.01
```

This guard also exists in the engine functions when computing radius from density.

### Internal Units

Fusion 360's API uses centimeters internally, even when the UI displays millimeters. The `ValueInput` objects handle unit conversion automatically, but be aware that raw `.value` properties return centimeters.

### Sketch Coordinate System

All drawing happens in 2D sketch space. The engines use `sketch.modelToSketchSpace()` to convert 3D model coordinates to 2D sketch coordinates. The `is_rotated` flag swaps X/Y axes when the cylinder or multi-face axis is oriented differently than expected.

---

## Testing

There is no automated test suite. Testing is done manually in Fusion 360:

1. Load the add-in.
2. Create test geometry (a box for Wall, a cylinder for Cylinder, a multi-faced extrusion for Multi).
3. Run each command with various shape types, grid types, and parameter combinations.
4. Verify that patterns are correctly placed, spaced, and aligned.
5. Test edge cases: very small radius, very high density, zero margin, interlocking mode.

---

## File Reference

| File | Purpose | Modify? |
|------|---------|---------|
| `PatternMaker.py` | All production code | Yes -- this is where all changes go |
| `PatternMaker.manifest` | Fusion 360 metadata (author, platform, type) | Rarely |
| `config.py` | Global DEBUG flag and naming constants | Occasionally |
| `resources/` | Icons for toolbar commands | When adding new engines |
| `commands/` | Template boilerplate (unused) | No |
| `lib/` | Autodesk utility helpers | No |
| `.vscode/launch.json` | Debug configuration | Rarely |
