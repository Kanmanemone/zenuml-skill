# Data Model: 다이어그램 노드 hover로 책임·협력 보기

저장소는 없다. 스크립트가 구조 뷰 파일 하나를 읽어 메모리에 만드는 구조와, 설정 옵션을 정리한다.

## 설정 옵션 (`settings.schema.json`, `hover` 그룹)

| key | type | 허용 값 | 기본값 | 비고 |
|---|---|---|---|---|
| `hover.enabled` | `boolean` | `true`, `false` | `true` | `false`면 나머지 값과 상관없이 꺼짐(FR-020) |
| `hover.responsibility` | `itemList` | `abstract`, `concrete` | `["abstract", "concrete"]` | 적은 순서대로, `[]`이면 없음(FR-008) |
| `hover.collaboration` | `itemList` | `targets`, `boundary`, `rationale`, `questions` | `["targets", "boundary", "rationale", "questions"]` | 적은 순서대로, `[]`이면 없음(FR-009). 본문에 질문이 없으면(`collaboration.questions`가 `false`) `questions`는 없는 항목처럼 동작(FR-009b) |
| `hover.position` | `enum` | `bottom`, `node` | `bottom` | `<style>` 블록만 바꿈(FR-019) |

`itemList` 검증: 배열, 원소는 모두 `items`의 문자열, 중복 없음. 어기면 그 옵션만 기본값 + 안내 한 줄(FR-009a). 모든 값의 토큰 영향은 `[0]`(FR-018).

**유효 설정(effective)**: 설정 파일 값 → 명령줄 재정의(research R4) 순으로 덮은 뒤, 해당 섹션이 파일에 없으면 그 목록을 `[]`로 본다(FR-010, research R5). `enabled`가 `false`이거나 두 목록이 모두 `[]`이면 **꺼짐**.

## 구조 뷰 파일에서 읽는 것

### Node

| 필드 | 설명 |
|---|---|
| `id` | Mermaid 노드 ID |
| `name` | 본문 연결용 이름. 라벨에서 ✨/♻️/🗑️와 `<b>`·`<s>`를 제거한 뒤 마지막 `&nbsp;` 뒤 토큰을 사용한다(003 FR-036 규격 표시어 제외). `&nbsp;`가 없으면 정리한 전체 라벨, 라벨이 없으면 `id`. |
| `order` | 코드 블록 안 선언 순서 |
| `classDef` | 노드에 붙은 색상 클래스 이름(`class Id xxx` 줄) |
| `link` | 링크 `click` 줄의 대상(경로·URL) 또는 없음 |

### Edge

`source`(id), `target`(id), `label`(관계 이름), `order`.

### ResponsibilityEntry

`names`(묶음이면 여러 이름), `abstract`(책임 (추상) 문장), `concrete`(역할 (구체) 문장). 원본은 `#### 요소의 책임` 아래 항목.

### CollaborationEntry

| 필드 | 설명 |
|---|---|
| `subject` | 첫 `<strong>` 이름 |
| `kind` | `oneWay`(…에 의존한다) 또는 `mutual`(…와 …는 서로 의존한다) |
| `objectText` | 대상 부분 글자(태그·링크 제거, `A와 B`나 묶음 이름 그대로) |
| `objectNames` | `objectText` 안의 노드 이름들(특정할 수 있을 때) |
| `boundary`, `rationale`, `questions` | 각 세부 분석의 하위 글머리 항목 목록 |

원본은 `#### 요소 간 비교` 아래 항목. 그룹 간 비교는 읽지 않는다(Edge Case "그룹 수준 항목").

## 만드는 것

### NodePanel (노드 하나의 툴팁 문자열)

```text
<b>{name}</b><br/>
{Responsibility 부분: responsibility 목록 순서대로, 줄 사이 <br/>}
<br/><br/>                                   ← 두 부분이 모두 있을 때만
{Collaboration 부분: 그 노드가 주어인 oneWay 항목 + 그 노드가 들어 있는 mutual 항목, 본문 순서대로}
```

- Responsibility 줄: `<b>책임 (추상)</b>: …`, `<b>역할 (구체)</b>: …`.
- 협력 하나: 머리줄 `<b>{objectText}에 의존한다 ({관계})</b>`(또는 `<b>{상대}와 서로 의존한다 ({관계})</b>`) 다음, 목록에 있는 세부 분석마다 `<b>{제목}</b>: {하위 항목을 공백으로 이은 문단}` 한 줄. `targets`가 목록에 없어도 다른 항목이 있으면 머리줄은 붙는다(FR-009).
- 협력 사이: 세부 분석 항목이 있으면 `<br/><br/>`, `targets`만 있으면 `<br/>`(FR-012).
- 두 부분이 모두 비면 NodePanel은 **없음** — 그 노드는 툴팁을 파일 이름으로 둔다(Edge Case).
- 글자 변환은 research R8.

### 파일 상태

```text
꺼짐(기능 도입 전 형태) ──apply-hover(켜짐 설정)──▶ 켜짐(툴팁·hoverOnly·cursor:auto·<style>)
켜짐 ──apply-hover(다른 설정·본문 수정)──▶ 켜짐(다시 계산된 내용)
켜짐 ──apply-hover(꺼짐 설정, 또는 NodePanel이 하나도 없음)──▶ 꺼짐
```

모든 전이는 멱등이다 — 같은 파일·같은 유효 설정으로 두 번 돌리면 두 번째는 바이트 단위로 바꾸지 않는다(FR-003, SC-004). 본문(`### Responsibility`·`### Collaboration` 아래)은 어떤 전이에서도 바뀌지 않는다(FR-002).
