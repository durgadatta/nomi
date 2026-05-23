"use strict";

// Nomi Rust AST JSON → Core IR JSON lowerer.
//
// Takes the JSON output of the Rust fast-ast parser and produces
// the { schema, version, root } envelope expected by core_runtime.js.

var CORE_IR_JSON_SCHEMA = typeof CORE_IR_JSON_SCHEMA !== "undefined" ? CORE_IR_JSON_SCHEMA : "nomi.core-ir";
var CORE_IR_JSON_VERSION = typeof CORE_IR_JSON_VERSION !== "undefined" ? CORE_IR_JSON_VERSION : 1;

// ─── Core IR factory functions ───────────────────────────────────────────────

function literal(value, valueType) {
  const node = { type: "Literal", value };
  if (valueType !== undefined) node.value_type = valueType;
  return node;
}

const NIL = literal(null, "nil");

function load(name)        { return { type: "Load", name }; }
function bind(name, value) { return { type: "Bind", name, value }; }
function call(func, args, block) {
  const node = { type: "Call", func, args: args || [] };
  if (block) node.block = block;
  return node;
}
function returnNode(value) { return { type: "Return", value: value || NIL }; }
function yieldNode(value)  { return { type: "Yield", value: value || NIL }; }
function branch(test, thenBody, elseBody) {
  return { type: "Branch", test, then_body: thenBody, else_body: elseBody || [] };
}
function noOp()            { return { type: "NoOp" }; }
function breakNode()       { return { type: "Break" }; }
function continueNode()    { return { type: "Continue" }; }
function unaryOp(op, operand)   { return { type: "UnaryOp", op, operand }; }
function binaryOp(left, op, right) { return { type: "BinaryOp", left, op, right }; }
function booleanOp(op, values)  { return { type: "BooleanOp", op, values }; }
function compareOp(left, ops, comparators) { return { type: "CompareOp", left, ops, comparators }; }
function conditionalExpr(test, thenVal, elseVal) {
  return { type: "ConditionalExpr", test, then_value: thenVal, else_value: elseVal };
}
function sequence(elements)  { return { type: "Sequence", elements: elements || [] }; }
function mappingLiteral(entries) { return { type: "MappingLiteral", entries: entries || [] }; }
function getItem(obj, key)   { return { type: "GetItem", object_: obj, key }; }
function getField(obj, field) { return { type: "GetField", object_: obj, field }; }
function spread(value)       { return { type: "Spread", value }; }
function diagnostic(message) { return { type: "Diagnostic", message }; }
function loopNode(test, body, elseBody) {
  const node = { type: "Loop", test, body };
  if (elseBody && elseBody.length) node.else_body = elseBody;
  return node;
}
function forEach(target, iterable, body, elseBody) {
  const node = { type: "ForEach", target, iterable, body };
  if (elseBody && elseBody.length) node.else_body = elseBody;
  return node;
}
function matchNode(subject, cases) { return { type: "Match", subject, cases }; }
function patternTest(pattern, guard, body) {
  const node = { type: "PatternTest", pattern, body };
  if (guard) node.guard = guard;
  return node;
}
function constructData(name, fields) {
  return { type: "ConstructData", name, fields: fields || [] };
}
function raiseNode(exception) { return { type: "Raise", exception: exception || NIL }; }
function handle(body, handlers, finalbody) {
  const node = { type: "Handle", body, handlers };
  if (finalbody && finalbody.length) node.finalbody = finalbody;
  return node;
}
function defer(body)    { return { type: "Defer", body }; }
function moduleNode(body) {
  return { type: "Module", body: body || [] };
}

// ─── Operator name maps (Rust AST → Core IR) ─────────────────────────────────

const BINOP_MAP = {
  Add: "+", Sub: "-", Mult: "*", Div: "/", FloorDiv: "//", Mod: "%",
  MatMult: "@", Pow: "**", BitAnd: "&", BitOr: "|", BitXor: "^",
  LShift: "<<", RShift: ">>"
};

const CMPOP_MAP = {
  Lt: "<", LtE: "<=", Gt: ">", GtE: ">=", Eq: "==", NotEq: "!=",
  Is: "is", IsNot: "is not", In: "in", NotIn: "not in"
};

const BOOLOP_MAP = { And: "and", Or: "or" };

const UNARYOP_MAP = { UAdd: "+", USub: "-", Not: "not", Invert: "~" };

const AUGOP_MAP = {
  Add: "+", Sub: "-", Mult: "*", Div: "/", FloorDiv: "//", Mod: "%",
  MatMult: "@", Pow: "**", BitAnd: "&", BitOr: "|", BitXor: "^",
  LShift: "<<", RShift: ">>"
};

// ─── Expression lowering ─────────────────────────────────────────────────────

let diagnosticCount = 0;

