"use strict";

const fs = require("fs");
const path = require("path");

function resolveRunPlan(options, exists = fs.existsSync) {
  const { filePath, workspacePath, runner = "auto" } = options;
  if (!["auto", "source", "installed"].includes(runner)) {
    throw new Error(`Unknown Nomi runner: ${runner}`);
  }
  const cwd = workspacePath || options.cwd || path.dirname(filePath);
  const configured = (options.sourceCliPath || "").trim();
  const candidate = configured
    ? path.resolve(cwd, configured)
    : workspacePath && path.join(workspacePath, "scripts", "cli.py");
  const sourceCli = candidate && exists(candidate) ? candidate : undefined;
  if (runner === "source" && !sourceCli) {
    throw new Error("Nomi source runner requested, but scripts/cli.py was not found.");
  }
  if (runner !== "installed" && sourceCli) {
    return { executable: options.pythonExecutable || "python3", args: [sourceCli, filePath], cwd };
  }
  return { executable: options.executable || "nomi", args: [filePath], cwd };
}

module.exports = { resolveRunPlan };
