(function (root) {
  "use strict";

  const NUMBER = /^-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?$/;
  const INTEGER = /^-?(?:0|[1-9][0-9]*)$/;
  const TRIM = " \t\n\v\f\r";
  const SCHEMAS = {
    "report-options": [["minimum_age", "integer", 13]],
    "report-batch": [["customers", "rows", null]],
    "report-row": [["id", "nonblank", null], ["name", "nonblank", null], ["age", "integer", null]],
  };
  const fullmatch = (pattern, value) => {
    const match = value.match(pattern);
    return Boolean(match && match[0].length === value.length);
  };

  class BoundaryBudget {
    constructor(limits = {}) {
      this.inputBytes = 0;
      this.work = 0;
      this.outputBytes = 0;
      const fields = {
        inputLimit: ["input_limit", "input_bytes_per_call", 262144],
        aggregateInputLimit: ["aggregate_input_limit", "aggregate_input_bytes", 262144],
        workLimit: ["work_limit", "work", 1000000],
        outputLimit: ["output_limit", "encoded_bytes_per_run", 65536],
        depthLimit: ["depth_limit", "depth", 32],
        nodeLimit: ["node_limit", "nodes", 8192],
        diagnosticLimit: ["diagnostic_limit", "diagnostic_bytes", 16384],
        errorLimit: ["error_limit", "errors", 64],
        numericDigits: ["numeric_digit_limit", "decimal_digits", 16],
      };
      for (const [name, [field, alias, maximum]] of Object.entries(fields)) {
        const value = limits[field] ?? limits[alias] ?? maximum;
        if (!Number.isSafeInteger(value) || value < 0) throw new TypeError(`${field} must be a non-negative Int`);
        this[name] = Math.min(value, maximum);
      }
      this.diagnosticLimit = Math.max(256, this.diagnosticLimit);
    }
    charge(field, amount, limit) {
      this[field] += amount;
      return this[field] <= limit;
    }
    receipt() {
      return { profile: "js-safe-int", input_bytes: this.inputBytes, work: this.work,
        encoded_bytes: this.outputBytes, numeric_digit_limit: this.numericDigits };
    }
  }

  class BoundaryRefusal extends Error {
    constructor(code, expected, message, path = []) {
      super(message);
      this.name = "BoundaryRefusal";
      this.code = code;
      this.expected = expected;
      this.path = [...path];
    }
  }
  class DecodeStopped extends Error {}
  class NumberToken { constructor(token) { this.token = token; } }
  const UNSUPPORTED = Object.freeze(new (class UnsupportedValue {})());
  const refuse = (code, expected, message, path = []) => { throw new BoundaryRefusal(code, expected, message, path); };
  const limit = (expected, message) => refuse("NOMI-BOUNDARY-LIMIT", expected, message);
  function work(budget, amount = 1) {
    if (!budget.charge("work", amount, budget.workLimit)) limit("bounded boundary work", "Boundary processing exceeds the configured work budget.");
  }
  function scalar(char, budget, path = []) {
    work(budget);
    const number = char.codePointAt(0);
    if (number >= 0xd800 && number <= 0xdfff) refuse("NOMI-TEXT-INVALID", "Unicode scalar Text", "Replace the lone surrogate with valid Unicode text.", path);
    return number < 0x80 ? 1 : number < 0x800 ? 2 : number < 0x10000 ? 3 : 4;
  }
  function escape(char) {
    const escapes = { "\b": "\\b", "\t": "\\t", "\n": "\\n", "\f": "\\f", "\r": "\\r", '"': '\\"', "\\": "\\\\" };
    return escapes[char] ?? (char.codePointAt(0) < 32 ? `\\u${char.codePointAt(0).toString(16).padStart(4, "0")}` : char);
  }
  function pathText(path) {
    return path.reduce((text, part) => text + (typeof part === "number" ? `[${part}]` : fullmatch(/^[A-Za-z_][A-Za-z_0-9]*$/, part) ? `.${part}` : `["${[...part].map(escape).join("")}"]`), "$");
  }
  const errorRecord = (code, path, expected, message) => ({ code, path: [...path], path_text: pathText(path), expected, message });

  function plainMap(value) {
    if (value === null || typeof value !== "object") return false;
    const prototype = Object.getPrototypeOf(value);
    if (prototype !== Object.prototype && prototype !== null) return false;
    return Reflect.ownKeys(value).every(key => typeof key === "string" && "value" in Object.getOwnPropertyDescriptor(value, key));
  }
  function strictList(value) {
    if (!Array.isArray(value) || Object.getPrototypeOf(value) !== Array.prototype) return false;
    const keys = Reflect.ownKeys(value);
    if (keys.length !== value.length + 1) return false;
    for (let index = 0; index < value.length; index++) {
      if (!Object.hasOwn(value, index) || !("value" in Object.getOwnPropertyDescriptor(value, index))) return false;
    }
    return true;
  }
  function orderedKeys(keys, budget) {
    return [...keys].sort((left, right) => {
      const a = left[Symbol.iterator](), b = right[Symbol.iterator]();
      while (true) {
        const x = a.next(), y = b.next();
        if (x.done || y.done) return x.done === y.done ? 0 : x.done ? -1 : 1;
        work(budget, 2);
        if (x.value !== y.value) return x.value.codePointAt(0) - y.value.codePointAt(0);
      }
    });
  }

  class Sink {
    constructor(budget, category, maximum, collect = true) {
      this.budget = budget;
      this.category = category;
      this.maximum = maximum;
      this.size = 0;
      this.parts = collect ? [] : null;
    }
    put(text) {
      let size = 0;
      for (const char of text) size += scalar(char, this.budget);
      work(this.budget, size);
      this.size += size;
      const field = this.category === "input" ? "inputBytes" : "outputBytes";
      const maximum = this.category === "input" ? this.budget.aggregateInputLimit : this.budget.outputLimit;
      if (this.size > this.maximum || (this.category && !this.budget.charge(field, size, maximum))) {
        if (this.category === "input") limit("bounded input bytes", "Input exceeds the configured byte budget.");
        limit("bounded encoded output", "Encoded output exceeds the configured byte budget.");
      }
      if (this.parts !== null) this.parts.push(text);
    }
    quote(text, path = []) {
      this.put('"');
      for (const char of text) {
        scalar(char, this.budget, path);
        this.put(escape(char));
      }
      this.put('"');
    }
  }

  function write(value, sink, path = [], depth = 0, active = new Set(), nodes = { count: 0 }) {
    work(sink.budget);
    if (++nodes.count > sink.budget.nodeLimit) limit("bounded value tree", "Input exceeds a structural boundary limit.");
    if (value === null) sink.put("null");
    else if (typeof value === "boolean") sink.put(value ? "true" : "false");
    else if (typeof value === "number" && Number.isInteger(value)) {
      if (!Number.isSafeInteger(value) || String(value).replace(/^-/, "").length > sink.budget.numericDigits) refuse("NOMI-NUMERIC-CAPACITY", "Int within backend capacity", "Use a backend that supports this exact integer.", path);
      const token = String(value);
      work(sink.budget, token.length);
      sink.put(token);
    } else if (typeof value === "string") sink.quote(value, path);
    else if (strictList(value) || plainMap(value)) {
      if (active.has(value)) refuse("NOMI-ENCODE-CYCLE", "acyclic structural value", "Remove the cycle from this value.", path);
      if (depth + 1 > sink.budget.depthLimit) limit("bounded value tree", "Input exceeds a structural boundary limit.");
      active.add(value);
      try {
        if (Array.isArray(value)) {
          sink.put("[");
          value.forEach((item, index) => {
            if (index) sink.put(",");
            write(item, sink, [...path, index], depth + 1, active, nodes);
          });
          sink.put("]");
        } else {
          const keys = Object.keys(value);
          for (const key of keys) {
            work(sink.budget);
            for (const char of key) scalar(char, sink.budget, [...path, key]);
          }
          sink.put("{");
          orderedKeys(keys, sink.budget).forEach((key, index) => {
            if (index) sink.put(",");
            sink.quote(key, [...path, key]);
            sink.put(":");
            write(value[key], sink, [...path, key], depth + 1, active, nodes);
          });
          sink.put("}");
        }
      } finally { active.delete(value); }
    } else refuse("NOMI-ENCODE-TYPE", "JSON structural value", "Provide only null, Bool, Int, Text, List, and text-keyed Map values.", path);
  }

  function failure(kind, refusal, { errors = null, complete = false, budget = new BoundaryBudget() } = {}) {
    if (errors === null) errors = [errorRecord(refusal.code, refusal.path, refusal.expected, refusal.message)];
    const result = { ok: false, kind, errors, complete };
    const sink = new Sink(new BoundaryBudget(), null, budget.diagnosticLimit, false);
    try { write(result, sink); }
    catch (error) {
      if (!(error instanceof BoundaryRefusal)) throw error;
      return { ok: false, kind, errors: [errorRecord("NOMI-BOUNDARY-LIMIT", [], "bounded diagnostic output", "Validation stopped at the diagnostic budget.")], complete: false };
    }
    return result;
  }

  class Scanner {
    constructor(text, budget) { this.chars = [...text]; this.budget = budget; this.index = 0; this.nodes = 0; }
    peek() { return this.chars[this.index] ?? ""; }
    take() { if (this.index === this.chars.length) this.syntax(); work(this.budget); return this.chars[this.index++]; }
    whitespace() { while (this.peek() && " \t\r\n".includes(this.peek())) this.take(); }
    syntax(message = "Correct the JSON syntax.") { refuse("NOMI-JSON-SYNTAX", "one JSON value", message); }
    hexadecimal() {
      let chars = "";
      for (let index = 0; index < 4; index++) chars += this.take();
      if (!/^[0-9a-fA-F]{4}$/.test(chars)) this.syntax();
      return parseInt(chars, 16);
    }
    string(path) {
      if (this.take() !== '"') this.syntax();
      const chars = [], escapes = { '"': '"', "\\": "\\", "/": "/", b: "\b", f: "\f", n: "\n", r: "\r", t: "\t" };
      while (true) {
        const char = this.take();
        if (char === '"') return chars.join("");
        if (char.codePointAt(0) < 32) this.syntax();
        if (char !== "\\") { chars.push(char); continue; }
        const escaped = this.take();
        if (Object.hasOwn(escapes, escaped)) chars.push(escapes[escaped]);
        else if (escaped === "u") {
          let number = this.hexadecimal();
          if (number >= 0xd800 && number <= 0xdbff) {
            if (this.peek() !== "\\") refuse("NOMI-TEXT-INVALID", "Unicode scalar Text", "Replace the lone surrogate with valid Unicode text.", path);
            this.take();
            if (this.take() !== "u") refuse("NOMI-TEXT-INVALID", "Unicode scalar Text", "Replace the lone surrogate with valid Unicode text.", path);
            const low = this.hexadecimal();
            if (low < 0xdc00 || low > 0xdfff) refuse("NOMI-TEXT-INVALID", "Unicode scalar Text", "Replace the lone surrogate with valid Unicode text.", path);
            number = 0x10000 + ((number - 0xd800) << 10) + low - 0xdc00;
          } else if (number >= 0xdc00 && number <= 0xdfff) refuse("NOMI-TEXT-INVALID", "Unicode scalar Text", "Replace the lone surrogate with valid Unicode text.", path);
          chars.push(String.fromCodePoint(number));
        } else this.syntax();
      }
    }
    value(path = [], depth = 0) {
      this.whitespace(); work(this.budget);
      if (++this.nodes > this.budget.nodeLimit) limit("bounded value tree", "Input exceeds a structural boundary limit.");
      const char = this.peek();
      if (char === '"') return { kind: "text", value: this.string(path) };
      if (char === "[" || char === "{") {
        if (depth + 1 > this.budget.depthLimit) limit("bounded value tree", "Input exceeds a structural boundary limit.");
        this.take(); this.whitespace();
        const closing = char === "[" ? "]" : "}", values = [], seen = new Set();
        if (this.peek() === closing) { this.take(); return char === "[" ? { kind: "list", items: values } : { kind: "map", entries: values }; }
        while (true) {
          if (char === "[") values.push(this.value([...path, values.length], depth + 1));
          else {
            this.whitespace();
            if (this.peek() !== '"') this.syntax();
            const key = this.string(path);
            work(this.budget, [...key].length + 1);
            if (seen.has(key)) refuse("NOMI-JSON-DUPLICATE-KEY", "unique object key", "Remove the duplicate object key.", [...path, key]);
            seen.add(key); this.whitespace();
            if (this.take() !== ":") this.syntax();
            values.push([key, this.value([...path, key], depth + 1)]);
          }
          this.whitespace();
          const separator = this.take();
          if (separator === closing) break;
          if (separator !== ",") this.syntax();
        }
        return char === "[" ? { kind: "list", items: values } : { kind: "map", entries: values };
      }
      for (const [token, node] of [["null", { kind: "null" }], ["true", { kind: "bool", value: true }], ["false", { kind: "bool", value: false }]]) {
        if (this.chars.slice(this.index, this.index + token.length).join("") === token) {
          for (const ignored of token) this.take();
          return node;
        }
      }
      if (char && "-0123456789".includes(char)) {
        const start = this.index;
        while (this.peek() && "-+0123456789.eE".includes(this.peek())) this.take();
        const token = this.chars.slice(start, this.index).join("");
        work(this.budget, token.length);
        if (!fullmatch(NUMBER, token)) this.syntax();
        return { kind: "number", token };
      }
      this.syntax();
    }
  }

  function parseJson(text, budget = new BoundaryBudget()) {
    if (typeof text !== "string") throw new TypeError("parse_json expects Text");
    try {
      let size = 0;
      for (const char of text) {
        const amount = scalar(char, budget); size += amount;
        if (size > budget.inputLimit || !budget.charge("inputBytes", amount, budget.aggregateInputLimit)) limit("bounded input bytes", "Input exceeds the configured byte budget.");
      }
      const scanner = new Scanner(text, budget), node = scanner.value();
      scanner.whitespace();
      if (scanner.index !== scanner.chars.length) scanner.syntax("Remove trailing content after the JSON value.");
      return { ok: true, value: { schema: "nomi.json-value", version: 1, root: node } };
    } catch (error) {
      if (!(error instanceof BoundaryRefusal)) throw error;
      return failure("input-format", error, { budget });
    }
  }

  function validateTree(tree, budget) {
    const invalid = (path = []) => refuse("NOMI-VALUE-TREE", "nomi.json-value version 1", "Provide a supported structural Value tree.", path);
    const exactKeys = (value, keys) => plainMap(value) && Object.keys(value).length === keys.length && keys.every(key => Object.hasOwn(value, key));
    work(budget);
    if (!exactKeys(tree, ["schema", "version", "root"]) || tree.schema !== "nomi.json-value" || tree.version !== 1) invalid();
    const sink = new Sink(budget, "input", budget.inputLimit, false), active = new Set(); let nodes = 0;
    const visit = (node, path, depth) => {
      work(budget);
      if (++nodes > budget.nodeLimit) limit("bounded value tree", "Input exceeds a structural boundary limit.");
      if (!plainMap(node) || active.has(node)) invalid(path);
      work(budget, Object.keys(node).length);
      const kind = node.kind, fields = { null: ["kind"], bool: ["kind", "value"], text: ["kind", "value"], number: ["kind", "token"], list: ["kind", "items"], map: ["kind", "entries"] };
      if (typeof kind !== "string" || !Object.hasOwn(fields, kind) || !exactKeys(node, fields[kind])) invalid(path);
      if ((kind === "list" || kind === "map") && depth + 1 > budget.depthLimit) limit("bounded value tree", "Input exceeds a structural boundary limit.");
      active.add(node);
      try {
        if (kind === "null") { sink.put("null"); return null; }
        if (kind === "bool") { if (typeof node.value !== "boolean") invalid(path); sink.put(node.value ? "true" : "false"); return node.value; }
        if (kind === "text") { if (typeof node.value !== "string") invalid(path); sink.quote(node.value, path); return node.value; }
        if (kind === "number") {
          if (typeof node.token !== "string") invalid(path);
          sink.put(node.token); work(budget, [...node.token].length);
          if (!fullmatch(NUMBER, node.token)) invalid(path);
          return new NumberToken(node.token);
        }
        if (kind === "list") {
          if (!strictList(node.items)) invalid(path);
          sink.put("[");
          const values = node.items.map((child, index) => { if (index) sink.put(","); return visit(child, [...path, index], depth + 1); });
          sink.put("]"); return values;
        }
        if (!strictList(node.entries)) invalid(path);
        sink.put("{"); const values = Object.create(null);
        node.entries.forEach((entry, index) => {
          work(budget);
          if (!strictList(entry) || entry.length !== 2 || typeof entry[0] !== "string") invalid(path);
          const [key, child] = entry;
          for (const char of key) scalar(char, budget, [...path, key]);
          work(budget, [...key].length + 1);
          if (Object.hasOwn(values, key)) invalid([...path, key]);
          if (index) sink.put(","); sink.quote(key, [...path, key]); sink.put(":");
          values[key] = visit(child, [...path, key], depth + 1);
        });
        sink.put("}"); return values;
      } finally { active.delete(node); }
    };
    return visit(tree.root, [], 0);
  }

  function decodeData(tree, schemaName, budget = new BoundaryBudget()) {
    if (typeof schemaName !== "string") throw new TypeError("decode_data schema name must be Text");
    if (!["report-options", "report-batch"].includes(schemaName)) throw new Error("Choose a supported report schema.");
    const errors = [], defaults = [];
    const add = (code, path, expected, message) => {
      if (errors.length === budget.errorLimit) throw new DecodeStopped();
      errors.push(errorRecord(code, path, expected, message));
    };
    const field = (value, shape, path) => {
      work(budget);
      if (shape === "integer") {
        if (!(value instanceof NumberToken)) { add("NOMI-DECODE-TYPE", path, "integer-form JSON number", "Use an integer-form JSON number for this field."); return null; }
        work(budget, value.token.length);
        if (!fullmatch(INTEGER, value.token)) { add("NOMI-DECODE-TYPE", path, "integer-form JSON number", "Use an integer-form JSON number for this field."); return null; }
        if (value.token.replace(/^-/, "").length > budget.numericDigits) refuse("NOMI-NUMERIC-CAPACITY", "Int within backend capacity", "Use a backend that supports this exact integer.", path);
        work(budget, value.token.length);
        const exact = BigInt(value.token), maximum = BigInt(Number.MAX_SAFE_INTEGER);
        if (exact > maximum || exact < -maximum) refuse("NOMI-NUMERIC-CAPACITY", "Int within backend capacity", "Use a backend that supports this exact integer.", path);
        const number = Number(exact);
        if (number < 0) add("NOMI-DECODE-CONSTRAINT", path, "non-negative Int", "Use an integer greater than or equal to zero.");
        return number;
      }
      if (shape === "nonblank") {
        if (typeof value !== "string") { add("NOMI-DECODE-TYPE", path, "Text", "Use Text for this field."); return null; }
        for (const char of value) scalar(char, budget, path);
        if (!trimText(value, budget)) add("NOMI-DECODE-CONSTRAINT", path, "nonblank Text", "Provide text that is nonblank after the declared trim.");
        return value;
      }
      if (!strictList(value)) { add("NOMI-DECODE-TYPE", path, "list", "Use a list for customers."); return null; }
      if (value.length > 128) { add("NOMI-DECODE-CONSTRAINT", path, "at most 128 customers", "Reduce the number of customers."); return null; }
      return value.map((row, index) => record(row, "report-row", [...path, index]));
    };
    const record = (value, descriptor, path) => {
      work(budget);
      if (!plainMap(value)) { add("NOMI-DECODE-TYPE", path, "object", path.length ? "Use an object for each customer." : "Use an object at this boundary."); return null; }
      const result = {}, fields = SCHEMAS[descriptor], names = new Set(fields.map(([name]) => name));
      for (const [name, shape, defaultValue] of fields) {
        work(budget); const childPath = [...path, name];
        if (!Object.hasOwn(value, name)) {
          if (defaultValue === null) add("NOMI-DECODE-MISSING", childPath, "required field", "Provide the required field.");
          else { result[name] = defaultValue; defaults.push(childPath); }
        } else result[name] = field(value[name], shape, childPath);
      }
      for (const key of orderedKeys(Object.keys(value), budget)) {
        work(budget, [...key].length + 1);
        if (!names.has(key)) add("NOMI-DECODE-EXTRA", [...path, key], "declared field", "Remove the unexpected field.");
      }
      return result;
    };
    try {
      const value = validateTree(tree, budget), result = record(value, schemaName, []);
      return errors.length ? failure("decode", null, { errors, complete: true, budget }) : { ok: true, value: result, defaults_applied: defaults };
    } catch (error) {
      if (error instanceof DecodeStopped) return failure("decode", null, { errors, complete: false, budget });
      if (!(error instanceof BoundaryRefusal)) throw error;
      return failure("decode", error, { budget });
    }
  }

  function trimText(text, budget = new BoundaryBudget()) {
    if (typeof text !== "string") throw new TypeError("trim_text expects Text");
    const chars = [];
    for (const char of text) { scalar(char, budget); chars.push(char); }
    let first = 0, last = chars.length;
    while (first < last) { work(budget); if (!TRIM.includes(chars[first])) break; first++; }
    while (first < last) { work(budget); if (!TRIM.includes(chars[last - 1])) break; last--; }
    return chars.slice(first, last).join("");
  }

  function encodeJson(value, budget = new BoundaryBudget()) {
    const sink = new Sink(budget, "output", budget.outputLimit);
    try { write(value, sink); return { ok: true, text: sink.parts.join("") }; }
    catch (error) {
      if (!(error instanceof BoundaryRefusal)) throw error;
      return failure("encode", error, { budget });
    }
  }

  const library = { BoundaryBudget, BoundaryRefusal, UNSUPPORTED, parseJson, decodeData, encodeJson, trimText, failure };
  if (typeof module !== "undefined" && module.exports) module.exports = library;
  root.NomiReportBoundary = library;
})(globalThis);