function lowerExpr(expr) {
  if (!expr || typeof expr !== "object") return NIL;

  switch (expr.type) {
    case "Name":     return load(expr.id);
    case "Number":   return lowerNumber(expr.value);
    case "String":   return literal(expr.value, "str");
    case "Constant": return lowerConstant(expr.value);

    case "List":
    case "Tuple": {
      const items = (expr.elements || expr.items || []).map(lowerExpr);
      return sequence(items);
    }
    case "Dict": {
      const keys = (expr.keys || []).map(lowerExpr);
      const values = (expr.values || []).map(lowerExpr);
      const entries = keys.map((k, i) => [k, values[i] || NIL]);
      return mappingLiteral(entries);
    }
    case "Attribute": return getField(lowerExpr(expr.value), expr.attr);
    case "Subscript": return getItem(lowerExpr(expr.value), lowerExpr(expr.slice));
    case "Call": {
      const func = lowerExpr(expr.func);
      const args = (expr.args || []).map(lowerExpr);
      return call(func, args);
    }
    case "BinOp": {
      const op = BINOP_MAP[expr.op] || expr.op;
      return binaryOp(lowerExpr(expr.left), op, lowerExpr(expr.right));
    }
    case "Compare": {
      const ops = (expr.ops || []).map(o => CMPOP_MAP[o] || o);
      const comparators = (expr.comparators || []).map(lowerExpr);
      return compareOp(lowerExpr(expr.left), ops, comparators);
    }
    case "BoolOp": {
      const op = BOOLOP_MAP[expr.op] || expr.op;
      const values = (expr.values || []).map(lowerExpr);
      return booleanOp(op, values);
    }
    case "UnaryOp": {
      const op = UNARYOP_MAP[expr.op] || expr.op;
      return unaryOp(op, lowerExpr(expr.value || expr.operand));
    }
    case "IfExp": {
      return conditionalExpr(
        lowerExpr(expr.test),
        lowerExpr(expr.body || expr.then),
        lowerExpr(expr.orelse || expr.else)
      );
    }
    case "FunctionDef": {
      const params = expr.params || [];
      const bodyStmt = lowerExpr(expr.body);
      const body = returnNode(bodyStmt);
      const fn = { type: "Function", params, body: moduleNode([body]), defaults: [] };
      // Unnamed lambdas become Function values directly
      if (!expr.name) return fn;
      // Named functions become a Bind of the Function
      return fn;
    }
    case "Raw": {
      return lowerRawExpr(expr.value || "");
    }
    default:
      return diagnostic("unknown expr type: " + expr.type);
  }
}

function lowerNumber(raw) {
  const n = Number(raw);
  if (Number.isInteger(n) && raw.indexOf(".") === -1) {
    return literal(n, "int");
  }
  return literal(n, "float");
}

function lowerConstant(value) {
  if (value === null || value === "None") return NIL;
  if (value === true || value === "True") return literal(true, "bool");
  if (value === false || value === "False") return literal(false, "bool");
  return literal(value, "str");
}

// ─── Statement lowering ──────────────────────────────────────────────────────

function lowerStmt(stmt) {
  if (!stmt || typeof stmt !== "object") return noOp();

  switch (stmt.type) {
    case "FunctionDef":
      return lowerFuncDef(stmt);

    case "Assign":
      return lowerAssign(stmt);

    case "AugAssign":
      return lowerAugAssign(stmt);

    case "Expr":
      return lowerExprStmt(stmt);

    case "Return":
      return returnNode(stmt.value ? lowerExpr(stmt.value) : null);

    case "Yield":
      return yieldNode(stmt.value ? lowerExpr(stmt.value) : null);

    case "Raise":
      return raiseNode(stmt.value ? lowerExpr(stmt.value) : null);

    case "Pass":
    case "pass":
      return noOp();

    case "Break":
    case "break":
      return breakNode();

    case "Continue":
    case "continue":
      return continueNode();

    case "Simple": {
      const text = stmt.value || "";
      if (text === "pass") return noOp();
      if (text === "break") return breakNode();
      if (text === "continue") return continueNode();
      if (text.startsWith("defer ")) return defer(moduleNode([lowerRawStmt(text.slice(6))]));
      if (text.startsWith("import ") || text.startsWith("from ")) return diagnostic("import not yet in JS lowerer");
      return diagnostic("unknown simple stmt: " + text);
    }

    case "Suite":
      return lowerSuite(stmt);

    default:
      return diagnostic("unknown stmt type: " + stmt.type);
  }
}

function lowerFuncDef(stmt) {
  const params = stmt.params || [];
  const bodyExpr = stmt.body ? lowerExpr(stmt.body) : NIL;
  const defaults = [];
  const fn = { type: "Function", params, body: moduleNode([returnNode(bodyExpr)]), defaults };
  return bind(stmt.name, fn);
}

