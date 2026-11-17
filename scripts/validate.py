import json
import sys

from common import WORK, read_csv
from extraction_schema import Extraction

MAX_STEPS = 50     # 공식을 펼칠 때 최대 반복 횟수 (무한 반복 방지)


def expand(rule):
    """공식(StepRule) 하나 → 구간 목록 [(최소 근속, 최대 근속, 값), ...]"""
    rows = []
    if rule.step_start_tenure > rule.base_min_tenure:
        rows.append((rule.base_min_tenure, rule.step_start_tenure, rule.base_value))
    tenure = rule.step_start_tenure
    value = rule.base_value + rule.step_value
    for _ in range(MAX_STEPS):
        if value >= rule.max_value:
            rows.append((tenure, None, rule.max_value))
            return rows
        rows.append((tenure, tenure + rule.step_years, value))
        tenure += rule.step_years
        value += rule.step_value
    raise ValueError(f"{MAX_STEPS}번을 넘게 늘어남: max_value를 확인하세요")


def to_intervals(extraction):
    """conditions + 펼친 step_rules → 같은 모양의 구간 목록"""
    out = []
    for c in extraction.conditions:
        out.append({"target_benefit": c.target_benefit, "min_tenure": c.min_tenure,
                    "max_tenure": c.max_tenure, "value": c.value, "unit": c.unit,
                    "quotes": [c.quote]})
    for r in extraction.step_rules:
        for lo, hi, v in expand(r):
            out.append({"target_benefit": r.target_benefit, "min_tenure": lo,
                        "max_tenure": hi, "value": v, "unit": r.unit, "quotes": r.quotes})
    return out


def key(i):
    """비교·정렬용: 비어 있는 최소는 -1, 비어 있는 최대는 9999로"""
    lo = -1 if i["min_tenure"] is None else i["min_tenure"]
    hi = 9999 if i["max_tenure"] is None else i["max_tenure"]
    return (i["target_benefit"], lo, hi, i["value"], i["unit"])


article_id = sys.argv[1] if len(sys.argv) > 1 else "Rule_WorkRules_Art20"

articles = {a["id"]: a for a in json.loads((WORK / "articles.json").read_text(encoding="utf-8"))}
text = articles[article_id]["text"]
extracted = Extraction.model_validate_json(
    (WORK / "extracted" / f"{article_id}.json").read_text(encoding="utf-8"))
benefit_ids = {r["leave_code"] for r in read_csv("leave_types.csv")}

errors = []

# 검사 1: 원문 인용이 조항 본문에 글자 그대로 있는가
quotes = ([c.quote for c in extracted.conditions]
          + [q for r in extracted.step_rules for q in r.quotes]
          + [u.quote for u in extracted.unsupported])
for q in quotes:
    if q not in text:
        errors.append(f"원문에 없는 인용: {q}")

# 검사 2: 대상 혜택 ID가 실제로 있는가
targets = [c.target_benefit for c in extracted.conditions] + [r.target_benefit for r in extracted.step_rules]
for t in targets:
    if t not in benefit_ids:
        errors.append(f"없는 혜택 ID: {t}")

# 검사 3: 값끼리 앞뒤가 맞는가
for c in extracted.conditions:
    if c.min_tenure is not None and c.max_tenure is not None and c.min_tenure >= c.max_tenure:
        errors.append(f"구간이 거꾸로임: {c.min_tenure} ~ {c.max_tenure}")
for r in extracted.step_rules:
    if r.base_min_tenure > r.step_start_tenure:
        errors.append(f"기본값 시작({r.base_min_tenure})이 가산 시작({r.step_start_tenure})보다 늦음")
    if r.step_years <= 0 or r.step_value <= 0:
        errors.append(f"가산 간격이나 가산 값이 0 이하: {r.step_years}년마다 {r.step_value}")
    if r.max_value is None:
        errors.append("한도(max_value)가 없는 공식: 끝없이 늘어남")

if not errors:
    # 검사 4: 공식을 펼친 뒤, 같은 혜택의 구간이 겹치는가
    intervals = sorted(to_intervals(extracted), key=key)
    for a, b in zip(intervals, intervals[1:]):
        if a["target_benefit"] == b["target_benefit"] and key(a)[2] > key(b)[1]:
            errors.append(f"구간 겹침: {a['min_tenure']}~{a['max_tenure']} 와 {b['min_tenure']}~{b['max_tenure']}")

if errors:
    print(f"검증 실패: {article_id}")
    for e in errors:
        print(" -", e)
    sys.exit(1)

# 정답지가 있으면 펼친 구간끼리 비교
expected_file = WORK / "expected" / f"{article_id}.json"
if expected_file.exists():
    expected = Extraction.model_validate_json(expected_file.read_text(encoding="utf-8"))
    same = [key(i) for i in intervals] == sorted(key(i) for i in to_intervals(expected))
    review = "정답지와 같음" if same else "정답지와 다름: 사람 검토 필요"
else:
    review = "정답지 없음: 사람 검토 필요"

out = WORK / "validated" / f"{article_id}.json"
out.parent.mkdir(parents=True, exist_ok=True)
result = {"article_id": article_id, "review": review, "conditions": intervals,
          "unsupported": [u.model_dump() for u in extracted.unsupported]}
out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"검증 통과 ({review}): 구간 {len(intervals)}개 -> {out}")