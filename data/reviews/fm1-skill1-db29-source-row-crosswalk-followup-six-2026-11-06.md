# DB29 Skill1 source-row crosswalk — 후속 6개 규칙 (2026-11-06)

## 기준 및 범위
Immutable release `fm1-carddb-29`의 source-match report `13384922100`에 기반한 카드 ID/source label 연결표다. CardDB의 source-match 감사는 Unicode NFKC + 공백 제거 후 canonical Manual label 또는 명시 alias의 정확 일치로 27개 규칙 모두에서 3,158개 Skill1 행을 찾았으며, 이 결과는 카드별 효과 의미나 실행 승인을 뜻하지 않는다.

이번 crosswalk는 직전 APK assertion 감사 대상인 `vampiric_attack`, `aging_attack`, `beast_tamer`, `spell_suppression`, `weapon_suppression`, `ability_seal`만 범위로 한다.

## 원본 Skill1 label 및 대표 DB29 카드

| Rule ID | canonical Skill1 label | DB29 source rows | source-evidence sample card IDs | 의미 검토 상태 |
|---|---|---:|---|---|
| `vampiric_attack` | 흡혈공격 | 115 | `10010624542` 다크카운티스; `10010624549` 리빙블러드; `10012024607` 플레임뱀프 | APK test의 다크카운티스는 source ID와 일치. 원문 효과·marker 예외를 각 카드로 일반화하지 않음 |
| `aging_attack` | 노화공격 | 53 | `13020626691` 타락자; `14043027368` 좀비제작자; `14091727606` 좀비솔져 | APK test의 타락자는 source ID와 일치. 음수 AP 결과의 범위는 별도 |
| `beast_tamer` | 야수조련 | 63 | `11011925567` 네추럴마스터; `11070625790` 리틀페어리; `11090725878` 묘인족소녀 | 정확 Skill1 label/ID 존재. 앞선 aggregate assertion은 이 source-card mapping 자체를 테스트한 것은 아님 |
| `spell_suppression` | 주문봉쇄 | 56 | `10010624550` 혼드비스트; `11062225775` 냉기의정령; `11070625788` 심해의인어 | 원본 label은 ‘주문봉쇄’. 앞선 설명의 ‘마법봉쇄’는 source label로 사용하지 않음 |
| `weapon_suppression` | 무기봉쇄 | 48 | `10010624543` 데크라프; `10020324651` 포레스키퍼; `10040724792` 오우거워리어 | 원본 label은 ‘무기봉쇄’. ‘무기뺏기’와 동의어로 임의 처리 금지 |
| `ability_seal` | 기술봉쇄 | 203 | `10020324644` 환상낚시꾼; `10021724690` 시서펜트; `10030324717` 커시드아이 | source match에서는 정확 Skill1 label로 존재. APK alias 표준명 `봉쇄공격`과 매핑은 검증 가능하나, 기술봉쇄의 개별 효과 의미는 Manual/handler 대조 필요 |

## 정정 사항
- 직전 audit의 ‘마법/마법능력’, ‘장비/장비능력’은 aggregate test에서 사용한 target tag 설명이다. CardDB source label은 각각 **주문봉쇄**, **무기봉쇄**다. 테스트 fixture tag와 카드의 Skill1 label을 혼동하지 않는다.
- `ability_seal`의 exact source rows 203개는 Skill1 label `기술봉쇄`에 해당한다. APK 내부 alias `기술봉쇄` → `봉쇄공격`는 이름 정규화 증거지만, source label 행만으로 봉쇄 효과의 대상/지속/예외가 완전히 확인되는 것은 아니다.
- 기존 APK tests에서 대표 카드 ID가 source index와 일치하는 vampiric/aging 사례는 카드 식별 근거를 보강한다. 테스트 자체의 Manual assertion scope는 기존 audit에 적힌 범위로 한정한다.

## 후속 실행 작업
1. 각 대표 카드의 source record에 연결된 원문 URL 및 Skill1/Skill2 fields를 카드 단위로 대조한다.
2. APK aggregate fixture를 exact DB29 source-card fixture로 옮길 수 있는 규칙은, 원문이 deterministic expected outcome을 제공할 때에만 전용 positive/negative/boundary assertion을 작성한다.
3. Beast-tamer, 주문봉쇄, 무기봉쇄의 source-linked dedicated test gap을 우선 검토한다.
4. 기술봉쇄는 target selection, seal 대상 능력 타입, 지속/해제 조건을 원문에서 확보하기 전까지 non-executable로 둔다.

## 변경 보호
- 문서 crosswalk만 추가. APK source/tests는 변경하지 않음.
- DB29 불변, DB30 미발행, PR #9/#28 병합 금지.
- source-row count는 검증 완료량/런타임 실행 가능량으로 해석하지 않는다.
