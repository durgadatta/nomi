// Nomi Core Runtime for serialized Core IR.
//
// This is the first non-Python evaluator: it consumes the JSON schema emitted
// by prototype.syntax.core_json and keeps values, frames, and control flow as
// explicit tagged runtime data.

"use strict";

const CORE_IR_JSON_SCHEMA = "nomi.core-ir";
const CORE_IR_JSON_VERSION = 1;

const NIL = Object.freeze({ kind: "nil" });

function native(name, call, expectsValues = false) {
  return { kind: "native", name, call, expectsValues };
}

function valueError(message) {
  const error = new Error(message);
  error.name = "ValueError";
  return error;
}

function box(value, valueType = null) {
  if (value && typeof value === "object" && typeof value.kind === "string") {
    return value;
  }
  if (value === null || value === undefined) return NIL;
  if (typeof value === "boolean") return { kind: "bool", value };
  if (typeof value === "number") {
    return valueType === "float" || !Number.isInteger(value)
      ? { kind: "float", value }
      : { kind: "int", value };
  }
  if (typeof value === "string") return { kind: "str", value };
  if (Array.isArray(value)) return { kind: "sequence", elements: value.map(box) };
  if (typeof value === "function") {
    return { kind: "native", name: value.name || "native", call: value };
  }
  if (typeof value === "object") {
    const entries = new Map();
    for (const [key, item] of Object.entries(value)) {
      entries.set(key, box(item));
    }
    return { kind: "mapping", entries };
  }
  throw new TypeError(`Cannot box ${typeof value}`);
}

function unbox(value) {
  switch (value.kind) {
    case "nil":
      return null;
    case "bool":
    case "int":
    case "float":
    case "str":
      return value.value;
    case "sequence":
      return value.elements.map(unbox);
    case "mapping": {
      const result = {};
      for (const [key, item] of value.entries) result[key] = unbox(item);
      return result;
    }
    case "data": {
      const fields = {};
      for (const [key, item] of Object.entries(value.fields)) {
        fields[key] = unbox(item);
      }
      return { [value.name]: fields };
    }
    case "constructor":
      return `<data ${value.name}>`;
    case "function":
      return `<function (${value.params.join(", ")})>`;
    case "native":
      return value.call;
    case "error":
      throw new Error(value.message);
    default:
      throw new TypeError(`Cannot unbox ${value.kind}`);
  }
}

function truthy(value) {
  switch (value.kind) {
    case "nil":
      return false;
    case "bool":
      return value.value;
    case "int":
    case "float":
      return value.value !== 0;
    case "str":
      return value.value !== "";
    case "sequence":
      return value.elements.length > 0;
    case "mapping":
      return value.entries.size > 0;
    default:
      return true;
  }
}

class Frame {
  constructor(parent = null) {
    this.parent = parent;
    this.bindings = new Map();
  }

  lookup(name) {
    if (this.bindings.has(name)) return this.bindings.get(name);
    return this.parent ? this.parent.lookup(name) : undefined;
  }

  bind(name, value) {
    this.bindings.set(name, value);
  }

  assign(name, value) {
    const frame = this.nearestFrameWith(name);
    if (frame) frame.bindings.set(name, value);
    else this.bindings.set(name, value);
  }

  nearestFrameWith(name) {
    if (this.bindings.has(name)) return this;
    return this.parent ? this.parent.nearestFrameWith(name) : null;
  }

  extend(params = [], args = []) {
    if (params.length !== args.length) {
      throw new TypeError(`Expected ${params.length} arguments, received ${args.length}`);
    }
    const child = new Frame(this);
    params.forEach((param, index) => child.bind(param, args[index]));
    return child;
  }
}

function signal(kind, value = NIL) {
  return { control: kind, value };
}

function isSignal(value) {
  return value && typeof value === "object" && typeof value.control === "string";
}

class CoreRuntime {
  constructor(hostCalls = {}) {
    this.stdout = [];
    this.defaultHostNames = new Set();
    this.globalFrame = new Frame();
    this.currentFrame = this.globalFrame;
    this.currentBlock = null;
    const calls = { ...this.defaultHostCalls(), ...hostCalls };
    for (const [name, call] of Object.entries(calls)) {
      this.globalFrame.bind(name, box(call));
      if (!(name in hostCalls)) this.defaultHostNames.add(name);
    }
  }

