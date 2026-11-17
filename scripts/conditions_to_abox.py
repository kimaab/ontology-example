import json
from decimal import Decimal

from rdflib import Literal

from common import HR, HRD, WORK, add_individual, new_graph, read_csv, save

APPROVED = {"정답지와 같음", "승인"}     # 이 상태인 파일만 그래프에 넣는다

benefit_names = {r["leave_code"]: r["leave_name"] for r in read_csv("leave_types.csv")}

g = new_graph()
seen = set()

for path in sorted((WORK / "validated").glob("*.json")):
    data = json.loads(path.read_text(encoding="utf-8"))
    if data["review"] not in APPROVED:
        print(f"건너뜀 ({data['review']}): {path.name}")
        continue

    for c in data["conditions"]:
        lo, hi, target = c["min_tenure"], c["max_tenure"], c["target_benefit"]

        # ID: 같은 입력이면 항상 같은 ID가 나오게 값으로 만든다
        cid = f"GC_{target}_{lo}_{'plus' if hi is None else hi}"
        if cid in seen:
            raise ValueError(f"부여 조건 ID가 겹침: {cid} ({path.name})")
        seen.add(cid)

        # 라벨: "연차휴가 근속 3년 이상 5년 미만"
        label = f"{benefit_names[target]} 근속 {lo}년 이상" + ("" if hi is None else f" {hi}년 미만")

        s = HRD[cid]
        add_individual(g, s, HR.GrantCondition, label)
        g.add((s, HR.hasTargetBenefit, HRD[target]))
        if lo is not None:
            g.add((s, HR.minimumTenure, Literal(lo)))
        if hi is not None:
            g.add((s, HR.maximumTenure, Literal(hi)))
        g.add((s, HR.benefitValue, Literal(Decimal(str(c["value"])))))   # float → xsd:decimal
        g.add((s, HR.unit, Literal(c["unit"])))
        g.add((s, HR.hasRegulation, HRD[data["article_id"]]))

    if data["unsupported"]:
        print(f"참고: {path.name}에 표현하지 못한 내용 {len(data['unsupported'])}건 (그래프에 넣지 않음)")

save(g, "grant_conditions.ttl")