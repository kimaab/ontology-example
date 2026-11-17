# 2단계: T-Box 초안 설명

파일: `02_tbox.ttl`

## 1. T-Box와 A-Box

온톨로지는 두 부분으로 나뉩니다.

| | T-Box (Terminology) | A-Box (Assertion) |
|---|---|---|
| 뜻 | **틀(스키마)**: 어떤 종류의 것이 있고, 서로 어떻게 연결될 수 있는가 | **실제 데이터**: 틀에 맞춰 채운 구체적인 사실 |
| 비유 | 엑셀의 **열 이름**, DB의 **테이블 정의** | 엑셀의 **행**, DB의 **레코드** |
| 예 | "위반행위는 범칙금액을 가진다" | "신호위반의 범칙금액은 60000이다" |

이번 단계에서는 T-Box만 만듭니다. A-Box는 4단계(데이터 변환)에서 자동으로 만들 예정입니다.

## 2. Turtle 문법 최소 지식

RDF는 모든 정보를 **3개짜리 문장(트리플)**으로 표현합니다.

```
주어        술어          목적어 .
law:Violation  a  owl:Class .     →  "Violation은 클래스다"
```

- `a`는 `rdf:type`의 줄임말이고, "~의 한 종류다 / ~이다"라는 뜻입니다.
- `;`는 **주어가 같은 문장을 이어 쓸 때** 씁니다. 아래 두 표기는 같은 뜻입니다.
  ```
  law:Violation a owl:Class ;
      rdfs:label "위반행위"@ko .

  law:Violation a owl:Class .
  law:Violation rdfs:label "위반행위"@ko .
  ```
- 문장 끝은 `.`입니다.
- `"위반행위"@ko`의 `@ko`는 한국어 글자라는 표시입니다.
- `law:Violation`은 `<https://example.org/law#Violation>`의 줄임말입니다. 맨 위 `@prefix`에서 별명을 정했습니다.
- `#` 뒤는 주석입니다.

## 3. 주로 쓴 어휘

| 어휘 | 뜻 |
|---|---|
| `owl:Class` | 클래스 (개체들의 종류) |
| `owl:ObjectProperty` | 개체 → **개체**를 잇는 관계 |
| `owl:DatatypeProperty` | 개체 → **값**(숫자, 문자열, 참/거짓)을 잇는 속성 |
| `rdfs:label` | 사람이 읽는 이름 |
| `rdfs:comment` | 사람이 읽는 설명 |
| `rdfs:domain` | 이 속성의 **주어**가 될 수 있는 클래스 |
| `rdfs:range` | 이 속성의 **목적어**가 될 수 있는 클래스나 값 타입 |

domain과 range를 예로 보겠습니다.

```
law:memberOf  rdfs:domain law:Violation ;       # 주어는 위반행위
              rdfs:range  law:ViolationGroup .  # 목적어는 위반행위 그룹

law:신호위반  law:memberOf  law:12대중과실 .      # 올바른 사용
```

> **주의:** RDFS의 domain과 range는 "틀리면 에러"를 내는 규칙이 아니라 **추론 규칙**입니다.
> `law:X law:memberOf law:Y` 라고 쓰면, 추론기는 "X는 Violation이고 Y는 ViolationGroup이구나" 하고
> **새 사실을 추가**합니다. 값이 틀렸는지 검사하려면 나중에 SHACL이라는 별도 도구를 씁니다.

## 4. 클래스 5개

| 클래스 | 이름 | 왜 필요한가 |
|---|---|---|
| `law:Violation` | 위반행위 | 모든 질문의 중심. 신호위반, 음주운전 등 |
| `law:ViolationGroup` | 위반행위 그룹 | "12대 중과실" 같은 묶음 (CQ3, CQ5) |
| `law:Article` | 조문 | 답변의 근거 (CQ2) |
| `law:AdministrativeAction` | 행정처분 | 면허정지, 면허취소 (CQ4) |
| `law:AlcoholLevelRule` | 음주 수치 기준 | "0.03% 이상 0.08% 미만이면 정지" 같은 규칙 (CQ4) |

### 설계 포인트 1: 12대 중과실을 왜 클래스가 아닌 개체로 만들었나?

두 가지 방법이 있습니다.

- **방법 A (클래스):** `law:GrossNegligence rdfs:subClassOf law:Violation` → 신호위반은 GrossNegligence의 한 종류
- **방법 B (개체):** `law:12대중과실 a law:ViolationGroup` → 신호위반이 이 그룹에 `memberOf`로 속함

이번에는 **B**를 골랐습니다. 그룹에 "보험 특례 배제 여부"나 "근거 조문"처럼 **그룹 자체의 정보**를 붙여야 하는데,
초보 단계에서는 클래스에 값을 붙이는 것보다 개체에 붙이는 쪽이 훨씬 단순하기 때문입니다.

### 설계 포인트 2: 음주 기준을 왜 별도 클래스로 만들었나?

"음주운전 → 면허정지"라고 바로 이으면 **수치에 따라 결과가 달라진다**는 정보를 담을 수 없습니다.
그래서 "구간 + 결과"를 하나의 개체로 묶었습니다.

```
기준1:  0.03 이상 ~ 0.08 미만  →  면허정지
기준2:  0.08 이상              →  면허취소
```

