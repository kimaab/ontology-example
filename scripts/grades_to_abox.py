import csv
from pathlib import Path
from common import HR, HRD, add_individual, new_graph, save

BASE = Path(__file__).resolve().parent.parent      # Chapter1 폴더
SRC  = BASE / "data" / "erp" / "grades.csv"


with open(SRC, encoding="utf-8-sig", newline="") as f:
    g = new_graph()
    for row in csv.DictReader(f):
        add_individual(g, HRD[row["grade_code"]], HR.Grade, row["grade_name"])

    save(g, "grades.ttl")