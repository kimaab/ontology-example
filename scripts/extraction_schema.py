import json
import sys
from pathlib import Path
from typing import Literal, Optional

from pydantic import BaseModel, Field


class Condition(BaseModel):
    """고정된 구간 하나: 이 근속 구간이면 이 값을 준다"""
    target_benefit: str = Field(description="대상 혜택 ID. 주어진 목록에서만 고른다")
    min_tenure: Optional[int] = Field(None, description="최소 근속연수(이상). 조건이 없으면 null")
    max_tenure: Optional[int] = Field(None, description="최대 근속연수(미만). 상한이 없으면 null")
    value: float = Field(description="혜택 값 (숫자만)")
    unit: Literal["일", "원", "%"]
    quote: str = Field(description="근거가 된 원문 문장을 조항에서 그대로 복사")


class StepRule(BaseModel):
    """근속에 따라 늘어나는 공식: 펼치기는 코드가 한다"""
    target_benefit: str = Field(description="대상 혜택 ID. 주어진 목록에서만 고른다")
    base_min_tenure: int = Field(description="기본값을 처음 받기 시작하는 최소 근속연수. 가산이 시작되기 전 구간도 포함하므로 step_start_tenure보다 작을 수 있다")
    base_value: float = Field(description="가산 전 기본값")
    step_start_tenure: int = Field(description="가산이 처음 적용되는 근속연수")
    step_years: int = Field(description="몇 년마다 가산하는지")
    step_value: float = Field(description="한 번에 가산하는 값")
    max_value: Optional[float] = Field(None, description="한도. 없으면 null")
    unit: Literal["일", "원", "%"]
    quotes: list[str] = Field(description="기본값, 가산, 한도의 근거가 된 원문 문장만 그대로 복사. 공식과 관계없는 문장은 넣지 않는다")


class Unsupported(BaseModel):
    """양식으로 표현할 수 없는 내용"""
    quote: str = Field(description="해당 원문 문장을 그대로 복사")
    reason: str = Field(description="표현할 수 없는 이유")


class Extraction(BaseModel):
    """조항 하나에서 뽑은 결과 전체"""
    conditions: list[Condition] = []
    step_rules: list[StepRule] = []
    unsupported: list[Unsupported] = []


# 정답지 파일이 양식에 맞는지 검사: python extraction_schema.py <파일>
if __name__ == "__main__":
    data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    result = Extraction.model_validate(data)
    print(f"OK: conditions {len(result.conditions)}, "
          f"step_rules {len(result.step_rules)}, unsupported {len(result.unsupported)}")