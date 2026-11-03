"""Shared RequireSoul token parser used by the decoder and SQLite builder.

Token identity and candidate color mappings are separate from game-rule
semantics. Hybrid mappings remain reviewable until independent known-cost
reference data is supplied to a validation run.
"""
from __future__ import annotations

COLOR_NAMES = ("dark", "fire", "earth", "water", "forest", "iron", "light", "neutral", "ncs", "bonus")
PURE_SOUL_CODES = {
    "11": "dark", "21": "fire", "31": "water", "41": "forest",
    "51": "iron", "61": "earth", "71": "light", "81": "neutral",
}
HYBRID_SOUL_CODES = {
    "12": ("dark", "earth"), "13": ("dark", "fire"),
    "14": ("dark", "light"), "15": ("dark", "water"),
    "22": ("fire", "forest"), "23": ("fire", "iron"),
    "24": ("fire", "water"), "32": ("earth", "water"),
    "33": ("forest", "water"), "42": ("forest", "iron"),
    "43": ("forest", "light"), "52": ("earth", "iron"),
    "53": ("iron", "light"), "62": ("earth", "light"),
}
SPECIAL_SOUL_CODES = {"82": "ncs", "83": "bonus"}
NO_COST_CODE = "01"


def parse_require_soul(raw: object, soul_meta: dict | None = None) -> dict:
    """Parse 4-character tokens while retaining unverified mapping flags."""
    result = {
        "raw": raw,
        "tokens": [],
        "colors": {name: 0 for name in COLOR_NAMES},
        "known": False,
        "mapping_review": False,
        "semantic_review": False,
        "error_reason": None,
    }
    if not isinstance(raw, str) or not raw:
        result["error_reason"] = "missing_or_non_string"
        return result
    if len(raw) % 4:
        result["error_reason"] = "invalid_token_length"
        return result

    meta_by_code = soul_meta or {}
    known = True
    for offset in range(0, len(raw), 4):
        token = raw[offset:offset + 4]
        code_text, amount_text = token[:2], token[2:]
        token_result = {
            "raw": token,
            "code": int(code_text) if code_text.isdigit() else None,
            "count": int(amount_text) if amount_text.isdigit() else None,
            "symbol": None,
            "icon": None,
            "normalized_color": None,
            "status": "unresolved",
        }
        if not token.isdigit():
            known = False
            result["error_reason"] = "invalid_token"
            result["tokens"].append(token_result)
            continue

        code = code_text
        amount = int(amount_text)
        metadata = meta_by_code.get(int(code), {})
        token_result["symbol"] = metadata.get("symbol")
        token_result["icon"] = metadata.get("icon")

        if code == NO_COST_CODE:
            if amount == 0:
                token_result["status"] = "no_cost"
                token_result["normalized_color"] = "none"
            else:
                known = False
                result["error_reason"] = "nonzero_none_token"
                token_result["status"] = "manual_review"
        elif code in PURE_SOUL_CODES:
            color = PURE_SOUL_CODES[code]
            result["colors"][color] += amount
            token_result["normalized_color"] = color
            token_result["status"] = "enum_decoded"
        elif code in HYBRID_SOUL_CODES:
            colors = HYBRID_SOUL_CODES[code]
            for color in colors:
                result["colors"][color] += amount
            token_result["normalized_color"] = "+".join(colors)
            token_result["status"] = "mapping_review"
            result["mapping_review"] = True
        elif code in SPECIAL_SOUL_CODES:
            color = SPECIAL_SOUL_CODES[code]
            result["colors"][color] += amount
            token_result["normalized_color"] = color
            token_result["status"] = "semantic_review"
            result["semantic_review"] = True
        else:
            known = False
            result["error_reason"] = "unsupported_token_" + code
            token_result["status"] = "manual_review"

        result["tokens"].append(token_result)

    result["known"] = known
    return result
