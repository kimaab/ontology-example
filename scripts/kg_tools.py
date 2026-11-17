from datetime import date
from functools import lru_cache

from rdflib import Graph, Literal

from common import BASE, HRD

PREFIXES = """
PREFIX hr:   <https://ai.knoc.co.kr/ai/hr#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
"""


@lru_cache(maxsize=1)
def load_graph():
    """지식그래프를 한 번만 읽고, 다음부터는 읽어 둔 것을 돌려준다"""
    return Graph().parse(BASE / "kg" / "hr_kg.ttl")


def to_number(value):
    """Decimal('16.0') → 16, Decimal('0.5') → 0.5"""
    return int(value) if value % 1 == 0 else float(value)


def tenure_years(hire_date, base_date):
    """만 근속연수: 올해 입사 기념일이 아직 안 지났으면 1을 뺀다"""
    years = base_date.year - hire_date.year
    if (base_date.month, base_date.day) < (hire_date.month, hire_date.day):
        years -= 1
    return years


def find_benefit_by_tenure(benefit_id, tenure):
    """근속연수에 맞는 부여 조건을 찾는다. 없으면 None"""
    query = PREFIXES + """
    SELECT ?gc ?label ?benefitName ?value ?unit ?regName
    WHERE {
      ?gc hr:hasTargetBenefit ?benefit ;
          rdfs:label ?label ;
          hr:minimumTenure ?min ;
          hr:benefitValue ?value ;
          hr:unit ?unit ;
          hr:hasRegulation ?reg .
      ?benefit rdfs:label ?benefitName .
      ?reg rdfs:label ?regName .
      OPTIONAL { ?gc hr:maximumTenure ?max }
      FILTER (?tenure >= ?min && (!BOUND(?max) || ?tenure < ?max))
    }
    """
    rows = list(load_graph().query(query, initBindings={
        "benefit": HRD[benefit_id], "tenure": Literal(tenure)}))
    if not rows:
        return None
    r = rows[0]
    return {
        "benefit": str(r.benefitName),
        "tenure": tenure,
        "value": to_number(r.value.toPython()),
        "unit": str(r.unit),
        "condition": str(r.label),
        "condition_id": r.gc.split("/")[-1],
        "regulation": str(r.regName),
    }


def find_employee(emp_no):
    """사번으로 직원의 이름, 입사일, 직급을 찾는다. 없으면 None"""
    query = PREFIXES + """
    SELECT ?name ?hire ?gradeName
    WHERE {
      ?emp a hr:Employee ;
           rdfs:label ?name ;
           hr:hireDate ?hire ;
           hr:hasGrade ?grade .
      ?grade rdfs:label ?gradeName .
    }
    """
    rows = list(load_graph().query(query, initBindings={"emp": HRD[emp_no]}))
    if not rows:
        return None
    r = rows[0]
    return {"emp_no": emp_no, "name": str(r.name),
            "hire_date": r.hire.toPython(), "grade": str(r.gradeName)}


def annual_leave_for_employee(emp_no, base_date):
    """직원 한 명의 연차휴가: 직원 찾기 → 근속 계산 → 부여 조건 찾기"""
    emp = find_employee(emp_no)
    if emp is None:
        return {"found": False, "reason": f"사번 {emp_no}인 직원이 그래프에 없음"}
    tenure = tenure_years(emp["hire_date"], base_date)
    leave = find_benefit_by_tenure("LV01", tenure)
    if leave is None:
        return {"found": False, "employee": emp, "tenure": tenure,
                "reason": f"근속 {tenure}년에 해당하는 연차휴가 부여 조건이 그래프에 없음"}
    return {"found": True, "employee": emp, "base_date": base_date, **leave}


if __name__ == "__main__":
    base = date(2026, 11, 16)
    for t in [3, 2, 21, 0]:
        print(f"근속 {t}년:", find_benefit_by_tenure("LV01", t))
    for e in ["E02007", "E02006", "E02001", "E09999"]:
        print(f"{e}:", annual_leave_for_employee(e, base))