  evaluate(corePayload, options = {}) {
    const root = this.unwrapPayload(corePayload);
    const result = this.evalModule(root);
    if (isSignal(result)) {
      throw new Error(`Unexpected ${result.control} at module level`);
    }
    if (result.kind === "error") {
      throw new Error(result.message);
    }
    const bindings = {};
    for (const [name, value] of this.globalFrame.bindings) {
      if (this.defaultHostNames.has(name)) continue;
      bindings[name] = unbox(value);
    }
    const hasValue = options.displayLastExpr === true && result !== NIL;
    return {
      backend: "js-core-runtime",
      bindings,
      value: hasValue ? unbox(result) : null,
      has_value: hasValue,
      stdout: this.stdout.join(""),
      diagnostics: [],
    };
  }

  unwrapPayload(corePayload) {
    if (corePayload && corePayload.schema === CORE_IR_JSON_SCHEMA) {
      if (corePayload.version !== CORE_IR_JSON_VERSION) {
        throw new Error(`Unsupported Core IR JSON version ${corePayload.version}`);
      }
      return corePayload.root;
    }
    return corePayload;
  }

  evalModule(node) {
    if (!node) return NIL;
    let last = NIL;
    for (const stmt of node.body || []) {
      last = this.eval(stmt);
      if (isSignal(last) || last.kind === "error") return last;
    }
    return last;
  }

  eval(node) {
    if (!node) return NIL;
    const method = this[`eval${node.type}`];
    if (!method) throw new Error(`JS Core Runtime does not dispatch ${node.type}`);
    return method.call(this, node);
  }

  evalModuleNode(node) {
    return this.evalModule(node);
  }

  evalLiteral(node) {
    return box(node.value, node.value_type || null);
  }

  evalLoad(node) {
    const value = this.currentFrame.lookup(node.name);
    if (value === undefined) throw new ReferenceError(`name '${node.name}' is not defined`);
    return value;
  }

  evalBind(node) {
    const value = this.eval(node.value);
    if (isSignal(value)) return value;
    this.currentFrame.assign(node.name, value);
    return value;
  }

  evalFunction(node) {
    return {
      kind: "function",
      params: node.params || [],
      body: node.body,
      closure: this.currentFrame,
    };
  }

  evalCall(node) {
    const func = this.eval(node.func);
    if (isSignal(func)) return func;
    const args = [];
    for (const argNode of node.args || []) {
      const arg = this.eval(argNode);
      if (isSignal(arg)) return arg;
      args.push(arg);
    }
    const block = node.block ? this.eval(node.block) : null;
    if (isSignal(block)) return block;
    if (block !== null && block.kind !== "function") {
      throw new TypeError(`${block.kind} is not a block`);
    }
    return this.applyCallable(func, args, block);
  }

  applyCallable(func, args, block = null) {
    if (func.kind === "native") return this.callNative(func, args);
    if (func.kind === "constructor") return this.constructData(func, args);
    if (func.kind !== "function") throw new TypeError(`${func.kind} is not callable`);

    const savedFrame = this.currentFrame;
    const savedBlock = this.currentBlock;
    this.currentFrame = func.closure.extend(func.params, args);
    this.currentBlock = block;
    try {
      const result = this.evalModule(func.body);
      if (isSignal(result) && result.control === "return") return result.value;
      return result;
    } finally {
      this.currentFrame = savedFrame;
      this.currentBlock = savedBlock;
    }
  }

  callNative(func, args) {
    try {
      const result = func.expectsValues
        ? func.call(...args)
        : func.call(...args.map(unbox));
      return box(result);
    } catch (error) {
      return {
        kind: "error",
        errorKind: error && error.name ? error.name : "Error",
        message: error && error.message ? error.message : String(error),
      };
    }
  }

  evalReturn(node) {
    const value = this.eval(node.value);
    if (isSignal(value)) return value;
    if (value.kind === "error") return value;
    return signal("return", value);
  }

  evalYield(node) {
    const value = this.eval(node.value);
    if (isSignal(value)) return value;
    if (value.kind === "error") return value;
    if (this.currentBlock !== null) {
      const args = this.currentBlock.params.length > 0 ? [value] : [];
      const result = this.applyCallable(this.currentBlock, args);
      if (isSignal(result)) return result;
      return NIL;
    }
    return signal("yield", value);
  }

