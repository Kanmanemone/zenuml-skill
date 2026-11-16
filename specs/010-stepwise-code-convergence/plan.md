# Implementation Plan: 꾸며낸 최소 코드에서 원본 코드까지 단계별로 구체화해 보여 주기

**Branch**: `010-stepwise-code-convergence` | **Date**: 2026-11-16 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/010-stepwise-code-convergence/spec.md`

## Summary

### 단위 펼치기 (아래의 모든 앞선 설계보다 우선)

단계는 사용 상황(`prose`) → 윤곽(`outline`) → 펼치기(`unfold`, 단위마다 반복) → 원본(`source`)이다. 모든 코드 장면은 `stages.py`가 원본 범위와 펼치기 입력에서 만든다. 메인 에이전트가 단계마다 수정 블록을 쓰던 `begin`/`apply`와 `edits.txt`, `work/02…` 작업 파일은 제거한다.

- `prepare`: 지금처럼 원본 범위를 자르고, 노드마다 펼치기 단위(spec FR-005a)를 계산해 manifest에 둔다. 단위별 원본 줄(범위 기준 줄 번호, 주석 포함)을 한 번만 출력해 메인 에이전트가 자리표시자와 접기를 정하게 한다. 1단계 프롬프트에는 구조 뷰에서 Mermaid `click` 줄을 뺀 내용을 넣는다(마우스오버 문구가 Responsibility·Collaboration을 되풀이해 프롬프트의 약 27%를 차지했다).
- 메인 에이전트: `work/outline.json` 하나에 노드별 `placeholders`와 `folds`를 쓴다.
- `build`: 펼치기 입력을 검증한다(개수, 빈 문장, 책임 줄과 같은 문장, 단위 밖이나 겹치는 접기). 장면을 만들고, 모두 펼친 장면이 원본과 같은지와 마지막 장면이 원본 범위와 같은지 확인한 뒤 문서를 쓴다.
- 단위 계산은 `mask_code`로 문자열·주석을 가린 뒤 괄호 깊이와 줄 끝·줄 머리의 이어짐 표시로 본문의 최상위 항목을 나눈다. 시제품(`tmp/unfold_proto.py`)으로 북마크 예제 7개 노드에서 모두 펼친 장면이 원본에서 주석을 뺀 것과 같음을 확인했다. 이번 구현에서는 주석을 멤버와 함께 펼치므로 모두 펼친 장면이 원본과 같아야 한다.
- 토큰: 북마크 예제 기준으로 메인 에이전트가 읽는 코드는 21,007자에서 약 7,900자로, 쓰는 입력은 11,583자에서 약 1,000자로 줄고, 주고받기는 7번에서 1번으로 준다.

**Complexity Tracking**: `begin`/`apply` 흐름을 지우고 단위 계산·장면 렌더링을 더한다. 모델이 장면 코드를 쓰는 더 단순한 방법은 노드·실행마다 나누는 크기가 달라지는 문제(사용자 우려)를 막지 못해 택하지 않는다.


### 첫 장면 정리 (앞선 장면 분리·책임 틀 통합 설계보다 우선)

첫 장면은 `kind=prose`인 상황 문단 하나다. 책임 문장은 상자 위 책임 한 줄이 맡으므로 격리 프롬프트는 그 문장을 되풀이하지 말고 책임 한 줄에 없는 상황만 쓰게 한다. 첫 장면에서 책임 틀을 없애고 `intro` 표현과 그 분리·거부 처리를 제거한다. 문장 장면 다음의 첫 코드 장면은 `begin`이 노드 이름만 담은 `이름 {`·`}` 작업 파일로 시작시키며, 이 시작 파일은 화면에 보이지 않는다. 책임 자리표시자는 선언의 종류 단계에서 처음 넣고 책임 한 줄을 그대로 되풀이하지 않는다. 현재 예제는 이후 코드 단계를 그대로 두고 첫 장면만 다시 쓴다.

### 2026-11-16 학습 단계 개편 (초기 설계보다 우선)

`stages.md`에 `표현`(`prose`/`code`, 기본 `code`), `반복`(`dependency`) 선택 필드를 추가한다. 첫 상황은 격리된 에이전트가 구조 뷰만 보고 쓰고, 상황과 책임은 하나의 첫 장면으로 작성하고 책임 틀부터 메인 에이전트가 작성한다. 가상의 API 발명 규칙은 제거한다. 단계의 정본은 이 파일 하나다.

직접 화살표와 라벨을 순서대로 읽어 Node의 `dependencies`로 보존한다. `prepare`는 반복 템플릿을 최대 직접 의존 수만큼 펼치고 노드별 상대를 `targets` 맵에 기록한다. 대상 없는 장면은 그 노드 화면에서 건너뛰고 번호를 다시 매긴다. `begin`은 이번 상대를 출력한다. 단계에 질문 문구는 표시하지 않는다. 기본 별명으로 반복 전체를 숨길 수 있고 합친 몫은 대상 정보를 보존한다. prose 숨기기는 다음 코드에 문장을 합치지 않는다.

내부 작업 파일 `.kt`는 유지한다. `kind=prose`는 HTML 이스케이프한 일반 문단으로 렌더링하며 fence·diff가 없다. code 장면끼리만 diff를 적용한다. 바깥 제목은 모든 장면에서 구조 뷰의 노드 이름을 그대로 사용한다. 상황 본문의 식별자 생략을 제목까지 확장하지 않는다. 노드 책임 고정 줄·분할·넘기기는 유지한다. 원본 없는 노드는 상황 장면까지만 생성한다. 마지막 원본 검증은 노드별 실제 마지막 번호를 사용한다. 기존 manifest는 새 필드 부재를 code로 처리한다.

기존 7단계 fixture는 테스트에서 legacy 정의를 명시해 회귀를 확인한다. 새 기본 정의는 학습 흐름 자동 테스트와 실제 북마크 7개 노드로 검증한다. 원본 및 구조 뷰는 보존한다. 새 의존성·설정 옵션은 없다. 헌법 I·II 통과, III 해당 없음. 실제 인지 부하 감소를 실측했다고 주장하지 않는다. 아래 과거의 가상 첫 코드·고정 7단계 전제는 대체된다.

새 스킬 `revealing-code-step-by-step`를 더한다. 이 스킬은 구조 뷰 파일(`.zenuml/<slug>.architecture.md`) 하나를 받아, 노드마다 상자 하나씩 정제 단계를 넘겨 보는 문서를 만든다. 첫 단계는 원본을 모르고 지어낸 최소 Kotlin 코드이고, 마지막 단계는 원본 파일에서 그 노드의 선언 구간을 그대로 잘라낸 코드다.

단계 목록은 스킬 폴더의 단계 정의 파일 `stages.md` 한 곳에만 둔다. 단계마다 보일지는 스킬 설정 `settings.jsonc`의 `stages` 맵(별명 → `true`/`false`)으로 정한다. 끈 단계는 만들지 않고, 그 단계가 맡던 변화는 다음에 보이는 단계에 합친다. 보이는 단계끼리 번호를 다시 매긴다(spec FR-009a). 결정적으로 정해지는 일은 번들 Python 스크립트 `scripts/stages.py`가 맡는다.

- `prepare`: 설정과 요청의 단계 보이기를 반영해 이번에 만들 단계 목록을 정한다. 구조 뷰를 읽고, 노드마다 원본 범위를 찾아 잘라 두고, 문서를 어떻게 나눌지 정한다.
- `begin`: 다음 단계의 작업 파일을 직전 단계에서 복사해 둔다.
- `build`: 단계별 문서를 조립하고, 마지막 단계가 원본 범위와 같은지 확인한다. 직전 단계와 달라진 줄은 VS Code의 git 변경 표시처럼 칠한다(추가는 초록, 변경은 파랑, 삭제는 빨간 삼각형). 이때 Kotlin 구문 색칠은 유지한다(research R7).

모델이 쓰는 것은 두 가지뿐이다.

- 1단계 코드: 원본을 모르는 새 서브에이전트가 구조 뷰 내용만 받아서 쓴다.
- 중간 단계 코드: 메인 에이전트가 복사된 직전 단계 파일을 고친다. 고칠 범위는 그 단계 정의, 구체화 사다리(보조 표기 `...`·`⟨설명⟩`), 다른 노드의 이름 맞추기 규칙이 정한다.

## Technical Context

**Language/Version**: Python 3.9 이상에서 동작하는 스크립트와 Markdown 지침 문서(SKILL.md, `stages.md`)로 이뤄진다. 스크립트는 표준 라이브러리만 쓰고 3.10 이상 전용 문법을 쓰지 않는다. 003 스킬과 같은 조건이다. 산출물의 코드는 Kotlin이다(spec FR-006).

**Primary Dependencies**: 없음. 표준 라이브러리(`argparse`, `json`, `re`, `pathlib`, `shutil`, `difflib`, `html`, `urllib.request`)만 쓴다. 003 스킬의 코드는 import하지 않는다(스킬 독립성, research R2).

**Storage**: 파일만 쓴다. 스킬 폴더의 `settings.jsonc`·`settings.schema.json`은 읽기만 한다.

- 입력(읽기만): `.zenuml/<slug>.architecture.md`와, 그 링크가 가리키는 원본 Kotlin 파일
- 산출물: `<output.directory>/<slug>.stages/` 아래의 문서(`*.md`)와 작업 폴더(`work/`). 기본값으로는 `.zenuml/<slug>.stages/`

**Testing**: 자동화 테스트 프레임워크는 없다(기존 스킬과 같다). [quickstart.md](quickstart.md)에 다음 세 가지 확인을 둔다.

- 고정 입력(fixture)에 스크립트를 돌려 기대 결과와 바이트 비교하기. fixture는 작은 구조 뷰, 여러 노드가 든 Kotlin 원본, 손으로 쓴 단계 작업 파일로 이뤄진다.
- VS Code 미리보기를 수동으로 확인하기
- 실제 구조 뷰 하나로 처음부터 끝까지 돌려 보기

**Target Platform**: Claude Code(Windows/macOS/Linux)에서 돌린다. 1단계는 Agent 도구로 띄운 새 general-purpose 서브에이전트가 만든다(fork는 쓰지 않는다). 결과는 VS Code 1.146 내장 Markdown 미리보기에서 확인한다. 기준은 실제 VS Code 미리보기 DOM에서 검증한 시제품 [prototype/code-gallery.md](prototype/code-gallery.md)이다.

**Project Type**: Claude Code skill(지침 문서 + 번들 스크립트)

**Performance Goals**: 모델 출력 토큰을 줄인다.

- 마지막 단계는 모델이 쓰지 않는다. 스크립트가 원본 범위를 복사한다.
- 중간 단계는 직전 단계의 복사본을 Edit로 고치므로, 바뀌지 않는 부분은 다시 쓰지 않는다.
- 스크립트는 구조 뷰 하나(노드 수십 개, 원본 수천 줄)를 몇 초 안에 처리한다.

**Constraints**:

- 원본 코드베이스와 구조 뷰 파일은 바꾸지 않는다(FR-019).
- 1단계를 만드는 주체에는 구조 뷰 내용만 준다(FR-003).
- 단계의 별명·순서·수는 `stages.md`만으로 정해진다(FR-007, SC-004).
- 마지막 단계는 원본 범위와 같은지 확인한다(FR-010).

**Scale/Scope**:

- 새 스킬 1개: SKILL.md, `stages.md`, `settings.jsonc`, `settings.schema.json`, `scripts/stages.py` 1개
- 새 설정 옵션 2개: `stages`(단계 별명 → 보이기), `output.directory`(결과 위치, 구조 뷰 폴더 기준 상대 경로, 기본값 `.`). 설정 로더는 기존 스킬과 같은 동작을 `stages.py` 안에 옮겨 쓴다.
- `.gitignore`의 허용 목록에 새 스킬 폴더 추가
- README 영어·한국어 두 벌에 항목 추가
- spec FR-008의 7단계 표는 `stages.md`로 옮기고, spec에는 링크만 남긴다.
- 003 스킬은 바꾸지 않는다(FR-001).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| 원칙 | 판단 | 근거 |
|---|---|---|
| I. 오버엔지니어링 금지 | 통과 | 설정 옵션은 spec이 요구하는 두 개만 둔다 — `stages`(FR-009a), `output.directory`(FR-019a). 설정 파일 형식과 주석 규칙은 기존 두 스킬의 관례(007)를 그대로 따르고, 로더도 그 동작을 옮겨 쓴다(R12). 스크립트는 파일 하나이고, 하위 명령 셋은 각각 spec 요구를 하나 이상 맡는다(R4). 새 의존성은 없다. URL 원본 지원은 spec Assumptions("원본 접근")가 요구하는 만큼만 하며, GitHub blob 주소 변환 하나로 한정한다(R8). 선언 구간 찾기는 Kotlin 전체 파서가 아니라 문자열·주석·괄호만 아는 최소 스캐너로 한다(R5). |
| II. 요청은 해당 Spec에서 진행 | 통과 | 010 spec의 구현이다. 003의 동작은 바꾸지 않는다. |
| III. 출력 변동성 수정에 Spec Kit 미사용 | 해당 없음 | 새 기능이다. |

Phase 1 설계를 마친 뒤 다시 확인했고, 달라진 것은 없다.

## Project Structure

### Documentation (this feature)

```text
specs/010-stepwise-code-convergence/
├── plan.md              # 이 파일
├── research.md          # Phase 0
├── data-model.md        # Phase 1
├── quickstart.md        # Phase 1
├── contracts/
│   └── stages-contract.md   # stages.md 형식, stages.py 실행 규약, 작업 폴더와 문서 형식
├── prototype/
│   └── code-gallery.md      # 기존 — 넘겨 보기 구조의 원본
└── tasks.md             # /speckit-tasks 산출물
```

### Source Code (repository root)

```text
.agents/skills/revealing-code-step-by-step/      # 신규
├── SKILL.md            # 작업 순서: prepare → 1단계 서브에이전트 → 단계마다 begin+apply → build → reply 응답
├── stage1-prompt.md    # 1단계 서브에이전트 지시의 틀 — prepare가 채워 work/stage1-prompt.md로 씀
├── stages.md           # 단계 정의 파일 — 단계 구성을 고치는 유일한 곳(spec FR-007·008)
├── settings.jsonc      # 단계마다 보일지(stages 맵), 결과 위치(output.directory) — 007 주석·토큰 기호 관례
├── settings.schema.json # 두 옵션의 정의(stageToggles 타입 기본값 {}, relativePath 타입 기본값 ".")
└── scripts/
    └── stages.py       # python scripts/stages.py prepare|begin|apply|build ...

