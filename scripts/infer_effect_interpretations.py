#!/usr/bin/env python3
"""Build provenance-preserving semantic candidates for every FM1 card-text clause."""
import hashlib,html,json,re,sqlite3,sys

def _uniq(values):
    out=[]
    for x in values:
        if x not in out: out.append(x)
    return out


def _stat_refs(text):
    token_map={"공방체":["ap","dp","hp"],"공/방/체":["ap","dp","hp"],
               "공체":["ap","hp"],"공/체":["ap","hp"],"공방":["ap","dp"],
               "AP":["ap"],"DP":["dp"],"HP":["hp"],"LP":["lp"],
               "공격력":["ap"],"방어력":["dp"],"체력":["hp"]}
    found=[]
    for token in re.findall(r"공방체|공/방/체|공체|공/체|공방|AP|DP|HP|LP|공격력|방어력|체력",text):
        for stat in token_map[token]:
            if stat not in found: found.append(stat)
    return found


def normalize_effect_name(value):
    return re.sub(r"[\W_]+","",str(value or ""),flags=re.UNICODE).casefold()


def extract_named_effect_definitions(card_id, card_name, raw_text):
    try:
        source_text=json.loads(raw_text) if isinstance(raw_text,str) else raw_text
    except Exception:
        source_text=raw_text
    if not isinstance(source_text,str) or not source_text.strip():
        return []
    text=html.unescape(re.sub(r"<br\s*/?>","\n",source_text,flags=re.I))
    text=re.sub(r"<[^>]+>","",text)
    lines=[line.strip() for line in text.splitlines()]
    source_hash=hashlib.sha256(str(raw_text).encode("utf-8")).hexdigest()
    out=[]
    seen=set()
    for index,line in enumerate(lines):
        if not line:
            continue
        m=re.match(r"^([▶★※◆◇])\s*([^:：\n]{2,50})\s*[:：]\s*(.+)$",line)
        if m:
            marker,label,body=m.groups()
            method="marker_label_colon"
        else:
            m=re.match(r"^(※)\s*([^:：\n]{2,50})\s*$",line)
            if not m:
                continue
            marker,label=m.groups()
            body_lines=[]
            for following in lines[index+1:]:
                if not following or re.match(r"^[▶★※◆◇]",following):
                    break
                body_lines.append(following)
            if not body_lines:
                continue
            body="\n".join(body_lines)
            method="marker_header_following_lines"
        label=label.strip()
        body=body.strip()
        key=(marker,label,body)
        if not label or not body or key in seen:
            continue
        seen.add(key)
        out.append({
            "source_card_id":str(card_id),"source_card_name":str(card_name or ""),
            "source_field":"TextExtra","marker":marker,"effect_name":label,
            "definition_text":body,"source_text_sha256":source_hash,
            "extraction_method":method,"verification_status":"source_text_extracted"
        })
    return out

