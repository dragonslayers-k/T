import test from "node:test";
import assert from "node:assert/strict";
import { paySoul, payTerrainLP, calculateNeutralMaintenance } from "../src/rules/soul.js";

const pool = { dark: 2, fire: 1, earth: 0, water: 0, forest: 0, metal: 0, light: 0, neutral: 0 };

test("colored cost requires matching colored soul", () => {
  const result = paySoul(pool, { dark: 1, fire: 0, earth: 0, water: 0, forest: 0, metal: 0, light: 0, neutral: 0 });
  assert.equal(result.paid, true);
  assert.equal(result.pool.dark, 1);
});

test("neutral cost may use any remaining color", () => {
  const result = paySoul(pool, { dark: 1, fire: 0, earth: 0, water: 0, wind: 0, light: 0, neutral: 2 });
  assert.equal(result.paid, true);
  assert.deepEqual(result.pool, { dark: 0, fire: 0, earth: 0, water: 0, forest: 0, metal: 0, light: 0, neutral: 0 });
});

test("failed payment is atomic and does not change input pool", () => {
  const before = structuredClone(pool);
  const result = paySoul(pool, { dark: 3, fire: 0, earth: 0, water: 0, forest: 0, metal: 0, light: 0, neutral: 0 });
  assert.equal(result.paid, false);
  assert.deepEqual(result.pool, before);
  assert.deepEqual(pool, before);
});

test("explicit LP zero is valid and consumes zero", () => {
  assert.deepEqual(payTerrainLP(0, 0), { paid: true, reason: null, lp: 0 });
});

test("missing LP is unknown, not a free terrain", () => {
  assert.equal(payTerrainLP(4, undefined).reason, "unknown-or-invalid-lp");
});

test("LP shortage rejects without mutation", () => {
  assert.deepEqual(payTerrainLP(1, 2), { paid: false, reason: "insufficient-lp", lp: 1 });
});

test("maintenance shortage is separated from the payment amount", () => {
  assert.deepEqual(calculateNeutralMaintenance([{ neutralSoulCost: 2 }, { neutralSoulCost: 1 }], 2), {
    valid: true, required: 3, paid: 2, shortage: 1, remaining: 0
  });
});