function lowerAssign(stmt) {
  const target = stmt.target || "";
  let value = stmt.value ? lowerExpr(stmt.value) : NIL;

  // _ placeholder → wrap as function: double = _ * 2 → double = x => x * 2
  if (containsUnderscore(value)) {
    value = wrapUnderscoreAsFunction(value);
  }

  // Function equation: f(x, y) = body
  if (target.includes("(") && target.endsWith(")")) {
    const paren = target.indexOf("(");
    const name = target.slice(0, paren).trim();
    const paramStr = target.slice(paren + 1, -1);
    const rawParams = paramStr ? paramStr.split(",").map(s => s.trim()).filter(s => s) : [];

    // Check for default-param syntax: f(x, y = default) = body
    let params = [];
    let defaults = [];
    let hasDefaults = false;
    for (const p of rawParams) {
      const eq = p.indexOf("=");
      if (eq >= 0) {
        params.push(p.slice(0, eq).trim());
        defaults.push(lowerRawExpr(p.slice(eq + 1).trim()));
        hasDefaults = true;
      } else {
        params.push(p);
      }
    }
    // If params contain non-identifiers, they're patterns; keep as-is for later merging
    return bind(name, { type: "Function", params, body: moduleNode([returnNode(value)]), defaults });
  }

  // Type alias: type X = ...
  if (target.startsWith("type ")) {
    return bind(target.slice(5).trim(), value);
  }

  // Annotation: x: T = value
  if (target.includes(":")) {
    const colon = target.indexOf(":");
    const name = target.slice(0, colon).trim();
    return bind(name, value);
  }

  return bind(target, value);
}

function lowerAugAssign(stmt) {
  const target = stmt.target || "";
  const op = AUGOP_MAP[stmt.op] || stmt.op || "+";
  const value = stmt.value ? lowerExpr(stmt.value) : NIL;
  return bind(target, binaryOp(load(target), op, value));
}

function lowerExprStmt(stmt) {
  const value = stmt.value ? lowerExpr(stmt.value) : NIL;

  // If the value is a Call, it can be used as a statement directly in Core IR.
  // The Core IR allows any expression as a statement.
  if (value.type === "Diagnostic") return value;

  // For expression statements, we lower the expression and wrap as needed.
  // In Core IR, any node in a Module body is valid; expressions don't need wrapping.
  return value;
}

// ─── Suite lowering ──────────────────────────────────────────────────────────

function lowerSuite(stmt) {
  const kind = stmt.kind || "";
  const head = stmt.head || "";
  const body = (stmt.body || []).map(lowerStmt);
  const clauses = stmt.clauses || [];

  // Extract else clause body if present
  function getElseBody() {
    for (const c of clauses) {
      if (c.kind === "Else") return (c.body || []).map(lowerStmt);
    }
    return [];
  }

  switch (kind) {
    case "Func": {
      const { name, params, defaults } = parseFuncHead(head);
      return bind(name, { type: "Function", params, body: moduleNode(body), defaults });
    }
    case "For": {
      const { target, iter } = parseForHead(head);
      return forEach(target, lowerExpr(iter), moduleNode(body), moduleNode(getElseBody()));
    }
    case "If": {
      // Check for if-let: if let x = expr
      if (head.startsWith("let ")) {
        const rest = head.slice(4).trim();
        const eq = rest.indexOf("=");
        if (eq >= 0) {
          const name = rest.slice(0, eq).trim();
          const value = rest.slice(eq + 1).trim();
          return branch(lowerRawExpr(value),
            moduleNode([bind(name, load("__if_let_value__")), ...body]),
            moduleNode(getElseBody())
          );
        }
      }
      const test = lowerRawExpr(head);
      return branch(test, moduleNode(body), moduleNode(getElseBody()));
    }
    case "While": {
      const test = lowerRawExpr(head);
      return loopNode(test, moduleNode(body), moduleNode(getElseBody()));
    }
    case "Unless": {
      const test = unaryOp("not", lowerRawExpr(head));
      return branch(test, moduleNode(body), []);
    }
    case "Class":
      return lowerDataLike("Class", head, body);
    case "Data":
      return lowerDataLike("Data", head, body);
    case "Match": {
      const subject = lowerRawExpr(head);
      const cases = body.map(s => lowerCaseClause(s)).filter(c => c);
      return matchNode(subject, cases);
    }
    case "Try": {
      const handlers = [];
      for (const c of clauses) {
        if (c.kind === "Except") {
          const handlerBody = (c.body || []).map(lowerStmt);
          const handler = lowerExceptHandler(c.head, handlerBody);
          if (handler) handlers.push(handler);
        }
      }
      let finalbody = [];
      for (const c of clauses) {
        if (c.kind === "Finally") {
          finalbody = (c.body || []).map(lowerStmt);
        }
      }
      return handle(moduleNode(body), handlers, moduleNode(finalbody));
    }
    case "BlockCall": {
      const callExpr = lowerRawExpr(head);
      return call(callExpr, [], { type: "Function", params: [], body: moduleNode(body), defaults: [] });
    }
    case "With":
      return diagnostic("with not yet in JS lowerer");
    case "Guard":
      return diagnostic("guard suite not yet in JS lowerer");
    case "ReturnMatch": {
      const subject = lowerRawExpr(head);
      const cases = body.map(s => lowerCaseClause(s)).filter(c => c);
      return returnNode(matchNode(subject, cases));
    }
    case "MatchAssign": {
      return diagnostic("match-assign not yet in JS lowerer");
    }
    case "WhereAssign": {
      const target = stmt.target || head.split("=")[0]?.trim() || "";
      const value = stmt.value ? lowerExpr(stmt.value) : lowerRawExpr(head.split("=").slice(1).join("=").trim());
      const whereBody = (stmt.body || []).map(lowerStmt);
      const iife = call(
        { type: "Function", params: [], body: moduleNode([...whereBody, returnNode(value)]), defaults: [] },
        []
      );
      return bind(target, iife);
    }
    case "WhereFunction": {
      const name = stmt.name || "";
      const params = stmt.params || [];
      const funcValue = stmt.value ? lowerExpr(stmt.value) : NIL;
      const whereBody = (stmt.body || []).map(lowerStmt);
      return bind(name, { type: "Function", params, body: moduleNode([...whereBody, returnNode(funcValue)]), defaults: [] });
    }
    default:
      return diagnostic("unknown suite kind: " + kind);
  }
}

