from rdflib import Graph
from rdflib.namespace import OWL, RDF, RDFS

from common import ABOX, BASE

tbox = Graph().parse(BASE / "hr_tbox.ttl")
abox = Graph()
for path in sorted(ABOX.glob("*.ttl")):
    abox.parse(path)

for kind, owl_type in [("클래스", OWL.Class),
                       ("관계 속성", OWL.ObjectProperty),
                       ("값 속성", OWL.DatatypeProperty)]:
    print(f"[{kind}]")
    for term in sorted(tbox.subjects(RDF.type, owl_type)):
        if owl_type == OWL.Class:
            count = len(set(abox.subjects(RDF.type, term)))       # 이 클래스의 개체 수
        else:
            count = len(list(abox.triples((None, term, None))))  # 이 속성을 쓴 트리플 수
        mark = "OK  " if count else "없음"
        print(f"  {mark} {term.split('#')[-1]:24} {tbox.value(term, RDFS.label)} {count}")