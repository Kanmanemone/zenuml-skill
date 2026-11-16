이 저장소에서 AI 코딩 에이전트(Claude Code, Codex, Gemini CLI 등)를 위한 프로젝트별 지침. 한국어와 영어 내용이 어긋나면 한국어를 따른다.

(English: Project-specific instructions for AI coding agents (Claude Code, Codex, Gemini CLI, ...) in this repository. If the Korean and English text disagree, the Korean text is authoritative.)

## 작업 흐름 (Workflow)

먼저 `.specify/memory/constitution.md`를 읽는다. 헌법은 이 파일보다
우선하며, 요청을 Spec Kit으로 진행할지와 어느 Spec에 속하는지를 정한다. Spec
Kit으로 진행하는 요청은 종류에 따라 흐름을 고른다:

- 깨진 동작 → **버그 흐름** (`bug` 확장이 설치돼 있을 때)
- 아이디어가 해볼 만한지 사용자가 묻는 경우 → **아이디어 평가**
  (`assess` 확장이 설치돼 있을 때)
- 그 외 전부 → **SDD 흐름**

명령은 각 에이전트가 제공하는 형식으로 호출한다. 형식이 달라도 단계는 같다.

(English: Read `.specify/memory/constitution.md` first. It overrides this file and
decides whether a request goes through Spec Kit at all and which Spec it
belongs to. For a request that does go through Spec Kit, choose the flow by
the kind of request:

- Broken behavior → **Bug flow** (if the `bug` extension is installed)
- The user asks whether an idea is worth pursuing → **Idea assessment**
  (if the `assess` extension is installed)
- Everything else → **SDD flow**

Invoke commands in whatever form your agent exposes them (`/speckit.specify`,
`/speckit-specify`, `$speckit-specify`, `/skill:speckit-specify`). The steps
are the same in every form.)

### SDD 흐름 (SDD flow)

`specify` → `plan` → `tasks` → `implement` → `converge` 순서로
실행한다. 요청이 모호하면 `plan` 전에 `clarify`를, `implement` 전에 `analyze`를
추가한다.

- **specify**: 무엇을, 왜 만드는지만 쓰고 기술 스택은 절대 넣지 않는다. 범위를
  구체적으로 적는다: 사용자와 역할, 작업 상태, 제외할 것, 지켜야 할 호환성
  경계. 기능은 단독으로 리뷰할 수 있는 크기로 유지한다.
- **clarify**: 초점 영역을 바꿔 가며 여러 번 실행해도 된다.
- **plan**: 구현 세부는 모두 여기에 쓴다. 기존 아키텍처, 의존성, 테스트 관례를
  재사용한다.
- **analyze**: 읽기 전용이다. 보고된 문제는 원천에서 고치고(요구사항 →
  `specify`나 `clarify`, 설계 → `plan`, 작업 → `tasks` 재생성), 깨끗해질 때까지
  다시 실행한다.
- **implement**: `tasks.md`를 의존 순서대로 실행한다. 큰 기능은 한 번에 한
  단계씩 실행하고, 검증한 뒤 다음으로 넘어간다.
- **converge**: 코드를 고치지 않고 작업을 추가하기만 한다. 작업이 추가되면
  수렴했다고 보고할 때까지 `implement`와 `converge`를 다시 실행한다.
- **checklist**: 사용자가 요청할 때만 실행한다. 체크리스트 항목은 리뷰어의
  것이다. 직접 체크하거나 표시를 바꾸지 않는다. 체크 안 된 항목 때문에
  `implement`가 멈추면 사용자에게 묻는다.

