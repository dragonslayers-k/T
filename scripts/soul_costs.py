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



# Human-readable aliases are explicit; unknown fragments remain unresolved.
TEXT_SOUL_ALIASES = {
    "dark":"dark","흑":"dark","암":"dark","암흑":"dark","다크":"dark",
    "fire":"fire","화":"fire","불":"fire","화염":"fire","파이어":"fire",
    "water":"water","수":"water","물":"water","워터":"water",
    "forest":"forest","목":"forest","숲":"forest","포레스트":"forest",
    "iron":"iron","metal":"iron","철":"iron","금속":"iron","아이언":"iron",
    "earth":"earth","지":"earth","대지":"earth","땅":"earth","어스":"earth",
    "light":"light","광":"light","빛":"light","라이트":"light",
    "neutral":"neutral","무":"neutral","무색":"neutral","중립":"neutral",
    "ncs":"ncs","bonus":"bonus",
}
import re
_TEXT_SOUL_PATTERN = re.compile(
    r"(?P<name>NCS|BONUS|dark|fire|water|forest|iron|metal|earth|light|neutral|암흑|다크|흑|암|화염|파이어|불|화|워터|물|수|포레스트|숲|목|금속|아이언|철|대지|어스|땅|지|라이트|빛|광|무색|중립|무)\s*(?:[:：=＝xX*×]?\s*)(?P<count>\d+)"
    r"|(?P<count_first>\d+)\s*(?P<name_first>NCS|BONUS|dark|fire|water|forest|iron|metal|earth|light|neutral|암흑|다크|흑|암|화염|파이어|불|화|워터|물|수|포레스트|숲|목|금속|아이언|철|대지|어스|땅|지|라이트|빛|광|무색|중립|무)", re.IGNORECASE
)
def _parse_human_readable_cost(raw: str, result: dict) -> bool:
    matches=list(_TEXT_SOUL_PATTERN.finditer(raw))
    if not matches:
        return False
    residue=list(raw)
    for match in matches:
        for i in range(match.start(),match.end()):
            residue[i]=" "
    if re.sub(r"[\s,，;；+＋|/／()（）\[\]{}<>:：=＝·ㆍ소울비용]", "", "".join(residue)):
        return False
    for match in matches:
        name=match.group("name") or match.group("name_first")
        count=int(match.group("count") or match.group("count_first"))
        color=TEXT_SOUL_ALIASES[name.casefold()]
        result["colors"][color]+=count
        result["tokens"].append({"raw":match.group(0),"code":None,"count":count,
            "symbol":name,"icon":None,"normalized_color":color,
            "status":"text_decoded","source_format":"human_readable"})
    result["known"]=True
    result["source_format"]="human_readable"
    return True


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
    # Numeric enum tokens may be displayed with separators in copied text.
    # Remove only known visual separators; any other character keeps the value unresolved.
    numeric_source = re.sub(r"[\s,，;；+＋]", "", raw)
    if not numeric_source.isdigit() or len(numeric_source) % 4:
        if _parse_human_readable_cost(raw, result):
            return result
        result["error_reason"] = "unparsed_human_readable_cost"
        return result

    meta_by_code = soul_meta or {}
    result["source_format"] = "numeric_enum"
    known = True
    for offset in range(0, len(numeric_source), 4):
        token = numeric_source[offset:offset + 4]
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
            # Preserve the decoded color pair but do not assert whether both colors
            # are required or whether either color can pay it. This needs a known-cost
            # reference or reproducible game test before the rule is finalized.
            token_result["status"] = "hybrid_identity_preserved_pending_rule"
            token_result["inference"] = "hybrid_color_pair_payment_rule_unverified"
            result["mapping_review"] = True
        elif code in SPECIAL_SOUL_CODES:
            color = SPECIAL_SOUL_CODES[code]
            # NCS/BONUS are retained as distinct resource identities. Do not
            # silently treat either as neutral until its payment rule is verified.
            result["colors"][color] += amount
            token_result["normalized_color"] = color
            token_result["status"] = "special_identity_preserved_pending_rule"
            token_result["inference"] = "special_soul_payment_rule_unverified"
            result["semantic_review"] = True
        else:
            known = False
            result["error_reason"] = "unsupported_token_" + code
            token_result["status"] = "manual_review"

        result["tokens"].append(token_result)

    result["known"] = known
    return result
