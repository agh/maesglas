import { readFileSync } from "node:fs";
import { stripTypeScriptTypes } from "node:module";
import { join } from "node:path";
import { runInNewContext } from "node:vm";

const root = process.argv[2];
const source = readFileSync(
  join(root, "src/vs/workbench/services/themes/common/colorThemeSchema.ts"),
  "utf8",
);
const semantic = readFileSync(
  join(root, "src/vs/platform/theme/common/tokenClassificationRegistry.ts"),
  "utf8",
);
const start =
  semantic.indexOf(" = {", semantic.indexOf("private tokenStylingSchema")) + 3;
const end = semantic.indexOf("\n\t};", start) + 3;
if (start < 3 || end < 3)
  throw new Error("Semantic token schema was not found");
const declarations = semantic
  .split("\n")
  .filter((line) =>
    /^const (TOKEN_CLASSIFIER_LANGUAGE_SEPARATOR|CLASSIFIER_MODIFIER_SEPARATOR|idPattern|selectorPattern|fontStylePattern) =/.test(
      line,
    ),
  )
  .join("\n");
const entry = semantic.slice(
  semantic.indexOf("function getStylingSchemeEntry("),
  semantic.indexOf("export const tokenStylingSchemaId"),
);
const program = [
  source.replace(/^import .*;\r?\n/gm, ""),
  declarations,
  entry,
  `const tokenStylingSchema = ${semantic.slice(start, end)};`,
  "JSON.stringify({ colorThemeSchema, textmateColorSchema, tokenStylingSchema });",
].join("\n");
const result = runInNewContext(
  stripTypeScriptTypes(program).replace(/\bexport /g, ""),
  {
    nls: { localize: (_key, value) => value },
    workbenchColorsSchemaId: "vscode://schemas/workbench-colors",
    tokenStylingSchemaId: "vscode://schemas/token-styling",
  },
  { timeout: 5000 },
);
process.stdout.write(result + "\n");
