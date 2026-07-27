# CLAUDE.md

이 저장소에서 Claude Code를 위한 프로젝트별 지침.

(English: Project-specific instructions for Claude Code in this repository.)

## 커밋 규칙

- 모든 커밋 메시지는 conventional-commit 타입을 붙인 한국어 제목 한 줄로 쓰고,
  빈 줄 다음에 (필요하면) 한국어 본문을, 다시 빈 줄 다음에 그 영어 번역을
  `(English: ...)` 형태로 덧붙인다. 일반 커밋, squash 커밋, 히스토리 재작성 커밋
  모두 이 형식을 따르되, 아래 Spec Kit 사후 실행 정책이 적용되는 경우는 예외로
  한다.

  (English: Write every commit message as a Korean conventional-commit subject,
  followed by a blank line, an optional Korean body, another blank line, and its
  English translation in an `(English: ...)` block. Apply this format to ordinary,
  squash, and history-rewrite commits unless the Spec Kit post-execution policy
  below applies.)

- 제목 한 줄만 읽어도 그 커밋이 **어떤 기능을 추가했는지 또는 무엇을 보완했는지**
  알 수 있게 쓴다. 건드린 파일이나 밟은 절차가 아니라, 사용자가 얻게 되는 능력의
  변화를 기준으로 기술한다.

  (English: The subject line alone must convey which capability the commit adds or
  what it improves. Describe the change in terms of the resulting user-facing
  capability, not the files touched or the process followed.)

- Spec Kit 같은 도구의 도입이나 버전 업그레이드는 기능 변경과 섞지 않고 언제나
  별도 커밋으로 분리한다.

  (English: Keep tooling changes — introducing Spec Kit, or upgrading its version —
  in their own commits, never mixed into a feature commit.)

- `.claude/` 아래(스킬, 커맨드, 에이전트 설정 등)의 변경에 conventional-commit
  타입을 고를 때는, 이 `.md`/설정 파일들이 이 저장소의 실제 산출물이지 코드에
  대한 부수적인 문서가 아님을 기억한다. 파일 확장자가 아니라 스킬 동작에 미치는
  효과로 분류한다 — 새 기능이면 `feat`, 깨지거나 불완전한 동작을 고친 것이면
  `fix`, 동작 변화 없는 재구성이면 `refactor`. `docs`는 스킬의 실제 동작에
  영향을 주지 않는 변경(이 파일 자체 편집, README 등)에만 쓴다.

  (English: When picking a conventional-commit type for changes under `.claude/`
  (skills, commands, agent configs, etc.), remember these `.md`/config files are
  this repository's actual product, not incidental documentation about code.
  Classify by the effect on skill behavior — `feat` for new capability, `fix` for
  correcting broken or incomplete behavior, `refactor` for no-behavior-change
  restructuring — not by file extension. Reserve `docs` for changes that don't
  affect what a skill actually does, such as editing this file or a README.)

- Spec Kit 스킬이 성공적으로 완료될 때마다, 실제 diff를 확인하고 그 스킬이 만든
  저장소 변경사항에 대해 정확히 커밋 하나를 완료 보고 전에 생성한다. 스킬이
  취소되었거나 실패했거나 저장소 변경이 없었다면 커밋하지 않는다. 관련 없는 기존
  변경사항은 포함하지 않는다.

  (English: After every successfully completed Spec Kit skill, inspect the actual
  diff and create exactly one commit for the repository changes produced by that
  skill before reporting completion. Do not commit when the skill was cancelled,
  failed, or made no repository changes. Do not include unrelated pre-existing
  changes.)

- Spec Kit 사후 실행 커밋은 `[Spec Kit] <Skill Name>: <간결한 한국어 제목>`
  형식으로 쓰고, 빈 줄, 실제 diff 기반의 간결한 한국어 설명, 다시 빈 줄, 그리고
  그 영어 번역 순으로 구성한다.

  (English: Format a Spec Kit post-execution commit as `[Spec Kit] <Skill Name>:
  <concise Korean title>`, a blank line, a concise Korean description based on the
  actual diff, another blank line, and its English translation.)

### 예시

일반 커밋:

```text
feat(analysis): 중단 후에도 이어서 실행할 수 있는 글 단위 라벨링 추가

(English: Add resumable article labeling)
```

Spec Kit 사후 실행 커밋:

```text
[Spec Kit] speckit-tasks: 의존성 순서를 지킨 태스크 목록 생성

구현 계획을 유저 스토리 우선순위에 따라 단계별 태스크로 분해한다.

(English: Break the implementation plan into phases and tasks, ordered by user
story priority.)
```
