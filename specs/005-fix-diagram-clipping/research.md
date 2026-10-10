# Research: 다이어그램 가장자리 잘림 수정

handoff 문서(`HANDOFF-export-clipping.md`, 다른 세션 작성)의 주장을 그대로 받아들이지 않고, 이 저장소에서 재현 샘플(가장 오른쪽 참여자에 긴 주석을 단 zenuml 다이어그램 + 일반 mermaid sequence)과 `.zenuml/*.md` 7개 다이어그램으로 직접 재현·측정했다. handoff가 검증에 쓴 `.zenuml/drawn-bullet-*.md` 파일들은 이 저장소에 없다(다른 프로젝트 `SplitLabelText`의 파일).

## Decision: 원인 — 렌더러가 계산한 viewBox가 실제 그림보다 좁다 (handoff 주장 검증됨)

- **Decision**: 원인을 "루트 `<svg>`의 `viewBox`가 실제 그림 범위를 덮지 못함"으로 확정한다.
- **Rationale**: 재현 샘플의 zenuml SVG는 `viewBox="0 0 473.5 494"`인데 브라우저 `getBBox()`는 폭 838.6까지 그려져 있음을 보였다. 잘린 주석 텍스트는 SVG 안에 `<text>`로 그대로 있고, PNG에서는 "State 읽기라서"까지만 보였다. mmdc는 PNG/PDF를 SVG 요소의 레이아웃 박스(`getBoundingClientRect`, 즉 viewBox 기준) 크기로 찍으므로 모든 형식이 같은 영향을 받는다. 일반 mermaid 다이어그램 7개는 넘침이 없었다.
- **Alternatives considered**:
  - 렌더러(zenuml-core) 자체 수정: 기각 — 외부 패키지 내부 계산이라 이 저장소에서 고칠 수 없다.
  - mmdc `--width`를 크게 주기: 기각 — viewBox 자체가 좁으므로 뷰포트를 넓혀도 viewBox 밖은 여전히 표시되지 않는다.

## Decision: 보정 방식 — getBBox 실측 후 넘친 쪽만 viewBox 확장, 루트 태그 문자열만 패치

- **Decision**: handoff 설계를 채택한다. 넘친 쪽에만 16 user unit 여백, 1 unit 이하 넘침은 무시, 넘침이 없으면 파일을 건드리지 않음. 루트 태그의 `viewBox="..."`와 `style`의 `max-width: Npx`만 정규식으로 바꾸고 DOM 재직렬화는 하지 않는다.
- **Rationale**: 실측이라 다이어그램 종류에 무관하다(FR-003). 허용 오차는 handoff의 실측 경험(일반 시퀀스 다이어그램도 1px 미만 넘침이 흔함)을 따른다 — 이 저장소의 샘플에서도 7개 모두 넘침 0으로 판정되어 바이트 동일을 확인했다. 문자열 패치는 HTML 파서로 재직렬화할 때 생길 수 있는 XML 비호환을 원천 차단한다.
- **Alternatives considered**: DOM에서 `outerHTML`로 재직렬화 — 기각(XML 유효성 위험, 바이트 동일성 깨짐).

## Decision: PNG/PDF는 보정된 SVG를 우리가 띄운 같은 Chromium으로 캡처/인쇄

- **Decision**: 다이어그램 단독 PNG는 viewBox 크기 뷰포트 + `deviceScaleFactor = 3`(기존 `PNG_SCALE`)으로 `<svg>` 요소를 screenshot, PDF는 viewBox 크기와 같은 한 페이지로 `page.pdf()`한다.
- **Rationale**: mmdc는 Mermaid 소스만 입력으로 받으므로 보정된 SVG를 다시 mmdc에 넣을 방법이 없다. 004 spec의 가정("별도 SVG→PNG 재변환은 다른 래스터라이저로 인한 폰트·크기 차이 위험")이 경계한 것은 *다른* 래스터라이저인데, 여기서는 mmdc와 같은 Puppeteer/Chromium을 쓰므로 그 위험에 해당하지 않는다. 잘리지 않던 일반 sequence 다이어그램(폭 450)에서 mmdc PNG와 새 PNG는 같은 크기(1350×777)이고 육안상 동일했다(배치가 몇 px 다른 정도 — mmdc 페이지의 body 여백/스케일 차이).
- **Alternatives considered**: 넘친 다이어그램만 새 경로, 나머지는 mmdc png/pdf 유지 — 기각(경로가 둘로 갈라져 복잡도만 늘고, 아래 PNG 크기 문제도 그대로 남음).

