# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PM2 (Pattern Maker 2) is a **Fusion 360 Add-in** that generates rectangular array patterns of shapes (hexagons, circles, rectangles, slots) on various surface types. Author: Kamil Sokalski.

## Architecture

The add-in has two coexisting systems:

### Core Engine (`PatternMaker.py`)
This is the actual production code. It contains everything in a single file:
- **`draw_shape()`** — Universal drawing engine that renders shapes onto a Fusion sketch
- **`execute_wall_engine()`** — Patterns on flat/planar faces
- **`execute_cylinder_engine()`** — Patterns wrapped around cylindrical surfaces (auto-unwraps circumference)
- **`execute_multi_engine()`** — Patterns across multiple connected faces (requires vertical + horizontal axis selection)
- **`run(context)` / `stop(context)`** — Entry points called by Fusion 360 to register/deregister the dropdown menu in `SolidCreatePanel`

Each engine has a matching set of event handler classes (e.g., `WallCreated`, `WallExecute`, `WallPreview`, `WallInputChanged`) that manage the Fusion command lifecycle. A global `_handlers` list prevents garbage collection of handler references.

### Template Command System (`commands/`)
Sample/boilerplate code from the Fusion 360 add-in template. The three modules (`commandDialog`, `paletteShow`, `paletteSend`) are **not used by the pattern engine** — they exist as reference implementations for future command expansion. Each command follows the `entry.py` pattern with `start()`/`stop()` functions orchestrated by `commands/__init__.py`.

### Utilities (`lib/fusionAddInUtils/`)
Reusable Fusion 360 helpers (Autodesk-provided):
- `general_utils.py` — `log()` and `handle_error()` functions
- `event_utils.py` — `add_handler()` for type-safe event handler creation

### Configuration
- `config.py` — Global vars (`DEBUG`, `ADDIN_NAME`, `COMPANY_NAME`)
- `PatternMaker.manifest` — Fusion 360 metadata (supports Windows + macOS)

## Development

**No build step required.** Fusion 360 add-ins are loaded directly as Python scripts.

- **Debug**: VSCode attach configuration in `.vscode/launch.json` (Python remote attach)
- **Install**: Place this folder in Fusion 360's add-in directory and enable via the Scripts & Add-Ins dialog
- **Icons**: Resource PNGs at 16x16, 32x32 sizes in `resources/` subdirectories (`wall/`, `cylinder/`, `multi/`)

## Key Patterns

- UI string values in dropdowns (e.g., `'Staggered (Brick)'`, `'Rows (Horizontal)'`) are used as both display labels AND comparison keys in engine logic — they must match exactly between `*Created` handlers and `execute_*_engine` functions
- Shape-specific inputs (slot length, slot orientation, rectangle height scale) are shown/hidden dynamically in `*InputChanged` handlers based on the selected shape type
- The cylinder engine computes pattern density from column count rather than absolute spacing, since it must wrap seamlessly around the circumference
- The multi engine uses two reference edges (vertical + horizontal) to construct a sketch plane via `setByTwoEdges`, then maps shapes relative to the computed perimeter circumference