.gitignore              # 개정 — !.agents/skills/revealing-code-step-by-step/ 추가
README.md, README.ko.md # 개정 — "추가 기능"·"요구 사항"에 이 스킬 항목
specs/010-stepwise-code-convergence/spec.md   # 개정 — FR-008의 표를 stages.md 링크로 바꿈

specs/010-stepwise-code-convergence/fixtures/   # 신규 — quickstart용 입력·작업 파일·기대 결과
```

**Structure Decision**: 003과 성격이 달라 스킬을 따로 둔다(FR-001). 스크립트는 이 스킬의 `scripts/`에 두고, 다른 스킬의 코드를 import하지 않는다.

`stages.md`는 SKILL.md와 분리한 단계 정의 파일이고, `settings.jsonc`는 단계 구성은 그대로 두고 보일지만 정하는 설정이다. 설정은 단계를 별명으로 가리키므로, 단계를 넣거나 옮겨도 설정을 고칠 필요가 없다(SC-006). 스크립트는 여기서 별명·순서를 읽고, 모델은 단계마다 바꿀 것을 읽는다.

산출물은 `.zenuml/<slug>.stages/`에 둔다. 원본 코드베이스의 빌드 대상과 섞이지 않게 하기 위해서다(FR-019).

## Complexity Tracking

위반 없음 — 비워 둔다.
