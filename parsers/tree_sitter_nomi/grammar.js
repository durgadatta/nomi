/// <reference types="tree-sitter-cli/dsl" />
// @ts-check

module.exports = grammar({
  name: "nomi",

  extras: $ => [
    /[\t \f ]+/,
    $.comment,
  ],

  word: $ => $.identifier,

  rules: {
    source_file: $ => repeat($.line),

    line: $ => seq(
      optional($.statement),
      $._newline,
    ),

    statement: $ => repeat1($._line_token),

    _line_token: $ => choice(
      $.string,
      $.number,
      $.hole,
      $.identifier,
      $.operator,
      $.punctuation,
    ),

    identifier: _ => /[^\W\d]\w*/,

    hole: _ => /\$([0-9]+|[^\W\d]\w*)/,

    number: _ => token(choice(
      /0[xX](_?[0-9a-fA-F])+/,
      /0[oO](_?[0-7])+/,
      /0[bB](_?[01])+/,
      /(([0-9](_?[0-9])*)?\.[0-9](_?[0-9])*|[0-9](_?[0-9])*\.[0-9](_?[0-9])*)([eE][+-]?[0-9](_?[0-9])*)?/,
      /[0-9](_?[0-9])*([eE][+-]?[0-9](_?[0-9])*)?/,
    )),

    string: _ => token(choice(
      /([uUbBfF]?[rR]?|[rR][uUbBfF]?)"([^"\\\n]|\\.)*"/,
      /([uUbBfF]?[rR]?|[rR][uUbBfF]?)'([^'\\\n]|\\.)*'/,
      /([uUbBfF]?[rR]?|[rR][uUbBfF]?)"""([^\\]|\\.|\n)*?"""/,
      /([uUbBfF]?[rR]?|[rR][uUbBfF]?)'''([^\\]|\\.|\n)*?'''/,
    )),

    operator: _ => token(choice(
      ">>>",
      "<<<",
      "=>",
      "->",
      "|>",
      "??",
      "?.",
      "..<",
      "..",
      "**=",
      "//=",
      "<<=",
      ">>=",
      "+=",
      "-=",
      "*=",
      "@=",
      "/=",
      "%=",
      "&=",
      "|=",
      "^=",
      "==",
      ">=",
      "<=",
      "<>",
      "!=",
      "<<",
      ">>",
      "**",
      "//",
      "+",
      "-",
      "~",
      "|",
      "^",
      "&",
      "*",
      "@",
      "/",
      "%",
      "=",
      ">",
      "<",
    )),

    punctuation: _ => token(choice(
      "(",
      ")",
      "[",
      "]",
      "{",
      "}",
      ",",
      ".",
      ":",
      ";",
    )),

    comment: _ => token(seq("#", /[^\n]*/)),
    _newline: _ => /\r?\n/,
  },
});
