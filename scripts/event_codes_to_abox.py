from common import HR, HRD, add_individual, new_graph, read_csv, save

# 경조사 이름 → 개체 ID (CSV에 "결혼" 단위 코드가 없어서 직접 정함)
EVENT_IDS = {"결혼": "Marriage", "출산": "Birth", "사망": "Death"}

g = new_graph()
done = set()

for row in read_csv("event_codes.csv"):
    # event_category(경사/조사): T-Box에 속성이 없어 사용하지 않음
    # relation(본인/자녀 등): 보류 항목(대상자 관계)에서 다룰 예정
    name = row["event_name"]
    if name in done:
        continue
    if name not in EVENT_IDS:
        raise ValueError(f"{row['event_code']}: ID가 정해지지 않은 경조사 {name}")

    add_individual(g, HRD[EVENT_IDS[name]], HR.FamilyEvent, name)
    done.add(name)

save(g, "event_codes.ttl")