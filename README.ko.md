# zenuml-skill

**언어:** [English](README.md) | 한국어

자연어로 설명한 프로세스를 정확하고 군더더기 없는 [ZenUML](https://github.com/mermaid-js/zenuml-core) 시퀀스 다이어그램 DSL로 바꿔주는 Claude Code 스킬 `generating-zenuml-diagrams`가 담긴 프로젝트입니다. 설명에 없는 참가자·메시지·분기는 지어내지 않습니다.

## 구성

```text
.claude/skills/generating-zenuml-diagrams/
├── SKILL.md          # skill instructions
└── references/
    └── syntax.md     # syntax reference
```

- **SKILL.md** — 생성 규칙, 예시, 안티-fluff 자기검증, 모호한 입력 처리
- **references/syntax.md** — ZenUML DSL 문법 레퍼런스, mermaid-js/zenuml-core 재구성, MIT
- **`.zenuml/`** — 처음 다이어그램을 생성할 때 여러분 프로젝트 루트에 생기는 폴더로, 결과물이 여기에 저장됩니다. 방금 받은 다이어그램을 고쳐달라고 하면 새 파일이 아니라 같은 파일이 갱신되고, 무엇을 왜 고쳤는지에 대한 전체 이력은 `.zenuml/log/`에 남습니다.

## 사용법

> [!CAUTION]
> **[`.claude/skills/generating-zenuml-diagrams/`](.claude/skills/generating-zenuml-diagrams/) 폴더만 복사하세요 — 프로젝트 전체를 복사하면 안 됩니다.**

1. [`.claude/skills/generating-zenuml-diagrams/`](.claude/skills/generating-zenuml-diagrams/) 폴더를 여러분 프로젝트의 `.claude/skills/`에 복사하세요.
2. Claude Code에서 `/generating-zenuml-diagrams <프로세스 설명>`을 실행하세요.

**예시:**

```text
/generating-zenuml-diagrams the client calls Server.getData()
```

새로 추가한 스킬이 `/` 목록에 안 보인다면 Claude Code를 재시작하거나, VS Code 명령 팔레트(`Ctrl+Shift+P`, Mac은 `Cmd+Shift+P`)에서 "Reload Window"를 실행하세요 — 스킬은 세션 시작 시점에만 스캔됩니다.

## 추가 기능

아래는 각각 독립된 스킬입니다 — 필요한 것만 `.claude/skills/`에 복사하세요. 핵심 스킬을 포함한 모든 스킬은 자기 폴더의 `settings.jsonc`를 읽으므로, 그 파일을 고쳐 동작을 바꿀 수 있습니다(각 옵션 위에 한국어 설명 주석이 있습니다):

- **[`generating-architecture-views`](.claude/skills/generating-architecture-views/)** — 구조 뷰(컴포넌트·그룹·의존관계)를 추가합니다. Dependency 다이어그램에 특정 Mermaid 렌더러(예: `elk`)를 쓰고 싶다면 요청에 그렇게 명시하세요 — 다이어그램 YAML `config`에 `layout`이 추가됩니다(스킬의 `settings.jsonc`에서 `dependency.renderer`로 기본값을 정할 수도 있습니다). 명시하지 않으면 추가되지 않습니다. VS Code Markdown 미리보기에서 Dependency 다이어그램의 노드에 마우스를 올리면, 그 노드의 Responsibility와 그 노드가 의존하는 Collaboration이 패널로 떠서 본문까지 스크롤하지 않아도 됩니다. 패널 내용은 구조 뷰를 저장한 뒤 번들 Python 스크립트가 본문에서 옮겨 채우므로 토큰이 더 들지 않습니다. 패널에 넣을 항목과 위치(미리보기 아래쪽 또는 노드 바로 아래)는 `settings.jsonc`의 `hover` 그룹에서 정하고, `hover.enabled`로 끌 수 있습니다. GitHub 등 다른 뷰어에서는 동작하지 않습니다.
- **[`exporting-markdown-diagrams`](.claude/skills/exporting-markdown-diagrams/)** — 다이어그램을 SVG/PNG로, 마크다운 파일 전체를 PDF(다이어그램은 텍스트 선택 가능한 벡터로 삽입)나 PNG로 변환합니다. 변환은 항상 번들 스크립트(mermaid-cli)로만 이뤄지고 LLM 추론을 거치지 않습니다. 그 스크립트가 쓰는 의존성을 받기 위해 `scripts/` 폴더에서 `npm install`을 한 번 실행하세요. 결과 파일은 원본과 같은 디렉토리가 아니라 그 아래 `exports/`(자동 생성)에 모입니다.

## 개발

각 기능의 스펙/계획/태스크 기록은 [`specs/`](specs/) 아래에 있습니다.

## 요구 사항

- [Claude Code](https://claude.com/product/claude-code)
- `generating-zenuml-diagrams`는 그 외 별도 의존성 없음 — 실행 코드가 없는 순수 Markdown 번들입니다.
- `generating-architecture-views`는 노드 hover 패널에 PC에 이미 있는 [Python](https://www.python.org/) 3.9 이상(`python3`, `python`, `py -3` 순으로 찾음)을 씁니다. 번들 스크립트(`.claude/skills/generating-architecture-views/scripts/`)는 표준 라이브러리만 써서 따로 설치할 것이 없습니다. Python이 없어도 구조 뷰는 만들어지고, hover 패널만 빠집니다.
- `exporting-markdown-diagrams`는 [Node.js](https://nodejs.org/)가 필요합니다 — 번들 스크립트(`.claude/skills/exporting-markdown-diagrams/scripts/`)에서 `npm install`을 한 번 실행해야 합니다.
