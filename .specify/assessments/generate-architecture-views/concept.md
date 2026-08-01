# Concept: 자연어 설명에서 구조 뷰(컴포넌트/그룹/의존성)를 생성하는 신규 스킬

- **Slug**: generate-architecture-views
- **Created**: 2026-07-31
- **Recommended option**: Option A — 최소 컴패니언 스킬 (Mermaid 구조 그래프 단건)

## Options

### Option A — 최소 컴패니언 스킬 (Mermaid 구조 그래프 단건)
- **Sketch**: `generating-zenuml-diagrams`와 동일하게 자연어 프로세스 설명을 입력으로 받는 **별도의 새 스킬**. 시퀀스 다이어그램은 만들지 않고, 참가자(Components)를 자동으로 그룹핑(Grouping)한 `subgraph`와 참가자 간 호출·의존 관계(Dependencies)를 화살표로 표현한 Mermaid `graph`/`flowchart` 한 장만 생성한다. 설계 의도(Intent)는 별도 섹션 없이 그래프 노드/엣지 옆 `%%` 주석으로 필요한 곳에만 짧게 붙인다. 결과는 기존 `.zenuml/<slug>.md`와 같은 슬러그를 공유하는 형제 파일(예: `.zenuml/<slug>.structure.md`)에 저장 — problem.md가 정리한 이 저장소의 "같은 슬러그=같은 폴더, 다른 성격 정보=다른 파일" 관례를 따름. 사용자는 시퀀스 다이어그램을 만들 때처럼 이 스킬을 독립적으로 호출한다(자동 연계 없음).
- **Appetite**: small (days)
- **Trade-offs**: **승**: 범위가 명확하고 기존 스킬의 검증된 패턴(파일 배치, ZenUML/Mermaid 렌더링 경로, anti-fluff 정신)을 그대로 재사용할 수 있어 리스크가 낮음. **패**: 두 스킬이 완전히 독립적이라 사용자가 "구조 뷰도 있다"는 걸 스스로 기억해서 호출해야 함 — 발견성(discoverability)이 낮을 수 있음. 자동 그룹핑 로직이 최소한(예: 설명에 언급된 계층/네임스페이스 단서만 사용)이라 복잡한 시스템에서는 그룹이 엉성할 수 있음.
- **Rabbit holes**: "자동 그룹핑"을 얼마나 똑똑하게 만들지가 스코프 블로우업 지점 — 결합도 분석, 클러스터링 알고리즘 등으로 빠지면 순식간에 medium/large로 번짐. 처음엔 "설명에 명시적으로 드러난 단서만 쓰고, 애매하면 그룹 하나로 묶는다"는 좁은 규칙으로 제한해야 함.

### Option B — 컴패니언 스킬 + 상호 연계 + 자체 검증 루프
- **Sketch**: Option A와 동일한 산출물이되, 두 가지를 추가한다: (1) `generating-zenuml-diagrams`의 SKILL.md에 "구조 뷰가 필요하면 이 스킬도 있다"는 안내 문구를 추가하고, 이 새 스킬도 완료 후 "시퀀스 다이어그램도 필요하면 기존 스킬을 쓰라"고 안내해 서로를 발견할 수 있게 함. (2) 기존 스킬의 AP-1~AP-5 anti-fluff 체크리스트에 대응하는 자체 체크리스트(예: "설명에 없는 컴포넌트/의존관계를 추가하지 않았는가", "그룹핑 근거가 설명에서 실제로 확인되는가")를 만들어 생성 전 자가 점검한다.
- **Appetite**: medium (weeks)
- **Trade-offs**: **승**: 발견성 문제 해결, 품질이 anti-fluff 체크리스트로 담보되어 "구조를 지어내는" 리스크가 줄어듦. **패**: 기존 `generating-zenuml-diagrams`의 SKILL.md를 건드리게 되어 problem.md의 Non-Goal("기존 스킬의 SKILL.md 자체를 수정하는 것은 범위 밖")과 충돌 — 채택하려면 그 Non-Goal을 재검토해야 함.
- **Rabbit holes**: 두 스킬 간 "언제 서로를 제안할지" 조건을 정교하게 다듬으려다 보면 대화 흐름 분류 로직이 계속 늘어날 위험. 체크리스트 항목을 너무 많이 늘리면 매 호출마다 오버헤드가 커짐.

### Option C — 통합 컴포지트 스킬 (시퀀스 + 구조 동시 생성)
- **Sketch**: 시퀀스 다이어그램과 구조 그래프를 하나의 파이프라인/스킬에서 한 번에 생성. 참가자 추출·파싱 로직을 두 산출물이 공유하고, 그룹핑 전략도 여러 방식(네임스페이스 기준/설명 내 계층 언급 기준/수동 지정) 중 선택 가능하게 하며, Intent도 그래프 주석뿐 아니라 필요 시 더 풍부한 설명을 옵션으로 제공.
- **Appetite**: large (months)
- **Trade-offs**: **승**: 사용자가 한 번의 요청으로 mental model 5단계 대부분(1~4단계 + 부분적 5단계)을 얻음, 두 산출물 간 일관성(같은 참가자 이름 등)이 자동 보장됨. **패**: 기존 `generating-zenuml-diagrams`를 사실상 재작성/흡수하게 되어 problem.md의 "별도의 새 스킬로 해결한다"는 이미 확정된 결정과 정면으로 배치됨. 요청되지 않은 다중 그룹핑 전략, 옵션형 Intent 상세도 등은 "범용 도구가 되지 않는다"는 Non-Goal과도 충돌.
- **Rabbit holes**: 기존 스킬 리팩터링(공유 파싱 모듈 추출) 자체가 별도의 대형 작업이며, "일관성 보장"을 위한 상태 공유 설계가 무한히 커질 수 있음. 사실상 이번 문제 정의의 스코프를 벗어난 재설계 프로젝트가 됨.