(English: Run in order: `specify` → `plan` → `tasks` → `implement` → `converge`.
When the request is ambiguous, add `clarify` before `plan` and `analyze`
before `implement`.

- **specify**: Describe what and why, never the tech stack. State the scope
  concretely: users and roles, workflow states, exclusions, and the
  compatibility boundaries that must hold. Keep the feature small enough to
  review on its own.
- **clarify**: May be run repeatedly, each time on a different focus area.
- **plan**: All implementation detail goes here. Reuse the existing
  architecture, dependencies, and test conventions.
- **analyze**: Read-only. Fix each reported problem at its source
  (requirements → `specify` or `clarify`, design → `plan`, tasks → regenerate
  `tasks`), then re-run until clean.
- **implement**: Execute `tasks.md` in dependency order. For a large feature,
  run one phase at a time and validate it before continuing.
- **converge**: It never edits code; it only appends tasks. If it appends
  any, run `implement` and `converge` again until it reports convergence.
- **checklist**: Run only when the user asks. Checklist items belong to the
  reviewer: never check them or change their markers yourself. If
  `implement` stops on unchecked items, ask the user.)

### 버그 흐름 (Bug flow)

`bug.assess` → `bug.fix` → `bug.test` 순서로 실행하고, 같은
slug(소문자 kebab-case)를 계속 쓴다.

- 소스 코드를 고치는 것은 `bug.fix`뿐이다. 평가가 있고 그 해결책이 실제로
  하려는 계획일 때만 실행한다.
- 평가에 나열된 파일 안에서만 고친다. 범위를 넓혀야 하면 그 이유를
  "Deviations from Assessment"에 기록한다.
- 판정을 부풀리지 않는다. 나열된 재현을 실행하지 않았으면 결과는
  `partial`이다. `partial`이나 `failed`는 수정 완료가 아니다.

(English: Run in order: `bug.assess` → `bug.fix` → `bug.test`, reusing one slug
(lowercase kebab-case).

- Only `bug.fix` edits source code. Run it only when the assessment exists
  and its remediation is the intended plan.
- Stay within the files the assessment lists. If the scope must widen,
  record why under "Deviations from Assessment".
- Never inflate the verdict. If a listed reproduction was not exercised, the
  result is `partial`. A `partial` or `failed` verdict is not a fix.)

### 아이디어 평가 (Idea assessment)

`assess.intake` → `assess.research` → `assess.define` →
`assess.shape` → `assess.decide` 순서로 실행하고, 같은 slug를 계속 쓴다.

- 조사에는 반대 근거도 반드시 넣는다. 출처 없는 주장은 `ASSUMPTION`으로
  표시하고, 인용을 지어내지 않는다.
- 평가는 SDD 흐름을 스스로 시작하지 않는다. `go` 판정의 인계 요약은 사용자가
  원할 때만 `specify`에 넘긴다.

(English: Run in order: `assess.intake` → `assess.research` → `assess.define` →
`assess.shape` → `assess.decide`, reusing one slug.

- Research must include evidence against the idea. Mark unsourced claims
  `ASSUMPTION` and never invent citations.
- Assessment never starts the SDD flow by itself. Pass a `go` handoff to
  `specify` only if the user chooses to.)

### 경계 (Boundaries)

- 요청 처리 중에 `constitution`을 실행하지 않는다. 사용자가 요청할 때만 고치고,
  이 저장소에서 이미 사실이거나 명시적으로 합의된 원칙만 넣는다.
- 현재 작업 중인 기능은 git 브랜치가 아니라 `.specify/feature.json`에서 읽는다.
  `git checkout`만으로는 기능이 바뀌지 않는다.
- `specify init`은 `--non-interactive`로 실행한다.

(English:

- Do not run `constitution` as part of a request. Change it only when the
  user asks, and only with principles that are already true in this
  repository or explicitly agreed.
- The active feature is read from `.specify/feature.json`, not from the git
  branch. `git checkout` alone does not switch features.
- Run `specify init` with `--non-interactive`.)

## 커밋 메시지 (Commit Messages)

모든 커밋 메시지는 squash 커밋과 히스토리 재작성 커밋을 포함해 아래 형태를
따른다:

