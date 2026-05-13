// Nomi Web Playground — Monaco editor boot, language, theme

async function initMonaco() {
  return new Promise((resolve) => {
    require.config({
      paths: { vs: "https://cdn.jsdelivr.net/npm/monaco-editor@0.52.0/min/vs" },
      "vs/nls": { availableLanguages: { "*": "en" } }
    });
    require(["vs/editor/editor.main"], function() {
      monaco.languages.register({ id: "nomi", extensions: [".nomi"], aliases: ["Nomi"] });
      monaco.languages.setMonarchTokensProvider("nomi", {
        tokenizer: {
          root: [
            [/#.*$/, "comment"],
            [/f?r?"""/, { token: "string.quote", bracket: "@open", next: "@tqstring" }],
            [/f?r?'''/, { token: "string.quote", bracket: "@open", next: "@tqstring2" }],
            [/f?r?"/, { token: "string.quote", bracket: "@open", next: "@dqstring" }],
            [/f?r?'/, { token: "string.quote", bracket: "@open", next: "@sqstring" }],
            [/@[a-zA-Z_]\w*/, "tag"],
            [/\b(func|class|data|const|module|export|type|guard|unless)\b/, "keyword"],
            [/\b(if|elif|else|for|while|try|except|finally|with|as|match|case|return|yield|from|raise|break|continue|pass|in|is|not|and|or|async|await|global|nonlocal|assert|del|import)\b/, "keyword"],
            [/\b(true|false|none|True|False|None|Ellipsis)\b/, "keyword"],
            [/\b\d+(\.\d+)?([eE][+-]?\d+)?\b/, "number"],
            [/[+\-*/%&|^~<>!=]=?|\.\.\.?|->|=>|:=|\?\?|\?\./, "operator"],
            [/[{}()[\]]/, "@brackets"],
            [/[A-Z][a-zA-Z_]\w*/, "type.identifier"],
            [/[a-zA-Z_]\w*(?=\s*\()/, "function.identifier"],
            [/[a-zA-Z_]\w*/, "identifier"],
          ],
          tqstring: [
            [/"""/, { token: "string.quote", bracket: "@close", next: "@pop" }],
            [/[^\\"]+/, "string"], [/./, "string"],
          ],
          tqstring2: [
            [/'''/, { token: "string.quote", bracket: "@close", next: "@pop" }],
            [/[^\\']+/, "string"], [/./, "string"],
          ],
          dqstring: [
            [/"/, { token: "string.quote", bracket: "@close", next: "@pop" }],
            [/\\[\\'"nrtbfv]/, "string.escape"],
            [/{/, { token: "string.interpolated", next: "@interp" }],
            [/[^\\"{]+/, "string"], [/./, "string"],
          ],
          sqstring: [
            [/'/, { token: "string.quote", bracket: "@close", next: "@pop" }],
            [/\\[\\'"nrtbfv]/, "string.escape"],
            [/{/, { token: "string.interpolated", next: "@interp" }],
            [/[^\\'{]+/, "string"], [/./, "string"],
          ],
          interp: [
            [/}/, { token: "string.interpolated", next: "@pop" }],
            [/[a-zA-Z_]\w*/, "identifier"],
            [/[^}]+/, "string"],
          ],
        },
      });
      monaco.languages.setLanguageConfiguration("nomi", {
        comments: { lineComment: "#" },
        brackets: [["{","}"],["[","]"],["(",")"]],
        autoClosingPairs: [{ open:"{",close:"}" },{ open:"[",close:"]" },{ open:"(",close:")" },{ open:'"',close:'"' },{ open:"'",close:"'" }],
        surroundingPairs: [["{","}"],["[","]"],["(",")"],['"','"'],["'","'"]],
        folding: { offSide: true },
        indentationRules: { increaseIndentPattern: /^.*:\s*$/, decreaseIndentPattern: /^\s*(elif|else|except|finally|case)\b/ },
      });
      monaco.editor.defineTheme("nomi-dark", {
        base: "vs-dark", inherit: true,
        rules: [
          { token: "comment", foreground: "7f8a83", fontStyle: "italic" },
          { token: "keyword", foreground: "d6a36f" },
          { token: "string", foreground: "a7d67a" },
          { token: "string.escape", foreground: "e8c16f" },
          { token: "string.interpolated", foreground: "e8c16f", fontStyle: "bold" },
          { token: "number", foreground: "f0b07a" },
          { token: "operator", foreground: "77d0c2" },
          { token: "tag", foreground: "ef8f8f" },
          { token: "type.identifier", foreground: "9bbdf2" },
          { token: "function.identifier", foreground: "eef3ef" },
          { token: "identifier", foreground: "dce5df" },
          { token: "", foreground: "eef3ef" },
        ],
        colors: {
          "editor.background": "#181c1a", "editor.foreground": "#eef3ef",
          "editor.lineHighlightBackground": "#202621", "editor.selectionBackground": "#405146",
          "editor.inactiveSelectionBackground": "#2d3530", "editorCursor.foreground": "#a7d67a",
          "editorLineNumber.foreground": "#657168", "editorLineNumber.activeForeground": "#c8d2cc",
          "editorIndentGuide.background1": "#2d3530", "editorIndentGuide.activeBackground1": "#526259",
          "editorGutter.background": "#181c1a", "editorWidget.background": "#1f2321", "editorWidget.border": "#3c443f",
        },
      });
      resolve();
    });
  });
}