  evalBranch(node) {
    const test = this.eval(node.test);
    if (isSignal(test)) return test;
    return this.evalModule(truthy(test) ? node.then_body : node.else_body);
  }

  evalNoOp(_node) {
    return NIL;
  }

  evalBreak(_node) {
    return signal("break");
  }

  evalContinue(_node) {
    return signal("continue");
  }

  evalLoop(node) {
    let last = NIL;
    while (true) {
      const test = this.eval(node.test);
      if (isSignal(test)) return test;
      if (!truthy(test)) return node.else_body ? this.evalModule(node.else_body) : last;
      const bodyResult = this.evalModule(node.body);
      if (isSignal(bodyResult) && bodyResult.control === "break") return NIL;
      if (isSignal(bodyResult) && bodyResult.control === "continue") continue;
      if (isSignal(bodyResult)) return bodyResult;
      last = bodyResult;
    }
  }

  evalForEach(node) {
    const iterable = this.eval(node.iterable);
    if (isSignal(iterable)) return iterable;
    let ran = false;
    let last = NIL;
    for (const item of this.iterValues(iterable)) {
      ran = true;
      this.currentFrame.assign(node.target, item);
      const bodyResult = this.evalModule(node.body);
      if (isSignal(bodyResult) && bodyResult.control === "break") return NIL;
      if (isSignal(bodyResult) && bodyResult.control === "continue") continue;
      if (isSignal(bodyResult)) return bodyResult;
      last = bodyResult;
    }
    return !ran && node.else_body ? this.evalModule(node.else_body) : last;
  }

  evalUnaryOp(node) {
    const operand = this.eval(node.operand);
    if (isSignal(operand)) return operand;
    const value = unbox(operand);
    if (node.op === "+") return box(+value, operand.kind);
    if (node.op === "-") return box(-value, operand.kind);
    if (node.op === "~") return box(~value);
    if (node.op === "not") return box(!truthy(operand));
    throw new Error(`Unsupported unary op ${node.op}`);
  }

  evalBinaryOp(node) {
    const left = this.eval(node.left);
    if (isSignal(left)) return left;
    const right = this.eval(node.right);
    if (isSignal(right)) return right;
    const result = this.applyBinaryOp(node.op, unbox(left), unbox(right));
    return box(result, this.binaryResultKind(node.op, left, right, result));
  }

  evalBooleanOp(node) {
    if (!node.values || node.values.length === 0) return NIL;
    let last = NIL;
    if (node.op === "and") {
      for (const valueNode of node.values) {
        last = this.eval(valueNode);
        if (isSignal(last) || !truthy(last)) return last;
      }
      return last;
    }
    if (node.op === "or") {
      for (const valueNode of node.values) {
        last = this.eval(valueNode);
        if (isSignal(last) || truthy(last)) return last;
      }
      return last;
    }
    throw new Error(`Unsupported boolean op ${node.op}`);
  }

  evalCompareOp(node) {
    const left = this.eval(node.left);
    if (isSignal(left)) return left;
    let current = unbox(left);
    for (let index = 0; index < node.ops.length; index += 1) {
      const right = this.eval(node.comparators[index]);
      if (isSignal(right)) return right;
      const rightValue = unbox(right);
      if (!this.applyCompareOp(node.ops[index], current, rightValue)) return box(false);
      current = rightValue;
    }
    return box(true);
  }

  evalConditionalExpr(node) {
    const test = this.eval(node.test);
    if (isSignal(test)) return test;
    return this.eval(truthy(test) ? node.then_value : node.else_value);
  }

  evalSequence(node) {
    const elements = [];
    for (const elementNode of node.elements || []) {
      if (elementNode.type === "Spread") {
        const spreadValue = this.eval(elementNode.value);
        if (isSignal(spreadValue)) return spreadValue;
        elements.push(...this.spreadElements(spreadValue));
        continue;
      }
      const value = this.eval(elementNode);
      if (isSignal(value)) return value;
      elements.push(value);
    }
    return { kind: "sequence", elements };
  }

  evalMappingLiteral(node) {
    const entries = new Map();
    for (const [keyNode, valueNode] of node.entries || []) {
      const key = this.eval(keyNode);
      if (isSignal(key)) return key;
      const value = this.eval(valueNode);
      if (isSignal(value)) return value;
      entries.set(unbox(key), value);
    }
    return { kind: "mapping", entries };
  }

