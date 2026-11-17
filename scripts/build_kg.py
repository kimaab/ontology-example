from rdflib import Graph, URIRef
from rdflib.namespace import RDF

from common import ABOX, BASE, HR, HRD

KG = BASE / "kg" / "hr_kg.ttl"

g = Graph()
g.bind("hr", HR)
g.bind("hrd", HRD)

g.parse(BASE / "hr_tbox.ttl")
print(f"{len(g):5} triples  hr_tbox.ttl")

for path in sorted(ABOX.glob("*.ttl")):
    before = len(g)
    g.parse(path)
    print(f"{len(g) - before:5} triples  abox/{path.name}")

# 끊긴 연결: hrd 개체를 가리키는데, 그 개체의 타입이 어디에도 없음
typed = set(g.subjects(RDF.type, None))
dangling = {o for o in g.objects() if isinstance(o, URIRef) and o.startswith(str(HRD)) and o not in typed}
if dangling:
    raise ValueError(f"끊긴 연결 {len(dangling)}개: {sorted(dangling)}")

KG.parent.mkdir(parents=True, exist_ok=True)
g.serialize(destination=KG, format="turtle", encoding="utf-8")
print(f"{len(g):5} triples  -> {KG}")