### Option D — 아무것도 만들지 않고 외부 도구로 대체 (do nothing / buy)
- **Sketch**: 자체 스킬을 만들지 않고 `swark` 같은 외부 도구(GitHub Copilot 기반, 실제 코드베이스를 분석해 Mermaid 아키텍처 다이어그램 생성)를 채택.
- **Appetite**: n/a (build 자체가 없음)
- **Trade-offs**: **승**: 구현 비용 0. **패**: 입력 모델이 근본적으로 다름 — swark는 실제 소스코드를 분석하지만, problem.md에서 이미 "입력은 기존과 동일한 자연어 프로세스 설명"으로 확정됨. 이 저장소의 스킬들은 코드가 아직 없는 단계(설계/논의 중인 프로세스)를 다이어그램화하는 데도 쓰이므로, 코드 분석 전제인 swark로는 이 사용 사례 자체를 커버하지 못함. — [source: research.md "Prior Art", problem.md Goals]
- **Rabbit holes**: 해당 없음(채택하지 않음).

## Recommendation

**Option A**를 권장한다. problem.md가 이미 확정한 제약(별도 신규 스킬, 자연어 입력 유지, 자동 그룹핑, Intent는 주석으로 간결하게, 범용 도구 금지)과 가장 정확히 들어맞고, 기존 `generating-zenuml-diagrams`가 검증한 파일 배치·렌더링 경로·anti-fluff 정신을 그대로 재사용해 리스크가 낮다. Option B의 "상호 연계"는 좋은 방향이지만 기존 스킬 문서 수정을 필요로 해 현재 확정된 Non-Goal과 충돌하므로, 이번 라운드에는 채택하지 않고 **후속 개선(반복 2)** 후보로 남긴다. Option C는 problem.md가 이미 명시적으로 배제한 "기존 스킬과의 통합/스코프 확장"에 해당해 기각한다. Option D는 problem.md가 확정한 입력 모델(자연어)과 근본적으로 맞지 않아 채택할 수 없다.

성공 지표("스킬 산출물만 보고 컴포넌트/그룹/의존관계를 설명할 수 있다")를 만족시키는 데 필요한 최소 범위가 Option A이며, 자동 그룹핑을 좁은 규칙으로 제한하면 appetite(days) 안에서 달성 가능하다고 판단한다.

## Out of Scope (for the recommended option)

- (problem.md Non-Goals 승계) 실제 코드베이스 파싱/정적 분석
- (problem.md Non-Goals 승계) 클래스/배포 다이어그램 등 임의 UML 유형 지원
- (problem.md Non-Goals 승계) 근거 없는 Intent 추측
- (problem.md Non-Goals 승계) 다이어그램의 지속적 자동 동기화(watch/CI 연동)
- (이번 개념화에서 추가) 기존 `generating-zenuml-diagrams`의 SKILL.md 수정 — Option B/C에서 필요했던 "상호 발견성" 기능은 이번 범위에서 제외
- (이번 개념화에서 추가) 정교한 그룹핑 알고리즘(결합도 분석, 클러스터링 등) — 설명에 명시적으로 드러난 단서만으로 그룹핑

## Assumptions to Validate

- 자연어 프로세스 설명만으로도 "의미 있는 그룹"을 자동으로 판단할 수 있을 만큼 충분한 단서(네임스페이스, 계층 언급 등)가 실제 입력에 보통 존재한다 — 그렇지 않다면 그룹핑이 항상 "그룹 하나"로 퇴화해 산출물의 가치가 떨어질 수 있음.
- Mermaid `graph`/`flowchart` + `subgraph` + `%%` 주석 조합이 VS Code 내장 Markdown Mermaid 프리뷰에서 `zenuml` 코드 블록과 동일하게 문제없이 렌더링된다 — 이번 조사에서 subgraph 자체의 VS Code 렌더링을 직접 재검증하지는 않았음(research.md Data & Constraints 참고).
- 사용자가 두 스킬(시퀀스/구조)을 별도로 호출하는 데 불편함을 느끼지 않는다 — 만약 반복 사용 중 발견성 문제가 실제로 드러나면 Option B의 상호 연계 기능을 후속 라운드에서 재검토한다.
- "간결한 Intent 주석"이 사용자가 원한 "모호함 해소"를 실제로 달성한다 — 이는 실사용 피드백(예: `.zenuml/log/` 방식의 피드백 로그)으로만 검증 가능하며, 이번 개념 단계에서는 가정으로 남긴다.
