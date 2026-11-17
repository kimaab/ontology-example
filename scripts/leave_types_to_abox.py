from common import HR, HRD, add_individual, new_graph, read_csv, save

g = new_graph()

# 혜택 종류 "휴가": CSV에는 없지만 모든 휴가 코드가 가리킬 대상이라 여기서 만든다
LEAVE = HRD["Leave"]
add_individual(g, LEAVE, HR.BenefitType, "휴가")

for row in read_csv("leave_types.csv"):
    # paid_yn: T-Box에 속성이 없어 사용하지 않음
    # basis: hasRegulation의 domain이 부여 조건이라 여기에 붙이지 않음 (부여 조건 단계에서 연결)
    s = HRD[row["leave_code"]]
    add_individual(g, s, HR.WelfareBenefit, row["leave_name"])
    g.add((s, HR.hasBenefitType, LEAVE))

save(g, "leave_types.ttl")