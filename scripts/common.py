import csv
from pathlib import Path

from rdflib import Graph, Literal, Namespace
from rdflib.namespace import OWL, RDF, RDFS

BASE = Path(__file__).resolve().parent.parent      # Chapter1 폴더
ERP = BASE / "data" / "erp"                        # 입력 CSV 폴더
ABOX = BASE / "abox"                               # 출력 TTL 폴더
REG = BASE / "data" / "regulations"                # 입력 규정 문서 폴더   ← 추가
WORK = BASE / "work"                               # 중간 결과 폴더        ← 추가

HR = Namespace("https://ai.knoc.co.kr/ai/hr#")       # T-Box 용어
HRD = Namespace("https://ai.knoc.co.kr/ai/hr/id/")    # A-Box 개체


def new_graph():
    g = Graph()
    g.bind("hr", HR)
    g.bind("hrd", HRD)
    return g

def read_csv(name):
    # CSV 파일 경로 생성
    file_path = ERP / name

    # CSV 파일 열기
    with open(file_path, encoding="utf-8-sig", newline="") as f:

        # CSV 파일 읽기 객체 생성
        reader = csv.DictReader(f)

        # CSV 데이터를 저장할 리스트
        result = []

        # 각 행을 반복
        for row in reader:

            # 각 컬럼의 값을 가져와 공백 제거
            data = {}

            for key, value in row.items():
                if value is None:
                    value = ""

                data[key] = value.strip()

            # 변환된 행을 리스트에 추가
            result.append(data)

        # 전체 데이터 반환
        return result


def add_individual(g, s, cls, label):
    g.add((s, RDF.type, cls))
    g.add((s, RDF.type, OWL.NamedIndividual))
    g.add((s, RDFS.label, Literal(label, lang="ko")))


def save(g, name):
    ABOX.mkdir(parents=True, exist_ok=True)
    out = ABOX / name
    g.serialize(destination=out, format="turtle", encoding="utf-8")
    print(f"{len(g)} triples -> {out}")