const assert = require("assert");
const vscode = require("vscode");

suite("Nomi extension", () => {
  test("activates", async () => {
    const extension = vscode.extensions.getExtension("nomi-lang.nomi-vscode");

    assert.ok(extension, "extension should be discoverable by publisher and name");
    await extension.activate();
    assert.strictEqual(extension.isActive, true);
  });

  test("provides symbols for Nomi files", async () => {
    const document = await vscode.workspace.openTextDocument({
      language: "nomi",
      content: [
        "func greet(name):",
        "    return name",
        "",
        "answer:int = 42",
        ""
      ].join("\n")
    });

    await vscode.window.showTextDocument(document);

    const symbols = await vscode.commands.executeCommand(
      "vscode.executeDocumentSymbolProvider",
      document.uri
    );

    assert.ok(Array.isArray(symbols));
    assert.ok(symbols.some((symbol) => symbol.name === "greet"));
    assert.ok(symbols.some((symbol) => symbol.name === "answer"));
  });

  test("finds simple same-document definitions", async () => {
    const document = await vscode.workspace.openTextDocument({
      language: "nomi",
      content: [
        "func greet(name):",
        "    return name",
        "",
        "print(greet(\"Ada\"))",
        ""
      ].join("\n")
    });

    await vscode.window.showTextDocument(document);

    const position = new vscode.Position(3, 7);
    const definitions = await vscode.commands.executeCommand(
      "vscode.executeDefinitionProvider",
      document.uri,
      position
    );

    assert.ok(Array.isArray(definitions));
    assert.strictEqual(definitions[0].range.start.line, 0);
  });
});