(English: Every commit message, including squash and history-rewrite commits,
has the shape below:)

```text
<type>(<scope>): <subject in Korean>

<body in Korean, optional>

(English: <translation of the subject and body>)

<trailers, optional>
```

- **제목**: 제목만 읽어도 그 커밋이 어떤 기능을 추가했는지 또는 무엇을
  보완했는지 알 수 있어야 한다. 건드린 파일이나 밟은 절차가 아니라, 사용자가
  얻게 되는 능력의 변화를 쓴다. 한국어로 쓰고 명사나 명사구로 끝맺으며("…추가",
  "…보완"), 끝에 마침표를 찍지 않고, 줄 전체를 72자 이내로 쓴다.
- **스코프**: 선택. 영향받는 영역을 가리키는 명사. `git log`에 이미 있는
  스코프를 재사용한다.
- **본문**: 한국어로 쓴다. 어떻게가 아니라 왜 바꿨는지와 어떤 동작이 바뀌는지를 쓴다. 72열에서
  줄바꿈한다. 제목으로 충분하면 생략한다.
- **영어 번역**: 제목과 본문을 영어로 옮겨 `(English: ...)` 블록에 쓴다. 번역한
  제목은 명령형으로("added"가 아니라 "add") 소문자로 시작한다.
- **트레일러**: 항상 맨 끝에, 한 줄에 `Token: value` 하나씩 쓴다(예:
  `Refs: #12`). 그래야 git이 파싱할 수 있다.
- **호환성을 깨는 변경**: 콜론 앞에 `!`를 붙이고 `BREAKING CHANGE: <깨지는 것>`
  트레일러를 추가한다.
- **Spec Kit 커밋**: Spec Kit 명령 하나가 만든 결과를 기록하는 커밋은
  `<type>(<scope>)` 자리에 `[Spec Kit] <스킬 이름>`을 쓴다(예:
  `[Spec Kit] speckit-tasks: …`). 본문은 실제 diff를 근거로 쓴다. 나머지 규칙은
  위와 같다.

(English:

- **Subject**: Conveys, on its own, which capability the commit adds or what
  it improves. Describe the resulting user-facing capability, not the files
  touched or the process followed. Write it in Korean, end it with a noun or
  noun phrase ("…추가", "…보완"), omit the trailing period, and keep the
  whole line within 72 characters.
- **Scope**: Optional. A noun naming the affected area; reuse scopes already
  present in `git log`.
- **Body**: Written in Korean. Explain why the change was made and what behavior changes, not
  how. Wrap at 72 columns. Omit it when the subject says everything.
- **English translation**: Translate the subject and body into English in
  an `(English: ...)` block. Write the translated subject in the imperative
  mood ("add", not "added"), starting lowercase.
- **Trailers**: Always last, one `Token: value` per line (e.g. `Refs: #12`),
  so git can parse them.
- **Breaking change**: Put `!` before the colon and add a
  `BREAKING CHANGE: <what breaks>` trailer.
- **Spec Kit commits**: A commit that records what one Spec Kit command
  produced replaces `<type>(<scope>)` with `[Spec Kit] <skill name>` (e.g.
  `[Spec Kit] speckit-tasks: …`). Base its body on the actual diff. Every
  other rule above still applies.)

### 타입 (Types)

타입은 변경의 성격으로 고른다:

- `feat`: 새 기능.
- `fix`: 깨지거나 불완전한 동작을 고친 것.
- `refactor`: 동작 변화 없는 재구성.
- `perf`: 다른 동작 변화 없이 더 빠르거나 가볍게 만든 것.
- `test`: 테스트만 추가하거나 고친 것.
- `docs`: 스킬의 실제 동작에 영향을 주지 않는 변경(이 파일 자체 편집, README
  등)에만 쓴다.
