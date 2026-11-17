import json
import re

from common import HR, HRD, REG, WORK, add_individual, new_graph, save

# 문서 파일 → 개체 ID에 쓸 영어 이름 (경조사 때처럼 직접 정함)
DOC_IDS = {
    "취업규칙_휴가편.md": "WorkRules",
    "복리후생규정.md": "WelfareRules",
    "교육훈련규정.md": "TrainingRules",
}

# 제목 줄의 모양
ARTICLE = re.compile(r"^## 제(\d+)조(?:의(\d+))?\((.+)\)\s*$")   # ## 제20조(연차유급휴가)
ANNEX = re.compile(r"^## \[별표 (\d+)\]\s*(.+?)\s*$")             # ## [별표 2] 경조사휴가 …

chunks = []

for file_name, doc_id in DOC_IDS.items():
    lines = (REG / file_name).read_text(encoding="utf-8").splitlines()
    doc_name = lines[0].lstrip("# ").split(" (")[0]    # "# 취업규칙 (제4장 휴가)" → "취업규칙"
    current = None

    for line in lines[1:]:
        article = ARTICLE.match(line)
        annex = ANNEX.match(line)

        if article:
            no, sub, title = article.groups()
            num = f"{no}_{sub}" if sub else no
            current = {
                "id": f"Rule_{doc_id}_Art{num}",
                "label": f"{doc_name} 제{no}조" + (f"의{sub}" if sub else ""),
                "title": title,
                "file": file_name,
                "lines": [],
            }
            chunks.append(current)
        elif annex:
            no, title = annex.groups()
            current = {
                "id": f"Rule_{doc_id}_Annex{no}",
                "label": f"{doc_name} 별표 {no}",
                "title": title,
                "file": file_name,
                "lines": [],
            }
            chunks.append(current)
        elif current is not None and line.strip() != "---":
            current["lines"].append(line)

# 줄 목록을 본문 하나로 합치기
for c in chunks:
    c["text"] = "\n".join(c.pop("lines")).strip()

# 출력 1: 중간 결과 (3단계 LLM 입력)
WORK.mkdir(parents=True, exist_ok=True)
out_json = WORK / "articles.json"
out_json.write_text(json.dumps(chunks, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"{len(chunks)} articles -> {out_json}")

# 출력 2: 근거 규정 개체
g = new_graph()
for c in chunks:
    add_individual(g, HRD[c["id"]], HR.Regulation, c["label"])
save(g, "regulations.ttl")