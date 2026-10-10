// Source-preserving notebook framing. Markers are column-zero # %% lines.
function splitNotebookDocument(source) {
  const markers = [...source.matchAll(/^#\s*%%[^\r\n]*(?:\r\n|\r|\n|$)/gm)];
  if (!markers.length) return { preamble: "", cells: [{ prefix: "", code: source, title: "" }] };
  let preamble = source.slice(0, markers[0].index);
  const cells = [];
  if (preamble.split(/\r\n|\r|\n/).some((line) => line.trim() && !line.trim().startsWith("#"))) {
    cells.push({ prefix: "", code: preamble, title: "Preamble" });
    preamble = "";
  }
  markers.forEach((marker, index) => {
    cells.push({
      prefix: marker[0],
      code: source.slice(marker.index + marker[0].length, markers[index + 1] ? markers[index + 1].index : source.length),
      title: marker[0].replace(/^#\s*%%/, "").trim(),
    });
  });
  return { preamble, cells };
}

function joinNotebookDocument(preamble, cells) {
  return preamble + cells.map((cell) => cell.prefix + (cell.prefix && cell.code && !/[\r\n]$/.test(cell.prefix) ? "\n" : "") + cell.code).join("");
}

function normalizeWorkbenchState(stored) {
  const record = stored && typeof stored === "object" && !Array.isArray(stored) ? stored : {};
  const entries = (value) => value && typeof value === "object" && !Array.isArray(value) ? Object.entries(value) : [];
  const bounded = (value, fallback, min, max) => typeof value === "number" && Number.isFinite(value) ? Math.max(min, Math.min(max, value)) : fallback;
  return {
    active: typeof record.active === "string" ? record.active : "calculate",
    drafts: Object.fromEntries(entries(record.drafts).filter(([key, value]) => /^[a-z0-9-]+$/.test(key) && typeof value === "string")),
    scratchDocs: Object.fromEntries(entries(record.scratchDocs).filter(([key, item]) => /^scratch-\d+$/.test(key) && item && typeof item.title === "string")),
    sidebarWidth: bounded(record.sidebarWidth, 272, 210, 420),
    resultPane: bounded(record.resultPane, 43, 28, 68),
  };
}

function diagnosticPosition(diagnostic, source) {
  const span = diagnostic.span || {};
  const line = span.line || span.start_line;
  const column = span.column || span.start_column || 1;
  const lines = source.split(/\r\n|\r|\n/);
  if (!Number.isInteger(line) || line < 1 || line > lines.length || !Number.isInteger(column) || column < 1) return null;
  const content = lines[line - 1];
  if (span.coordinate_unit === "unicode-code-point" && column > Array.from(content).length + 1) return null;
  const utf16Column = span.coordinate_unit === "unicode-code-point"
    ? Array.from(content).slice(0, column - 1).join("").length + 1 : column;
  if (utf16Column > content.length + 1) return null;
  return { lineNumber: line, column: utf16Column };
}

if (typeof module !== "undefined") module.exports = { splitNotebookDocument, joinNotebookDocument, diagnosticPosition, normalizeWorkbenchState };
