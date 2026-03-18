# Pattern Maker 2 (PM2)

A **Fusion 360 Add-in** that generates rectangular array patterns of shapes on various surface types. Designed for creating ventilation grilles, decorative panels, knurling textures, and other repetitive geometric patterns directly inside Fusion 360.

**Author:** Kamil Sokalski
**Original project:** https://modelowanie3d.org/patternmaker/

### Changes from original
1. Translated Polish to English
2. Security check of code
3. Set `DEBUG` to `False`

---

## Features

### Shape Types

| Shape | Description |
|-------|-------------|
| **Hexagon** | Regular hexagon defined by a circumscribed radius. Always uses a staggered (brick) grid layout. |
| **Circle** | Simple circle defined by radius. |
| **Rect / Square** | Rectangle with an adjustable height scale (10%--500% of the width). At 100% it produces a square. |
| **Slot** | Rounded-end slot (stadium shape) with configurable length and orientation (vertical or horizontal). |

### Surface Types (Engines)

| Engine | Command | Surface | Use Case |
|--------|---------|---------|----------|
| **Wall** | `PM: Wall` | Single flat/planar face | Ventilation grids, simple grates, decorative flat panels |
| **Cylinder** | `PM: Cylinder` | Cylindrical face | Knurling, seamless wrapped textures, round enclosures |
| **Multi** | `PM: Multi` | Multiple connected faces | Complex enclosures, multi-sided housings, irregular perimeters |

### Grid and Layout Options

- **Grid Types:** Checkerboard or Staggered (Brick)
- **Shift Direction:** Rows (Horizontal) or Columns (Vertical) -- controls which axis receives the stagger offset
- **Vertical Interlocking:** Alternating overlap mode for staggered grids (available for non-hexagon shapes)
- **Pattern Alignment (Multi engine):** Symmetrical (Center) or From Axis (Start)
- **Live Preview:** A "Generate / Refresh Preview" button lets you visualize the pattern before committing

### Common Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| Base Radius (R) | Half-width of each shape element | 5 mm |
| Spacing | Gap between adjacent shapes | 1 mm |
| Margin | Inset distance from face edges | 5 mm |
| Density (Columns) | Number of columns around the circumference (Cylinder and Multi engines only) | 20 |
| Slot Length | End-to-end length of a slot shape (visible only when Slot is selected) | 10 mm |
| Slot Orientation | Vertical or Horizontal (visible only when Slot is selected) | Vertical |
| Rectangle Height (%) | Height as a percentage of width (visible only when Rect / Square is selected) | 100% |

> **Note:** The Wall engine uses absolute Base Radius values, while the Cylinder and Multi engines derive shape size from the Density (column count) so the pattern wraps seamlessly around the circumference.

---

## Installation

### Prerequisites

