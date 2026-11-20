// SPDX-License-Identifier: Apache-2.0
// Second-implementation check of the MAV Grid schemas with Ajv (JSON Schema 2020-12).
//
//   npm install ajv@8 ajv-formats@3
//   node tools/check_ajv.mjs . '{"allErrors":true,"strictTypes":false}'
//
// The first argument is the folder that holds schema/, data/ and examples/.
// Ajv's strictTypes lint is switched off: the class dispatch in part.schema.json states
// each type once at the parent, not again inside every if / then branch.
import Ajv2020 from "ajv/dist/2020.js";
import addFormats from "ajv-formats";
import fs from "node:fs";
import path from "node:path";
const root = process.argv[2] || ".";
const ajv = new Ajv2020(JSON.parse(process.argv[3] || "{}"));
addFormats(ajv);
const schemas = {};
for (const f of fs.readdirSync(path.join(root, "schema"))) {
  const s = JSON.parse(fs.readFileSync(path.join(root, "schema", f), "utf8"));
  schemas[f] = s; ajv.addSchema(s);
}
let bad = 0;
const check = (schemaFile, file, expectValid) => {
  const validate = ajv.getSchema(schemas[schemaFile].$id);
  const ok = validate(JSON.parse(fs.readFileSync(file, "utf8")));
  const pass = ok === expectValid;
  if (!pass) { bad++; console.log("MISMATCH", file, "valid:", ok, JSON.stringify(validate.errors?.slice(0, 3))); }
  return pass;
};
let n = 0;
for (const d of ["params", "kinds", "support", "rules", "decisions", "tests", "vectors"]) { check(`${d}.schema.json`, path.join(root, "data", `${d}.json`), true); n++; }
for (const f of fs.readdirSync(path.join(root, "examples/valid"))) { check("part.schema.json", path.join(root, "examples/valid", f), true); n++; }
const exp = JSON.parse(fs.readFileSync(path.join(root, "examples/invalid/expected.json"), "utf8"));
for (const [f, e] of Object.entries(exp)) { check("part.schema.json", path.join(root, "examples/invalid", f), e.schema_valid); n++; }
console.log(`Ajv, JSON Schema 2020-12: ${n} documents checked, ${bad} mismatches`);
process.exit(bad ? 1 : 0);
