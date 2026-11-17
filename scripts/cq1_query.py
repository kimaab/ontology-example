import sys

from rdflib import Graph, Literal
from rdflib.namespace import XSD

from common import BASE

BASE_DATE = sys.argv[1] if len(sys.argv) > 1 else "2026-11-12"   # 근속을 계산하는 기준일

QUERY = """
PREFIX hr:   <https://ai.knoc.co.kr/ai/hr#>
PREFIX hrd:  <https://ai.knoc.co.kr/ai/hr/id/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?emp ?name ?hire ?tenure ?days ?regName
WHERE {
  ?emp a hr:Employee ;
       rdfs:label ?name ;
       hr:hireDate ?hire .

  BIND (YEAR(?today) - YEAR(?hire)
        - IF(MONTH(?today) < MONTH(?hire)
             || (MONTH(?today) = MONTH(?hire) && DAY(?today) < DAY(?hire)), 1, 0)
        AS ?tenure)

  OPTIONAL {
    ?gc hr:hasTargetBenefit hrd:LV01 ;
        hr:minimumTenure ?min ;
        hr:benefitValue ?days ;
        hr:hasRegulation ?reg .
    ?reg rdfs:label ?regName .
    OPTIONAL { ?gc hr:maximumTenure ?max }
    FILTER (?tenure >= ?min && (!BOUND(?max) || ?tenure < ?max))
  }
}
ORDER BY ?hire
"""

g = Graph().parse(BASE / "kg" / "hr_kg.ttl")
rows = g.query(QUERY, initBindings={"today": Literal(BASE_DATE, datatype=XSD.date)})

print(f"기준일 {BASE_DATE}")
for r in rows:
    days = "정보 없음" if r.days is None else f"{int(r.days.toPython())}일 ({r.regName})"
    print(f"{r.emp.split('/')[-1]}  {r.name}  입사 {r.hire}  근속 {r.tenure}년  →  연차 {days}")