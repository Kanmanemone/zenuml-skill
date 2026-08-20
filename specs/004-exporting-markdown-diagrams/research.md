# Phase 0 Research: Markdown 다이어그램/PDF export 스킬

이 문서는 `plan.md`의 Technical Context에 남아 있던 구현 수준 결정 사항을 정리한다. 문제/증거 수준 조사는 이미 `.specify/assessments/exporting-markdown-diagrams/research.md`에서 완료되었으므로, 여기서는 그 결론을 계승해 **스킬을 실제로 어떻게 구성할지**에 대한 남은 결정만 다룬다.

## Decision: 다이어그램 렌더링/변환 엔진

- **Decision**: `@mermaid-js/mermaid-cli`(`mmdc`)를 채택한다.
- **Rationale**: 평가 리서치에서 이미 확인됐듯, `mmdc`는 (1) zenuml 플레이버를 네이티브로 지원하고(PR #566, 2023-08-03 머지 이후 버전), (2) markdown 입력에서 코드펜스로 등장하는 모든 mermaid/zenuml 다이어그램을 자동으로 찾아 각각 렌더링하며, (3) 출력이 `.md` 파일이면 원본 마크다운의 다이어그램 코드펜스를 렌더링된 이미지에 대한 표준 마크다운 이미지 참조로 자동 치환해준다. 이번 계획 단계에서 소스(`mermaid-js/mermaid-cli` `src/index.js`)를 직접 읽어 다음을 확인했다: SVG 출력은 렌더링된 DOM의 `<svg>` 요소를 직렬화하는 것이고, PNG 출력은 같은 렌더링 패스에서 그 SVG의 bounding box로 클리핑한 스크린샷을 찍는 것이며, PDF 출력은 그 DOM을 그대로 `page.pdf()`로 인쇄하는 것이다 — 셋 다 하나의 브라우저 렌더링 패스에서 파생되므로 spec.md의 FR-004(렌더러 지정 보존)와 Assumptions(PNG 재변환 불필요)를 그대로 만족한다.
- **Alternatives considered**: `mermaidx`(Python, QuickJS+resvg로 브라우저 불필요) — 더 가볍지만 zenuml 플레이버 지원 여부가 검증되지 않았고 커뮤니티 성숙도가 낮아 이 저장소의 주력 산출물(zenuml 시퀀스 다이어그램)에 대한 위험이 크다. Pandoc 기반 — 이 개발 환경에 설치돼 있지 않고, Mermaid 코드펜스를 이해하지 못해 별도 필터가 필요해 오히려 복잡도가 늘어난다.

## 확인된 사실: 헤드리스 브라우저가 사용자의 평소 브라우저와 충돌하지 않음

- **질문**: `mmdc`가 렌더링(특히 elk 같은 커스텀 레이아웃 렌더러)에 헤드리스 브라우저를 쓴다면, 사용자가 이미 다른 브라우저 창을 띄워둔 상태에서 실행할 때 충돌하지 않는가?
- **확인**: 충돌하지 않는다. `mermaid-cli` 소스(`src/index.js`)에서 `puppeteer.launch({ headless: "shell" })`을 호출하는 것을 확인했다 — `chrome-headless-shell`은 사용자의 일반 Chrome/Edge와는 별도로 빌드·배포되는, 헤드리스 자동화 전용 바이너리다. `executablePath`나 `userDataDir`를 커스텀 지정하는 코드가 없으므로 Puppeteer의 기본 동작대로 매 실행마다 격리된 임시 프로필을 자동 생성하고 종료 시 정리한다. 사용자의 실제 브라우저 프로세스·프로필과는 바이너리도 프로필 디렉터리도 겹치지 않는다.
- **결론**: 이 스킬의 번들 스크립트(`export-diagrams.js`, `export-document-pdf.js`)는 `mmdc`의 이 기본 동작을 그대로 따르며, `puppeteerConfig`에 `executablePath`/`userDataDir`를 지정하지 않는다 — 별도의 격리 로직을 새로 만들 필요가 없다(이미 안전하므로 추가 태스크 불필요). 충돌은 오직 이 기본값을 벗어나 Puppeteer를 사용자의 실제 브라우저 프로필 경로로 명시적으로 설정했을 때만 발생하며, 이 계획은 그렇게 하지 않는다.

## Decision: `mermaid-cli` 버전 고정

- **Decision**: 번들 스크립트가 호출하는 `@mermaid-js/mermaid-cli`는 zenuml 지원이 병합된 2023-08-03 이후 릴리스된 버전으로 `package.json`에 고정(예: `^11` 계열의 안정 버전)한다.
- **Rationale**: 평가 리서치에서 재현한 `UnknownDiagramError`(오래된 `mmdc`가 zenuml을 인식하지 못함)가 조용히 재발하는 것을 막는다. 버전을 고정해두면 이 저장소의 주력 산출물(zenuml 시퀀스 다이어그램) 변환이 실패하는 시점을 설치/업데이트 시점에 명확히 드러낼 수 있다.
- **Alternatives considered**: 버전 고정 없이 `latest` 사용 — 재현성이 없고, 향후 `mermaid-cli`가 다시 호환성을 깨뜨려도 조용히 실패할 위험을 그대로 안는다.

## Decision: User Story 1(다이어그램만 export) 구현 방식

- **Decision**: `export-diagrams.js`는 대상 마크다운 파일과 선택된 형식을 그대로 `mmdc -i <입력> -o <출력>.<형식>`에 전달한다. 문서에 다이어그램이 여러 개 있으면 별도의 "다이어그램 찾기" 로직을 새로 만들지 않고 `mmdc` 자체의 다중 다이어그램 처리(발견된 순서대로 번호를 매겨 개별 파일로 저장)를 그대로 활용한다.
- **Rationale**: 소스 코드에서 이미 확인했듯 이 동작은 `mmdc`에 내장돼 있다 — 재구현은 spec.md Assumptions의 기본값("모든 다이어그램을 각각 개별 파일로 변환")과 정확히 일치하는 기능을 중복 개발하는 것이므로 불필요하다.
- **Alternatives considered**: 스킬이 직접 마크다운을 파싱해 다이어그램을 하나씩 추출한 뒤 각각 `mmdc`를 호출 — 동일한 결과를 더 많은 코드로 재구현하는 것이라 기각.

## Decision: User Story 2(문서 전체 PDF export) 파이프라인

- **Decision**: 2단계로 구성한다.
  1. **1단계(다이어그램 추출)**: `mmdc -i <원본.md> -o <중간>.md -e svg`를 호출한다. `mmdc`가 각 다이어그램을 개별 SVG 파일로 렌더링하고, 원본 마크다운의 다이어그램 코드펜스를 그 SVG 파일에 대한 이미지 참조(`![...](...-N.svg)`)로 치환한 중간 마크다운 파일을 만들어준다 — 이 변환 자체는 이미 `mmdc` 안에 구현돼 있다.
  2. **2단계(HTML화 및 PDF 인쇄)**: 그 중간 마크다운을 HTML로 변환하되(마크다운→HTML 변환 라이브러리 사용), 남아 있는 `<img src="*.svg">` 참조를 실제 SVG 파일의 내용으로 **인라인 치환**한다(파일 링크가 아니라 `<svg>...</svg>` 마크업 자체를 문서에 삽입). 그 결과 HTML을 헤드리스 브라우저로 열어 `page.pdf()`로 인쇄한다.
- **Rationale**: spec.md FR-007(다이어그램이 벡터로 삽입되어 텍스트가 선택·복사 가능해야 함)을 만족하려면 최종적으로 인쇄되는 HTML의 DOM에 실제 `<svg>` 요소가 존재해야 한다. `mmdc` 자신의 PDF 출력 경로도 정확히 이 방식(DOM에 존재하는 `<svg>`를 `page.pdf()`로 인쇄)을 쓰고 있음을 소스에서 확인했으므로 신뢰할 수 있는 선례다. 반대로 `<img src="diagram.svg">`처럼 파일 링크로만 남겨두면, 브라우저의 인쇄 경로가 그 이미지를 벡터로 유지할지 래스터로 변환할지가 보장되지 않는 동작이므로, 인라인 치환이 FR-007을 확실하게 만족시키는 유일하게 검증된 방법이다.
- **Alternatives considered**: Pandoc 기반 md→PDF — 미설치·Mermaid 미이해로 기각(평가 리서치에서 이미 확인). 다이어그램을 PNG로 먼저 렌더링해 삽입 — 구현은 더 단순하지만 FR-007이 요구하는 텍스트 선택·복사가 원천적으로 불가능해 기각. `<img src>` 링크를 그대로 두고 브라우저 인쇄에 맡김 — 벡터 유지가 보장되지 않아 기각.

## Decision: 마크다운→HTML 변환 라이브러리

- **Decision**: 정확한 라이브러리(예: `markdown-it`, `marked` 등)는 태스크 단계에서 확정한다 — 둘 다 널리 쓰이는 성숙한 선택지이고, 이 결정이 spec.md의 어떤 요구사항에도 영향을 주지 않는 순수 구현 세부사항이기 때문이다.
- **Rationale**: 오버엔지니어링 방지 — 이 계획 문서가 다뤄야 할 것은 "다이어그램이 벡터로 삽입되어야 한다"는 요구사항을 만족시키는 파이프라인의 형태(위 Decision)이지, 그 안에서 쓸 특정 라이브러리 이름이 아니다.
- **Alternatives considered**: N/A — 태스크 단계로 명시적으로 이월.

## Decision: PNG 출력 경로

- **Decision**: `export-diagrams.js`는 PNG 요청 시 `mmdc -e png`를 직접 호출한다 — SVG로 먼저 렌더링한 뒤 별도 도구로 래스터화하는 재변환 단계를 두지 않는다.
- **Rationale**: 위 "다이어그램 렌더링/변환 엔진" Decision에서 이미 확인했듯, `mmdc`의 SVG와 PNG 출력은 하나의 렌더링 패스에서 파생되는 두 가지 캡처 방식일 뿐 서로 다른 파이프라인이 아니다. 별도 재변환을 추가하면 이점 없이 처리 단계와 위험(다른 래스터라이저로 인한 폰트·크기 차이)만 늘어난다. spec.md Assumptions에 이미 반영된 결론을 그대로 계승한다.
- **Alternatives considered**: `mmdc -e svg`로 SVG를 만든 뒤 별도 SVG→PNG 도구(예: `sharp`, `resvg`)로 재변환 — 기각(위 Rationale).

## Decision: PNG 해상도

- **Decision**: PNG 변환 시 `mmdc`에 `-s`/`--scale 3`을 고정값으로 넘긴다. `mmdc`는 PNG 출력 시 `page.setViewport({ deviceScaleFactor: scale })`로 뷰포트를 설정한 뒤 다이어그램의 실제 렌더링 크기(`getBoundingClientRect()`로 측정한 SVG bounding box)에 맞춰 스크린샷을 찍는다(`src/index.js` 확인) — 즉 `--width`/`--height`는 초기 뷰포트일 뿐 최종 출력 크기를 결정하지 않고, `--scale`(Puppeteer의 `deviceScaleFactor`, 일반 화면 96 CSS px/in 기준의 배율 — 3이면 대략 288 DPI에 해당)만이 같은 레이아웃을 몇 배 밀도로 캡처할지 결정한다. 기본값(`scale=1`)으로는 다이어그램이 클수록 표시 크기 대비 픽셀 수가 부족해 흐릿하게 나온다(실사용 리포트로 확인).
- **Rationale**: 가로·세로 픽셀 수를 직접 정하면 다이어그램마다 크기가 다른데도 화질이 다이어그램 크기에 반비례하게 된다. `--scale`은 다이어그램의 실제 레이아웃 크기와 무관하게 일정한 선명도(고정 배율)를 보장하는 mmdc/Puppeteer가 이미 제공하는 방법이라, 새 로직을 만들 필요가 없다(spec.md FR-013).
- **Alternatives considered**:
  - `--width`/`--height`를 크게 고정: 기각 — 다이어그램 종횡비가 그 값과 다르면 여백/잘림이 생기고, 크기가 커져도 실제 해상도(선명도)는 그대로다(위 mmdc 동작 확인 결과, 어차피 bounding box로 재설정됨).
  - PNG를 먼저 만들고 별도 업스케일링 도구로 보정: 기각 — 손실된 디테일을 사후에 복원할 수 없고, 새 의존성과 처리 단계만 늘어난다(오버엔지니어링).
