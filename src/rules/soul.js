// Pure FM1 soul/LP helpers. These functions do not mutate the input state.
export const SOUL_COLORS = Object.freeze([
  "dark", "fire", "earth", "water", "wind", "light", "neutral"
]);

function isNonNegativeInteger(value) {
  return Number.isInteger(value) && value >= 0;
}

export function validateSoulPool(pool) {
  if (!pool || typeof pool !== "object" || Array.isArray(pool)) return false;
  return SOUL_COLORS.every((color) => isNonNegativeInteger(pool[color] ?? 0));
}

/**
 * Colored requirements must be paid by the same color.
 * Neutral requirements may be paid by any remaining color.
 * A failed payment returns the original pool unchanged.
 */
export function paySoul(pool, cost) {
  if (!validateSoulPool(pool) || !validateSoulPool(cost)) {
    return { paid: false, reason: "invalid-soul-data", pool: { ...pool } };
  }

  const next = Object.fromEntries(SOUL_COLORS.map((color) => [color, pool[color] ?? 0]));
  const required = Object.fromEntries(SOUL_COLORS.map((color) => [color, cost[color] ?? 0]));

  for (const color of SOUL_COLORS.filter((c) => c !== "neutral")) {
    if (next[color] < required[color]) {
      return { paid: false, reason: "insufficient-colored-soul", pool: { ...pool } };
    }
    next[color] -= required[color];
  }

  let neutralNeed = required.neutral;
  for (const color of SOUL_COLORS.filter((c) => c !== "neutral")) {
    const used = Math.min(next[color], neutralNeed);
    next[color] -= used;
    neutralNeed -= used;
  }
  const neutralUsed = Math.min(next.neutral, neutralNeed);
  next.neutral -= neutralUsed;
  neutralNeed -= neutralUsed;

  if (neutralNeed > 0) {
    return { paid: false, reason: "insufficient-neutral-soul", pool: { ...pool } };
  }
  return { paid: true, reason: null, pool: next };
}

/** Explicit requiredLP: 0 is valid; null/undefined is unknown and must not be treated as free. */
export function payTerrainLP(currentLP, requiredLP) {
  if (!isNonNegativeInteger(currentLP) || !isNonNegativeInteger(requiredLP)) {
    return { paid: false, reason: "unknown-or-invalid-lp", lp: currentLP };
  }
  if (currentLP < requiredLP) {
    return { paid: false, reason: "insufficient-lp", lp: currentLP };
  }
  return { paid: true, reason: null, lp: currentLP - requiredLP };
}

/** Neutral soul maintenance is a recurring cost; the caller applies the shortage as deck loss. */
export function calculateNeutralMaintenance(units, generatedSoul) {
  if (!Array.isArray(units) || !isNonNegativeInteger(generatedSoul)) {
    return { valid: false, required: null, shortage: null, remaining: null };
  }
  const required = units.reduce((sum, unit) => {
    const cost = unit?.neutralSoulCost;
    return sum + (isNonNegativeInteger(cost) ? cost : NaN);
  }, 0);
  if (!Number.isFinite(required)) {
    return { valid: false, required: null, shortage: null, remaining: null };
  }
  const paid = Math.min(required, generatedSoul);
  return {
    valid: true,
    required,
    paid,
    shortage: required - paid,
    remaining: generatedSoul - paid
  };
}