function parseFuncHead(head) {
  if (!head) return { name: "", params: [], defaults: [] };
  const paren = head.indexOf("(");
  if (paren < 0) return { name: head.trim(), params: [], defaults: [] };
  const name = head.slice(0, paren).trim();
  const close = head.lastIndexOf(")");
  const paramStr = head.slice(paren + 1, close >= 0 ? close : head.length);
  const params = [];
  const defaults = [];
  if (paramStr.trim()) {
    for (const p of paramStr.split(",")) {
      const eq = p.indexOf("=");
      if (eq >= 0) {
        params.push(p.slice(0, eq).trim());
        defaults.push(lowerRawExpr(p.slice(eq + 1).trim()));
      } else {
        const trimmed = p.trim();
        if (trimmed) params.push(trimmed);
      }
    }
  }
  return { name, params, defaults };
}

function parseForHead(head) {
  const m = head.match(/^(.+?)\s+in\s+(.+)$/);
  if (m) return { target: m[1].trim(), iter: m[2].trim() };
  return { target: "_", iter: head };
}

function lowerCaseClause(stmt) {
  if (!stmt) return null;

  // Case clauses from the Rust parser are Suite nodes with kind="Case"
  if (stmt.type === "Suite" && stmt.kind === "Case") {
    return lowerCaseFromSuite(stmt);
  }

  return null;
}

function lowerCaseFromSuite(stmt) {
  const head = stmt.head || "";
  const body = (stmt.body || []).map(lowerStmt);

  // "case _: ..." → wildcard
  if (head.trim() === "_") {
    return patternTest(literal(null, "nil"), null, moduleNode(body));
  }

  // "case pattern if guard: ..."
  const ifIdx = head.lastIndexOf(" if ");
  let patternText = head;
  let guard = null;
  if (ifIdx >= 0) {
    patternText = head.slice(0, ifIdx).trim();
    guard = lowerRawExpr(head.slice(ifIdx + 4).trim());
  }

  const pattern = lowerPatternText(patternText);
  return patternTest(pattern, guard, moduleNode(body));
}

function lowerPatternText(text) {
  text = text.trim();
  if (!text || text === "_") return literal(null, "nil");

  // Number literal
  if (/^-?\d/.test(text)) return lowerNumber(text);

  // String literal
  if ((text.startsWith('"') && text.endsWith('"')) ||
      (text.startsWith("'") && text.endsWith("'"))) {
    return literal(text.slice(1, -1), "str");
  }

  // None / True / False
  if (text === "None") return NIL;
  if (text === "True") return literal(true, "bool");
  if (text === "False") return literal(false, "bool");

  // Name / variable pattern
  return load(text);
}

function lowerExceptHandler(head, body) {
  if (!head) return patternTest(literal(null, "nil"), null, moduleNode(body));
  const asIdx = head.indexOf(" as ");
  let excType = head;
  let bindName = null;
  if (asIdx >= 0) {
    excType = head.slice(0, asIdx).trim();
    bindName = head.slice(asIdx + 4).trim();
  }
  const excLoad = load(excType);
  if (bindName) {
    body = [bind(bindName, load("__exc_value__")), ...(body || [])];
  }
  return patternTest(excLoad, null, moduleNode(body));
}