## Decision: PNG 픽셀 크기 — 축소 없이 실제 레이아웃 크기 × 3 (기존 동작 수정, handoff에 없던 발견)

- **Decision**: PNG를 viewBox 원래 크기 × 3으로 찍는다. 기존보다 넓은 다이어그램의 PNG가 커진다.
- **Rationale**: 검증 중 발견 — 기존 mmdc PNG는 mmdc 기본 뷰포트(폭 800)에서 `<svg width="100%" style="max-width: …">`가 body 여백을 뺀 784 CSS px로 **축소**된 상태를 찍기 때문에, 폭이 784를 넘는 다이어그램은 항상 PNG 폭 2352px(=784×3)로 고정되고 글자가 작아졌다(예: `navigation3` 1357폭 → 2352px, 새 방식 4071px). 004 research.md "PNG 해상도"의 "mmdc는 다이어그램의 실제 렌더링 크기에 맞춰 찍는다"는 서술은 이 축소를 놓친 것이고, 004 spec FR-013("실제 레이아웃 크기에 맞춰 픽셀 수가 정해지고, 큰 다이어그램일수록 더 큰 PNG")을 실제로 만족하는 것은 새 방식이다. 또한 보정으로 넓어진 다이어그램을 784로 축소하면 잘림은 사라져도 글자가 더 작아져 수정 의도와 어긋난다.
- **Alternatives considered**: 784 CSS px 상한 유지(기존과 픽셀 크기 동일) — 기각(FR-013 위반 상태 유지, 넓어진 다이어그램일수록 더 흐릿).

## Decision: 다이어그램 단독 PDF — 다이어그램 크기에 맞춘 한 페이지

- **Decision**: 기존 mmdc 기본값(용지 크기 페이지) 대신 viewBox 크기 한 페이지 PDF.
- **Rationale**: mmdc 자신의 `--pdfFit`과 같은 방식이며, 004 research.md가 이미 "검증된 방식"으로 채택한 패턴(문서 전체 PDF `single` 모드)과 같다. 다이어그램 단독 PDF에서 용지 여백·축소는 이점이 없다.

## Decision: 측정 브라우저 = 렌더 브라우저 (같은 프로세스, 같은 launch 설정)

- **Decision**: 한 스크립트 실행 안에서 브라우저를 한 번 띄워 fit 측정과 PNG/PDF 생성에 같이 쓴다. launch 설정은 mmdc 기본값과 같은 `headless: "shell"`.
- **Rationale**: 검증 중 발견 — 같은 SVG의 `getBBox()` 폭이 `chrome-headless-shell`에서는 823.4, `chrome`(`headless: true`)에서는 838.6으로 달랐다. generic `sans-serif`가 전자는 Arial, 후자는 로캘(ko) 기본 글꼴로 풀리기 때문이다. 측정과 렌더가 다른 브라우저면 여백이 모자라 다시 잘릴 수 있다.

## Decision: 임시 디렉토리 정리

- **Decision**: `export-diagrams.js`의 mmdc 중간 SVG는 OS 임시 디렉토리에 만들고, `process.exit` 경로에서도 지워지도록 정리 시점을 보장한다.
- **Rationale**: handoff 코드는 `try` 안의 `fail()`(즉 `process.exit`)이 `finally`를 건너뛰어 실패 시 임시 디렉토리가 남는다. 출력 디렉토리 대신 임시 디렉토리를 쓰면 이전 실행 잔여 파일이 결과 목록에 섞이는 문제(FR-009)도 함께 사라진다.
