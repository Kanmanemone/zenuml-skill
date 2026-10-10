# Research: 변환 중 터미널 창 깜빡임 제거

모든 결론은 이 세션에서 Windows 11(기본 터미널 = Windows Terminal)에 창 감시 스크립트(`EnumWindows`로 새 가시 최상위 창을 30ms 간격 기록)를 띄워 놓고 실측했다.

## Decision: 원인 — `chrome-headless-shell.exe`가 Windows Terminal 창을 만든다

- **Decision**: 창의 원인을 콘솔 서브시스템 실행파일인 `chrome-headless-shell.exe`로 확정한다.
- **Rationale**: 변환 중 새로 생긴 창은 `CASCADIA_HOSTING_WINDOW_CLASS`(Windows Terminal, 제목 = `chrome-headless-shell.exe` 경로)와 그 `PseudoConsoleWindow`(소유 프로세스 `chrome-headless-shell`)였고, 브라우저 launch 1회당 정확히 1개였다(다이어그램 PNG 1회 + 문서 PDF 1회 = 3개 관찰 — 005 이전 기준. 005 이후에는 각 변환이 mmdc용 1개 + 스크립트용 1개로 2개씩). Puppeteer(`@puppeteer/browsers` 3.2.1)는 이미 `windowsHide: true`로 spawn하지만 `detached: true`(Windows에서 `DETACHED_PROCESS`)라 콘솔 없이 뜬 콘솔 앱 쪽에서 새 콘솔이 할당되고, 기본 터미널이 Windows Terminal이면 그 창이 보인다. 우리 쪽 `spawnSync`(mmdc 호출)는 이미 `windowsHide: true`다.
- **Alternatives considered**:
  - spawn 플래그 조정(`CREATE_NO_WINDOW`): 기각 — Puppeteer가 `detached`/플래그를 launch 옵션으로 노출하지 않는다. 패치하려면 node_modules를 고쳐야 한다.
  - 창을 최소화/구석 배치: 기각 — 창 생성 자체를 막을 수 있으므로 불필요.

## Decision: `headless: true`(GUI 서브시스템 `chrome.exe`) + `--lang=en-US`

- **Decision**: 모든 launch를 `{ headless: true, args: ["--lang=en-US"] }`로 한다.
- **Rationale**:
  - `headless: true`로 launch하면 새 창 0개, `"shell"`은 1개(같은 측정). 시간은 웜 상태에서 ~600ms로 같고, 첫 실행만 ~1.8s(콜드).
  - 하지만 `headless: true`만 주면 산출물이 바뀐다: generic `sans-serif`가 shell에서는 Arial, chrome에서는 UI 로캘(ko) 기본 글꼴(Noto Sans KR)로 풀린다(CDP `CSS.getPlatformFontsForNode`로 확인). mmdc SVG 7+2개 비교 결과 `headless: true`만으로는 2개가 달랐고, `--lang=en-US`를 더하면 **전부 바이트 동일**했다.
  - 005의 잘림 보정은 측정 브라우저와 렌더 브라우저의 글자 폭이 같아야 하므로, mmdc와 스크립트가 반드시 같은 설정을 써야 한다.
- **Alternatives considered**:
  - Windows에서만 적용: 기각 — OS 분기가 늘고, 모든 OS에서 같은 브라우저로 렌더링하는 편이 결과 일관성에도 낫다.
  - 글꼴을 CSS로 강제: 기각 — 다이어그램 SVG 내용을 바꾸게 되어 FR-002 위반.

## Decision: 설정의 단일 원천 = `scripts/puppeteer-config.json`

- **Decision**: launch 옵션을 JSON 파일 하나에 두고, `run-mmdc.js`는 항상 `-p <그 파일>`을 붙이며, 스크립트들은 `lib/browser-config.js`가 읽어 준 같은 객체로 `puppeteer.launch()`한다.
- **Rationale**: mmdc는 Puppeteer 설정을 파일로만 받는다(`-p`). 같은 값을 JS에 따로 적으면 두 곳이 어긋날 수 있다(FR-003). mmdc는 이 파일을 기본값 `{ headless: "shell" }` 위에 `Object.assign`하므로 `headless`가 확실히 덮어쓰인다(`src/index.js` 확인).

## 구현 후 확인: PNG는 픽셀 단위로는 미세하게 다르다

- SVG 산출물은 전부 바이트 동일(잘림 보정된 다이어그램의 viewBox까지 같음 — 측정 결과도 같다는 뜻)이지만, 같은 SVG를 래스터화한 PNG는 `chrome`과 `chrome-headless-shell` 사이에서 픽셀의 약 1%가 다르다(도형 테두리·글자 가장자리의 안티에일리어싱 값, 크기는 동일). 확대 비교에서 육안 차이는 없었다. 스펙의 바이트 동일 요구(FR-002)는 SVG 기준이므로 수용한다.
- 시간: 같은 PNG 변환의 웜 실행이 약 3.5초 → 약 4.1초(+0.6초, SC-003의 1초 이내).