def parse(text, known_skills=None, known_cards=None, known_named_effects=None, known_named_effect_fragments=None):
    raw_text=(text or "").strip()
    t=raw_text
    # Strip visual source markers only from the analysis copy; preserve rawText.
    t=re.sub(r"^[◇◆※▶★☆◈●○]+\s*","",t).strip()
    t=re.sub(r"^\*\s+","",t).strip()
    # FM1 card effects often append flavor/lore in square brackets to the same
    # source clause. Parse the rule sentence separately, but preserve the quote.
    flavor_text=None
    flavor_match=re.search(r"\s+\[([^\]]{12,})\]\s*(?:By\s*-\s*.+)?$",t)
    if flavor_match:
        flavor_text=flavor_match.group(1).strip()
        t=t[:flavor_match.start()].strip()
    compact="".join(t.split())
    if re.fullmatch(r"[.。…\s]+",t):
        return {"classification":"punctuation_artifact","triggers":[],"actors":[],"targets":[],
                "conditions":[],"operations":[{"kind":"punctuation_artifact","executable":False}],
                "numbers":[],"rawText":raw_text,"flavorText":flavor_text,
                "inferenceMethod":"punctuation_artifact_v1","confidence":"not_applicable"}
    if any(token in t for token in ("구입에 오류","구매를 부탁","툴팁이 다음주 수정","설명이 수정되었습니다","상시구매란?","카드상점에서 상시구매")):
        return {"classification":"administrative_or_shop_note","triggers":[],"actors":[],"targets":[],
                "conditions":[],"operations":[{"kind":"administrative_note","rawText":raw_text,"executable":False}],
                "numbers":[],"rawText":raw_text,"flavorText":flavor_text,
                "inferenceMethod":"admin_note_v1","confidence":"not_applicable"}
    if t.startswith("[") and t.endswith("]") and len(t)>=40:
        return {"classification":"flavor_or_lore","triggers":[],"actors":[],"targets":[],
                "conditions":[],"operations":[{"kind":"flavor_text","rawText":raw_text,"executable":False}],
                "numbers":[],"rawText":raw_text,"flavorText":t[1:-1],
                "inferenceMethod":"bracketed_lore_v1","confidence":"not_applicable"}
    no_effect=re.search(r"효과\s*없음",t)
    if no_effect:
        condition=t[:no_effect.start()].strip(" .。,:：")
        return {"classification":"conditional_no_effect" if condition else "no_effect_marker",
                "triggers":[],"actors":[],"targets":[],"conditions":[condition] if condition else [],
                "operations":[{"kind":"no_effect_condition" if condition else "no_effect_marker",
                               "conditionText":condition or None,"executable":False}],
                "numbers":re.findall(r"(?<!\d)\d+",t),"rawText":raw_text,"flavorText":flavor_text,
                "inferenceMethod":"no_effect_marker_v1","confidence":"medium" if condition else "not_applicable"}
    if "무속성 이벤트 마법은 이벤트 마법으로 취급됩니다" in t:
        return {"classification":"card_type_treatment_rule","triggers":[],"actors":[],"targets":[],
                "conditions":[],"operations":[{"kind":"card_type_treatment","sourceType":"neutral_event_magic",
                    "treatedAs":"event_magic","executable":False}],
                "numbers":[],"rawText":raw_text,"flavorText":flavor_text,
                "inferenceMethod":"neutral_event_magic_type_v1","confidence":"medium"}
    if "무속성 마법은 시스카이의 대상이 되지 않습니다" in t:
        return {"classification":"target_exclusion_rule","triggers":[],"actors":[],"targets":["neutral_magic"],
                "conditions":[],"operations":[{"kind":"exclude_target","targetType":"neutral_magic",
                    "against":"시스카이","executable":False}],
                "numbers":[],"rawText":raw_text,"flavorText":flavor_text,
                "inferenceMethod":"neutral_magic_target_exclusion_v1","confidence":"medium"}
    status_definition=re.match(r"^(?P<name>[^:：]{2,40}상태)\s*[:：]\s*(?P<body>.+)$",t)
    if status_definition:
        status_name=status_definition.group("name").strip()
        body=status_definition.group("body").strip()
        operations=[]
        level=re.search(r"레벨\s*([+-])\s*(\d+)",body)
        if level:
            operations.append({"kind":"modify_level","operator":level.group(1),"value":int(level.group(2)),"executable":False})
        for stat_match in re.finditer(r"\b(AP|DP|HP)\s*[×xX*]\s*(\d+)",body,re.I):
            operations.append({"kind":"multiply_stat","stat":stat_match.group(1).lower(),
                               "multiplier":int(stat_match.group(2)),"executable":False})
        if operations:
            defs=(known_named_effects or {}).get(normalize_effect_name(status_name),[])
            return {"classification":"named_status_definition","triggers":[],"actors":[],
                    "targets":["unit"],"conditions":[],"operations":[
                        {"kind":"named_status_definition","statusName":status_name,
                         "definitionText":body,"definitionIds":[x["definition_id"] for x in defs],
                         "sourceCardIds":_uniq([x["source_card_id"] for x in defs]),"executable":False}
                    ]+operations,
                    "numbers":re.findall(r"(?<!\d)\d+",body),"rawText":raw_text,"flavorText":flavor_text,
                    "inferenceMethod":"named_status_formula_v1","confidence":"medium"}
    normalized_name=normalize_effect_name(t)
    named_defs=(known_named_effects or {}).get(normalized_name,[])
    if named_defs and len(normalized_name)>=4 and not re.search(r"[:：]",t):
        return {"classification":"named_effect_reference","triggers":[],"actors":[],
                "targets":["named_effect"],"conditions":[],
                "operations":[{"kind":"named_effect_reference","effectName":t,
                    "definitionIds":[x["definition_id"] for x in named_defs],
                    "definitionCardIds":_uniq([x["source_card_id"] for x in named_defs]),
                    "definitionTexts":_uniq([x["definition_text"] for x in named_defs]),
                    "executable":False}],
                "numbers":[],"rawText":raw_text,"flavorText":flavor_text,
                "inferenceMethod":"cross_field_named_effect_reference_v1","confidence":"medium"}
    if normalized_name in (known_named_effect_fragments or {}):
        fragments=(known_named_effect_fragments or {})[normalized_name]
        return {"classification":"named_effect_definition_body","triggers":[],"actors":[],
                "targets":["named_effect_definition"],"conditions":[],
                "operations":[{"kind":"named_effect_definition_body","effectNames":_uniq([x["effect_name"] for x in fragments]),
                    "definitionIds":_uniq([x["definition_id"] for x in fragments]),
                    "sourceCardIds":_uniq([x["source_card_id"] for x in fragments]),"executable":False}],
                "numbers":re.findall(r"(?<!\d)\d+",t),"rawText":raw_text,"flavorText":flavor_text,
                "inferenceMethod":"named_effect_definition_body_v1","confidence":"medium"}
    named_definition=re.match(r"^(?P<name>[^:：]{2,40})\s*[:：]\s*(?P<body>.+)$",t)
    if named_definition:
        label=named_definition.group("name").strip()
        defs=(known_named_effects or {}).get(normalize_effect_name(label),[])
        if defs:
            return {"classification":"named_effect_definition","triggers":[],"actors":[],
                    "targets":["named_effect_definition"],"conditions":[],
                    "operations":[{"kind":"named_effect_definition","effectName":label,
                        "definitionText":named_definition.group("body").strip(),
                        "definitionIds":[x["definition_id"] for x in defs],
                        "sourceCardIds":_uniq([x["source_card_id"] for x in defs]),"executable":False}],
                    "numbers":re.findall(r"(?<!\d)\d+",t),"rawText":raw_text,"flavorText":flavor_text,
                    "inferenceMethod":"named_effect_definition_v1","confidence":"medium"}
    metadata=re.match(r"^(?P<label>시점|능력|장착가능한 유닛|카드종류)\s*[:：]\s*(?P<value>.+)$",t)
    if metadata:
        kind={"시점":"trigger_timing_metadata","능력":"ability_type_metadata",
              "장착가능한 유닛":"equip_condition_metadata","카드종류":"card_type_metadata"}[metadata.group("label")]
        return {"classification":kind,"triggers":[],"actors":[],"targets":[],
                "conditions":[metadata.group("value").strip()],
                "operations":[{"kind":kind,"value":metadata.group("value").strip(),"executable":False}],
                "numbers":re.findall(r"(?<!\d)\d+",t),"rawText":raw_text,"flavorText":flavor_text,
                "inferenceMethod":"card_metadata_label_v1","confidence":"medium"}
    if re.search(r"조건을 먼저 체크한 뒤",t):
        return {"classification":"condition_evaluation_order","triggers":[],"actors":[],
                "targets":[],"conditions":[t],
                "operations":[{"kind":"condition_evaluation_order","rawRule":t,"executable":False}],
                "numbers":re.findall(r"(?<!\d)\d+",t),"rawText":raw_text,"flavorText":flavor_text,
                "inferenceMethod":"condition_order_note_v1","confidence":"medium"}
    if re.search(r"가장 많은 카드로 체크하지 않기 때문에",t):
        return {"classification":"card_counting_rule","triggers":[],"actors":[],
                "targets":[],"conditions":[t],
                "operations":[{"kind":"card_counting_rule","rawRule":t,"executable":False}],
                "numbers":re.findall(r"(?<!\d)\d+",t),"rawText":raw_text,"flavorText":flavor_text,
                "inferenceMethod":"card_counting_note_v1","confidence":"medium"}
    tier=re.match(r"^(?P<range>\d+(?:~\d+)?레벨(?:\s*이상)?)\s*[-–:：]\s*(?P<name>.+)$",t)
    if tier:
        return {"classification":"level_tier_mapping","triggers":[],"actors":[],
                "targets":["level_tier"],"conditions":[tier.group("range")],
                "operations":[{"kind":"level_tier_mapping","levelRange":tier.group("range"),
                               "mappedName":tier.group("name").strip(),"executable":False}],
                "numbers":re.findall(r"(?<!\d)\d+",t),"rawText":raw_text,"flavorText":flavor_text,
                "inferenceMethod":"level_tier_mapping_v1","confidence":"medium"}
    if t.startswith("(") and t.endswith(")") and len(t)>3:
        if any(x in t for x in ("발동안함","발동하지","조건","일 경우","이면","없으면")):
            classification="parenthetical_activation_condition"
        elif any(x in t for x in ("수정되었습니다","이미 안내되어","같이 발매된")):
            classification="parenthetical_reference_note"
        else:
            classification="parenthetical_rule_note"
        return {"classification":classification,"triggers":[],"actors":[],
                "targets":[],"conditions":[t[1:-1]],
                "operations":[{"kind":classification,"rawRule":t,"executable":False}],
                "numbers":re.findall(r"(?<!\d)\d+",t),"rawText":raw_text,"flavorText":flavor_text,
                "inferenceMethod":"parenthetical_note_v1","confidence":"medium"}

    if re.search(r"^매직랜드는 .*맨 앞의 매직랜드만 발동",t):
        return {"classification":"terrain_activation_rule_candidate","triggers":["terrain_activation"],
                "actors":[],"targets":["frontmost_magic_land"],"conditions":[t],
                "operations":[{"kind":"activation_order_constraint","rawRule":t,"executable":False}],
                "numbers":[],"rawText":raw_text,"flavorText":flavor_text,
                "inferenceMethod":"terrain_order_note_v1","confidence":"medium"}
    if re.search(r"^유닛간 상성으로 인한 상태와 .*상성은 사라지지 않습니다",t):
        return {"classification":"persistent_state_rule_candidate","triggers":[],
                "actors":[],"targets":["matchup_state"],"conditions":[t],
                "operations":[{"kind":"state_persistence_constraint","rawRule":t,"executable":False}],
                "numbers":[],"rawText":raw_text,"flavorText":flavor_text,
                "inferenceMethod":"state_persistence_note_v1","confidence":"medium"}
    if re.fullmatch(r".+상태의 조건 대상이 됩니다[.]?", t):
        return {"classification":"state_condition_target_reference","triggers":[],"actors":[],
                "targets":["status_condition_target"],"conditions":[t],
                "operations":[{"kind":"status_condition_target_reference","rawRule":t,"executable":False}],
                "numbers":[],"rawText":raw_text,"flavorText":flavor_text,
                "inferenceMethod":"status_condition_target_note_v1","confidence":"medium"}
    if ("핸드 빈공간이 없을 경우" in t or "핸드 빈공간이 없으면" in t
            or ("자신과 같은 속성의" in t and "없으면 발동하지" in t)
            or "발동시 아군 유닛" in t or ("핸드 또는 필드에" in t and "존재시 발동" in t)
            or ("발동하지" in t and any(k in t for k in ("DP가 0","묘지가 0","핸드 카드가 없거나")))):
        return {"classification":"effect_activation_requirement","triggers":[],
                "actors":[],"targets":[],"conditions":[t],
                "operations":[{"kind":"activation_restriction","conditionText":t,"executable":False}],
                "numbers":re.findall("[0-9]+",t),"rawText":raw_text,"flavorText":flavor_text,
                "inferenceMethod":"activation_restriction_v2","confidence":"medium"}
    if "상성효과" in t and (":" in t or "：" in t):
        return {"classification":"matchup_effect_reference_candidate","triggers":[],
                "actors":[],"targets":[],"conditions":[t],
                "operations":[{"kind":"matchup_effect_reference","rawRule":t,"executable":False}],
                "numbers":[],"rawText":raw_text,"flavorText":flavor_text,
                "inferenceMethod":"matchup_effect_reference_v1","confidence":"medium"}
    if t.startswith("1)") and "아군 핸드/필드 카드종류수 이하" in t:
        return {"classification":"effect_activation_requirement","triggers":[],
                "actors":[],"targets":[],"conditions":[t],
                "operations":[{"kind":"activation_condition","conditionText":t,"executable":False}],
                "numbers":[],"rawText":raw_text,"flavorText":flavor_text,
                "inferenceMethod":"card_count_requirement_v1","confidence":"medium"}
    if "아군 필드 빈공간 수가" in t and (":" in t or "：" in t):
        return {"classification":"conditional_branch_reference","triggers":[],
                "actors":[],"targets":[],"conditions":[t],
                "operations":[{"kind":"conditional_branch","conditionText":t,"executable":False}],
                "numbers":re.findall("[0-9]+",t),"rawText":raw_text,"flavorText":flavor_text,
                "inferenceMethod":"field_space_branch_v1","confidence":"medium"}
    if "①과 ②중 조건에 맞는 하나의 효과만 발동" in t:
        return {"classification":"effect_selection_rule_candidate","triggers":[],
                "actors":[],"targets":[],"conditions":[t],
                "operations":[{"kind":"exclusive_effect_selection","rawRule":t,"executable":False}],
                "numbers":[],"rawText":raw_text,"flavorText":flavor_text,
                "inferenceMethod":"exclusive_effect_selection_v1","confidence":"medium"}
    if "코러스 상태" in t and (":" in t or "：" in t):
        return {"classification":"named_status_rule_candidate","triggers":["on_status_activate"],
                "actors":["friendly"],"targets":["unit"],"conditions":[t],
                "operations":[{"kind":"count_based_status_rule","rawRule":t,"executable":False}],
                "numbers":[],"rawText":raw_text,"flavorText":flavor_text,
                "inferenceMethod":"named_status_rule_v1","confidence":"medium"}
    if "상태가 사라지면" in t and ("원래대로" in t or "원상복구" in t):
        return {"classification":"state_reversion_rule_candidate","triggers":["on_status_removed"],
                "actors":[],"targets":["unit"],"conditions":[t],
                "operations":[{"kind":"restore_previous_state","rawRule":t,"executable":False}],
                "numbers":[],"rawText":raw_text,"flavorText":flavor_text,
                "inferenceMethod":"state_reversion_note_v1","confidence":"medium"}
    if t.startswith("짝수 :") or t.startswith("홀수 :") or t.startswith("짝수：") or t.startswith("홀수："):
        return {"classification":"conditional_branch_reference","triggers":[],
                "actors":[],"targets":[],"conditions":[t],
                "operations":[{"kind":"parity_branch","conditionText":t,"executable":False}],
                "numbers":[],"rawText":raw_text,"flavorText":flavor_text,
                "inferenceMethod":"parity_branch_v1","confidence":"medium"}
    if t.startswith("연계카드 :") or t.startswith("연계카드："):
        label,body=re.split("[:：]",t,maxsplit=1)
        name_key="".join(body.strip(" .。").split())
        if known_cards and name_key in known_cards:
            return {"classification":"card_reference_list","triggers":[],"actors":[],
                    "targets":[],"conditions":[],"operations":[{"kind":"related_card_reference",
                        "cardName":body.strip(),"cardIds":known_cards[name_key],"executable":False}],
                    "numbers":[],"rawText":raw_text,"flavorText":flavor_text,
                    "inferenceMethod":"linked_card_reference_v1","confidence":"medium"}
    if re.match(r"^(?:아군|적군).{0,100}(?:필드|핸드).{0,80}(?:필요|없으면|없을 경우|존재하면|보유)",t):
        return {"classification":"effect_activation_requirement","triggers":[],
                "actors":[],"targets":[],"conditions":[t],
                "operations":[{"kind":"activation_condition","conditionText":t,"executable":False}],
                "numbers":re.findall(r"(?<!\d)\d+",t),"rawText":raw_text,"flavorText":flavor_text,
                "inferenceMethod":"activation_requirement_note_v1","confidence":"medium"}
    if re.match(r"^(?:실패시|성공시)\s*[:：=]",t):
        return {"classification":"conditional_branch_reference","triggers":[],
                "actors":[],"targets":[],"conditions":[t],
                "operations":[{"kind":"conditional_branch","conditionText":t,"executable":False}],
                "numbers":re.findall(r"(?<!\d)\d+",t),"rawText":raw_text,"flavorText":flavor_text,
                "inferenceMethod":"success_failure_branch_v1","confidence":"medium"}
    if re.match(r"^(?:기본효과|발동후 효과|발동 후 효과)",t):
        return {"classification":"effect_timing_rule_candidate","triggers":[],
                "actors":[],"targets":[],"conditions":[t],
                "operations":[{"kind":"effect_timing_constraint","rawRule":t,"executable":False}],
                "numbers":[],"rawText":raw_text,"flavorText":flavor_text,
                "inferenceMethod":"effect_timing_note_v1","confidence":"medium"}
    if re.match(r"^무한턴일 때\s*\d+턴으로 처리",t):
        return {"classification":"turn_duration_override_candidate","triggers":[],
                "actors":[],"targets":[],"conditions":[t],
                "operations":[{"kind":"turn_duration_override","rawRule":t,"executable":False}],
                "numbers":re.findall(r"(?<!\d)\d+",t),"rawText":raw_text,"flavorText":flavor_text,
                "inferenceMethod":"infinite_turn_override_v1","confidence":"medium"}
    if re.match(r"^해당 유닛을 필드에 올리면 .+상태가 바로 발동",t):
        return {"classification":"on_play_status_trigger_candidate","triggers":["on_play"],
                "actors":["played_unit"],"targets":[],"conditions":[],
                "operations":[{"kind":"apply_status","rawRule":t,"executable":False}],
                "numbers":[],"rawText":raw_text,"flavorText":flavor_text,
                "inferenceMethod":"on_play_status_note_v1","confidence":"medium"}
    status_delta=re.match(r"^(?P<target>[^:：]+)[:：]\s*(?P<status>.+?)\s*(?P<sign>[+-])\s*(?P<turns>\d+)\s*턴[.。]?$",t)
    if status_delta:
        return {"classification":"status_duration_change_candidate","triggers":[],
                "actors":[],"targets":[status_delta.group("target").strip()],"conditions":[],
                "operations":[{"kind":"modify_status_duration","targetText":status_delta.group("target").strip(),
                    "statusText":status_delta.group("status").strip(),
                    "turnDelta":int(status_delta.group("turns"))*(1 if status_delta.group("sign")=="+" else -1),
                    "executable":False}],
                "numbers":[status_delta.group("turns")],"rawText":raw_text,"flavorText":flavor_text,
                "inferenceMethod":"status_duration_note_v1","confidence":"medium"}
    if re.match(r"^(?:만능|마법|장비|야수)\s*[:：].*상태\s*\([^)]+\)",t):
        return {"classification":"unit_ability_profile_reference","triggers":[],
                "actors":[],"targets":[],"conditions":[t],
                "operations":[{"kind":"ability_stat_profile_reference","rawRule":t,"executable":False}],
                "numbers":re.findall(r"(?<!\d)[+-]?\d+",t),"rawText":raw_text,"flavorText":flavor_text,
                "inferenceMethod":"ability_profile_reference_v1","confidence":"not_applicable"}
    if re.match(r"^(?:중급|상급|하급)\s*[가-힣A-Za-z0-9]+\s*[;；:]?$",t) or re.match(r"^(?:유닛 목록[.]?|튜터능력|챕터\d+ 스페설 마법 특징)$",t):
        return {"classification":"section_heading","triggers":[],"actors":[],"targets":[],
                "conditions":[],"operations":[{"kind":"section_heading","rawText":raw_text,"executable":False}],
                "numbers":[],"rawText":raw_text,"flavorText":flavor_text,
                "inferenceMethod":"section_heading_v2","confidence":"not_applicable"}
    if known_cards and re.search(r"[:：]",t):
        label,body=re.split(r"[:：]",t,maxsplit=1)
        label_key="".join(label.split())
        if label_key in known_cards and re.search(r"[=+*-]?\s*\d+\s*/\s*[=+*-]?\s*\d+\s*/\s*[=+*-]?\s*\d+",body):
            return {"classification":"card_stat_profile_reference","triggers":[],
                    "actors":[],"targets":[],"conditions":[],
                    "operations":[{"kind":"related_card_definition","cardName":label.strip(),
                        "cardIds":known_cards[label_key],"statText":body.strip(),"executable":False}],
                    "numbers":re.findall(r"(?<!\d)[+-]?\d+",body),"rawText":raw_text,
                    "flavorText":flavor_text,"inferenceMethod":"card_stat_profile_link_v1","confidence":"medium"}
    if known_cards:
        card_list=[x.strip() for x in re.split(r"[,，、]",t) if x.strip()]
        if len(card_list)>1 and all("".join(x.split()) in known_cards for x in card_list):
            return {"classification":"card_reference_list","triggers":[],"actors":[],
                    "targets":[],"conditions":[],"operations":[{"kind":"related_card_reference",
                        "entries":[{"label":x,"cardIds":known_cards["".join(x.split())]} for x in card_list],
                        "executable":False}],"numbers":[],"rawText":raw_text,"flavorText":flavor_text,
                    "inferenceMethod":"known_card_list_link_v1","confidence":"medium"}

    # Source notes, credits, collection restrictions and headings are not game effects.
    metadata_patterns=[
      r"^invalid$",
      r"^.*구입.*오류.*$",
      r"^.*FAQ\s*검색.*$",
      r"^상성효과[.]?$",
      r"^디스히어로 카드$",
      r"^디스인첸트 카드$",
      r"^(?:유닛 목록|마법 목록|아이템 목록|인첸트 목록|인챈트 목록|기본형 마법 소개|복제공식에 관한 안내)[.]?$",
      r"^.*카드는 .*이벤트 카드",
      r"^.*카드는 확장앨범 .*재료카드",
      r"^.*퀘스트.*(?:완료하면|받을 수|완료해야)",
      r"^.*(?:소속|종족)은 큰 이미지의",
      r"^.*(?:글자|글자로) 취급됩니다?[.]?$",
      r"^.*등급.*(?:동일하게 취급|범주에 포함)",
      r"^.*(?:오타|오류).*(?:수정|적혀있|예정)",
      r"^.*카드.*(?:상점|검색).*(?:확인|검색)",
      r"^.*특수능력을 지닌 유니크등급의 유니트카드입니다[.]?$",
      r"^◈?\s*illustrated by\b",
      r"^\d+차\s*강화\s*유닛\s*특징$",
      r"^상성(?:효과|카드|유닛|아이템)\s*:?\s*$",
      r"^(?:성장목록|성장유닛|오오라 능력|변경되는 유닛 리스트)$",
      r"^해당\s*(?:지형|유닛|아이템|마법|카드).*(?:입니다|가지고 있습니다|확인하실 수|확인할 수|FAQ를 참조|획득 가능합니다|획득할 수 있습니다)",
      r"^3차 강화 카드는 만능능력 유닛으로 아이템 착용에 있어서 제한이 없습니다",
      r"^아이템 착용에 있어서 제한이 전혀 없는 특징을 갖고 있는 유닛입니다",
      r"^에카마엘 유닛은 .*전용테두리로 표시됩니다",
      r"^모든 \[마일리지카드\]는",
      r"^농민은 에피소드 농민만 해당됩니다",
      r"^좌측 히어로 창을 클릭한 후",
      r"^해당 기술은 유닛의 고유기술로서",
      r"^해당 아이템은 \d차 강화능력을 보유",
      r"^해당 유닛은 .*을 보유하고 있습니다",
      r"^Expansion 일일퀘스트 .*보상으로 받을",
      r"^이카젠 등급은 유니크 등급과 동일하게 취급",
      r"^종족은 유닛 카드 큰 이미지",
      r"^종족 스페셜 카드들은 특수한 능력을 가지고 있습니다",
      r"^SP/보석카드 종류",
      r"^챕터 유닛은 .*모든 유닛을 말합니다",
      r"^소드걸즈 유닛은 모두 동일한 아티스트값",
      r"^자세한 사항은 FAQ를 참고",
      r"^해당 상태에 대한 자세한 설명은 FAQ",
      r"^FM올림픽 이벤트 .*상품 카드입니다",
      r"^.*최초로 제작하신 카드입니다",
      r"^※표시 확인",
      r"^해당 마법은 .*로 발동됩니다",
      r"^에카마엘 유닛 \(챕터\)",
      r"^하급에카마엘상태$",
      r"^유닛,인첸트:HP$",
      r"^상성 안내$",
      r"^상성(?:유닛|아이템)\s*[:：]",
      r"^(?:랭크가 있는 카드입니다|랭크 카드 안내|랭크카드 각각에 대한 설명은)",
      r"^(?:FM 도움말|고객센터|홈페이지 메인화면|이벤트 페이지를 확인)",
      r"^20\d\d년.*(?:이벤트|부스터).*(?:획득|제공|유닛|카드)",
      r"^에카마엘과 관련하여 특별한 효과를 발휘합니다[.]?$",
      r"^표시 확인\)?$",
      r"^필드 슬롯 번호[.]?$",
      r"^기술방어보다 먼저 발동하는 기술 목록",
      r"^기호 소개[.]?$",
      r"^상성$",
      r"^표시 확인\)?$",
      r"^필드 슬롯 번호[.]?$",
      r"^기술방어보다 먼저 발동하는 기술 목록",
      r"^기호 소개[.]?$",
      r"^고정기호\s*[:：]",
      r"^.*카드는 디스펠 타입의 카드입니다",
      r"^나만의 카드를 GET 이벤트로 지급된 특수 카드입니다",
      r"^.*이벤트.*(?:특수 카드|유닛|카드)[.]?$",
      r"^\d+점\s*[=：]",
      r"^\d+(?:~\d+)?\s*[:：=]\s*(?:효과없음|Free|N Rank|C~B Rank|A~S Rank|Rare|Unique|Legend)",
      r"^\*?\s*(?:AP|DP|HP)\s*[:：]",
      r"^.*상성효과\s*[:：]\s*하단 참조",
      r"^By\s*[-:].*",
      r"^고정기호\s*[:：]",
      r"^.*카드는 디스펠 타입의 카드입니다",
      r"^나만의 카드를 GET 이벤트로 지급된 특수 카드입니다",
      r"^.*이벤트.*(?:특수 카드|유닛|카드)[.]?$",
      r"^.*\[.*\]\s*By\s*[-:]",
      r"^\d+점\s*[=：]",
      r"^\d+(?:~\d+)?\s*[:：=]\s*(?:효과없음|Free|N Rank|C~B Rank|A~S Rank|Rare|Unique|Legend)",
      r"^.*상성효과\s*[:：]\s*(?:하단 참조|방어고정)",
      r"^By\s*[-:].*",
      r"^20\d\d년.*(?:이벤트|부스터).*(?:획득|제공)",
      r"^상성(?:유닛|아이템)\s*[:：]",
      r"^◈\s*",
      r"^자세한 사항은 FAQ에서",
      r"^아이템빌드업\s*\(",
      r"^이후 .*수정될 예정이오니",
      r"^카드 큰이미지 오류가 수정되었습니다",
      r"^자세한 내용은 이벤트 페이지를 확인",
      r"^.*카드는 .*스토리모드.*퀘스트.*(?:완료|받을 수)",
      r"^.*카드는 .*퀘스트.*완료하면 받을 수",
      r"^종족은 큰 이미지의 중앙 부분",
      r"^타입은 고급검색에서 검색할 수",
      r"^용의인장 카드는 게임내 MAP",

      r"^(?:자세한 내용|더 자세한 내용).*(?:고객센터|홈페이지|FAQ|검색창|검색하여)",
      r"^(?:고객센터|홈페이지 메인화면).*(?:FAQ|검색창|검색하여)",

      r"^\d+차 강화 카드는 .+ 유닛입니다",
      r"^따라서,?\s*아이템 착용에 있어서 제한",
      r"^(?:만능능력|에카마엘 유닛|에카마엘상태)$",
      r"^에카마엘 카드와 같은 레벨",
      r"^-\s*자신을 제외한 아군 유닛에게 영향을 미칩니다",
      r"^\(\s*20\d\d-\d\d-\d\d.*(?:오류수정|오타 수정|특이사항)",
      r"^\(\s*게임내 특이사항.*(?:오타 수정|수정)",
      r"^수집랭커 .*(?:구매가 가능합니다|검색해 보세요)",
      r"^\(암흑:.*(?:불:|물:|숲:|금속:|대지:|빛:).*\)$",
      r"^ex[)）.]",
      r"^~\s*$",
      r"^:\s*$",
    ]
    if any(re.search(p,t,re.I) for p in metadata_patterns):
        return {"classification":"reference_or_metadata","triggers":[],"actors":[],
                "targets":[],"conditions":[],"operations":[{"kind":"source_metadata","rawText":raw_text}],
                "numbers":re.findall(r"(?<!\d)[+-]?\d+(?:\.\d+)?%?",t),
                "rawText":raw_text,"inferenceMethod":"source_metadata_patterns_v2","confidence":"not_applicable"}

    # A lone ellipsis is a source placeholder rather than an omitted parse.
    if re.fullmatch(r"(?:\.\.\.|…|⋯)",t):
        return {"classification":"source_placeholder","triggers":[],"actors":[],
                "targets":[],"conditions":[],"operations":[
                    {"kind":"source_text_placeholder","rawText":raw_text,"executable":False}],
                "numbers":[],"rawText":raw_text,"flavorText":flavor_text,
                "inferenceMethod":"source_placeholder_v1","confidence":"not_applicable"}

    # Activation-only notes are gates, not executable effect operations.
    if any(x in t for x in ("발동하지","발동되지","발동합니다","발동됩니다","발동.")) and not any(
            x in t for x in ("AP+","AP-","DP+","DP-","HP+","HP-","공방체","공체","공방","증가시킨다","감소시킨다","파괴한다","이동시킨다","회복시킨다","변환시킨다")):
        return {"classification":"effect_activation_requirement","triggers":[],"actors":[],
                "targets":[],"conditions":[t],
                "operations":[{"kind":"effect_activation_requirement","conditionText":t,"executable":False}],
                "numbers":[],"rawText":raw_text,
                "flavorText":flavor_text,"inferenceMethod":"activation_gate_note_v2","confidence":"medium"}

    # Exact skill names are linked to the rule catalogue; they are not re-parsed as prose.
    if known_skills and compact in known_skills:
        return {"classification":"ability_name_reference","triggers":[],"actors":[],"targets":[],
                "conditions":[],"operations":[{"kind":"skill_reference","ruleId":known_skills[compact]}],
                "numbers":[],"rawText":raw_text,"flavorText":flavor_text,
                "inferenceMethod":"catalogue_name_link_v2","confidence":"medium"}

    # Exact card names and known card-name pairs are references, not effects.
    if known_cards and compact in known_cards:
        return {"classification":"card_name_reference","triggers":[],"actors":[],
                "targets":[],"conditions":[],"operations":[
                    {"kind":"related_card_reference","cardName":t,
                     "cardIds":known_cards[compact],"executable":False}],
                "numbers":[],"rawText":raw_text,"flavorText":flavor_text,
                "inferenceMethod":"known_card_name_link_v1","confidence":"medium"}
    if known_cards and re.search(r"[:：]",t):
        label,body=re.split(r"[:：]",t,maxsplit=1)
        label_key="".join(label.split()); body_key="".join(body.split())
        if label_key in known_cards and body_key in known_cards:
            return {"classification":"card_reference_list","triggers":[],"actors":[],
                    "targets":[],"conditions":[],"operations":[
                        {"kind":"related_card_reference","entries":[
                            {"label":label.strip(),"cardIds":known_cards[label_key]},
                            {"label":body.strip(),"cardIds":known_cards[body_key]}],
                         "executable":False}],
                    "numbers":[],"rawText":raw_text,"flavorText":flavor_text,
                    "inferenceMethod":"known_card_pair_link_v1","confidence":"medium"}

    # Explanatory examples, flavor-only build-up labels, and acquisition/display
    # notes are reference material rather than executable in-game effects.
    if re.match(r"^(?:예\)|예시\))",t):
        return {"classification":"example_or_reference","triggers":[],"actors":[],
                "targets":[],"conditions":[],"operations":[
                    {"kind":"effect_explanation_example","exampleText":t,"executable":False}],
                "numbers":re.findall(r"(?<!\d)[+-]?\d+(?:\.\d+)?%?",t),
                "rawText":raw_text,"flavorText":flavor_text,
                "inferenceMethod":"example_prefix_v1","confidence":"not_applicable"}

    # Text arrows denote evolution/build-up sequences in this source catalogue.
    # They are preserved as related-card references, not interpreted as effects.
    if re.search(r"(?:->|→|⇒)",t) and not re.search(
        r"(?:공격|방어|효과|발동|증가|감소|부여|파괴|이동|회복)",t):
        stages=[x.strip(" .。") for x in re.split(r"\s*(?:->|→|⇒)\s*",t) if x.strip()]
        if len(stages)>=2:
            return {"classification":"card_progression_reference","triggers":[],
                    "actors":[],"targets":[],"conditions":[],
                    "operations":[{"kind":"card_progression_reference","stages":stages,
                                   "executable":False}],
                    "numbers":[],"rawText":raw_text,"flavorText":flavor_text,
                    "inferenceMethod":"arrow_card_sequence_v1","confidence":"not_applicable"}

    # Named status and named ability labels are references, not free-form effects.
    if t.endswith("상태") and (t.startswith('"') or t.startswith("“")):
        return {"classification":"named_status_reference","triggers":[],"actors":[],
                "targets":[],"conditions":[],"operations":[{"kind":"status_reference",
                    "statusName":t[1:-3].strip(),"executable":False}],
                "numbers":[],"rawText":raw_text,"flavorText":flavor_text,
                "inferenceMethod":"quoted_status_reference_v1","confidence":"medium"}
    if len(t)<30 and t.endswith("상태") and t[:-2].strip() and not t.startswith("[") and not any(x in t for x in ("발동","부여","제거","해제")):
        return {"classification":"named_status_reference","triggers":[],"actors":[],
                "targets":[],"conditions":[],"operations":[{"kind":"status_reference",
                    "statusName":t[:-2].strip(),"executable":False}],
                "numbers":[],"rawText":raw_text,"flavorText":flavor_text,
                "inferenceMethod":"named_status_reference_v2","confidence":"medium"}
    if ("(공격기술)" in t or "(방어기술)" in t or "[방어기술]" in t) and len(t)<50:
        return {"classification":"named_ability_reference_candidate","triggers":[],
                "actors":[],"targets":[],"conditions":[],
                "operations":[{"kind":"ability_name_reference_candidate","name":t,"executable":False}],
                "numbers":[],"rawText":raw_text,"flavorText":flavor_text,
                "inferenceMethod":"named_ability_label_v1","confidence":"medium"}
    status_ref=re.fullmatch(r"\[([^\]]+)\]\s*상태\s*[:：]?",t)
    if status_ref:
        return {"classification":"named_status_reference","triggers":[],"actors":[],
                "targets":[],"conditions":[],"operations":[
                    {"kind":"status_reference","statusName":status_ref.group(1),"executable":False}],
                "numbers":[],"rawText":raw_text,"flavorText":flavor_text,
                "inferenceMethod":"bracketed_status_reference_v1","confidence":"medium"}

    # Legacy card databases sometimes store elemental/card pair labels as a list,
    # e.g. '금-유리가면'. These are references rather than game-effect sentences.
    card_ref=re.fullmatch(r"(금|물|불|빛|숲|암|흑|대지|철|목|수|화|광)\s*[-–—]\s*(.+)",t)
    if card_ref:
        return {"classification":"card_reference_list","triggers":[],"actors":[],
                "targets":[],"conditions":[],"operations":[
                    {"kind":"related_card_reference","label":card_ref.group(1),
                     "cardName":card_ref.group(2).strip(),"executable":False}],
                "numbers":[],"rawText":raw_text,"flavorText":flavor_text,
                "inferenceMethod":"element_card_reference_v1","confidence":"not_applicable"}

    # Element-to-card and type-to-card rows are catalogue relations.
    # Only classify these as references when no game-action verb is present.
    relation_rows=re.findall(
        r"(암흑|암|불|물|숲|금속|대지|빛|철|목|수|화|광|지형|유닛|마법|아이템)\s*[:：-]\s*([^,;■◇◆]+)",
        t)
    if relation_rows and not re.search(
        r"(?:증가|감소|공격|방어|발동|파괴|부여|적용|변경|된다|시킨다|회복|이동)",t):
        return {"classification":"card_reference_list","triggers":[],"actors":[],
                "targets":[],"conditions":[],"operations":[
                    {"kind":"related_card_reference","entries":[
                        {"label":a,"value":b.strip(" .。")} for a,b in relation_rows],
                     "executable":False}],
                "numbers":re.findall(r"(?<!\d)[+-]?\d+(?:\.\d+)?%?",t),
                "rawText":raw_text,"flavorText":flavor_text,
                "inferenceMethod":"element_or_type_relation_v1","confidence":"not_applicable"}

    # Rarity/gemstone tables and category bonuses are metadata or reference values.
    if re.match(r"^(?:프리|커먼|언커먼|레어|유니크|시크릿|에픽|이벤트|스페셜|에메랄드|토파즈|탄자나이트)(?:\s*[,/、]\s*(?:프리|커먼|언커먼|레어|유니크|시크릿|에픽|이벤트|스페셜))*\s*[:：]",t):
        return {"classification":"rarity_or_category_reference","triggers":[],
                "actors":[],"targets":[],"conditions":[],
                "operations":[{"kind":"rarity_or_category_mapping","rawText":raw_text,
                               "executable":False}],
                "numbers":re.findall(r"(?<!\d)[+-]?\d+(?:\.\d+)?%?",t),
                "rawText":raw_text,"flavorText":flavor_text,
                "inferenceMethod":"rarity_category_reference_v1","confidence":"not_applicable"}

    triggers=[]
    for key,pat in [
      ("on_attack",r"공격\s*시|공격할 때|공격 선언"),
      ("on_defense",r"방어\s*시|방어할 때|방어 선언"),
      ("on_self_destroy",r"자신\s*파괴\s*시|자신이 파괴|자신 파괴"),
      ("on_enemy_destroy",r"적\s*\d*\s*파괴\s*시|적 유닛 파괴"),
      ("on_summon",r"소환\s*시|배치\s*시|필드로 소환"),
      ("on_status_expire",r"상태\s*해제\s*시|상태해제시|상태\s*발동\s*시"),
      ("on_soul_cost",r"소울\s*코스트\s*시|유지비\s*지불\s*시"),
      ("on_receive_attack",r"공격을\s*받을\s*때|공격받을\s*때|피격\s*시"),
      ("on_damage",r"피해를?\s*입을\s*때|데미지를?\s*받을\s*때"),
      ("on_kill",r"적(?:군)?\s*유닛을?\s*파괴\s*시|적\s*처치\s*시"),
      ("on_leave_field",r"필드에서\s*(?:제거|떠날|이탈)\s*시|필드\s*이탈\s*시"),
      ("on_discard",r"버려질\s*때|버릴\s*때|핸드에서\s*버리"),
      ("turn_start",r"턴 시작|준비 단계 시작"),
      ("turn_end",r"턴 종료|턴 끝"),
      ("each_turn",r"매\s*턴|턴마다"),
      ("on_play",r"발동\s*시|사용\s*시|장착\s*시")]:
        if re.search(pat,t): triggers.append(key)
    stat_name_map={"AP":"ap","공격력":"ap","DP":"dp","방어력":"dp","HP":"hp","체력":"hp","LP":"lp"}
    actors=[]
    for key,pat in [("self",r"자신|자기"),("friendly",r"아군"),("enemy",r"적군|상대|적 "),("both_sides",r"아군.{0,8}적군|양쪽")]:
        if re.search(pat,t): actors.append(key)
    targets=[]
    for key,pat in [
      ("unit",r"유닛"),("terrain",r"지형|백필드"),("spell",r"마법|인챈트|인첸트"),
      ("item",r"아이템|장비"),("hand",r"핸드"),("deck",r"덱|소각장"),
      ("player",r"플레이어|LP"),("field",r"필드")]:
        if re.search(pat,t): targets.append(key)

    ops=[]
    conditions=[]
    # Three-part legacy AP/DP/HP vectors are preserved as explicit candidates.
    vector_match=re.search(r"([=+-]?[0-9]+) */ *([=+-]?[0-9]+) */ *([=+-]?[0-9]+)",t)
    if vector_match:
        vector_values=list(vector_match.groups())
        target_text=t[:vector_match.start()].strip(" ,:：")
        catalogue_entry=raw_text.lstrip().startswith(("★","☆","*"))
        ops.append({"kind":"combat_stat_vector_reference" if catalogue_entry else "set_combat_stats_vector",
                    "targetText":target_text,"values":vector_values,
                    "rawText":raw_text,"executable":False})
    # Numeric stat deltas and assignments, including Korean names and grouped stats.
    stat_patterns={
      "ap":r"AP|공격력|공격치|공격\s*수치",
      "dp":r"DP|방어력|방어치|방어\s*수치",
      "hp":r"HP|체력|체력치",
      "lp":r"LP|랜드\s*포인트"
    }
    for stat,pat in stat_patterns.items():
        for m in re.finditer(r"("+pat+r")\s*([+-])\s*(\d+)",t):
            ops.append({"kind":"modify_stat","stat":stat,"operator":m.group(2),"value":int(m.group(3))})
        for m in re.finditer(r"("+pat+r")\s*=\s*([★▲▼]?\s*\d+)",t):
            ops.append({"kind":"set_stat","stat":stat,"value":m.group(2).replace(" ","")})
    if re.search(r"공방체|공체|공방|공격력|방어력|체력",t) and re.search(r"증가|감소|변경|상승|하락|올리|내리|영구",t):
        ops.append({"kind":"modify_combat_stats","statGroup":re.findall(r"공방체|공체|공방|공격력|방어력|체력",t),
                    "direction":"text_defined","rawText":raw_text})
    # Exact legacy stat copying, assignments, and multipliers.
    # These candidates retain raw formula text and are never executable by default.
    stat_ref_pattern=r"(AP|DP|HP|LP|공격력|방어력|체력)"
    stat_copy=re.search(
        r"(AP|DP|HP|공격력|방어력|체력)\s*(?:은|는|을|를)?\s*(?:적\s*필드\s*유닛\s*\d+의?\s*)?(AP|DP|HP|공격력|방어력|체력)와?\s*동일해?지",
        t)
    if stat_copy:
        ops.append({"kind":"copy_stat_value","targetStat":stat_name_map.get(stat_copy.group(1),stat_copy.group(1).lower()),
                    "sourceStat":stat_name_map.get(stat_copy.group(2),stat_copy.group(2).lower()),
                    "rawText":raw_text,"executable":False})
    for m in re.finditer(r"(AP|DP|HP|공격력|방어력|체력)\s*(?:는|을|를)?\s*([^,;。]+?)\s*(?:와|과)?\s*(?:같게|동일하게)\s*(?:만든다|한다)",t):
        ops.append({"kind":"set_stat_from_expression","stat":stat_name_map.get(m.group(1)),
                    "expressionText":m.group(2).strip(),"rawText":raw_text,"executable":False})
    for m in re.finditer(r"(AP|DP|HP|공격력|방어력|체력)\s*(?:를|을)?\s*\*\s*(\d+(?:\.\d+)?)\s*(?:로)?\s*(?:만든다|한다)",t):
        ops.append({"kind":"multiply_stat","stat":stat_name_map.get(m.group(1)),
                    "multiplier":float(m.group(2)),"rawText":raw_text,"executable":False})
    if re.search(r"(?:AP|DP|HP|공격력|방어력|체력).{0,35}(?:적 필드 유닛|아군 필드 유닛|적군 전체|아군 전체).{0,25}(?:동일|같게|만큼)",t):
        stats=[stat_name_map[x] for x in re.findall(r"AP|DP|HP|공격력|방어력|체력",t)]
        ops.append({"kind":"set_stat_from_field_expression","stats":_uniq(stats),
                    "expressionText":t,"rawText":raw_text,"executable":False})
    if re.search(r"적군\s*하나를?\s*아군\s*하나의?\s*(?:AP|DP|HP|공방체|공체|공방).{0,20}같게\s*만든다",t):
        ops.append({"kind":"copy_combat_stats_from_unit","stats":_stat_refs(t),
                    "rawText":raw_text,"executable":False})
    if re.search(r"(?:필드번호|필드 위치).{0,20}(?:레벨|위치|번호).{0,20}(?:된다|정한다|맞춘다|편다)",t):
        ops.append({"kind":"set_field_position_from_expression","expressionText":t,
                    "rawText":raw_text,"executable":False})
    if re.search(r"행동가능한 아군\s*\d+의?\s*AP.{0,20}적군의?\s*AP.{0,8}더한다",t):
        ops.append({"kind":"add_stat_from_target_expression","stat":"ap",
                    "sourceExpression":"friendly_unit.ap + enemy.ap",
                    "rawText":raw_text,"executable":False})

    # Coin formulas: preserve exact source formula rather than approximating arithmetic.
    coin_tokens=re.findall(r"(?:[+-]?\s*\d*C\d+|[+-]?\s*C\d+|AC[+-]?\d+|HC[+-]?\d+|[+-]\d+%)",t)
    if coin_tokens or re.search(r"코인|동전|코인수|코인 수|코인확률|코인 확률",t):
        ops.append({"kind":"modify_coin","formulas":coin_tokens,"rawText":raw_text})
    if re.search(r"기호|★|▲|▼",t) and re.search(r"변경|삭제|부여|제거|하향|상향|유지",t):
        ops.append({"kind":"modify_stat_marks","rawText":raw_text})
    if re.search(r"상태",t) and re.search(r"부여|추가|제거|해제|변경|전환|유지|증가|감소",t):
        ops.append({"kind":"modify_status","rawText":raw_text})
    if re.search(r"특수\s*공격\s*기술|공격\s*기술|방어\s*기술|특수기술|기술",t) and re.search(r"부여|추가|변경|삭제|제거|일반공격|일반방어|봉쇄|로\s*된다|로\s*바뀐다",t):
        ops.append({"kind":"modify_skill","rawText":raw_text})
    if re.search(r"소환|소환한|소환시|소환할|배치",t):
        ops.append({"kind":"summon_or_deploy","rawText":raw_text})
    if re.search(r"파괴|소멸|함께 파괴|소각",t):
        ops.append({"kind":"destroy_or_exile","rawText":raw_text})
    if re.search(r"데미지|피해",t):
        ops.append({"kind":"deal_damage","rawText":raw_text})
    if re.search(r"회복|치료|흡수",t):
        ops.append({"kind":"heal_or_recover","rawText":raw_text})
    if re.search(r"드로우|뽑|덱.{0,8}(?:파괴|소각)|핸드로 이동",t):
        ops.append({"kind":"draw_or_mill","rawText":raw_text})
    if re.search(r"이동|교체|변신|변경.{0,8}카드|다음 단계|성장|진화|폴리모프",t):
        ops.append({"kind":"transform_or_move_card","rawText":raw_text})
    if re.search(r"레벨.{0,12}(?:감소|증가|변경)|소울.{0,12}(?:감소|증가|변경)|코스트.{0,12}(?:감소|증가|변경)",t):
        ops.append({"kind":"modify_card_cost_or_level","rawText":raw_text})
    if re.search(r"종족|소속",t) and re.search(r"없음|삭제|변경|부여",t):
        ops.append({"kind":"modify_race_or_faction","rawText":raw_text})
    if re.search(r"장착|해제|아이템을 장착",t):
        ops.append({"kind":"equip_or_unequip","rawText":raw_text})
    if re.search(r"오오라|오라|아레아",t):
        ops.append({"kind":"aura_or_area_effect","rawText":raw_text})
    # Common legacy battle-rule sentences. These are deterministic surface
    # interpretations used by many cards; formula details remain non-executable.
    if re.search(r"DP.{0,14}무시.{0,18}HP.{0,12}직접\s*공격|HP를?\s*직접공격",t):
        ops.append({"kind":"direct_hp_damage","ignoresDefenderDP":True,
                    "formula":"text_defined_attack_value","rawText":raw_text,"executable":False})
    if re.search(r"(?:자신의\s*)?AP.{0,16}DP.{0,12}(?:더해|더하고|합산).{0,12}공격",t):
        ops.append({"kind":"attack_with_ap_and_dp","formula":"attacker.ap + attacker.dp",
                    "rawText":raw_text,"executable":False})
    if re.search(r"상대의?\s*DP.{0,12}(?:깎|감소|낮추|내리)",t):
        amount_match=re.search(r"DP.{0,8}?([+-]?\d+)",t)
        ops.append({"kind":"modify_stat","target":"defender","stat":"dp",
                    "direction":"decrease","value":int(amount_match.group(1)) if amount_match else None,
                    "valueSource":"text" if amount_match else "unspecified_in_source",
                    "rawText":raw_text,"executable":False})
    if re.search(r"(?:상대의\s*)?AP.{0,12}(?:와|및|/)\s*(?:상대의\s*)?HP.{0,12}(?:바뀐다|교환|서로)",t):
        ops.append({"kind":"swap_stats","target":"defender","stats":["ap","hp"],
                    "rawText":raw_text,"executable":False})
    if re.search(r"상대의?\s*AP.{0,12}(?:로|를 사용해)\s*공격",t):
        ops.append({"kind":"attack_using_target_stat","stat":"defender.ap",
                    "rawText":raw_text,"executable":False})
    consecutive=re.search(r"AP\s*(\d+)\s*감소\s*후.{0,12}(?:x|×)\s*(\d+).{0,12}AP.{0,8}공격",t,re.I)
    if consecutive:
        ops.append({"kind":"sequential_attack_formula","firstOperation":{"kind":"modify_stat","stat":"ap",
                    "operator":"-","value":int(consecutive.group(1))},
                    "secondOperation":{"kind":"attack","stat":"ap","multiplier":int(consecutive.group(2))},
                    "rawText":raw_text,"executable":False})
    if re.search(r"특수\s*기술.{0,16}(?:일반\s*기술|일반공격기술).{0,8}(?:바뀐다|변경|전환)",t):
        ops.append({"kind":"modify_skill","target":"defender","operation":"replace_special_with_normal",
                    "rawText":raw_text,"executable":False})

    if re.search(r"DP\s*기호.{0,12}(?:반대로|반전|변환)",t):
        ops.append({"kind":"modify_stat_marks","target":"defender","stat":"dp",
                    "operation":"reverse_sign","rawText":raw_text,"executable":False})
    if re.search(r"DP\s*(?:양수\s*[,，/]\s*음수|음수\s*[,，/]\s*양수)\s*기호.{0,12}(?:반대로|반전|변환|바꾼)",t):
        ops.append({"kind":"modify_stat_marks","target":"defender","stat":"dp",
                    "operation":"reverse_sign","rawText":raw_text,"executable":False})
    if re.search(r"(?:turn|턴).{0,16}(?:1의 자리|일의 자리|일의자리)",t,re.I):
        ops.append({"kind":"dynamic_attack_formula","formula":"turn % 10",
                    "target":"defender","rawText":raw_text,"executable":False})
    if re.search(r"(?:적군|상대).{0,12}DP.{0,16}(?:자신|아군).{0,8}HP.{0,8}(?:증가|회복)",t):
        ops.append({"kind":"modify_stat","target":"self","stat":"hp","operator":"+",
                    "valueFormula":"enemy_field_dp_total_or_target_dp","rawText":raw_text,"executable":False})
    if re.search(r"자신의\s*AP.{0,16}(?:반만큼|절반|/\s*2).{0,16}(?:적|상대).{0,8}AP.{0,12}(?:감소|낮추)",t):
        ops.append({"kind":"transfer_stat_value","sourceStat":"attacker.ap",
                    "transferFormula":"ceil(attacker.ap/2)","targetStat":"defender.ap",
                    "alsoApplyTo":"attacker.ap","rawText":raw_text,"executable":False})
    if re.search(r"동일한 능력.{0,16}유닛수만큼.{0,12}HP.{0,8}증가|같은 능력.{0,16}유닛수만큼.{0,12}HP.{0,8}증가",t):
        ops.append({"kind":"modify_stat","target":"self","stat":"hp","operator":"+",
                    "valueFormula":"count_friendly_units_with_same_ability_excluding_self",
                    "rawText":raw_text,"executable":False})
    if re.search(r"상대 유닛.{0,16}상태 보유 수.{0,16}효과 발동",t):
        ops.append({"kind":"conditional_effect_trigger","condition":"target_status_count",
                    "rawText":raw_text,"executable":False})
    if re.search(r"(?:AP|DP|HP).{0,12}(?:/|,|및).{0,12}(?:AP|DP|HP).{0,16}(?:증가|감소|상승|하락)",t):
        stats=[x.lower() for x in re.findall(r"AP|DP|HP",t)]
        direction="decrease" if re.search(r"감소|하락|낮추",t) else "increase"
        ops.append({"kind":"modify_combat_stats","stats":stats,
                    "direction":direction,"rawText":raw_text,"executable":False})
    if re.search(r"적 유닛은.{0,12}=\s*\d+\s*/\s*=\s*\d+\s*/\s*=\s*\d+",t):
        vals=[int(x) for x in re.findall(r"=\s*(\d+)",t)]
        ops.append({"kind":"set_combat_stats","target":"enemy_unit",
                    "order":["ap","dp","hp"],"values":vals,"rawText":raw_text,"executable":False})
    # Text-defined grouped stat changes and formulaic stat transfers.
    for stat,pat in [("ap",r"AP|공격력"),("dp",r"DP|방어력"),("hp",r"HP|체력")]:
        m=re.search(r"("+pat+r").{0,18}?(\d+)\s*(?:만큼|씩)?\s*(증가|감소|상승|하락)",t)
        if m:
            ops.append({"kind":"modify_stat","stat":stat,
                        "operator":"+" if m.group(3) in ("증가","상승") else "-",
                        "value":int(m.group(2)),"rawText":raw_text,"executable":False})
    if re.search(r"상대의 DP를 자신의 AP에 더해 HP를 직접 공격|DP를 자신의 AP에 더해 HP를 직접 공격",t):
        ops.append({"kind":"direct_hp_damage","ignoresDefenderDP":False,
                    "attackValueFormula":"attacker.ap + defender.dp",
                    "rawText":raw_text,"executable":False})
    if re.search(r"상대의 AP.{0,12}및.{0,12}HP.{0,12}증가|AP.{0,12},.{0,12}HP.{0,12}증가",t):
        ops.append({"kind":"modify_combat_stats","target":"self","stats":["ap","hp"],
                    "direction":"increase","valueFormula":"count_matching_enemy_field_units",
                    "rawText":raw_text,"executable":False})
    if re.search(r"자신의 AP.{0,12}상대 DP보다 높으면.{0,30}상대의 DP/HP를 1 감소",t):
        ops.append({"kind":"conditional_multi_stat_decrease","target":"defender",
                    "stats":["dp","hp"],"value":1,"condition":"attacker.ap > defender.dp",
                    "rawText":raw_text,"executable":False})

    # Compound stat selectors such as "AP/DP/HP 중 가장 높은 수치" were
    # missed by the simple AP+N / DP-N patterns. Preserve the selector and amount.
    selector = re.search(r"(AP\s*[/·,및]\s*DP(?:\s*[/·,및]\s*HP)?|공방체|공방|공체).{0,35}?(최고|최저|가장 높은|가장 낮은|중 하나|각각)",t)
    direction = "decrease" if re.search(r"감소|낮추|하락|내리",t) else "increase" if re.search(r"증가|높이|상승|올리",t) else None
    amount = re.search(r"(?:최고|최저|가장 높은|가장 낮은|중 하나|각각)?.{0,20}?(\d+)\s*(?:만큼|씩)?\s*(?:영구히|영구적으로)?\s*(?:감소|증가|낮춘|높인|내린|올린)",t)
    if selector and direction and amount:
        ops.append({"kind":"modify_selected_combat_stat","selector":selector.group(0),
                    "selection":selector.group(2),"direction":direction,
                    "value":int(amount.group(1)),"rawText":raw_text,"executable":False})

    # Broad Korean action vocabulary. Exact operations above retain explicit
    # numbers/formulas; this layer also captures legacy card verbs whose wording
    # differs across editions. It remains a non-executable candidate.
    action_patterns = [
      ("grant_or_apply",r"부여|추가|적용|부착|부여받|발생시키|생성|만들어|얻는다|획득한다"),
      ("remove_or_disable",r"제거|해제|무효화|무효|차단|방지|봉쇄|금지|봉인|잠금|없앤다|사라진다|막는다"),
      ("modify_or_exchange",r"변경|전환|교환|반전|복사|대체|뒤바꾼|바꾼다|변신|진화|성장"),
      ("resource_or_cost",r"지불|소모|충전|획득|회수|빼앗|코스트|소울|유지비|소비"),
      ("move_or_select",r"이동|선택|지정|옮긴다|되돌린다|반환|보내|돌려보낸다|버린다|버려진다|추방"),
      ("battle_interaction",r"반격|반사|되받아|공격을 막|공격을 받|방어한다|공격한다|직접공격|타격"),
      ("state_or_duration",r"유지|지속|종료|만료|누적|중첩|초기화|마비|빙결|기절|침묵|혼란|중독|화상|공포|실명"),
      ("stat_or_probability",r"증가|감소|상승|하락|높아진다|낮아진다|확률|수치|능력치|공방체|깎|깍|나누|곱하|절반"),
      ("status_or_disabled_state",r"행동불능|행동불능상태|무력화|상태가 된다|상태에 걸린다|걸린다"),
      ("calculated_stat_assignment",r"AP.{0,20}HP.{0,20}(?:된다|설정|정해)|DP.{0,20}(?:된다|설정|정해)|공방체.{0,20}(?:된다|정해)"),
    ]
    action_candidates=[key for key,pat in action_patterns if re.search(pat,t)]
    if action_candidates:
        ops.append({"kind":"generic_effect_operation","actionCandidates":action_candidates,
                    "rawText":raw_text,"executable":False})

    # Named status terms are useful even when the source text omits the generic
    # word '상태'. Keep the exact term list and the original sentence.
    status_terms=re.findall(r"마비|빙결|기절|침묵|혼란|중독|독|화상|공포|실명|구속|봉인|저주|출혈",t)
    if status_terms and re.search(r"부여|걸린|적용|해제|제거|유지|면역|무효|상태",t):
        ops.append({"kind":"apply_or_change_named_status","statusTerms":_uniq(status_terms),
                    "rawText":raw_text,"executable":False})

    # Explicit "no effect" clauses are condition gates, not unparsed prose.
    if re.search(r"(?:경우|때|이상|이하|초과|미만).{0,100}효과\s*없음|효과\s*없음.{0,100}(?:경우|때|이상|이하|초과|미만)",t):
        ops.append({"kind":"suppress_effect_when_condition","conditionText":t,
                    "rawText":raw_text,"executable":False})
    if re.search(r"핸드에.{0,35}(?:없는 경우|없을 경우)|AP나 HP가 발동 후 0이하",t):
        ops.append({"kind":"effect_activation_restriction","conditionText":t,
                    "rawText":raw_text,"executable":False})

    # Preserve formula-like stat assignments and arithmetic as explicit, non-executable
    # candidates. This covers legacy descriptions such as HP=hand size, a stat becoming
    # the count of field units, or combat stats being divided by a computed value.
    stat_name_map={"AP":"ap","공격력":"ap","DP":"dp","방어력":"dp","HP":"hp","체력":"hp","LP":"lp"}
    for m in re.finditer(r"(AP|DP|HP|LP|공격력|방어력|체력)\s*=\s*([^,;。]+)",t):
        rhs=m.group(2).strip()
        if not re.fullmatch(r"[★▲▼]?\s*[+-]?\d+",rhs):
            stat_token=m.group(1)
            ops.append({"kind":"set_stat_formula","stat":stat_name_map[stat_token],
                        "formulaText":rhs,"rawText":raw_text,"executable":False})
    if re.search(r"(?:나눈다|나눈다\.|나누어|나눠|나눔|곱한다|곱하여|곱해|곱한|차이만큼|수로\s*깎|수로\s*감소|깎는다|깍는다)",t):
        referenced_stats=_stat_refs(t)
        if referenced_stats:
            operation_kind=("divide_stat_by_expression" if re.search(r"나누|나눈|나눔",t)
                            else "multiply_or_scale_stat" if re.search(r"곱",t)
                            else "formula_based_stat_change")
            ops.append({"kind":operation_kind,"stats":_uniq(referenced_stats),
                        "formulaText":t,"rawText":raw_text,"executable":False})
    if re.search(r"(?:AP|DP|HP|공격력|방어력|체력).{0,35}(?:절반|반이 된다|반으로|짝수는)",t):
        referenced_stats=_stat_refs(t)
        ops.append({"kind":"halve_selected_stats","stats":_uniq(referenced_stats),
                    "selectionText":t,"rawText":raw_text,"executable":False})
    if re.search(r"(?:AP|DP|HP|공방체|공방|공체).{0,35}(?:깎|깍|감소|낮추|나누|절반|된다|바뀐다)",t):
        referenced_stats=[stat_name_map[x] for x in re.findall(
            r"AP|DP|HP|공격력|방어력|체력",t)]
        ops.append({"kind":"formula_based_combat_stat_rule","stats":_uniq(referenced_stats),
                    "formulaText":t,"rawText":raw_text,"executable":False})
    if re.search(r"지형.{0,30}(?:변화|바뀐다|변경|된다)",t):
        ops.append({"kind":"transform_terrain","formulaText":t,"rawText":raw_text,"executable":False})

    # Separate named state changes from numeric operations. These are still candidates
    # until a rule is independently verified.
    named_states=re.findall(
        r"한파|행동불능|영혼지배|마비|빙결|기절|침묵|혼란|중독|독|화상|공포|실명|구속|봉인|저주|출혈",t)
    if named_states and re.search(r"상태|걸린다|된다|부여|적용|해제|제거|면역|무효",t):
        ops.append({"kind":"apply_or_change_named_status","statusTerms":_uniq(named_states),
                    "rawText":raw_text,"executable":False})

    # A colon-prefixed label is often a split skill/effect heading, not a reference.
    # Record the label and body as an effect definition when the body contains an
    # action phrase, rather than classifying the whole clause as an opaque reference.
    if not ops and re.search(r"[:：].{1,}",t):
        label, body = re.split(r"[:：]",t,maxsplit=1)
        label=label.strip(); body=body.strip()
        label_is_condition=bool(re.search(
            r"(?:레벨|턴|킬|랭크|장|개|소울|코인|점수|포인트|수치|경우|이상|이하|초과|미만)",label))
        if body:
            body_result=parse(body,known_skills,known_cards)
            if body_result["confidence"]!="low":
                ops.append({"kind":"labeled_effect_definition","label":label,
                            "bodyText":body,"derivedOperations":body_result["operations"],
                            "executable":False})
                triggers.extend(x for x in body_result.get("triggers",[]) if x not in triggers)
                actors.extend(x for x in body_result.get("actors",[]) if x not in actors)
                targets.extend(x for x in body_result.get("targets",[]) if x not in targets)
                conditions.extend(x for x in body_result.get("conditions",[]) if x not in conditions)
            elif label_is_condition:
                ops.append({"kind":"conditional_branch_reference","conditionText":label,
                            "branchValue":body,"executable":False})
            else:
                body_actions=[key for key,pat in action_patterns if re.search(pat,body)]
                if body_actions:
                    ops.append({"kind":"labeled_effect_definition","label":label,
                                "bodyText":body,"actionCandidates":body_actions,"executable":False})

    # Legacy compact formulas and shorthand found in the low-confidence review queue.
    # Keep every derived operation explicitly non-executable until independently tested.
    for m in re.finditer(r"\b(AP|DP|HP)\s*(?:[xX×])\s*(\d+(?:\.\d+)?)",t,re.I):
        stat=m.group(1).lower()
        if not any(x.get("kind")=="multiply_stat" and x.get("stat")==stat for x in ops):
            ops.append({"kind":"multiply_stat","stat":stat,"multiplier":float(m.group(2)),
                        "rawText":raw_text,"executable":False})
    if re.search(r"(?:카드이름수|이름수).{0,30}(?:공/체|공방체|공체).{0,20}(?:된다|변한다|정해진다)",t):
        ops.append({"kind":"set_combat_stats_from_expression","statGroup":["ap","hp"],
                    "expressionText":t,"rawText":raw_text,"executable":False})
    if re.search(r"(?:AP|DP|HP).{0,20}(?:와|및|,).{0,20}(?:AP|DP|HP).{0,25}(?:1로 변|1이 된다|1로 만든)",t,re.I):
        stats=[x.lower() for x in re.findall(r"AP|DP|HP",t,re.I)]
        ops.append({"kind":"set_multiple_stats_from_rule","stats":_uniq(stats),
                    "value":1,"expressionText":t,"rawText":raw_text,"executable":False})
    if "좌우대칭" in raw_text and "레벨" in raw_text:
        ops.append({"kind":"mirror_or_swap_card_levels","scopeText":t,
                    "rawText":raw_text,"executable":False})
    if re.search(r"(?:공격기술|방어기술|특수기술|기술).{0,25}(?:가진다|보유한다|얻는다)",t):
        ops.append({"kind":"grant_or_reference_skill","skillText":t,
                    "rawText":raw_text,"executable":False})
    if re.search(r"대미지|데미지|피해",t) and not any(x.get("kind")=="deal_damage" for x in ops):
        ops.append({"kind":"deal_damage","rawText":raw_text,"executable":False})
    if re.search(r"(?:취급된다|취급됩니다|로 취급)",t):
        ops.append({"kind":"card_category_treatment_rule","rawText":raw_text,"executable":False})
    if re.search(r"(?:없으면|없는 경우|없을 경우).{0,50}(?:발동 안|발동하지|효과가 없|아무런 효과)",t):
        ops.append({"kind":"effect_activation_requirement","conditionText":t,
                    "rawText":raw_text,"executable":False})

    # Card-to-card conditions and ranges are kept separately from effect operations.
    for pat in [
      r"\d+\s*(?:~|-|∼)\s*\d+\s*(?:레벨|턴|킬|장|개)",
      r"\d+\s*레벨\s*(?:이상|이하|초과|미만)",
      r"\d+\s*턴\s*(?:이상|이하|초과|미만|동안)",
      r"이하",r"이상",r"초과",r"미만",r"같으면",r"경우",r"조건",
      r"홀수|짝수",r"같은\s*(?:종족|소속|이름|속성)",r"차이만큼",
      r"최고|최저|절반|올림|내림",r"행동가능한",r"다음\s*위치"
    ]:
        if re.search(pat,t): conditions.append(pat)
    nums=re.findall(r"(?<!\d)[+-]?\d+(?:\.\d+)?%?",t)
    ops=_uniq([json.dumps(x,ensure_ascii=False,sort_keys=True) for x in ops])
    ops=[json.loads(x) for x in ops]

    if not ops and re.search(
        r"(?:FAQ\s*검색|구입에\s*오류|카드상점에서|상시구매|판매됩니다|정기점검|수정될\s*예정|수정되었습니다|불편을\s*드려|이벤트\s*카드입니다|카드는.{0,35}받을\s*수|종족은.{0,35}표시|카드의\s*종류는|유닛의\s*이름은|이름은\s*\d+글자|카드\s*버그|툴팁.{0,20}수정|디스히어로(?:카드)?(?:\s*\[[^]]*\])?|운명의퍼즐)",
        t,re.I):
        classification="reference_or_metadata"; confidence="not_applicable"
        ops=[{"kind":"source_note_or_card_metadata","rawText":raw_text,"executable":False}]
    if not ops:
        if re.match(r"^\s*(?:invalid$|▶|※|★|☆|illustrated|해당 카드는|카드타입)",t,re.I):
            classification="reference_or_flavor"; confidence="not_applicable"
            ops=[{"kind":"source_note","rawText":raw_text}]
        elif re.match(r"^\s*(?:상성유닛|상성아이템|상성카드)\s*[:：]",t):
            classification="card_reference_list"; confidence="not_applicable"
            ops=[{"kind":"related_card_reference","rawText":raw_text}]
        elif re.match(r"^\s*\[[^\]]{2,}\]\s*$",t):
            classification="flavor_or_lore"; confidence="not_applicable"
            ops=[{"kind":"flavor_text","rawText":raw_text}]
        elif re.match(r"^\s*(?:성장목록|성장유닛|변경되는 유닛 리스트|상성효과|오오라 능력)\s*$",t):
            classification="section_heading"; confidence="not_applicable"
            ops=[{"kind":"section_heading","rawText":raw_text}]
        elif re.search(r"[:：].{1,}",t) or re.search(r"(?:레벨|턴|킬|핸드카드|유닛수|필드 카드수).*(?:이상|이하|:)",t):
            classification="conditional_or_reference_candidate"; confidence="low"
            ops=[{"kind":"conditional_rule_candidate","rawText":raw_text}]
        else:
            classification="unparsed_effect_text"; confidence="low"
            ops=[{"kind":"unparsed_operation","rawText":raw_text}]
    else:
        classification="effect_candidate"; confidence="medium"
    return {"classification":classification,"triggers":triggers,"actors":actors,
            "targets":targets,"conditions":conditions,"operations":ops,
            "numbers":nums,"rawText":raw_text,"flavorText":flavor_text,
            "mechanicText":t,"inferenceMethod":"keyword_pattern_v4",
            "confidence":confidence}