  evalGetItem(node) {
    const objectValue = this.eval(node.object_);
    if (isSignal(objectValue)) return objectValue;
    const key = this.eval(node.key);
    if (isSignal(key)) return key;
    const keyValue = unbox(key);
    if (objectValue.kind === "sequence") return objectValue.elements[keyValue];
    if (objectValue.kind === "mapping") return objectValue.entries.get(keyValue);
    return box(unbox(objectValue)[keyValue]);
  }

  evalSpread(_node) {
    throw new Error("Spread can only be evaluated inside Sequence");
  }

  evalConstructData(node) {
    const allFieldsEmpty = (node.fields || []).every(
      ([, fieldNode]) => fieldNode.type === "Literal" && fieldNode.value === null,
    );
    if (allFieldsEmpty) {
      const constructor = {
        kind: "constructor",
        name: node.name,
        fields: node.fields.map(([name]) => name),
      };
      this.currentFrame.assign(node.name, constructor);
      return constructor;
    }
    const fields = {};
    for (const [name, fieldNode] of node.fields || []) {
      const value = this.eval(fieldNode);
      if (isSignal(value)) return value;
      fields[name] = value;
    }
    return { kind: "data", name: node.name, fields };
  }

  evalGetField(node) {
    const objectValue = this.eval(node.object_);
    if (isSignal(objectValue)) return objectValue;
    if (objectValue.kind === "mapping" && node.field === "get") {
      return native("mapping.get", (key, defaultValue = NIL) => {
        const keyValue = unbox(key);
        return objectValue.entries.has(keyValue)
          ? objectValue.entries.get(keyValue)
          : defaultValue;
      }, true);
    }
    if (objectValue.kind !== "data") {
      throw new TypeError(`${objectValue.kind} has no field '${node.field}'`);
    }
    if (!(node.field in objectValue.fields)) throw new Error(node.field);
    return objectValue.fields[node.field];
  }

  evalMatch(node) {
    const subject = this.eval(node.subject);
    if (isSignal(subject)) return subject;
    for (const caseNode of node.cases || []) {
      if (caseNode.type !== "PatternTest") {
        throw new TypeError(`Match case must be PatternTest, got ${caseNode.type}`);
      }
      const [matched, result] = this.evalPatternTestWithSubject(caseNode, subject);
      if (matched) return result;
    }
    return NIL;
  }

  evalPatternTest(_node) {
    throw new Error("PatternTest can only be evaluated inside Match or Handle");
  }

  evalPatternTestWithSubject(node, subject) {
    const snapshot = new Map(this.currentFrame.bindings);
    if (!this.patternMatches(node.pattern, subject)) {
      this.currentFrame.bindings = snapshot;
      return [false, NIL];
    }
    if (node.guard !== null && node.guard !== undefined) {
      const guard = this.eval(node.guard);
      if (isSignal(guard)) return [true, guard];
      if (!truthy(guard)) {
        this.currentFrame.bindings = snapshot;
        return [false, NIL];
      }
    }
    return [true, this.evalModule(node.body)];
  }

  patternMatches(pattern, subject) {
    if (!pattern) return true;
    if (pattern.type === "Literal") return unbox(subject) === pattern.value;
    if (pattern.type === "Load") {
      if (pattern.name === "_") return true;
      this.currentFrame.bind(pattern.name, subject);
      return true;
    }
    if (pattern.type === "Sequence") {
      return subject.kind === "sequence" && this.sequencePatternMatches(pattern, subject);
    }
    if (pattern.type === "Spread") {
      if (pattern.value && pattern.value.type === "Load" && pattern.value.name !== "_") {
        this.currentFrame.bind(pattern.value.name, subject);
      }
      return true;
    }
    if (pattern.type === "MappingLiteral") {
      if (subject.kind !== "mapping") return false;
      for (const [keyPattern, valuePattern] of pattern.entries || []) {
        const key = this.eval(keyPattern);
        if (isSignal(key)) return false;
        const keyValue = unbox(key);
        if (!subject.entries.has(keyValue)) return false;
        if (!this.patternMatches(valuePattern, subject.entries.get(keyValue))) return false;
      }
      return true;
    }
    throw new TypeError(`Unsupported pattern node ${pattern.type}`);
  }