function lowerDataLike(kind, head, body) {
  const paren = head.indexOf("(");
  const name = paren >= 0 ? head.slice(0, paren).trim() : head.trim();
  const fields = [];
  for (const s of body) {
    if (s.type === "Bind") {
      fields.push([load(s.name), s.value || NIL]);
    } else if (s.type === "Assign") {
      // Assign from Rust parser
      const val = s.value ? lowerExpr(s.value) : NIL;
      fields.push([load(s.target), val]);
    }
  }
  return constructData(name, fields);
}

// ─── Raw expression lowering ─────────────────────────────────────────────────

function lowerRawExpr(raw) {
  const text = raw.trim();
  if (!text) return diagnostic("empty raw expression");

  // Literals — handle before heuristics
  if (text === "None") return NIL;
  if (text === "True") return literal(true, "bool");
  if (text === "False") return literal(false, "bool");
  if (/^-?\d+(\.\d*)?$/.test(text)) return lowerNumber(text);
  if ((text.startsWith('"') && text.endsWith('"')) || (text.startsWith("'") && text.endsWith("'"))) {
    return literal(text.slice(1, -1), "str");
  }

  // Simple name
  if (/^[a-zA-Z_]\w*$/.test(text)) return load(text);

  // Dict/mapping literal: { key: value, ... }
  if (text.startsWith("{") && text.endsWith("}")) return lowerDictExpr(text);

  // $variable → environment/signal reference
  if (text.startsWith("$")) return load(text);

  // try ... except ... [finally ...] expression
  if (/^try\s/.test(text)) return lowerRawTryExpr(text);

  // inline match: match subject: case ... → ...
  if (/^match\s/.test(text)) return lowerRawMatchExpr(text);

  // Operator sections: (+) (+x) (x+)
  if (text.startsWith("(") && text.endsWith(")")) {
    const inner = text.slice(1, -1).trim();
    if (/^[+\-*/%@|&^~]/.test(inner) || /[+\-*/%@|&^~]$/.test(inner) || inner === "+" || inner === "-") {
      return lowerSectionExpr(inner);
    }
  }

  // Nullish coalescing: a ?? b
  if (text.includes("??")) return lowerNullishExpr(text);

  // Safe navigation: a?.b, a?.b?.c
  if (text.includes("?.")) return lowerSafeNavExpr(text);

  // Call-like: f (args, with, spaces) — must come before |>
  // so print(1 .. 10 |> sum) parses as call, not pipeline
  if (/^\w+\s*\(/.test(text)) return lowerCallExpr(text);

  // Pipeline: a |> b |> c
  if (text.includes("|>")) return lowerPipelineExpr(text);

  // Composition: f >>> g
  if (text.includes(">>>")) return lowerComposeExpr(text);

  // Arrow function: x => expr
  if (text.includes("=>")) {
    const idx = text.indexOf("=>");
    if (idx > 0) return lowerArrowExpr(text);
  }

  // Ranges: start..end, start..<end, start..end by step
  if (text.includes("..")) return lowerRangeExpr(text);

  // Comparison operators: left op right
  if (/[><=!]/.test(text) || /\b(?:is|in|not)\b/.test(text)) return lowerComparisonExpr(text);

  // Everything else: potentially Python-specific expression → diagnostic (triggers fallback)
  return diagnostic("raw expr not yet in JS lowerer: " + text.slice(0, 60));
}

function lowerRawTryExpr(text) {
  const tryMatch = text.match(/^try\s+(.+?)\s+except\s+(.+?)(?:\s+finally\s+(.+))?$/s);
  if (!tryMatch) return diagnostic("malformed try expr: " + text.slice(0, 60));

  const bodyExpr = lowerRawExpr(tryMatch[1].trim());
  const exceptText = tryMatch[2].trim();
  const finallyText = (tryMatch[3] || "").trim();

  let excType = "Exception";
  let handlerBody;
  const asIdx = exceptText.indexOf(":");
  if (asIdx >= 0) {
    const before = exceptText.slice(0, asIdx).trim();
    const after = exceptText.slice(asIdx + 1).trim();
    if (before) excType = before;
    handlerBody = lowerRawExpr(after);
  } else {
    handlerBody = lowerRawExpr(exceptText);
  }

  const handlers = [patternTest(load(excType), null, moduleNode([returnNode(handlerBody)]))];
  const finalbody = finallyText ? moduleNode([returnNode(lowerRawExpr(finallyText))]) : [];

  // Wrap as IIFE: (_ => try { return body } except { return handler })
  return call(
    { type: "Function", params: ["_"], body: moduleNode([
      handle(moduleNode([returnNode(bodyExpr)]), handlers, finalbody)
    ]), defaults: [] },
    []
  );
}

function lowerRawMatchExpr(text) {
  const m = text.match(/^match\s+(.+?)\s*:\s*(.+)$/s);
  if (!m) return diagnostic("malformed match expr: " + text.slice(0, 60));

  const subject = lowerRawExpr(m[1].trim());
  const rest = m[2].trim();

  // Parse "case pattern => body; case pattern => body"
  const parts = rest.split(/\s*;\s*case\s+/);
  parts[0] = parts[0].replace(/^case\s+/, "");

  const cases = [];
  for (const part of parts) {
    const arrow = part.indexOf("=>");
    if (arrow < 0) continue;
    const patternText = part.slice(0, arrow).trim();
    const bodyText = part.slice(arrow + 2).trim();
    cases.push(patternTest(
      lowerPatternText(patternText),
      null,
      moduleNode([returnNode(lowerRawExpr(bodyText))])
    ));
  }

  return call(
    { type: "Function", params: [], body: moduleNode([matchNode(subject, cases)]), defaults: [] },
    []
  );
}

function lowerSectionExpr(inner) {
  if (inner === "+" || inner === "-") {
    // Unary operator section
    const op = inner === "+" ? "+" : "-";
    return { type: "Function", params: ["_1"], body: moduleNode([returnNode(unaryOp(op, load("_1")))]), defaults: [] };
  }

  const opMatch = inner.match(/^([+\-*/%|&^~@]+)\s*(\w*)\s*$/);
  if (opMatch) {
    // Left section: (+x) — partially applied operator
    const op = opMatch[1];
    const operand = opMatch[2] ? lowerRawExpr(opMatch[2]) : null;
    if (operand) {
      return { type: "Function", params: ["_1"], body: moduleNode([returnNode(binaryOp(operand, op, load("_1")))]), defaults: [] };
    }
    return { type: "Function", params: ["_1"], body: moduleNode([returnNode(binaryOp(load("_1"), op, load("_1")))]), defaults: [] };
  }

  const rightMatch = inner.match(/^(\w+)\s*([+\-*/%|&^~@]+)\s*$/);
  if (rightMatch) {
    // Right section: (x+) — partially applied operator
    const operand = lowerRawExpr(rightMatch[1]);
    const op = rightMatch[2];
    return { type: "Function", params: ["_1"], body: moduleNode([returnNode(binaryOp(load("_1"), op, operand))]), defaults: [] };
  }

  return diagnostic("unrecognized section: " + inner);
}

function lowerNullishExpr(text) {
  const parts = text.split(/\?\?/);
  let result = lowerRawExpr(parts[parts.length - 1]);
  for (let i = parts.length - 2; i >= 0; i--) {
    const left = lowerRawExpr(parts[i]);
    result = conditionalExpr(
      compareOp(left, ["is not"], [NIL]),
      left,
      result
    );
  }
  return result;
}

function lowerSafeNavExpr(text) {
  // obj?.prop and obj?.method(args)
  // Each ?. segment wraps the left side in an IIFE:
  //   (_0 => _0 is not None ? _0.prop : None)(obj)
  const parts = text.split(/\?\./);
  let result = lowerRawExpr(parts[0].trim());
  for (let i = 1; i < parts.length; i++) {
    const segment = parts[i].trim();
    const accessExpr = parseSafeNavSegment(segment);
    result = wrapSafeNavStep(result, accessExpr);
  }
  return result;
}

// Parse the right side of ?. as either a property name or method call.
// Returns a Core IR node that references load("_0") as the object.
function parseSafeNavSegment(text) {
  const paren = text.indexOf("(");
  if (paren >= 0) {
    const methodName = text.slice(0, paren).trim();
    const close = text.lastIndexOf(")");
    const argsStr = text.slice(paren + 1, (close >= 0 ? close : text.length)).trim();
    const args = argsStr ? splitCallArgs(argsStr).map(s => lowerRawExpr(s.trim())) : [];
    return call(getField(load("_0"), methodName), args);
  }
  return getField(load("_0"), text);
}

// Wrap step: (_0 => _0 is not None ? accessExpr : None)(currentResult)
function wrapSafeNavStep(leftObj, accessExpr) {
  return call(
    { type: "Function", params: ["_0"], body: moduleNode([
      branch(
        compareOp(load("_0"), ["is not"], [NIL]),
        moduleNode([returnNode(accessExpr)]),
        moduleNode([returnNode(NIL)])
      )
    ]), defaults: [] },
    [leftObj]
  );
}

function lowerPipelineExpr(text) {
  const parts = text.split(/\s*\|\>\s*/);
  let result = lowerRawExpr(parts[0]);
  for (let i = 1; i < parts.length; i++) {
    const right = lowerRawExpr(parts[i]);
    if (right.type === "Call") {
      // Push result as first arg
      result = call(right.func, [result, ...right.args]);
    } else if (right.type === "Load") {
      result = call(right, [result]);
    } else {
      result = call(right, [result]);
    }
  }
  return result;
}

function lowerComposeExpr(text) {
  const parts = text.split(/\s*>>>\s*/);
  // f >>> g → x => g(f(x))
  const innerLoad = load("__x__");
  let result = call(lowerRawExpr(parts[0]), [innerLoad]);
  for (let i = 1; i < parts.length; i++) {
    result = call(lowerRawExpr(parts[i]), [result]);
  }
  return { type: "Function", params: ["__x__"], body: moduleNode([returnNode(result)]), defaults: [] };
}

function lowerArrowExpr(text) {
  const arrow = text.indexOf("=>");
  const paramStr = text.slice(0, arrow).trim();
  const bodyText = text.slice(arrow + 2).trim();

  let params = [];
  // x => expr OR (x, y) => expr
  if (paramStr.startsWith("(") && paramStr.endsWith(")")) {
    params = paramStr.slice(1, -1).split(",").map(s => s.trim()).filter(s => s);
  } else {
    params = [paramStr];
  }

  const body = lowerRawExpr(bodyText);
  return { type: "Function", params, body: moduleNode([returnNode(body)]), defaults: [] };
}

function lowerRangeExpr(text) {
  // Parse: start..end, start..<end, start..end by step
  const exclusiveIdx = text.indexOf("..<");
  const inclusiveIdx = text.indexOf("..");
  let sepIdx = exclusiveIdx >= 0 ? exclusiveIdx : inclusiveIdx;
  let exclusive = exclusiveIdx >= 0;

  if (sepIdx < 0) return diagnostic("malformed range: " + text);

  const start = text.slice(0, sepIdx).trim();
  const afterSep = text.slice(sepIdx + (exclusive ? 3 : 2));

  let end, step = "1";
  const byIdx = afterSep.indexOf(" by ");
  if (byIdx >= 0) {
    end = afterSep.slice(0, byIdx).trim();
    step = afterSep.slice(byIdx + 4).trim();
  } else {
    end = afterSep.trim();
  }

  // Desugar to: list(range(start, end, step)) or with exclusive: lambda style
  // Core IR uses host calls. We'll use a simpler desugaring:
  // list(range(start, end + (exclusive ? 0 : 1), step))
  // For now, emit a Call to the 'range' function
  // Inclusive range: end + 1 so range(1, 10+1) gives [1..10]
  const endNode = end ? lowerRawExpr(end) : null;
  const adjustedEnd = !endNode ? NIL : (exclusive ? endNode : binaryOp(endNode, "+", literal(1, "int")));

  const rangeArgs = [
    start ? lowerRawExpr(start) : NIL,
    adjustedEnd
  ];
  if (step !== "1") rangeArgs.push(lowerRawExpr(step));

  return call(load("list"), [call(load("range"), rangeArgs)]);
}

function lowerCallExpr(text) {
  const paren = text.indexOf("(");
  const close = text.lastIndexOf(")");
  if (paren < 0 || close < 0) return diagnostic("malformed call: " + text);

  const funcName = text.slice(0, paren).trim();
  const argsStr = text.slice(paren + 1, close).trim();

  const args = argsStr ? splitCallArgs(argsStr).map(s => lowerRawExpr(s.trim())) : [];
  return call(load(funcName), args);
}

// Split call arguments respecting nested parens/brackets
function splitCallArgs(text) {
  const result = [];
  let depth = 0;
  let current = "";
  for (let i = 0; i < text.length; i++) {
    const ch = text[i];
    if (ch === "," && depth === 0) {
      result.push(current);
      current = "";
    } else {
      if (ch === "(" || ch === "{" || ch === "[") depth++;
      if (ch === ")" || ch === "}" || ch === "]") depth--;
      current += ch;
    }
  }
  if (current.trim()) result.push(current);
  return result;
}

function lowerDictExpr(text) {
  const inner = text.slice(1, -1).trim();
  if (!inner) return mappingLiteral([]);
  const entries = [];
  const parts = splitCallArgs(inner);
  for (const part of parts) {
    const colon = part.indexOf(":");
    if (colon >= 0) {
      const key = lowerRawExpr(part.slice(0, colon).trim());
      const value = lowerRawExpr(part.slice(colon + 1).trim());
      entries.push([key, value]);
    }
  }
  return mappingLiteral(entries);
}

function lowerComparisonExpr(text) {
  // Try multi-char ops first, then single-char
  const ops = ["not in", "is not", ">=", "<=", "!=", "==", " in ", " is ", ">", "<"];
  for (const op of ops) {
    const idx = op.includes(" ") ? text.indexOf(op) : text.indexOf(op);
    if (idx > 0) {
      const left = text.slice(0, idx).trim();
      const right = text.slice(idx + op.length).trim();
      if (left && right) {
        const opName = op.trim();
        const opMap = { ">=": ">=", "<=": "<=", "!=": "!=", "==": "==", ">": ">", "<": "<",
                         "in": "in", "not in": "not in", "is": "is", "is not": "is not" };
        return compareOp(lowerRawExpr(left), [opMap[opName] || opName], [lowerRawExpr(right)]);
      }
    }
  }
  return diagnostic("raw comparison not handled: " + text.slice(0, 60));
}

function lowerRawStmt(text) {
  text = text.trim();
  if (text.startsWith("return ")) return returnNode(lowerRawExpr(text.slice(7)));
  if (text.startsWith("raise ")) return raiseNode(lowerRawExpr(text.slice(6)));
  const expr = lowerRawExpr(text);
  return expr;
}

// ─── Underscore placeholder detection ────────────────────────────────────────

function containsUnderscore(node) {
  if (!node || typeof node !== "object") return false;
  if (node.type === "Load" && node.name === "_") return true;
  for (const key of Object.keys(node)) {
    const val = node[key];
    if (Array.isArray(val)) {
      for (const item of val) {
        if (containsUnderscore(item)) return true;
      }
    } else if (typeof val === "object" && val !== null) {
      if (containsUnderscore(val)) return true;
    }
  }
  return false;
}

function wrapUnderscoreAsFunction(node) {
  return { type: "Function", params: ["_"], body: moduleNode([returnNode(node)]), defaults: [] };
}

// ─── Main entry point ────────────────────────────────────────────────────────

function lowerRustAstToCoreIr(rustAst) {
  diagnosticCount = 0;

  const body = (rustAst.body || []).map(lowerStmt);

  // Merge consecutive same-name function bindings into match-based functions.
  // E.g., fact(1) = 1; fact(n) = fact(n-1) * n → single match-based fact function.
  const merged = mergeFunctionOverloads(body);

  diagnosticCount += countDiagnostics({ type: "Module", body: merged });

  return {
    schema: CORE_IR_JSON_SCHEMA,
    version: CORE_IR_JSON_VERSION,
    root: moduleNode(merged),
    diagnosticCount
  };
}

// Merge consecutive Bind statements for the same name into match-based functions.
function mergeFunctionOverloads(body) {
  const result = [];
  let i = 0;
  while (i < body.length) {
    const stmt = body[i];
    if (stmt.type === "Bind" && stmt.value && stmt.value.type === "Function") {
      const name = stmt.name;
      const funcs = [];
      while (i < body.length && body[i].type === "Bind" && body[i].name === name && body[i].value && body[i].value.type === "Function") {
        funcs.push(body[i].value);
        i++;
      }
      if (funcs.length === 1) {
        result.push(bind(name, funcs[0]));
      } else {
        result.push(mergeIntoMatchFunction(name, funcs));
      }
    } else {
      result.push(stmt);
      i++;
    }
  }
  return result;
}

// Merge multiple function definitions into a single match-based function.
// Each function's params become match patterns; only simple patterns are handled.
function mergeIntoMatchFunction(name, funcs) {
  const matchParam = "__0";
  const cases = funcs.map(func => {
    const funcBody = func.body.body || [];
    // Extract the return value from the function body
    const returnStmt = funcBody.find(s => s.type === "Return");
    const caseBody = moduleNode([returnNode(returnStmt ? returnStmt.value : NIL)]);
    // Convert each param to a pattern
    const patterns = (func.params || []).map(p => paramToPattern(p));
    // For single-param functions, use a simple pattern
    const pattern = patterns.length === 1 ? patterns[0] : sequence(patterns);
    return patternTest(pattern, null, caseBody);
  });

  const fn = {
    type: "Function",
    params: [matchParam],
    body: moduleNode([matchNode(load(matchParam), cases)]),
    defaults: []
  };
  return bind(name, fn);
}

// Convert a function param string to a match pattern.
// "1" → Literal(1), "n" → Load("n"), '"x"' → Literal("x")
function paramToPattern(p) {
  if (p === "_") return NIL;
  if (p === "None") return NIL;
  if (p === "True") return literal(true, "bool");
  if (p === "False") return literal(false, "bool");
  if (/^-?\d+(\.\d*)?$/.test(p)) return lowerNumber(p);
  if ((p.startsWith('"') && p.endsWith('"')) || (p.startsWith("'") && p.endsWith("'"))) {
    return literal(p.slice(1, -1), "str");
  }
  return load(p);
}

function countDiagnostics(node) {
  if (!node || typeof node !== "object") return 0;
  let count = 0;
  if (node.type === "Diagnostic") count++;
  for (const key of Object.keys(node)) {
    const val = node[key];
    if (Array.isArray(val)) {
      for (const item of val) count += countDiagnostics(item);
    } else if (typeof val === "object" && val !== null) {
      count += countDiagnostics(val);
    }
  }
  return count;
}

// ─── Exports ─────────────────────────────────────────────────────────────────

if (typeof module !== "undefined" && module.exports) {
  module.exports = { lowerRustAstToCoreIr };
}
if (typeof self !== "undefined") {
  self.NomiCoreLowerer = { lowerRustAstToCoreIr };
}
