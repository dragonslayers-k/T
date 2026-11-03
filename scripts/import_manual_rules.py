#!/usr/bin/env python3
"""Import source-versioned manual/community unit-skill rules into the normalized card DB.

The source card fields remain unchanged. This adds evidence-backed mappings and
keeps community-only observations non-executable until implemented and tested.
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import unicodedata
from collections import Counter
from pathlib import Path


def norm(value: str) -> str:
    return "".join(unicodedata.normalize("NFKC", str(value or "")).split())


def load_catalog(path: Path) -> dict:
    data=json.loads(path.read_text(encoding="utf-8"))
    if data.get("schemaVersion") != 1:
        raise ValueError("Unsupported skill catalogue schemaVersion")
    rules=data.get("manualRules",[])+data.get("communityCandidates",[])
    ids=set()
    aliases={}
    for rule in rules:
        rid=rule.get("id")
        if not rid or rid in ids:
            raise ValueError(f"Missing or duplicate rule id: {rid}")
        ids.add(rid)
        if rule.get("authority") not in ("manual","community"):
            raise ValueError(f"Invalid authority on {rid}")
        if rule.get("authority")=="manual" and rule.get("verificationStatus")!="manual_verified":
            raise ValueError(f"Manual rule must retain manual_verified status: {rid}")
        if rule.get("authority")=="community" and rule.get("playableByDefault") is not False:
            raise ValueError(f"Community-only rule must not be playable by default: {rid}")
        for alias in [rule.get("name","")]+list(rule.get("aliases",[])):
            key=norm(alias)
            if not key:
                continue
            prev=aliases.get(key)
            if prev and prev["id"]!=rid:
                raise ValueError(f"Skill alias collision {alias!r}: {prev['id']} vs {rid}")
            aliases[key]=rule
    return {"data":data,"rules":rules,"aliases":aliases}


def create_schema(db: sqlite3.Connection) -> None:
    db.executescript("""
    CREATE TABLE IF NOT EXISTS game_rule_catalog (
        rule_id TEXT PRIMARY KEY,
        rule_family TEXT NOT NULL,
        canonical_name TEXT NOT NULL,
        aliases_json TEXT NOT NULL,
        definition_json TEXT NOT NULL,
        source_authority TEXT NOT NULL,
        confidence TEXT NOT NULL,
        verification_status TEXT NOT NULL,
        implementation_status TEXT NOT NULL,
        source_references_json TEXT NOT NULL,
        source_conflicts_json TEXT NOT NULL,
        playable_by_default INTEGER NOT NULL DEFAULT 0,
        catalogue_version INTEGER NOT NULL
    );
    CREATE TABLE IF NOT EXISTS card_rule_mappings (
        card_id TEXT NOT NULL REFERENCES cards(card_id),
        source_field TEXT NOT NULL,
        source_enum_value TEXT NOT NULL,
        source_name TEXT NOT NULL,
        rule_id TEXT REFERENCES game_rule_catalog(rule_id),
        mapping_status TEXT NOT NULL,
        confidence TEXT NOT NULL,
        evidence_references_json TEXT NOT NULL,
        PRIMARY KEY(card_id, source_field)
    );
    CREATE INDEX IF NOT EXISTS idx_card_rule_mappings_rule ON card_rule_mappings(rule_id);
    CREATE INDEX IF NOT EXISTS idx_card_rule_mappings_status ON card_rule_mappings(mapping_status);
    CREATE TABLE IF NOT EXISTS skill_enum_inventory (
        source_field TEXT NOT NULL,
        source_enum_value TEXT NOT NULL,
        source_name TEXT NOT NULL,
        card_count INTEGER NOT NULL,
        mapped_card_count INTEGER NOT NULL,
        manual_verified_card_count INTEGER NOT NULL,
        community_candidate_card_count INTEGER NOT NULL,
        mapping_status TEXT NOT NULL,
        rule_id TEXT,
        PRIMARY KEY(source_field, source_enum_value, source_name)
    );
    """)
    # Migrate earlier experimental catalog schemas without replacing source tables.
    columns={r[1] for r in db.execute("PRAGMA table_info(game_rule_catalog)")}
    if "playable_by_default" not in columns:
        db.execute("ALTER TABLE game_rule_catalog ADD COLUMN playable_by_default INTEGER NOT NULL DEFAULT 0")


def import_rules(db: sqlite3.Connection, catalogue: dict) -> dict:
    create_schema(db)
    data=catalogue["data"]
    rules=catalogue["rules"]
    alias_map=catalogue["aliases"]
    source_refs=[]
    for rule in rules:
        source_refs.append(rule.get("source") or {})
        source_refs.extend(x.get("source") or {} for x in rule.get("sourceConflicts",[]))
    unique_refs=[]
    seen=set()
    for ref in source_refs:
        key=(ref.get("kind"),ref.get("url") or ref.get("dropboxUrl"),ref.get("member"),ref.get("section"),ref.get("publishedDate"))
        if key not in seen:
            seen.add(key)
            unique_refs.append(ref)

    with db:
        db.execute("DELETE FROM card_rule_mappings")
        db.execute("DELETE FROM skill_enum_inventory")
        db.execute("DELETE FROM game_rule_catalog")
        for rule in rules:
            source=rule.get("source") or {}
            refs=[source]
            refs.extend(x.get("source") or {} for x in rule.get("sourceConflicts",[]))
            db.execute("""
                INSERT INTO game_rule_catalog(
                    rule_id,rule_family,canonical_name,aliases_json,definition_json,
                    source_authority,confidence,verification_status,implementation_status,
                    source_references_json,source_conflicts_json,playable_by_default,catalogue_version
                ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,(
                rule["id"],rule["ruleFamily"],rule["name"],
                json.dumps(rule.get("aliases",[]),ensure_ascii=False,sort_keys=True),
                json.dumps(rule.get("ruleDefinition") or rule.get("definition") or rule.get("effect") or {},ensure_ascii=False,sort_keys=True),
                rule["authority"],rule["confidence"],rule["verificationStatus"],
                rule.get("implementationStatus","not_implemented"),
                json.dumps(refs,ensure_ascii=False,sort_keys=True),
                json.dumps(rule.get("sourceConflicts",[]),ensure_ascii=False,sort_keys=True),
                int(rule.get("playableByDefault",False)),int(data["schemaVersion"])
            ))

        source_rows=db.execute("""
            SELECT card_id,field_key,COALESCE(source_value_json,''),COALESCE(normalized_value,'')
            FROM card_fields
            WHERE field_key IN ('Skill1','Skill2')
            ORDER BY card_id,field_id
        """).fetchall()
        # One normalized source field per card/Skill1 or card/Skill2. If the raw
        # source repeats a field, preserve only the final normalized source row.
        by_card={}
        for card_id,field,enum_value,name in source_rows:
            by_card[(card_id,field)]=(enum_value,name)
        inventory=Counter()
        mapped=Counter()
        manual=Counter()
        community=Counter()
        for (card_id,field),(enum_value,name) in by_card.items():
            if name in ("", "없음") or enum_value in ("", "0", "1") and name=="없음":
                status="no_special_skill"
                rule=None
                refs=[]
                confidence="source_enum"
            else:
                rule=alias_map.get(norm(name))
                if rule:
                    status="manual_verified" if rule["authority"]=="manual" else "community_documented_candidate"
                    refs=[rule.get("source") or {}]
                    confidence=rule.get("confidence","medium")
                    mapped[(field,name,enum_value)]+=1
                    if status=="manual_verified":
                        manual[(field,name,enum_value)]+=1
                    else:
                        community[(field,name,enum_value)]+=1
                else:
                    status="unmapped"
                    rule=None
                    refs=[]
                    confidence="unreviewed"
            rid=rule["id"] if rule else None
            db.execute("""
                INSERT INTO card_rule_mappings(
                    card_id,source_field,source_enum_value,source_name,rule_id,
                    mapping_status,confidence,evidence_references_json
                ) VALUES(?,?,?,?,?,?,?,?)
            """,(
                card_id,field,enum_value,name,rid,status,confidence,
                json.dumps(refs,ensure_ascii=False,sort_keys=True)
            ))
            inventory[(field,enum_value,name)]+=1

        for (field,enum_value,name),n in inventory.items():
            mapped_n=mapped[(field,name,enum_value)]
            manual_n=manual[(field,name,enum_value)]
            community_n=community[(field,name,enum_value)]
            if name in ("", "없음"):
                status="no_special_skill"
                rid=None
            elif manual_n:
                status="manual_verified"
                rid=alias_map[norm(name)]["id"]
            elif community_n:
                status="community_documented_candidate"
                rid=alias_map[norm(name)]["id"]
            else:
                status="unmapped"
                rid=None
            db.execute("""
                INSERT INTO skill_enum_inventory(
                    source_field,source_enum_value,source_name,card_count,mapped_card_count,
                    manual_verified_card_count,community_candidate_card_count,mapping_status,rule_id
                ) VALUES(?,?,?,?,?,?,?,?,?)
            """,(field,enum_value,name,n,mapped_n,manual_n,community_n,status,rid))

    return {
        "catalogueVersion":data["schemaVersion"],
        "manualRuleCount":sum(r["authority"]=="manual" for r in rules),
        "communityCandidateRuleCount":sum(r["authority"]=="community" for r in rules),
        "mappedCardFieldRows":len(by_card),
        "manualVerifiedMappings":sum(manual.values()),
        "communityCandidateMappings":sum(community.values()),
        "unmappedCardFieldRows":sum(1 for (card_id,field),(enum_value,name) in by_card.items()
            if name not in ("","없음") and norm(name) not in alias_map),
        "inventoryRows":len(inventory),
        "playableCommunityCandidates":sum(int(r.get("playableByDefault",False)) for r in rules if r["authority"]=="community")
    }