  sequencePatternMatches(pattern, subject) {
    const elements = pattern.elements || [];
    const spreadIndex = elements.findIndex((element) => element.type === "Spread");
    if (spreadIndex === -1) {
      return elements.length === subject.elements.length
        && elements.every((element, index) => this.patternMatches(element, subject.elements[index]));
    }
    const prefix = elements.slice(0, spreadIndex);
    const suffix = elements.slice(spreadIndex + 1);
    if (subject.elements.length < prefix.length + suffix.length) return false;
    for (let index = 0; index < prefix.length; index += 1) {
      if (!this.patternMatches(prefix[index], subject.elements[index])) return false;
    }
    const suffixValues = suffix.length > 0 ? subject.elements.slice(-suffix.length) : [];
    for (let index = 0; index < suffix.length; index += 1) {
      if (!this.patternMatches(suffix[index], suffixValues[index])) return false;
    }
    const restEnd = subject.elements.length - suffix.length;
    const rest = { kind: "sequence", elements: subject.elements.slice(prefix.length, restEnd) };
    return this.patternMatches(elements[spreadIndex], rest);
  }

  evalRaise(node) {
    const value = this.eval(node.exception);
    if (isSignal(value)) return value;
    if (value.kind === "error") return value;
    return {
      kind: "error",
      errorKind: "RuntimeError",
      message: String(unbox(value)),
      payload: value,
    };
  }

  evalHandle(node) {
    const result = this.evalModule(node.body);
    if (result.kind === "error") {
      const handled = this.handleError(result, node.handlers || []);
      const finalResult = this.evalModule(node.finalbody);
      if (isSignal(finalResult)) return finalResult;
      return handled;
    }
    const finalResult = this.evalModule(node.finalbody);
    if (isSignal(finalResult)) return finalResult;
    return result;
  }

  handleError(error, handlers) {
    for (const handler of handlers) {
      if (handler.type !== "PatternTest") continue;
      const [matched, result] = this.evalErrorHandler(handler, error);
      if (matched) return result;
    }
    return error;
  }

  evalErrorHandler(handler, error) {
    if (handler.pattern && !this.errorPatternMatches(handler.pattern, error)) {
      return [false, NIL];
    }
    if (handler.guard !== null && handler.guard !== undefined) {
      const guard = this.eval(handler.guard);
      if (isSignal(guard)) return [true, guard];
      if (!truthy(guard)) return [false, NIL];
    }
    return [true, this.evalModule(handler.body)];
  }

  errorPatternMatches(pattern, error) {
    if (pattern.type === "Load") {
      return ["_", "Exception", error.errorKind].includes(pattern.name);
    }
    if (pattern.type === "Literal") {
      return pattern.value === error.errorKind || pattern.value === error.message;
    }
    return this.patternMatches(pattern, error);
  }

  evalDiagnostic(node) {
    throw new Error(`Unexecutable Core diagnostic: ${node.message}`);
  }

  constructData(constructor, args) {
    if (args.length !== constructor.fields.length) {
      throw new TypeError(
        `${constructor.name} expected ${constructor.fields.length} arguments, received ${args.length}`,
      );
    }
    const fields = {};
    constructor.fields.forEach((field, index) => {
      fields[field] = args[index];
    });
    return { kind: "data", name: constructor.name, fields };
  }

  iterValues(value) {
    if (value.kind === "sequence") return value.elements;
    if (value.kind === "mapping") return Array.from(value.entries.keys()).map(box);
    return unbox(value).map(box);
  }

  spreadElements(value) {
    if (value.kind === "sequence") return value.elements;
    if (value.kind === "mapping") return Array.from(value.entries.keys()).map(box);
    return unbox(value).map(box);
  }

  displayValue(value) {
    if (value.kind === "nil") return "None";
    if (value.kind === "bool") return value.value ? "True" : "False";
    if (value.kind === "str") return value.value;
    if (value.kind === "float" && Number.isInteger(value.value)) {
      return value.value.toFixed(1);
    }
    if (value.kind === "sequence") {
      return `[${value.elements.map((item) => this.displayValue(item)).join(", ")}]`;
    }
    if (value.kind === "mapping") return JSON.stringify(unbox(value));
    if (value.kind === "data") {
      const fields = Object.entries(value.fields)
        .map(([name, fieldValue]) => `${name}=${this.displayValue(fieldValue)}`)
        .join(", ");
      return `${value.name}(${fields})`;
    }
    return String(unbox(value));
  }

