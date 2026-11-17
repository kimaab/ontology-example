import json
import sys

from langchain_core.messages import HumanMessage, SystemMessage

from common import WORK, read_csv
from extraction_schema import Extraction
from llm_client import make_llm

SYSTEM_PROMPT = """너는 회사 규정 조항에서 복지혜택의 부여 조건을 뽑아 양식에 채우는 도구다.

규칙:
1. 조항에 적힌 내용만 쓴다. 적혀 있지 않은 값은 추측하지 않는다.
2. target_benefit은 주어진 혜택 ID 목록에서만 고른다.
3. quote와 quotes는 조항 본문의 문장을 글자 하나 바꾸지 않고 그대로 복사한다. 항 번호 기호(①, ② 등)는 넣지 않는다.
4. 근속에 따라 일정하게 늘어나는 규칙은 step_rules에 숫자만 넣는다. 구간을 직접 펼치지 않는다.
5. 근속연수 구간과 값 하나로 표현할 수 없는 조건은 conditions나 step_rules에 넣지 말고, unsupported에 원문과 이유를 쓴다.
6. 숫자에는 쉼표를 쓰지 않는다.
7. 공식의 기본값을 정한 문장은 step_rules에 반영하고, conditions에 따로 넣지 않는다. 기본값 문장에 기간 표현(예: "N년간")이 있으면 그 기간을 최소 근속연수로 본다.
8. 한 문장의 일부만 양식으로 표현할 수 있으면, 표현할 수 있는 부분은 양식에, 나머지 조건은 unsupported에 나눠 넣는다.
9. 같은 혜택에 대한 근속 구간끼리 겹치지 않게 한다."""

article_id = sys.argv[1] if len(sys.argv) > 1 else "Rule_WorkRules_Art20"

articles = {a["id"]: a for a in json.loads((WORK / "articles.json").read_text(encoding="utf-8"))}
article = articles[article_id]

benefit_list = "\n".join(f"- {r['leave_code']}: {r['leave_name']}" for r in read_csv("leave_types.csv"))

user_prompt = f"""혜택 ID 목록:
{benefit_list}

조항: {article['label']}({article['title']})
본문:
{article['text']}"""

llm = make_llm().with_structured_output(Extraction, method="json_schema")
print(f"system message {SystemMessage(SYSTEM_PROMPT)}" )
print(f"human message {HumanMessage(user_prompt)}" )
result = llm.invoke([SystemMessage(SYSTEM_PROMPT), HumanMessage(user_prompt)])

out = WORK / "extracted" / f"{article_id}.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(result.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
print(f"conditions {len(result.conditions)}, step_rules {len(result.step_rules)}, "
      f"unsupported {len(result.unsupported)} -> {out}")