def self_test(catalogue: dict) -> None:
    db=sqlite3.connect(":memory:")
    db.execute("PRAGMA foreign_keys=ON")
    db.executescript("""
        CREATE TABLE cards(card_id TEXT PRIMARY KEY);
        CREATE TABLE card_fields(
            field_id INTEGER PRIMARY KEY,card_id TEXT,field_key TEXT,
            source_value_json TEXT,normalized_value TEXT
        );
        INSERT INTO cards VALUES('unit-1'),('unit-2'),('unit-3');
        INSERT INTO card_fields VALUES
          (1,'unit-1','Skill1','243','방어무시'),
          (2,'unit-2','Skill1','82','기술봉쇄'),
          (3,'unit-3','Skill1','602','주문봉쇄'),
          (4,'unit-1','Skill2','1','없음');
    """)
    result=import_rules(db,catalogue)
    rows=db.execute("""
        SELECT source_name,rule_id,mapping_status FROM card_rule_mappings
        ORDER BY source_field,card_id
    """).fetchall()
    assert ("방어무시","defense_bypass","manual_verified") in rows
    assert ("기술봉쇄","ability_seal","manual_verified") in rows
    assert ("주문봉쇄","spell_suppression","manual_verified") in rows
    assert ("없음",None,"no_special_skill") in rows
    assert result["manualRuleCount"]==27
    assert result["playableCommunityCandidates"]==0
    assert db.execute("PRAGMA foreign_key_check").fetchall()==[]
    db.close()
    print("manual special-skill catalogue self-test passed")


def main() -> None:
    parser=argparse.ArgumentParser()
    parser.add_argument("--db",type=Path,default=Path("data/fm1_cards.sqlite"))
    parser.add_argument("--catalogue",type=Path,default=Path("data/rules/fm1-skill-catalog-v1.json"))
    parser.add_argument("--self-test",action="store_true")
    args=parser.parse_args()
    catalogue=load_catalog(args.catalogue)
    if args.self_test:
        self_test(catalogue)
        return
    db=sqlite3.connect(args.db)
    db.execute("PRAGMA foreign_keys=ON")
    try:
        result=import_rules(db,catalogue)
        result["foreignKeyErrors"]=len(db.execute("PRAGMA foreign_key_check").fetchall())
        print(json.dumps(result,ensure_ascii=False,sort_keys=True))
        if result["foreignKeyErrors"]:
            raise SystemExit("Manual rule import produced foreign-key errors")
    finally:
        db.close()


if __name__=="__main__":
    main()
