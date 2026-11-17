# zenuml-skill

**언어:** [English](README.md) | 한국어

자연어로 설명한 프로세스를 정확하고 군더더기 없는 [ZenUML](https://github.com/mermaid-js/zenuml-core) 시퀀스 다이어그램 DSL로 바꿔주는 Claude Code 스킬 `generating-zenuml-diagrams`가 담긴 프로젝트입니다. 설명에 없는 참가자·메시지·분기는 지어내지 않습니다.

## 구성

```text
.agents/skills/generating-zenuml-diagrams/
├── SKILL.md          # skill instructions
└── references/
    └── syntax.md     # syntax reference
```

- **SKILL.md** — 생성 규칙, 예시, 안티-fluff 자기검증, 모호한 입력 처리
- **references/syntax.md** — ZenUML DSL 문법 레퍼런스, mermaid-js/zenuml-core 재구성, MIT
- **`.zenuml/`** — 처음 다이어그램을 생성할 때 여러분 프로젝트 루트에 생기는 폴더로, 결과물이 여기에 저장됩니다. 방금 받은 다이어그램을 고쳐달라고 하면 새 파일이 아니라 같은 파일이 갱신되고, 무엇을 왜 고쳤는지에 대한 전체 이력은 `.zenuml/log/`에 남습니다.

## 사용법

> [!CAUTION]
> **[`.agents/skills/generating-zenuml-diagrams/`](.agents/skills/generating-zenuml-diagrams/) 폴더만 복사하세요 — 프로젝트 전체를 복사하면 안 됩니다.**

1. [`.agents/skills/generating-zenuml-diagrams/`](.agents/skills/generating-zenuml-diagrams/) 폴더를 여러분 프로젝트의 `.claude/skills/`(Claude Code) 또는 `.agents/skills/`(Codex 등 [Agent Skills](https://agentskills.io) 폴더를 읽는 에이전트)에 복사하세요. 이 저장소에서는 스킬 원본이 `.agents/skills/`에 있고, `.claude/skills/<이름>`은 그곳을 가리키는 심볼릭 링크입니다.
2. Claude Code에서 `/generating-zenuml-diagrams <프로세스 설명>`을 실행하세요.

**예시:**

```text
/generating-zenuml-diagrams the client calls Server.getData()
```

새로 추가한 스킬이 `/` 목록에 안 보인다면 Claude Code를 재시작하거나, VS Code 명령 팔레트(`Ctrl+Shift+P`, Mac은 `Cmd+Shift+P`)에서 "Reload Window"를 실행하세요 — 스킬은 세션 시작 시점에만 스캔됩니다.

## 추가 기능

아래는 각각 독립된 스킬입니다 — 필요한 것만 `.claude/skills/`에 복사하세요. 핵심 스킬을 포함한 모든 스킬은 자기 폴더의 `settings.jsonc`를 읽으므로, 그 파일을 고쳐 동작을 바꿀 수 있습니다(각 옵션 위에 한국어 설명 주석이 있습니다):

- **[`generating-architecture-views`](.agents/skills/generating-architecture-views/)** — 구조 뷰(컴포넌트·그룹·의존관계)를 추가합니다. Dependency 다이어그램에 특정 Mermaid 렌더러(예: `elk`)를 쓰고 싶다면 요청에 그렇게 명시하세요 — 다이어그램 YAML `config`에 `layout`이 추가됩니다(스킬의 `settings.jsonc`에서 `dependency.renderer`로 기본값을 정할 수도 있습니다). 명시하지 않으면 추가되지 않습니다. VS Code Markdown 미리보기에서 Dependency 다이어그램의 노드에 마우스를 올리면, 그 노드의 Responsibility와 그 노드가 의존하는 Collaboration이 패널로 떠서 본문까지 스크롤하지 않아도 됩니다. 패널 내용은 구조 뷰를 저장한 뒤 번들 Python 스크립트가 본문에서 옮겨 채우므로 토큰이 더 들지 않습니다. 패널에 넣을 항목과 위치(미리보기 아래쪽 또는 노드 바로 아래)는 `settings.jsonc`의 `hover` 그룹에서 정하고, `hover.enabled`로 끌 수 있습니다. GitHub 등 다른 뷰어에서는 동작하지 않습니다.
- **[`exporting-markdown-diagrams`](.agents/skills/exporting-markdown-diagrams/)** — 다이어그램을 SVG/PNG로, 마크다운 파일 전체를 PDF(다이어그램은 텍스트 선택 가능한 벡터로 삽입)나 PNG로 변환합니다. 변환은 항상 번들 스크립트(mermaid-cli)로만 이뤄지고 LLM 추론을 거치지 않습니다. 그 스크립트가 쓰는 의존성을 받기 위해 `scripts/` 폴더에서 `npm install`을 한 번 실행하세요. 결과 파일은 원본과 같은 디렉토리가 아니라 그 아래 `exports/`(자동 생성)에 모입니다.
- **[`revealing-code-step-by-step`](.agents/skills/revealing-code-step-by-step/)** — **먼저 `generating-architecture-views`로 만든 구조 뷰(`.zenuml/<slug>.architecture.md`)가 있어야 합니다.** 구조 뷰의 노드·원본 링크·Responsibility·Collaboration을 읽으므로 그 스킬을 먼저 실행하세요. 구조 뷰를 받아, 노드마다 Kotlin 코드를 *정제 단계*로 넘겨 보는 문서를 만듭니다. 노드의 책임 한 줄을 상자 위에 고정해 두고, 사용 상황 → 모든 단계를 번호 붙은 자리표시자로 보이는 윤곽(안쪽 단계는 감싸는 단계 아래에 들여 씀) → 원본을 한 겹씩 펼치기 순서로 보여 줍니다. 그래서 람다가 여러 겹 든 호출도 한 장면에 몰려 나오지 않습니다. 원본을 스코프 트리로 나누고, 각 줄을 한 번씩만 보이고, 모든 코드 장면을 만드는 것은 스크립트입니다. 에이전트는 안쪽 스코프부터 하나씩 목적 문장과 함께 열 자식만 정합니다. 첫 상황은 원본을 보지 않은 별도 에이전트가 씁니다. VS Code Markdown 미리보기에서 노드마다 상자 하나를 ← →로 넘기며, 직전 단계와 달라진 줄은 VS Code의 git 변경 표시처럼 칠해집니다(추가 초록, 변경 파랑, 삭제 빨간 삼각형). Kotlin 구문 색칠은 그대로입니다. 단계 구성은 스킬의 `stages.md`에 있으며, 토큰을 늘리지 않고 단계를 고치는 원칙도 그곳에 적혀 있습니다. `settings.jsonc`에서 단계마다 보일지(`stages`)와 결과 위치(`output.directory`)를 정합니다. GitHub 등 다른 뷰어에서는 넘기기 대신 모든 단계가 순서대로 나열됩니다.

## 개발

각 기능의 스펙/계획/태스크 기록은 [`specs/`](specs/) 아래에 있습니다.

### 스킬 폴더 구조

스킬 원본은 [`.agents/skills/`](.agents/skills/)에 있고(Agent Skills 표준 폴더라 Codex 등이 바로 읽습니다), `.claude/skills/<이름>`은 그곳을 가리키는 심볼릭 링크입니다. 스킬을 고칠 때는 `.agents/skills/` 쪽을 고치세요.

### Windows에서 clone할 때

Windows는 심볼릭 링크를 만들려면 권한이 필요합니다. 아래 설정 없이 clone하면 `.claude/skills/<이름>`이 대상 경로 한 줄이 적힌 텍스트 파일로 풀려, Claude Code에 스킬이 보이지 않습니다(Codex 등 `.agents/skills`를 읽는 에이전트는 영향이 없습니다).

1. 개발자 모드를 켭니다: 설정 → 시스템 → 개발자용 → 개발자 모드. (또는 Git을 관리자 권한으로 실행합니다.)
2. 링크를 살려서 clone합니다.

   ```bash
   git clone -c core.symlinks=true https://github.com/Kanmanemone/zenuml-skill.git
   ```

   개발자 모드를 켜면 Git for Windows가 이를 감지해 링크 지원을 스스로 켜기도 하지만, `-c core.symlinks=true`를 붙이면 확실합니다.

이미 clone했다면 저장소 안에서 다음을 실행합니다.

```bash
git config core.symlinks true
git checkout -- .claude/skills
```

확인: `.claude/skills/` 안의 스킬 이름이 폴더(링크)로 열리고 그 안에 `SKILL.md`가 있으면 됩니다.

> 스킬 하나만 가져다 쓰는 경우("사용법"대로 폴더 복사)에는 이 설정이 필요 없습니다. `.agents/skills/<이름>` 폴더를 복사하면 진짜 파일이 옮겨집니다.

## 요구 사항

- [Claude Code](https://claude.com/product/claude-code)
- `generating-zenuml-diagrams`는 그 외 별도 의존성 없음 — 실행 코드가 없는 순수 Markdown 번들입니다.
- `generating-architecture-views`는 노드 hover 패널에 PC에 이미 있는 [Python](https://www.python.org/) 3.9 이상(`python3`, `python`, `py -3` 순으로 찾음)을 씁니다. 번들 스크립트(`.agents/skills/generating-architecture-views/scripts/`)는 표준 라이브러리만 써서 따로 설치할 것이 없습니다. Python이 없어도 구조 뷰는 만들어지고, hover 패널만 빠집니다.
- `revealing-code-step-by-step`은 번들 스크립트에 PC에 있는 [Python](https://www.python.org/) 3.9 이상을 씁니다(표준 라이브러리만 사용). 없으면 문서를 만들지 않습니다. 구조 뷰가 링크한 Kotlin 원본만 다룹니다.
- `exporting-markdown-diagrams`는 [Node.js](https://nodejs.org/)가 필요합니다 — 번들 스크립트(`.agents/skills/exporting-markdown-diagrams/scripts/`)에서 `npm install`을 한 번 실행해야 합니다.
