# Data Model: 스킬별 사용자 편집 설정 파일

## Option Definition (`settings.schema.json`)

스킬마다 하나. 그 스킬 옵션 전체의 유일한 기준(FR-016).

| 필드 | 설명 |
|------|------|
| `options[]` | 옵션 항목 배열(비어 있을 수 있음) |
| `options[].key` | 점으로 묶음을 나타낸 키. 예: `responsibility.display` → 설정 파일의 `{"responsibility": {"display": …}}` |
| `options[].type` | `enum` / `boolean` / `number` / `relativePath` |
| `options[].values` | `enum`일 때 허용 값 목록 |
| `options[].min` | `number`일 때 이 값보다 커야 함 |
| `options[].base` | `relativePath`일 때 기준 위치 설명: `projectRoot` 또는 `sourceFileDir` |
| `options[].default` | 키가 없거나 값이 잘못됐을 때 쓰는 값. 배포 `settings.jsonc`의 값과 같아야 함(FR-003) |
| `options[].description` | 한국어 한 줄 설명 |
| `options[].tokenImpact` | 값별 토큰 소모 표시. `enum`/`boolean`은 값마다, 그 외는 `"*"` 하나. 값은 `[-]`(줄어듦) / `[0]`(거의 같음) / `[+]`(늘어남) / `[++]`(큼) 중 하나 |

**검증 규칙**: `default`는 자기 `type`·제약을 만족해야 한다. `key`는 스킬 안에서 유일하다.

## Settings File (`settings.jsonc`)

사용자 편집용. 옵션 정의의 `key`를 묶음 객체로 펼친 구조이며, 각 옵션 바로 위에 한국어 주석(의미, 허용 값 각각의 뜻과 토큰 영향, 기본값)을 둔다(FR-020).

## Resolved Settings (실행 중 값)

| 필드 | 설명 |
|------|------|
| `values` | 옵션 키 → 이번 실행에 쓸 값 |
| `notices[]` | 채팅 응답에 붙일 안내 문구(없을 수 있음) |

**해석 규칙**(공통 절차, FR-002·FR-004·FR-005·FR-017·FR-019):

| 상황 | 값 | 안내 |
|------|----|------|
| 설정 파일 없음 | 모든 키 기본값 | 없음 |
| 파일을 읽을 수 없음(주석 제거 후 JSON 파싱 실패, 최상위가 객체가 아님) | 모든 키 기본값 | `읽지 못함` 한 줄 |
| 키 없음 | 기본값 | 없음 |
| 값이 타입·제약 위반 | 그 키만 기본값 | `<키>` 값이 허용되지 않아 기본값 사용 |
| 정의에 없는 키(묶음 객체 안의 잎 키 기준) | 무시 | `<키>` 무시 |
| 요청 문장이 그 옵션의 값을 직접 밝힘 | 요청 값(이번 요청만) | 없음 |

## 현재 옵션 목록

| 스킬 | key | type | 값 |
|------|-----|------|----|
| architecture | `responsibility.display` | enum | `hidden`/`plain`/`collapsed`/`expanded` |
| architecture | `collaboration.display` | enum | 위와 같음 |
| architecture | `collaboration.questions` | boolean | — |
| architecture | `dependency.renderer` | enum | `default`/`elk` |
| architecture | `dependency.nodeNameFormat.declarationMarkers` | boolean | — |
| architecture | `dependency.nodeNameFormat.fileExtensions` | boolean | — |
| architecture | `dependency.nodeNameFormat.functionParentheses` | boolean | — |
| architecture | `dependency.sourceFile.enabled` | boolean | — |
| architecture | `dependency.sourceFile.position` | enum | `left`/`center`/`right` |
| architecture | `log.directory` | relativePath(projectRoot) | — |
| zenuml | `log.directory` | relativePath(projectRoot) | — |
| exporting | `questions.enabled` | boolean | — |
| exporting | `defaults.format` | enum | `none`/`svg`/`png`/`pdf` |
| exporting | `defaults.scope` | enum | `none`/`diagram`/`document` |
| exporting | `defaults.pdfLayout` | enum | `none`/`single`/`paginated` |
| exporting | `png.scale` | number(min 0) | — |
| exporting | `output.directory` | relativePath(sourceFileDir) | — |

기본값은 이 표에 두지 않는다. 각 스킬 `settings.schema.json`의 `default`가 유일한 기준이고, 배포 `settings.jsonc` 값은 그와 같다(FR-003).

`dependency.nodeNameFormat`의 세 boolean은 독립적으로 조합한다. `declarationMarkers`는 확인된 파일 내부 선언 키워드만, `fileExtensions`는 파일 자체 노드의 마지막 확장자만, `functionParentheses`는 확인된 함수 이름 끝의 `()`만 제어한다. 모두 Dependency 라벨에만 적용하며 본문 이름·노드 ID·링크·hover 데이터는 바꾸지 않는다.

## Collapsible Section (구조 뷰 산출물 안)

`display`가 `collapsed`/`expanded`인 섹션의 모양 — research.md "접은 글 상자 마크업" 참고. `hidden`이면 헤딩·내용·그 섹션 전용 자기검증이 모두 없다.
