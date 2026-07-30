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

**`/`를 입력해도 스킬이 목록에 안 보이나요?** Claude Code를 재시작/리로드하세요 — VS Code에서는 명령 팔레트(`Ctrl+Shift+P`, Mac은 `Cmd+Shift+P`)를 연 뒤 "Reload Window"를 입력하고 Enter를 누르면 됩니다. `.claude/skills/`의 스킬은 세션 시작 시점에 스캔되므로, 세션 도중 추가한 스킬은 다음 리로드 전까지 안 보입니다.

## 개발 히스토리

[Spec Kit](https://github.com/github/spec-kit) 스펙 기반 개발 파이프라인을 거쳐 만들어졌습니다. 아래는 개발한 순서대로입니다. 각 기능의 전체 스펙/계획/태스크 기록은 `specs/` 아래에 있습니다:

1. [`specs/001-zenuml-diagram-skill/`](specs/001-zenuml-diagram-skill/) — 위에서 설명한 핵심 스킬
2. [`specs/002-diagram-feedback-log/`](specs/002-diagram-feedback-log/) — 다이어그램을 그 자리에서 재생성하고 무엇을 왜 고쳤는지 로그로 남김

## 요구 사항

- [Claude Code](https://claude.com/product/claude-code)
- 그 외 별도 의존성 없음 — 스킬은 실행 코드가 없는 순수 Markdown 번들입니다.
