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
> **[`.agents/skills/`](.agents/skills/) 아래의 스킬 폴더만 설치하세요 — 프로젝트 전체를 복사하면 안 됩니다.**

스킬은 네 개이고, `revealing-code-step-by-step`이 `generating-architecture-views`의 구조 뷰를 읽는 것을 빼면 각각 따로 동작합니다. 자세한 설명은 아래 "추가 기능"에 있습니다.

- **[`generating-zenuml-diagrams`](.agents/skills/generating-zenuml-diagrams/)** — 말로 설명한 프로세스를 [ZenUML](https://github.com/mermaid-js/zenuml-core) 시퀀스 다이어그램으로 바꿉니다. 말하지 않은 참여자나 메시지를 지어내지 않습니다. 다른 준비물이 없습니다.
- **[`generating-architecture-views`](.agents/skills/generating-architecture-views/)** — 시스템의 구조 뷰(구성 요소·그룹·의존)를 그리고, 구성 요소마다 책임과 원본 링크를 붙입니다. 마우스오버 패널에 Python 3.9 이상을 씁니다(없어도 됨).
- **[`exporting-markdown-diagrams`](.agents/skills/exporting-markdown-diagrams/)** — Markdown 파일 속 다이어그램을 SVG/PNG로, 파일 전체를 PDF/PNG로 번들 스크립트가 변환합니다. Node.js가 필요하고, npm 패키지는 설치 명령이나 첫 사용 때 스킬이 `scripts/` 폴더에 설치합니다.
- **[`revealing-code-step-by-step`](.agents/skills/revealing-code-step-by-step/)** — 구조 뷰 뒤의 코드를 사용 상황에서 원본까지 한 겹씩 펼쳐 보여 줍니다. Python 3.9 이상과 `generating-architecture-views`로 만든 구조 뷰가 필요합니다.

아래 두 방법 가운데 하나로 설치한 뒤 실행하세요("스킬 실행" 참고).

### 내려받아 복사해서 설치

1. [저장소를 ZIP으로](https://github.com/Kanmanemone/zenuml-skill/archive/refs/heads/main.zip) 내려받아(GitHub의 **Code → Download ZIP**도 같음) 압축을 푸세요.
2. 압축을 푼 폴더의 `.agents/skills/`에서 원하는 스킬의 폴더를 — 전부라면 네 개 모두 — 여러분 프로젝트의 `.claude/skills/`(Claude Code) 또는 `.agents/skills/`(Codex 등 [Agent Skills](https://agentskills.io) 폴더를 읽는 에이전트)에 복사하세요.
   - 이름이 `.`으로 시작하는 폴더는 macOS Finder에서 숨겨집니다. `Cmd+Shift+.`을 누르면 보입니다.
   - `.claude/skills/`가 아니라 `.agents/skills/`에서 복사하세요. 이 저장소의 `.claude/skills/<이름>`은 링크라서 ZIP에는 그대로 담기지 않습니다.

### 터미널에 붙여넣어 설치

프로젝트 루트 폴더에서 아래 명령 가운데 하나를 붙여넣으세요. 스킬을 `.agents/skills/`에 내려받고 `.claude/skills/<이름>`에 각각을 가리키는 링크를 만들어, Claude Code와 다른 에이전트가 같은 파일을 읽게 합니다. 이 저장소와 같은 구조입니다.

#### 1. 모든 스킬 전부

**macOS / Linux**

```bash
t=; curl -fsSL -o z.tgz https://github.com/Kanmanemone/zenuml-skill/archive/refs/heads/main.tar.gz && mkdir -p .agents && t=$(mktemp -d .agents/zenuml-tmp.XXXXXX) && { tar -xzf z.tgz -C "$t" --strip-components=3 zenuml-skill-main/.agents/skills || { rm -rf "$t"; t=; }; }; rm -f z.tgz
if [ -n "$t" ]; then mkdir -p .agents/skills .claude/skills; for s in $(ls "$t"); do if [ -d .agents/skills/$s ]; then mkdir -p .agents/skills-backup && mv .agents/skills/$s .agents/skills-backup/$s-$(date +%Y%m%d%H%M%S); fi; mv "$t/$s" .agents/skills/$s && ln -sfn ../../.agents/skills/$s .claude/skills/$s; done; rm -rf "$t"; fi
if [ -d .agents/skills/exporting-markdown-diagrams/scripts ] && command -v npm >/dev/null; then npm ci --no-audit --no-fund --prefix .agents/skills/exporting-markdown-diagrams/scripts; fi
```

**Windows (PowerShell)**

```powershell
$t = $null; curl.exe -fsSL -o z.tgz https://github.com/Kanmanemone/zenuml-skill/archive/refs/heads/main.tar.gz; if ($?) { $t = (mkdir ".agents\zenuml-tmp-$(New-Guid)").FullName; tar -xzf z.tgz -C $t --strip-components=3 zenuml-skill-main/.agents/skills; if (!$?) { rmdir -Recurse $t; $t = $null }; del z.tgz }
if ($t) { mkdir -Force .agents\skills, .claude\skills >$null; foreach ($s in (dir $t -Directory).Name) { if (Test-Path .agents\skills\$s) { mkdir -Force .agents\skills-backup >$null; move .agents\skills\$s .agents\skills-backup\$s-$(Get-Date -f yyyyMMddHHmmss) }; move $t\$s .agents\skills\$s; cmd /c "rmdir .claude\skills\$s 2>nul & (mklink /D .claude\skills\$s ..\..\.agents\skills\$s 2>nul || mklink /J .claude\skills\$s .agents\skills\$s) >nul" }; rmdir -Recurse $t }
if ((Test-Path .agents\skills\exporting-markdown-diagrams\scripts) -and (Get-Command npm.cmd -ErrorAction SilentlyContinue)) { npm.cmd ci --no-audit --no-fund --prefix .agents\skills\exporting-markdown-diagrams\scripts }
```

#### 2. `generating-zenuml-diagrams`

**macOS / Linux**

```bash
t=; curl -fsSL -o z.tgz https://github.com/Kanmanemone/zenuml-skill/archive/refs/heads/main.tar.gz && mkdir -p .agents && t=$(mktemp -d .agents/zenuml-tmp.XXXXXX) && { tar -xzf z.tgz -C "$t" --strip-components=3 zenuml-skill-main/.agents/skills/generating-zenuml-diagrams || { rm -rf "$t"; t=; }; }; rm -f z.tgz
if [ -n "$t" ]; then mkdir -p .agents/skills .claude/skills; for s in $(ls "$t"); do if [ -d .agents/skills/$s ]; then mkdir -p .agents/skills-backup && mv .agents/skills/$s .agents/skills-backup/$s-$(date +%Y%m%d%H%M%S); fi; mv "$t/$s" .agents/skills/$s && ln -sfn ../../.agents/skills/$s .claude/skills/$s; done; rm -rf "$t"; fi
```

**Windows (PowerShell)**

```powershell
$t = $null; curl.exe -fsSL -o z.tgz https://github.com/Kanmanemone/zenuml-skill/archive/refs/heads/main.tar.gz; if ($?) { $t = (mkdir ".agents\zenuml-tmp-$(New-Guid)").FullName; tar -xzf z.tgz -C $t --strip-components=3 zenuml-skill-main/.agents/skills/generating-zenuml-diagrams; if (!$?) { rmdir -Recurse $t; $t = $null }; del z.tgz }
if ($t) { mkdir -Force .agents\skills, .claude\skills >$null; foreach ($s in (dir $t -Directory).Name) { if (Test-Path .agents\skills\$s) { mkdir -Force .agents\skills-backup >$null; move .agents\skills\$s .agents\skills-backup\$s-$(Get-Date -f yyyyMMddHHmmss) }; move $t\$s .agents\skills\$s; cmd /c "rmdir .claude\skills\$s 2>nul & (mklink /D .claude\skills\$s ..\..\.agents\skills\$s 2>nul || mklink /J .claude\skills\$s .agents\skills\$s) >nul" }; rmdir -Recurse $t }
```

#### 3. `generating-architecture-views`

**macOS / Linux**

```bash
t=; curl -fsSL -o z.tgz https://github.com/Kanmanemone/zenuml-skill/archive/refs/heads/main.tar.gz && mkdir -p .agents && t=$(mktemp -d .agents/zenuml-tmp.XXXXXX) && { tar -xzf z.tgz -C "$t" --strip-components=3 zenuml-skill-main/.agents/skills/generating-architecture-views || { rm -rf "$t"; t=; }; }; rm -f z.tgz
if [ -n "$t" ]; then mkdir -p .agents/skills .claude/skills; for s in $(ls "$t"); do if [ -d .agents/skills/$s ]; then mkdir -p .agents/skills-backup && mv .agents/skills/$s .agents/skills-backup/$s-$(date +%Y%m%d%H%M%S); fi; mv "$t/$s" .agents/skills/$s && ln -sfn ../../.agents/skills/$s .claude/skills/$s; done; rm -rf "$t"; fi
```

**Windows (PowerShell)**

```powershell
$t = $null; curl.exe -fsSL -o z.tgz https://github.com/Kanmanemone/zenuml-skill/archive/refs/heads/main.tar.gz; if ($?) { $t = (mkdir ".agents\zenuml-tmp-$(New-Guid)").FullName; tar -xzf z.tgz -C $t --strip-components=3 zenuml-skill-main/.agents/skills/generating-architecture-views; if (!$?) { rmdir -Recurse $t; $t = $null }; del z.tgz }
if ($t) { mkdir -Force .agents\skills, .claude\skills >$null; foreach ($s in (dir $t -Directory).Name) { if (Test-Path .agents\skills\$s) { mkdir -Force .agents\skills-backup >$null; move .agents\skills\$s .agents\skills-backup\$s-$(Get-Date -f yyyyMMddHHmmss) }; move $t\$s .agents\skills\$s; cmd /c "rmdir .claude\skills\$s 2>nul & (mklink /D .claude\skills\$s ..\..\.agents\skills\$s 2>nul || mklink /J .claude\skills\$s .agents\skills\$s) >nul" }; rmdir -Recurse $t }
```

#### 4. `exporting-markdown-diagrams`

**macOS / Linux**

```bash
t=; curl -fsSL -o z.tgz https://github.com/Kanmanemone/zenuml-skill/archive/refs/heads/main.tar.gz && mkdir -p .agents && t=$(mktemp -d .agents/zenuml-tmp.XXXXXX) && { tar -xzf z.tgz -C "$t" --strip-components=3 zenuml-skill-main/.agents/skills/exporting-markdown-diagrams || { rm -rf "$t"; t=; }; }; rm -f z.tgz
if [ -n "$t" ]; then mkdir -p .agents/skills .claude/skills; for s in $(ls "$t"); do if [ -d .agents/skills/$s ]; then mkdir -p .agents/skills-backup && mv .agents/skills/$s .agents/skills-backup/$s-$(date +%Y%m%d%H%M%S); fi; mv "$t/$s" .agents/skills/$s && ln -sfn ../../.agents/skills/$s .claude/skills/$s; done; rm -rf "$t"; fi
if [ -d .agents/skills/exporting-markdown-diagrams/scripts ] && command -v npm >/dev/null; then npm ci --no-audit --no-fund --prefix .agents/skills/exporting-markdown-diagrams/scripts; fi
```

**Windows (PowerShell)**

```powershell
$t = $null; curl.exe -fsSL -o z.tgz https://github.com/Kanmanemone/zenuml-skill/archive/refs/heads/main.tar.gz; if ($?) { $t = (mkdir ".agents\zenuml-tmp-$(New-Guid)").FullName; tar -xzf z.tgz -C $t --strip-components=3 zenuml-skill-main/.agents/skills/exporting-markdown-diagrams; if (!$?) { rmdir -Recurse $t; $t = $null }; del z.tgz }
if ($t) { mkdir -Force .agents\skills, .claude\skills >$null; foreach ($s in (dir $t -Directory).Name) { if (Test-Path .agents\skills\$s) { mkdir -Force .agents\skills-backup >$null; move .agents\skills\$s .agents\skills-backup\$s-$(Get-Date -f yyyyMMddHHmmss) }; move $t\$s .agents\skills\$s; cmd /c "rmdir .claude\skills\$s 2>nul & (mklink /D .claude\skills\$s ..\..\.agents\skills\$s 2>nul || mklink /J .claude\skills\$s .agents\skills\$s) >nul" }; rmdir -Recurse $t }
if ((Test-Path .agents\skills\exporting-markdown-diagrams\scripts) -and (Get-Command npm.cmd -ErrorAction SilentlyContinue)) { npm.cmd ci --no-audit --no-fund --prefix .agents\skills\exporting-markdown-diagrams\scripts }
```

#### 5. `revealing-code-step-by-step`

**macOS / Linux**

```bash
t=; curl -fsSL -o z.tgz https://github.com/Kanmanemone/zenuml-skill/archive/refs/heads/main.tar.gz && mkdir -p .agents && t=$(mktemp -d .agents/zenuml-tmp.XXXXXX) && { tar -xzf z.tgz -C "$t" --strip-components=3 zenuml-skill-main/.agents/skills/revealing-code-step-by-step || { rm -rf "$t"; t=; }; }; rm -f z.tgz
if [ -n "$t" ]; then mkdir -p .agents/skills .claude/skills; for s in $(ls "$t"); do if [ -d .agents/skills/$s ]; then mkdir -p .agents/skills-backup && mv .agents/skills/$s .agents/skills-backup/$s-$(date +%Y%m%d%H%M%S); fi; mv "$t/$s" .agents/skills/$s && ln -sfn ../../.agents/skills/$s .claude/skills/$s; done; rm -rf "$t"; fi
```

**Windows (PowerShell)**

```powershell
$t = $null; curl.exe -fsSL -o z.tgz https://github.com/Kanmanemone/zenuml-skill/archive/refs/heads/main.tar.gz; if ($?) { $t = (mkdir ".agents\zenuml-tmp-$(New-Guid)").FullName; tar -xzf z.tgz -C $t --strip-components=3 zenuml-skill-main/.agents/skills/revealing-code-step-by-step; if (!$?) { rmdir -Recurse $t; $t = $null }; del z.tgz }
if ($t) { mkdir -Force .agents\skills, .claude\skills >$null; foreach ($s in (dir $t -Directory).Name) { if (Test-Path .agents\skills\$s) { mkdir -Force .agents\skills-backup >$null; move .agents\skills\$s .agents\skills-backup\$s-$(Get-Date -f yyyyMMddHHmmss) }; move $t\$s .agents\skills\$s; cmd /c "rmdir .claude\skills\$s 2>nul & (mklink /D .claude\skills\$s ..\..\.agents\skills\$s 2>nul || mklink /J .claude\skills\$s .agents\skills\$s) >nul" }; rmdir -Recurse $t }
```

각 명령은 세 가지 일을 하므로, 같은 명령을 다시 붙여넣는 것이 곧 업데이트입니다.

1. 최신판을 내려받아 `.agents/` 아래 임시 폴더에 풉니다. 둘 중 하나라도 실패하면 아무것도 바꾸지 않고 멈춥니다.
2. 그 스킬의 기존 폴더가 있으면 `.agents/skills-backup/<이름>-<날짜시각>`으로 옮긴 뒤, 새 스킬을 `.agents/skills/<이름>`으로 옮깁니다. 이 저장소에서 지운 파일이 남지 않습니다. 아무것도 지우지 않으므로, 스킬 폴더에 직접 넣어 둔 파일과 고친 `settings.jsonc`는 그 백업에 그대로 남습니다.
3. `.claude/skills/<이름>`이 그 폴더를 가리키도록 링크를 다시 만듭니다.

- 모든 스킬 명령은 그 시점에 저장소에 있는 스킬을 모두 설치하므로, 나중에 추가된 스킬은 다음 업데이트 때 함께 들어오고, 이 저장소에서 빠진 스킬은 직접 지울 때까지 프로젝트에 남습니다.
- 업데이트한 뒤 고친 설정이 있었다면 백업에서 옮겨 오고, 필요 없어진 백업은 지우세요. 백업은 `.agents/skills/` 밖에 있으므로 에이전트가 같은 스킬을 둘로 읽지 않습니다.
- `exporting-markdown-diagrams`를 업데이트하면 `node_modules`도 백업으로 옮겨집니다. npm이 있으면 업데이트 명령이 다시 설치하고, 없으면 첫 사용 때 스킬이 설치합니다.
- Windows에서는 먼저 상대 경로 심볼릭 링크(`mklink /D`)를 만들어 봅니다. 이것은 개발자 모드나 관리자 권한이 필요합니다. 실패하면 대신 디렉터리 정션(`mklink /J`)을 만드는데, 정션은 권한이 필요 없지만 절대 경로를 담으므로 프로젝트 폴더를 옮겼다면 명령을 다시 붙여넣으세요.

### 스킬 실행

Claude Code에서 `/generating-zenuml-diagrams <프로세스 설명>`을 실행하세요.

**예시:**

```text
/generating-zenuml-diagrams the client calls Server.getData()
```

새로 추가한 스킬이 `/` 목록에 안 보인다면 Claude Code를 재시작하거나, VS Code 명령 팔레트(`Ctrl+Shift+P`, Mac은 `Cmd+Shift+P`)에서 "Reload Window"를 실행하세요 — 스킬은 세션 시작 시점에만 스캔됩니다.

## 추가 기능

아래는 각각 독립된 스킬이며, "사용법"에 스킬마다 설치 명령이 있습니다(명령 1은 모든 스킬을 설치). 핵심 스킬을 포함한 모든 스킬은 자기 폴더의 `settings.jsonc`를 읽으므로, 그 파일을 고쳐 동작을 바꿀 수 있습니다(각 옵션 위에 한국어 설명 주석이 있습니다):

- **[`generating-architecture-views`](.agents/skills/generating-architecture-views/)** — 구조 뷰(컴포넌트·그룹·의존관계)를 추가합니다. Dependency 다이어그램에 특정 Mermaid 렌더러(예: `elk`)를 쓰고 싶다면 요청에 그렇게 명시하세요 — 다이어그램 YAML `config`에 `layout`이 추가됩니다(스킬의 `settings.jsonc`에서 `dependency.renderer`로 기본값을 정할 수도 있습니다). 명시하지 않으면 추가되지 않습니다. VS Code Markdown 미리보기에서 Dependency 다이어그램의 노드에 마우스를 올리면, 그 노드의 Responsibility와 그 노드가 의존하는 Collaboration이 패널로 떠서 본문까지 스크롤하지 않아도 됩니다. 패널 내용은 구조 뷰를 저장한 뒤 번들 Python 스크립트가 본문에서 옮겨 채우므로 토큰이 더 들지 않습니다. 패널에 넣을 항목과 위치(미리보기 아래쪽 또는 노드 바로 아래)는 `settings.jsonc`의 `hover` 그룹에서 정하고, `hover.enabled`로 끌 수 있습니다. GitHub 등 다른 뷰어에서는 동작하지 않습니다.
- **[`exporting-markdown-diagrams`](.agents/skills/exporting-markdown-diagrams/)** — 다이어그램을 SVG/PNG로, 마크다운 파일 전체를 PDF(다이어그램은 텍스트 선택 가능한 벡터로 삽입)나 PNG로 변환합니다. 변환은 항상 번들 스크립트(mermaid-cli)로만 이뤄지고 LLM 추론을 거치지 않습니다. 그 스크립트가 쓰는 npm 패키지는 lock 파일대로 `scripts/` 폴더에 설치됩니다. npm이 있으면 설치 명령이, 없으면 첫 실행 때 스킬이 묻지 않고 설치합니다. 결과 파일은 원본과 같은 디렉토리가 아니라 그 아래 `exports/`(자동 생성)에 모입니다.
- **[`revealing-code-step-by-step`](.agents/skills/revealing-code-step-by-step/)** — **먼저 `generating-architecture-views`로 만든 구조 뷰(`.zenuml/<slug>.architecture.md`)가 있어야 합니다.** 구조 뷰의 노드·원본 링크·Responsibility·Collaboration을 읽으므로 그 스킬을 먼저 실행하세요. 구조 뷰를 받아, 노드마다 원본 코드를 *정제 단계*로 넘겨 보는 문서를 만듭니다. 노드의 책임 한 줄을 상자 위에 고정해 두고, 사용 상황 → 모든 단계를 번호 붙은 자리표시자로 보이는 윤곽(안쪽 단계는 감싸는 단계 아래에 들여 씀) → 원본을 한 겹씩 펼치기 순서로 보여 줍니다. 그래서 람다가 여러 겹 든 호출도 한 장면에 몰려 나오지 않습니다. 원본을 스코프 트리로 나누고, 각 줄을 한 번씩만 보이고, 모든 코드 장면을 만드는 것은 스크립트입니다. 에이전트는 안쪽 스코프부터 하나씩 목적 문장과 함께 열 자식만 정합니다. 첫 상황은 원본을 보지 않은 별도 에이전트가 씁니다. VS Code Markdown 미리보기에서 노드마다 상자 하나를 ← →로 넘기며, 직전 단계와 달라진 줄은 VS Code의 git 변경 표시처럼 칠해집니다(추가 초록, 변경 파랑, 삭제 빨간 삼각형). 구문 색칠은 그대로입니다. 단계 구성은 스킬의 `stages.md`에 있으며, 토큰을 늘리지 않고 단계를 고치는 원칙도 그곳에 적혀 있습니다. `settings.jsonc`에서 단계마다 보일지(`stages`)와 결과 위치(`output.directory`)를 정합니다. GitHub 등 다른 뷰어에서는 넘기기 대신 모든 단계가 순서대로 나열됩니다.

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

> "사용법"대로 스킬을 가져다 쓸 때는 이 설정이 필요 없습니다. 그 명령은 진짜 파일을 내려받고, Windows에서는 심볼릭 링크를 만들 수 없으면 권한이 필요 없는 디렉터리 정션으로 대신 링크합니다.

## 요구 사항

- [Claude Code](https://claude.com/product/claude-code)
- `generating-zenuml-diagrams`는 그 외 별도 의존성 없음 — 실행 코드가 없는 순수 Markdown 번들입니다.
- `generating-architecture-views`는 노드 hover 패널에 PC에 이미 있는 [Python](https://www.python.org/) 3.9 이상(`python3`, `python`, `py -3` 순으로 찾음)을 씁니다. 번들 스크립트(`.agents/skills/generating-architecture-views/scripts/`)는 표준 라이브러리만 써서 따로 설치할 것이 없습니다. Python이 없어도 구조 뷰는 만들어지고, hover 패널만 빠집니다.
- `revealing-code-step-by-step`은 번들 스크립트에 PC에 있는 [Python](https://www.python.org/) 3.9 이상을 씁니다(표준 라이브러리만 사용). 없으면 문서를 만들지 않습니다. 스크립트가 블록 구조를 아는 언어 — 중괄호 계열(Kotlin, Java, Scala, Groovy, Swift, C#, Go, Rust, Dart, JavaScript, TypeScript, C, C++)과 Python — 는 한 겹씩 펼칩니다. 파일 자체를 가리키는 노드(예: `colors.xml`)는 파일 전체가 원본이며, 마크업·데이터 파일과 그 밖의 언어는 사용 상황 다음에 바로 보입니다.
- `exporting-markdown-diagrams`는 [Node.js](https://nodejs.org/)가 필요합니다 — 번들 스크립트(`.agents/skills/exporting-markdown-diagrams/scripts/`)의 npm 패키지는 설치 명령이나 첫 사용 때 자동으로 설치됩니다.
