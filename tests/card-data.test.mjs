import test from "node:test";
import assert from "node:assert/strict";
import { validateCards } from "../scripts/validate-cards.mjs";

const valid = {
  id: "T00001", name: "예시 지형", type: "unit", text: "", description: "",
  cost: {}, costKnown: false, artImage: "fm1/images/T00001.webp"
};

test("accepts valid source card with unknown cost", () => {
  assert.deepEqual(validateCards([valid]), []);
});

test("does not treat an explicit zero as missing in source data", () => {
  const card = { ...valid, costKnown: true, cost: { neutral: 0 } };
  assert.deepEqual(validateCards([card]), []);
});

test("rejects duplicate card IDs", () => {
  assert.ok(validateCards([valid, { ...valid }]).some((e) => e.includes("duplicate")));
});

test("rejects inferred values when cost is marked unknown", () => {
  const card = { ...valid, cost: { light: 2 } };
  assert.ok(validateCards([card]).some((e) => e.includes("unknown cost")));
});

test("rejects unsupported card type", () => {
  assert.ok(validateCards([{ ...valid, type: "other" }]).some((e) => e.includes("unsupported type")));
});

test("accepts source land records without costKnown", () => {
  const land = { ...valid, id: "L00001", type: "land", costKnown: undefined, cost: {}, souls: { neutral: 1 }, soulValue: 1 };
  assert.deepEqual(validateCards([land]), []);
});
