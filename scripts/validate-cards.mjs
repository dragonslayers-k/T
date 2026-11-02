import { readFile } from "node:fs/promises";

const input = process.argv[2] ?? "cards.json";
const allowedTypes = new Set(["terrain", "unit", "item", "spell", "enchant"]);

function validateCards(cards) {
  const errors = [];
  if (!Array.isArray(cards)) return ["root must be a JSON array"];
  const ids = new Set();
  for (let i = 0; i < cards.length; i++) {
    const card = cards[i];
    const at = `cards[${i}]`;
    if (!card || typeof card !== "object" || Array.isArray(card)) {
      errors.push(`${at}: must be an object`);
      continue;
    }
    if (typeof card.id !== "string" || !card.id.trim()) errors.push(`${at}.id: required non-empty string`);
    else if (ids.has(card.id)) errors.push(`${at}.id: duplicate ${card.id}`);
    else ids.add(card.id);
    if (typeof card.name !== "string" || !card.name.trim()) errors.push(`${at}.name: required non-empty string`);
    if (!allowedTypes.has(card.type)) errors.push(`${at}.type: unsupported type ${String(card.type)}`);
    if (typeof card.text !== "string") errors.push(`${at}.text: must preserve source text as string`);
    if (typeof card.description !== "string") errors.push(`${at}.description: must preserve source description as string`);
    if (typeof card.costKnown !== "boolean") errors.push(`${at}.costKnown: required boolean`);
    if (card.costKnown === false && card.cost && Object.keys(card.cost).length > 0) {
      errors.push(`${at}.cost: unknown cost must not contain inferred values`);
    }
    if (typeof card.artImage !== "string" || !card.artImage) errors.push(`${at}.artImage: required image reference`);
  }
  return errors;
}

if (process.argv[1] && new URL(import.meta.url).pathname === process.argv[1]) {
  try {
    const cards = JSON.parse(await readFile(input, "utf8"));
    const errors = validateCards(cards);
    if (errors.length) {
      console.error(errors.slice(0, 100).join("\\n"));
      console.error(`Validation failed: ${errors.length} error(s)`);
      process.exitCode = 1;
    } else {
      console.log(`Validated ${cards.length} cards; unique IDs and required source fields are intact.`);
    }
  } catch (error) {
    console.error(error.message);
    process.exitCode = 1;
  }
}

export { validateCards };