- `style`: 포맷팅만 바꾼 것.
- `build` / `ci`: 빌드 시스템이나 의존성 / CI 설정.
- `chore`: 위 어디에도 맞지 않는 유지보수.
- `revert`: push된 커밋을 `git revert`로 되돌린 것. 본문에 되돌린 SHA를
  적는다.

(English: Choose the type by what the change does:

- `feat`: a new capability.
- `fix`: corrects broken or incomplete behavior.
- `refactor`: restructuring with no behavior change.
- `perf`: faster or lighter, with no other behavior change.
- `test`: adds or corrects tests only.
- `docs`: only for changes that do not affect the skill's actual behavior
  (editing this file itself, README, etc.).
- `style`: formatting only.
- `build` / `ci`: build system or dependencies / CI configuration.
- `chore`: maintenance that fits none of the above.
- `revert`: undoes a pushed commit with `git revert`; name the reverted SHA
  in the body.)

### 예시 (Examples)

```text
feat(analysis): 중단 후에도 이어서 실행할 수 있는 글 단위 라벨링 추가

(English: add resumable article labeling)
```

```text
feat(export)!: 라벨을 JSON Lines로 출력

각 라벨을 생성 즉시 기록하므로, 큰 실행도 메모리에 다 올릴 필요가 없다.

(English: write labels as JSON Lines

Large runs no longer have to fit in memory, because each label is
flushed as soon as it is produced.)

BREAKING CHANGE: the export file is no longer a single JSON array
Refs: #12
```

```text
[Spec Kit] speckit-tasks: 의존성 순서를 지킨 태스크 목록 생성

구현 계획을 유저 스토리 우선순위에 따라 단계별 태스크로 분해한다.

(English: generate a dependency-ordered task list

Break the implementation plan into phases and tasks, ordered by user
story priority.)
```

## 커밋 히스토리 (Commit History)

커밋 히스토리를 사람이 읽기 좋게 최적화하라. 커밋 단위는 **원자적
커밋**, 즉 하나의 완결된 논리적 변경이다. 같은 주제라는 것만으로는 합칠 이유가
되지 않는다.

원자적 커밋의 조건: 단독으로 빌드와 테스트가 통과한다. 독립적으로 revert할 수
있다. 제목을 "그리고" 없이 한 문장으로 쓸 수 있다. 리팩터링과 동작 변경,
포맷팅과 로직 변경을 섞지 않는다.

(English: Optimize the commit history for human readers. The unit of a commit is an
**atomic commit**: one complete, self-contained logical change. Belonging to
the same topic is not by itself a reason to combine changes.

A commit is atomic when: it builds and passes tests on its own; it can be
reverted independently; its subject is one sentence without "and"; it never
mixes refactoring with behavior changes, or formatting with logic.)

### 작업 중 (While working)

- 그 커밋에 속하는 파일만 경로를 지정해 stage한다. `git add -A`는 쓰지 않는다.
- `--no-verify`로 훅을 건너뛰지 않는다.
- push 안 된 커밋에 한해:
  - HEAD의 연장이나 수정이면 → `git commit --amend`
  - 더 앞선 커밋에 속하면 → `git commit --fixup=<sha>`
  - 그 외에는 → 새 커밋

(English:

- Stage files by path, only those that belong to the commit; never
  `git add -A`.
- Never skip hooks with `--no-verify`.
- For unpushed commits only:
  - Continuation or fix of HEAD → `git commit --amend`
  - Belongs to an earlier commit → `git commit --fixup=<sha>`
  - Otherwise → new commit)

### push하기 전마다 (Before every push)

`git log --oneline @{u}..HEAD`를 확인하고(upstream이 없으면 기본
브랜치와 비교) 다시 써라:

- 관련 커밋을 인접시키고, 합친 결과가 여전히 원자적일 때만 합쳐라.
  예: `A, B, A', C, B'` → `A+A', B+B', C`.