- [Autodesk Fusion 360](https://www.autodesk.com/products/fusion-360/) (Windows or macOS)

### Steps

1. **Download** or clone this repository.

2. **Launch** Fusion 360.

3. Open Utilities > Add-Inns > Scripts and Add-ins > + at the top > Script or Add-In from device

4. Choose the directory that you cloned pattern maker add-in

5. In the **Add-Ins** tab, find **PatternMaker** in the list.

6. Click **Run** to start the add-in. Optionally check **Run on Startup** to load it automatically.

7. A **Pattern Maker** dropdown menu will appear in the **Solid > Create** toolbar panel.

---

## Usage

### PM: Wall (Flat Surfaces)

Use this engine to pattern shapes on a single planar face.

1. Open the **Pattern Maker** dropdown in the Solid Create toolbar.
2. Select **PM: Wall**.
3. **Select a planar face** on your model.
4. Choose a **Shape** (Hexagon, Circle, Rect / Square, or Slot).
5. Configure **Grid Type**, **Spacing**, **Radius**, and **Margin**.
6. Click **Generate / Refresh Preview** to see the result in the viewport.
7. Adjust parameters as needed and click **OK** to finalize.

The engine projects the face boundary into a sketch, applies the margin offset, then fills the bounded region with a rectangular array of the selected shape. After the sketch is created, you can use Fusion's **Extrude** (cut) operation to punch through the face.

### PM: Cylinder (Cylindrical Surfaces)

Use this engine for patterns that wrap seamlessly around a cylinder.

1. Select **PM: Cylinder** from the Pattern Maker dropdown.
2. **Select a cylindrical face** on your model.
3. Choose a **Shape** and configure parameters.
4. Set the **Density (Columns)** slider to control how many shapes appear around the circumference. The shape radius is calculated automatically from the density and spacing so the pattern closes seamlessly.
5. Click **Generate / Refresh Preview** to verify the layout.
6. Click **OK** to finalize.

The engine creates a construction plane tangent to the cylinder, then computes a flat sketch that represents the unwrapped circumference. The resulting sketch can be wrapped back onto the cylinder using Fusion's sheet metal or projection tools.

### PM: Multi (Multiple Connected Faces)

The most advanced engine, for patterning across multiple connected faces on complex geometry.

1. Select **PM: Multi** from the Pattern Maker dropdown.
2. **Select a vertical axis edge** (labeled "1. Vertical Axis (H)") -- this defines the height direction.
3. **Select a horizontal axis edge** (labeled "2. Horizontal Axis (X)") -- this defines the circumferential direction.
4. **Select one or more perimeter faces** (labeled "3. Perimeter Faces") -- these are the faces the pattern will cover.
5. Choose **Alignment**: Symmetrical (Center) centers the pattern on the vertical axis; From Axis (Start) begins at the axis edge.
6. Configure shape, density, spacing, and margin.
7. Click **Generate / Refresh Preview** and then **OK**.

The engine constructs a sketch plane from the two reference edges, computes the total perimeter circumference from the combined face areas, and distributes shapes accordingly.

---

## Architecture Overview

```
PM2/
  PatternMaker.py          Core add-in: all engines, drawing, UI registration
  PatternMaker.manifest    Fusion 360 add-in metadata
  config.py                Global configuration (DEBUG, ADDIN_NAME, COMPANY_NAME)
  AddInIcon.svg            Add-in icon
  CLAUDE.md                AI-assistant context file
  resources/
    wall/                  Wall command icons (16x16, 32x32) + tooltip image
    cylinder/              Cylinder command icons + tooltip image
    multi/                 Multi command icons + tooltip image
    main/                  Main dropdown icons
  commands/                Template command modules (not used by pattern engine)
    commandDialog/         Sample command dialog
    paletteShow/           Sample HTML palette
    paletteSend/           Sample palette messaging
  lib/
    fusionAddInUtils/      Autodesk-provided utility helpers
      general_utils.py     log() and handle_error()
      event_utils.py       add_handler() for type-safe event wiring
  .vscode/
    launch.json            VSCode Python remote-attach debug configuration
```

### Core Components

**`PatternMaker.py`** contains the entire production system in a single file:

- **`draw_shape()`** -- Universal drawing function. Accepts a sketch, shape type, center coordinates, radius, and shape-specific parameters. Draws the geometry using Fusion's sketch API (lines, arcs, circles).

- **`execute_wall_engine()`** -- Reads UI inputs, projects the selected face boundary into a sketch, applies margin offset, computes row/column counts from the bounding box and spacing, then iterates to draw each shape.

- **`execute_cylinder_engine()`** -- Reads the cylinder's axis and radius from the selected face geometry, creates a tangent construction plane, computes shape size from density (column count), and fills the unwrapped circumference.

- **`execute_multi_engine()`** -- Uses two user-selected edges to define a sketch plane via `setByTwoEdges`, computes effective circumference from the total area of selected faces, and distributes shapes with optional centering or axis-aligned layout.

- **`run(context)` / `stop(context)`** -- Fusion 360 lifecycle entry points. `run()` registers the three commands under a "Pattern Maker" dropdown in the Solid Create panel. `stop()` cleans up all UI elements.

Each engine has four associated event handler classes following the naming pattern `{Engine}Created`, `{Engine}Execute`, `{Engine}Preview`, and `{Engine}InputChanged`.

### Key Design Patterns

- **String-based dispatch:** UI dropdown labels (e.g., `'Staggered (Brick)'`, `'Rows (Horizontal)'`) serve as both display text and comparison keys in engine logic. These strings must match exactly between the `*Created` handler (where they are defined) and the `execute_*_engine` function (where they are read).

- **Dynamic input visibility:** Shape-specific parameters (slot length, slot orientation, rectangle height scale) are shown or hidden in `*InputChanged` handlers based on the currently selected shape type.

- **Deferred sketch computation:** Engines set `sketch.isComputeDeferred = True` before drawing all shapes, then set it back to `False` afterward. This batches all geometry creation for significantly better performance.

- **Handler reference retention:** A global `_handlers` list holds references to all event handler instances to prevent Python's garbage collector from releasing them while Fusion still needs them.

---

## Configuration

Edit `config.py` to change global settings:

```python
DEBUG = True           # Enable verbose logging to the Text Command window
ADDIN_NAME = 'PM2'     # Auto-detected from the folder name
COMPANY_NAME = 'ACME'  # Used as a prefix for internal UI element IDs
```

---

## Screenshots

<!-- Add screenshots of Pattern Maker in action here -->

### Wall Engine
<!-- ![Wall Engine Dialog](screenshots/wall-dialog.png) -->
<!-- ![Wall Engine Result](screenshots/wall-result.png) -->
*Screenshot placeholder: Wall engine dialog and result on a flat face*

### Cylinder Engine
<!-- ![Cylinder Engine Dialog](screenshots/cylinder-dialog.png) -->
<!-- ![Cylinder Engine Result](screenshots/cylinder-result.png) -->
*Screenshot placeholder: Cylinder engine dialog and wrapped pattern result*

### Multi Engine
<!-- ![Multi Engine Dialog](screenshots/multi-dialog.png) -->
<!-- ![Multi Engine Result](screenshots/multi-result.png) -->
*Screenshot placeholder: Multi engine dialog showing axis selection and multi-face result*

---

## Platform Support

- **Windows** and **macOS** (as specified in `PatternMaker.manifest`)
- Fusion 360 (any current version with Python API support)

---

## Security Audit

**Overall Risk: LOW.** The add-in runs inside Fusion 360's sandboxed Python environment with no network I/O, no external dependencies, and no unsafe code patterns.

| Severity | Finding |
|----------|---------|
| Medium | `DEBUG = True` hardcoded in `config.py` — should be `False` for distribution |
| Medium | Full stack traces displayed to users via `messageBox` on errors |
| Medium | `innerHTML` XSS in template palette JS (unused code) |
| Low | 14 bare `except: pass` clauses silently swallow all exceptions |
| Low | No upper bound on pattern count — could freeze Fusion 360 with extreme inputs |
| Info | No secrets, no network I/O, no eval/exec, no SQL, no external dependencies — very clean |

---

## License

No license file is currently included in this repository. Please contact the author for licensing terms.