def main(path="data/fm1_cards.sqlite"):
    db=sqlite3.connect(path); db.execute("PRAGMA foreign_keys=ON")
    db.executescript("""
    CREATE TABLE IF NOT EXISTS card_effect_interpretations(
      clause_id INTEGER PRIMARY KEY REFERENCES card_effect_clauses(clause_id),
      card_id TEXT NOT NULL REFERENCES cards(card_id),
      source_detail_url TEXT,
      source_text TEXT NOT NULL,
      interpretation_json TEXT NOT NULL,
      verification_status TEXT NOT NULL,
      confidence TEXT NOT NULL,
      inference_method TEXT NOT NULL
    );
    CREATE INDEX IF NOT EXISTS idx_effect_interpretations_card ON card_effect_interpretations(card_id);
    """)
    db.execute("DELETE FROM card_effect_interpretations")
    db.executescript("""
    CREATE TABLE IF NOT EXISTS card_named_effect_definitions(
      definition_id INTEGER PRIMARY KEY,
      source_card_id TEXT NOT NULL REFERENCES cards(card_id),
      source_card_name TEXT NOT NULL,
      source_field TEXT NOT NULL,
      marker TEXT NOT NULL,
      effect_name TEXT NOT NULL,
      definition_text TEXT NOT NULL,
      source_text_sha256 TEXT NOT NULL,
      extraction_method TEXT NOT NULL,
      verification_status TEXT NOT NULL,
      UNIQUE(source_card_id,source_field,marker,effect_name,definition_text)
    );
    CREATE INDEX IF NOT EXISTS idx_named_effect_definitions_name
      ON card_named_effect_definitions(effect_name,marker);
    """)
    db.execute("DELETE FROM card_named_effect_definitions")
    definition_rows=[]
    for cid,card_name,raw in db.execute("""SELECT f.card_id,c.name,f.source_value_json
        FROM card_fields f JOIN cards c USING(card_id)
        WHERE f.field_key='TextExtra' AND f.source_value_json IS NOT NULL"""):
        for definition in extract_named_effect_definitions(cid,card_name,raw):
            definition_rows.append((definition["source_card_id"],definition["source_card_name"],
                definition["source_field"],definition["marker"],definition["effect_name"],
                definition["definition_text"],definition["source_text_sha256"],
                definition["extraction_method"],definition["verification_status"]))
    if definition_rows:
        db.executemany("""INSERT OR IGNORE INTO card_named_effect_definitions
          (source_card_id,source_card_name,source_field,marker,effect_name,definition_text,
           source_text_sha256,extraction_method,verification_status)
          VALUES(?,?,?,?,?,?,?,?,?)""",definition_rows)
    known_named_effects={}
    known_named_effect_fragments={}
    for row in db.execute("""SELECT definition_id,source_card_id,source_card_name,marker,effect_name,definition_text
        FROM card_named_effect_definitions"""):
        item={"definition_id":row[0],"source_card_id":row[1],"source_card_name":row[2],
              "marker":row[3],"effect_name":row[4],"definition_text":row[5]}
        key=normalize_effect_name(item["effect_name"])
        if item["marker"] in ("▶","★","※") and len(key)>=4 and not key.startswith("유닛"):
            known_named_effects.setdefault(key,[]).append(item)
        for fragment in item["definition_text"].splitlines():
            fragment_key=normalize_effect_name(fragment)
            if len(fragment_key)>=8:
                known_named_effect_fragments.setdefault(fragment_key,[]).append(item)
    known_skills={}
    known_cards={}
    for cid,card_name in db.execute("SELECT card_id,name FROM cards WHERE name IS NOT NULL"):
        key="".join(str(card_name).split())
        if key: known_cards.setdefault(key,[]).append(str(cid))
    for rid,canonical,aliases_json in db.execute("SELECT rule_id,canonical_name,aliases_json FROM game_rule_catalog"):
        for label in [canonical]+(json.loads(aliases_json or "[]")):
            known_skills["".join(str(label).split())]=rid
    for field,name,rid in db.execute("SELECT source_field,source_name,rule_id FROM skill_enum_inventory WHERE rule_id IS NOT NULL"):
        known_skills["".join(str(name).split())]=rid
    rows=db.execute("""SELECT cl.clause_id,cl.card_id,cl.segment_text,cl.segment_type,c.source_card_url
      FROM card_effect_clauses cl JOIN cards c ON c.card_id=cl.card_id
      ORDER BY cl.card_id,cl.clause_index""").fetchall()
    counts={}
    with db:
      for clause_id,cid,text,segtype,url in rows:
        parsed=parse(text,known_skills,known_cards,known_named_effects,known_named_effect_fragments)
        status=("not_applicable" if segtype=="separator" or parsed["classification"] in
                ("reference_or_flavor","reference_or_metadata","card_reference_list","card_name_reference","card_stat_profile_reference","unit_ability_profile_reference","section_heading","state_condition_target_reference","flavor_or_lore","named_status_reference","named_effect_reference","named_effect_definition","named_effect_definition_body","administrative_or_shop_note","punctuation_artifact","parenthetical_reference_note","parenthetical_rule_note","no_effect_marker","trigger_timing_metadata","ability_type_metadata","equip_condition_metadata","card_type_metadata","example_or_reference","source_placeholder")
                else "linked_rule_reference" if parsed["classification"]=="ability_name_reference" else "inferred")
        db.execute("""INSERT INTO card_effect_interpretations VALUES(?,?,?,?,?,?,?,?)""",
          (clause_id,cid,url,text,json.dumps(parsed,ensure_ascii=False,sort_keys=True),status,
           parsed["confidence"],parsed["inferenceMethod"]))
        counts[status]=counts.get(status,0)+1
    total=db.execute("SELECT COUNT(*) FROM card_effect_interpretations").fetchone()[0]
    missing=db.execute("""SELECT COUNT(*) FROM card_effect_clauses cl LEFT JOIN card_effect_interpretations i USING(clause_id) WHERE i.clause_id IS NULL""").fetchone()[0]
    fk=len(db.execute("PRAGMA foreign_key_check").fetchall())
    low=db.execute("SELECT COUNT(*) FROM card_effect_interpretations WHERE confidence='low'").fetchone()[0]
    low_by_class=db.execute("""
      SELECT COALESCE(json_extract(interpretation_json,'$.classification'),'unknown') AS classification,
             COUNT(*) AS n,COUNT(DISTINCT source_text) AS distinct_texts
      FROM card_effect_interpretations
      WHERE confidence='low'
      GROUP BY classification ORDER BY n DESC
    """).fetchall()
    low_examples=db.execute("""
      SELECT i.source_text,COUNT(*) AS card_count,MIN(i.card_id) AS example_card_id,
             MIN(i.source_detail_url) AS example_url,
             json_extract(MIN(i.interpretation_json),'$.classification') AS classification
      FROM card_effect_interpretations i
      WHERE i.confidence='low' AND length(trim(i.source_text))>0
      GROUP BY i.source_text ORDER BY card_count DESC,i.source_text LIMIT 120
    """).fetchall()
    result={"sourceClauses":len(rows),"interpretationRows":total,"statusCounts":counts,
            "namedEffectDefinitionRows":db.execute("SELECT COUNT(*) FROM card_named_effect_definitions").fetchone()[0],
            "namedEffectDefinitionNames":db.execute("SELECT COUNT(DISTINCT effect_name) FROM card_named_effect_definitions").fetchone()[0],
            "namedEffectReferenceRows":db.execute("SELECT COUNT(*) FROM card_effect_interpretations WHERE json_extract(interpretation_json,'$.classification')='named_effect_reference'").fetchone()[0],
            "lowConfidenceRows":low,"missingInterpretations":missing,"foreignKeyErrors":fk,
            "lowConfidenceByClassification":[{"classification":x[0],"count":x[1],"distinctTexts":x[2]} for x in low_by_class],
            "lowConfidenceDistinctTexts":db.execute(
              "SELECT COUNT(DISTINCT source_text) FROM card_effect_interpretations WHERE confidence='low'"
            ).fetchone()[0],
            "lowConfidenceSamples":[{"text":x[0],"cardCount":x[1],"cardId":x[2],
                                     "url":x[3],"classification":x[4]} for x in low_examples]}
    print(json.dumps(result,ensure_ascii=False,indent=2)); db.close()
    if missing or fk or total!=len(rows): sys.exit(2)

if __name__=="__main__": main(sys.argv[1] if len(sys.argv)>1 else "data/fm1_cards.sqlite")