- 의존 순서를 우선하되 병합된 그룹 단위로 판단하고, 그 외에는 처음 등장한
  순서를 유지하라. 예: A가 B에 의존하면 → `B+B', A+A', C`.
- 아직 기본 브랜치에 없는 기능은 Spec Kit 단계별 중간 커밋을 단계마다 하나로
  합쳐라: `specify`(그 `clarify` 수정 포함), `plan`, `tasks`, `analyze`,
  `implement`(그 `converge` 반복 포함).
- 합쳤을 때 순환 의존이 생기면 분리해 둬라. 커밋 수보다 올바른 순서가 우선이다.
- 합친 커밋의 메시지는 합쳐진 전체 변경을 설명해야 한다.
- 순 변경이 0인 변경(+-0)은 처음부터 없었던 것처럼 지워라. 서로 상쇄되는
  커밋들(순서를 바꿨다가 되돌린 것, 변경과 그 revert, 추가했다가 삭제한 것)은
  모두 버린다. 합친 결과가 빈 커밋이 되어도 버린다.
- 대화형 rebase를 쓸 수 없으니 비대화형으로 실행하라:
  `GIT_SEQUENCE_EDITOR=true git rebase -i --autosquash <base>`, 또는 todo
  파일을 작성한 뒤
  `GIT_SEQUENCE_EDITOR="cp /tmp/rebase-todo" git rebase -i <base>`.

(English: Review `git log --oneline @{u}..HEAD` (with no upstream, compare against the
default branch) and rewrite:

- Make related commits adjacent, and squash them only if the result is still
  atomic. E.g. `A, B, A', C, B'` → `A+A', B+B', C`.
- Order by dependency, judged at the merged-group level; otherwise keep the
  order of first appearance. E.g. if A depends on B → `B+B', A+A', C`.
- For a feature not yet on the default branch, squash the intermediate
  commits of each Spec Kit step into one commit per step: `specify`
  (including its `clarify` edits), `plan`, `tasks`, `analyze`, `implement`
  (including its `converge` rounds).
- If squashing would create a circular dependency, keep the commits separate.
  Correct order matters more than fewer commits.
- A squashed commit's message describes the combined change.
- Erase net-zero changes as if they never happened. If commits cancel each
  other out (a reorder and its reversal, a change and its revert, something
  added and then removed), drop all of them. Drop a squash that ends up
  empty.
- Interactive rebase is unavailable, so run it non-interactively:
  `GIT_SEQUENCE_EDITOR=true git rebase -i --autosquash <base>`, or write a
  todo file and run
  `GIT_SEQUENCE_EDITOR="cp /tmp/rebase-todo" git rebase -i <base>`.)

### 안전 규칙 (Safety)

이 규칙들은 위의 모든 규칙보다 우선한다.

- 사용자가 명시적으로 요청하지 않는 한 push된 커밋을 다시 쓰거나 force-push하지
  마라. 요청받았을 때는 `--force`가 아니라 `--force-with-lease`를 써라.
- 먼저 `BEFORE=$(git rev-parse HEAD)`로 HEAD를 저장하라. 다시 쓴 뒤
  `git diff --quiet $BEFORE HEAD`가 통과해야 하고, 실패하면
  `git reset --hard $BEFORE`로 되돌린 뒤 보고하라.
- 간단히 풀 수 없는 충돌이 나면 `git rebase --abort`로 중단하고 보고하라.
- 관련 여부가 불확실하면 분리해 둬라.

(English: These rules override everything above.

- Never rewrite pushed commits or force-push unless the user explicitly asks.
  When asked, use `--force-with-lease`, never `--force`.
- Save `BEFORE=$(git rev-parse HEAD)` first. After rewriting,
  `git diff --quiet $BEFORE HEAD` must pass; if it fails, run
  `git reset --hard $BEFORE` and report.
- On a non-trivial conflict, run `git rebase --abort` and report.
- If unsure whether commits are related, keep them separate.)
