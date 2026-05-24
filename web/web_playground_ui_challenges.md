# Web Playground UI — Challenges & Observations

## Side-by-side layout / Monaco scrolling (FIXED)

The side-by-side layout (editor left, output right) for single-cell/non-notebook
samples has a persistent scrolling issue: neither the Monaco editor pane nor the
output pane scrolls independently.

### What was tried

1. **`overflow: hidden` on the editor container** — clips Monaco's internal
   scrollbar DOM elements, breaking scrolling.
2. **`overflow: hidden` on parent grid/flex containers** — constrains the layout
   chain but when removed from the editor, Monaco's content expands the container
   beyond the viewport, pushing the output panel out of sight.
3. **`overflow: hidden` on `.workspace` grid only** — gives the chain a definite
   height, but without clipping at the editor level, Monaco doesn't detect the
   constrained dimensions and doesn't show its scrollbar.
4. **`min-height: 0` throughout the flex/grid chain** — correctly allows elements
   to shrink below content size, but alone doesn't create scroll boundaries.
5. **Added `grid-template-rows: minmax(0, 1fr)` to `.workspace`** — fixes the
   height chain (the workspace grid row was `auto`, collapsing to content height).
   This was a genuine bug: without it, the entire side-by-side chain had no
   definite height.

### Root cause hypothesis

Monaco's `automaticLayout: true` uses a ResizeObserver to detect container size
changes. The container must have a definite pixel height for Monaco to allocate
its internal viewport and show scrollbars. The CSS grid/flex chain delivers this
height, but the interplay between:

- Monaco's internal `overflow: hidden` (on its own root element)
- The container's `overflow` property
- The grid track sizing (`1fr` vs `minmax(0, 1fr)`)
- Whether the container fills its grid cell

…creates a fragile layout where small CSS changes toggle between "no scrollbar"
and "content overflows viewport."

### Fix

The side-by-side path now gives Monaco explicit container dimensions when the
playground enters single-cell or plain mode. `layoutEditor()` reads the editor
pane's actual grid-cell rectangle and calls `editor.layout({ width, height })`
after layout settles, on resize, and after sidebar dragging. The editor pane
uses `overflow: hidden` only after Monaco is explicitly sized, while the output
pane has `min-height: 0` and `overflow: auto` so it scrolls independently.

### Previous state

The side-by-side layout is in place with the `single-cell` CSS class toggled by
JS when only one cell exists. The `grid-template-rows` fix on `.workspace` gives
the chain a definite height. The editor container has no `overflow` restriction.
In practice, scrolling still did not work reliably because Monaco's automatic
layout could miss the final split-pane dimensions.

### Alternative approaches (not tried)

- Give the editor container an explicit pixel height via JS after layout
- Use `editor.layout({ width, height })` explicitly instead of `automaticLayout`
- Switch from CSS grid to absolute positioning for the side-by-side panes
- Use Monaco's diff editor or split-pane API instead of CSS

---

## Pyodide session persistence (FIXED)

The original `pyodide.globals` API was removed in Pyodide ≥ 0.25. The
replacement (`setattr(js, key, value)` / `getattr(js, key, None)`) wraps Python
objects in `PyProxy` instances that don't survive roundtrips between
`runPythonAsync` calls. The fix: store the `Interpreter` instance in a plain
Python `_Store` object (module-level, persists within a Pyodide session) and
remove the JS globals sync entirely.

## Cell execution counters (FIXED)

Implemented Jupyter-style `In[N]:` / `Out[N]:` numbering using a global
`_executionCounter` and `data-exec-count` attributes on cells. Handles reindex,
deletion, Run All, and Restart correctly.
