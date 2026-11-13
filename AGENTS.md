# AGENTS.md

이 저장소에서 AI 코딩 에이전트(Claude Code, Codex, Gemini CLI 등)를 위한 프로젝트별 지침.

(English: Project-specific instructions for AI coding agents (Claude Code, Codex, Gemini CLI, ...) in this repository.)

## 커밋 규칙

- 모든 커밋 메시지는 conventional-commit 타입을 붙인 한국어 제목 한 줄로
  쓰고, 빈 줄 다음에 (필요하면) 한국어 본문을, 다시 빈 줄 다음에 그 영어 번역을
  `(English: ...)` 형태로 덧붙인다. 일반 커밋, squash 커밋, 히스토리 재작성 커밋
  모두 이 형식을 따른다.

  (English: Write every commit message as a Korean conventional-commit subject,
  followed by a blank line, an optional Korean body, another blank line, and
  its English translation in an `(English: ...)` block. Apply this format to
  ordinary, squash, and history-rewrite commits.)

- 제목 한 줄만 읽어도 그 커밋이 **어떤 기능을 추가했는지 또는 무엇을
  보완했는지** 알 수 있게 쓴다. 건드린 파일이나 밟은 절차가 아니라, 사용자가
  얻게 되는 능력의 변화를 기준으로 기술한다.

  (English: The subject line alone must convey which capability the commit adds or what
  it improves. Describe the change in terms of the resulting user-facing
  capability, not the files touched or the process followed.)

### 예시

```text
feat(analysis): 중단 후에도 이어서 실행할 수 있는 글 단위 라벨링 추가

(English: add resumable article labeling)
```