이렇게 **관계 자체에 조건이 붙을 때 그 관계를 개체로 만드는 방식**은 온톨로지에서 자주 쓰는 패턴입니다(n-ary relation).

## 5. 속성 10개

### 객체 속성 (개체 → 개체)

| 속성 | 주어 → 목적어 | 쓰는 질문 |
|---|---|---|
| `law:legalBasis` | (아무거나) → 조문 | CQ2, CQ5 |
| `law:memberOf` | 위반행위 → 위반행위 그룹 | CQ3, CQ5 |
| `law:resultsIn` | 음주 수치 기준 → 행정처분 | CQ4 |

`legalBasis`에만 domain이 없는 이유는, 위반행위·그룹·기준 **모두** 근거 조문을 가질 수 있기 때문입니다.
domain을 `law:Violation`으로 정하면, 그룹에 근거 조문을 붙였을 때 추론기가 "이 그룹은 위반행위다"라는
**틀린 결론**을 내립니다.

### 데이터 속성 (개체 → 값)

| 속성 | 주어 | 값 타입 | 쓰는 질문 |
|---|---|---|---|
| `law:fineAmount` | 위반행위 | 정수 (원) | CQ1 |
| `law:penaltyPoints` | 위반행위 | 정수 (점) | CQ1 |
| `law:lawName` | 조문 | 문자열 | CQ2 |
| `law:articleNumber` | 조문 | 문자열 | CQ2 |
| `law:minBAC` | 음주 수치 기준 | 소수 (%) | CQ4 |
| `law:maxBAC` | 음주 수치 기준 | 소수 (%) | CQ4 |
| `law:excludesInsuranceException` | 위반행위 그룹 | 참/거짓 | CQ5 |

조 번호를 숫자가 아니라 **문자열**로 둔 이유는 `제5조의2`처럼 숫자로 표현할 수 없는 조가 있기 때문입니다.

## 6. 역량 질문과 맞는지 확인

설계가 끝나면 "모든 CQ에 답할 수 있는가"를 확인합니다. 화살표는 그래프에서 따라가는 경로입니다.

| CQ | 그래프에서 답을 찾는 경로 |
|---|---|
| CQ1 범칙금, 벌점 | 신호위반 → `fineAmount`, `penaltyPoints` |
| CQ2 근거 조문 | 신호위반 → `legalBasis` → 조문 → `lawName`, `articleNumber` |
| CQ3 12대 중과실 목록 | ? → `memberOf` → 12대중과실 (거꾸로 찾기) |
| CQ4 0.05%의 처분 | `minBAC` ≤ 0.05 < `maxBAC` 인 기준 → `resultsIn` → 처분 |
| CQ5 보험 가입 + 신호위반 | 신호위반 → `memberOf` → 그룹 → `excludesInsuranceException` = true → "처벌 가능" |

모든 질문에 경로가 있으므로, 이 T-Box는 CQ1~CQ5에 답할 수 있습니다.
CQ5처럼 **두 단계 이상 관계를 따라가야 하는 질문**이 LLM 혼자서는 자주 틀리는 부분이고,
지식그래프를 쓰면 일관되게 답할 수 있는 부분입니다.

## 7. 일부러 단순화한 것 (다음 버전 후보)

| 단순화 | 실제 법 | 나중에 바꾸는 방법 |
|---|---|---|
| 범칙금을 승용차 기준 하나로만 저장 | 차종(승용, 승합, 이륜)마다 다름 | 음주 기준처럼 "위반 + 차종 → 금액" 개체로 분리 |
| 형사처벌(징역, 벌금)이 없음 | 음주운전은 수치별로 형사처벌도 다름 | `law:CriminalPenalty` 클래스 추가 |
| 법령을 `lawName` 문자열로만 저장 | 법령도 하나의 개체 | `law:Act` 클래스 + `law:partOf` 관계 |
| 시점(개정 이력)이 없음 | 법은 개정되며 금액이 바뀜 | 시행일 속성 추가 |

## 8. 미리 보기: A-Box는 이렇게 생깁니다

다음 단계에서 실제 데이터로 채울 모양입니다. **(아래 숫자는 예시입니다. 실제 값은 시행령 별표에서 수집합니다.)**

```turtle
law:신호위반 a law:Violation ;
    rdfs:label "신호위반"@ko ;
    law:fineAmount 60000 ;
    law:penaltyPoints 15 ;
    law:legalBasis law:도로교통법_제5조 ;
    law:memberOf law:12대중과실 .

law:12대중과실 a law:ViolationGroup ;
    law:excludesInsuranceException true ;
    law:legalBasis law:교통사고처리특례법_제3조 .

law:도로교통법_제5조 a law:Article ;
    law:lawName "도로교통법" ;
    law:articleNumber "제5조" .
```

## 9. 직접 확인해 보기

문법이 맞는지 rdflib로 읽어 볼 수 있습니다 (63개 트리플이 나오면 정상).

```bash
uv run --with rdflib python -c "import rdflib; g=rdflib.Graph(); g.parse('Chapter1/02_tbox.ttl'); print(len(g))"
```

그래프 모양을 눈으로 보고 싶다면 [Protégé](https://protege.stanford.edu/)(무료 온톨로지 편집기)에서
`02_tbox.ttl`을 열어 보세요. 클래스와 속성이 트리로 보입니다.
