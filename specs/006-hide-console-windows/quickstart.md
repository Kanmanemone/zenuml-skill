# Quickstart: 변환 중 터미널 창 깜빡임 제거 검증

## 준비

- Windows, `SK=.claude/skills/exporting-markdown-diagrams/scripts`, `npm install` 완료.
- 창 감시 스크립트(PowerShell): `user32!EnumWindows`로 가시 최상위 창 목록을 30ms 간격으로 찍어, 시작 시점에 없던 창을 `시각 | 클래스 | 제목 | 프로세스`로 로그에 남긴다. 숨김 창으로 백그라운드 실행.
- 샘플: 005 quickstart.md의 `clip.md`.

## 시나리오 1 — 새 창 0개 (US1/AC1·AC2, SC-001)

감시 스크립트를 켠 상태에서:

```sh
node $SK/export-diagrams.js clip.md png
node $SK/export-document-pdf.js clip.md "" --layout single
```

- 기대: 로그에 새 창이 하나도 없다(변경 전에는 `CASCADIA_HOSTING_WINDOW_CLASS … chrome-headless-shell.exe`가 변환마다 2개).

## 시나리오 2 — 산출물 동일 (US1/AC3, SC-002)

변경 전 커밋의 스크립트와 변경 후 스크립트로 `.zenuml/*.md`와 `clip.md`를 SVG로 뽑아 `cmp`로 비교한다. 전부 바이트 동일해야 한다.

## 시나리오 3 — 시간 (SC-003)

같은 PNG 변환을 변경 전/후 각각 2번씩 실행해 두 번째(웜) 실행 시간을 비교한다. 증가가 1초 이내여야 한다.