  defaultHostCalls() {
    return {
      abs: (value) => Math.abs(value),
      bool: native("bool", (value) => truthy(value), true),
      filter: native("filter", (func, sequence) => {
        const kept = [];
        for (const item of this.iterValues(sequence)) {
          const result = this.applyCallable(func, [item]);
          if (isSignal(result)) throw new Error(`Unexpected ${result.control} inside filter`);
          if (truthy(result)) kept.push(item);
        }
        return { kind: "sequence", elements: kept };
      }, true),
      float: (value) => {
        const number = Number(value);
        if (Number.isNaN(number)) throw valueError(`could not convert string to float: '${value}'`);
        return number;
      },
      int: (value) => {
        const number = Number(value);
        if (Number.isNaN(number)) throw valueError(`invalid literal for int(): '${value}'`);
        return Math.trunc(number);
      },
      len: (value) => value.length,
      list: (value) => (value === undefined || value === null ? [] : Array.from(value)),
      map: native("map", (func, sequence) => {
        const mapped = [];
        for (const item of this.iterValues(sequence)) {
          const result = this.applyCallable(func, [item]);
          if (isSignal(result)) throw new Error(`Unexpected ${result.control} inside map`);
          mapped.push(result);
        }
        return { kind: "sequence", elements: mapped };
      }, true),
      print: native("print", (...values) => {
        this.stdout.push(`${values.map((value) => this.displayValue(value)).join(" ")}\n`);
        return null;
      }, true),
      range: (...args) => {
        const [start, stop, step] =
          args.length === 1 ? [0, args[0], 1] : [args[0], args[1], args[2] || 1];
        const values = [];
        for (let i = start; step > 0 ? i < stop : i > stop; i += step) values.push(i);
        return values;
      },
      str: native("str", (value) => this.displayValue(value), true),
      sum: (values) => values.reduce((total, item) => total + item, 0),
    };
  }

  applyBinaryOp(op, left, right) {
    if (op === "+") {
      if (Array.isArray(left) && Array.isArray(right)) return left.concat(right);
      return left + right;
    }
    if (op === "-") return left - right;
    if (op === "*") return left * right;
    if (op === "/") return left / right;
    if (op === "//") return Math.floor(left / right);
    if (op === "%") return left % right;
    if (op === "**") return left ** right;
    if (op === "<<") return left << right;
    if (op === ">>") return left >> right;
    if (op === "|") return left | right;
    if (op === "^") return left ^ right;
    if (op === "&") return left & right;
    throw new Error(`Unsupported binary op ${op}`);
  }

  binaryResultKind(op, left, right, result) {
    if (typeof result !== "number") return null;
    if (op === "/") return "float";
    if (left.kind === "float" || right.kind === "float") return "float";
    return null;
  }

  applyCompareOp(op, left, right) {
    if (op === "==") return left === right;
    if (op === "!=") return left !== right;
    if (op === "<") return left < right;
    if (op === "<=") return left <= right;
    if (op === ">") return left > right;
    if (op === ">=") return left >= right;
    if (op === "is") return left === right;
    if (op === "is not") return left !== right;
    if (op === "in") return right.includes(left);
    if (op === "not in") return !right.includes(left);
    throw new Error(`Unsupported compare op ${op}`);
  }
}

function evaluateCorePayload(payload, options = {}) {
  return new CoreRuntime(options.hostCalls || {}).evaluate(payload, options);
}

if (typeof module !== "undefined") {
  module.exports = {
    CORE_IR_JSON_SCHEMA,
    CORE_IR_JSON_VERSION,
    CoreRuntime,
    evaluateCorePayload,
  };
}

if (typeof self !== "undefined") {
  self.NomiCoreRuntime = {
    CORE_IR_JSON_SCHEMA,
    CORE_IR_JSON_VERSION,
    CoreRuntime,
    evaluateCorePayload,
  };
}

if (typeof require !== "undefined" && require.main === module) {
  const fs = require("node:fs");
  const args = process.argv.slice(2);
  const sourcePath = args.find((arg) => !arg.startsWith("--"));
  const source = sourcePath
    ? fs.readFileSync(sourcePath, "utf8")
    : fs.readFileSync(0, "utf8");
  const payload = JSON.parse(source);
  const displayLastExpr = args.includes("--display-last-expr");
  process.stdout.write(
    `${JSON.stringify(evaluateCorePayload(payload, { displayLastExpr }), null, 2)}\n`,
  );
}
