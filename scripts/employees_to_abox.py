from datetime import date
from pathlib import Path

from rdflib import Graph, Literal
from common import HR, HRD, add_individual, new_graph, save, read_csv

BASE = Path(__file__).resolve().parent.parent      # Chapter1 폴더
SRC = BASE / "data" / "erp" / "employees.csv"
GRADES = BASE / "data" / "erp" / "grades.csv"      # 직급 코드 검사용 (읽기만 함)

valid_grades = {r["grade_code"] for r in read_csv("grades.csv")}

g = new_graph()


for row in read_csv("employees.csv"):
    emp_no = row["emp_no"].strip()
    hire = date.fromisoformat(row["hire_date"])

    if row["grade_code"] not in valid_grades:
        raise ValueError(f"{emp_no}: 없는 직급 코드 {row['grade_code']}")

    s = HRD[emp_no]
    add_individual(g, s, HR.Employee, row["emp_name"])
    g.add((s, HR.hireDate, Literal(hire)))  # 날짜 객체 → ^^xsd:date 자동
    g.add((s, HR.hasGrade, HRD[row["grade_code"]]))  # 다른 개체(IRI)를 가리킴

save(g,"employees.ttl")