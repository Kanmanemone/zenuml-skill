# Data Model: 다이어그램 가장자리 잘림 수정

영속 데이터는 없다. 스크립트 내부에서 다루는 값만 정리한다.

## ViewBox

루트 `<svg>`의 `viewBox` 속성 값. `{ x, y, width, height }` (SVG user unit, 소수 허용).

- 루트 태그에 `viewBox`가 없거나 네 값 중 하나라도 숫자가 아니면 → 보정 대상 아님(파일 그대로).

## DrawnBBox

브라우저에서 루트 `<svg>`의 `getBBox()`로 잰 실제 그림 범위. `{ x, y, width, height }` (같은 user unit).

## FitResult (`fitSvgFile` 반환값)

| 필드 | 의미 |
|------|------|
| changed | viewBox가 바뀌었는지 |
| before | 원래 ViewBox(없으면 null) |
| after | 보정 후 ViewBox(없으면 null) |

### 보정 규칙 (각 변 독립)

| 변 | 넘침 조건 | 넘쳤을 때 새 값 | 아니면 |
|----|-----------|----------------|--------|
| 왼쪽 | `bbox.x < vb.x - 1` | `floor(bbox.x - 16)` | `vb.x` |
| 위 | `bbox.y < vb.y - 1` | `floor(bbox.y - 16)` | `vb.y` |
| 오른쪽 | `bbox.x+w > vb.x+w + 1` | `ceil(bbox 오른쪽 + 16)` | 원래 오른쪽 |
| 아래 | `bbox.y+h > vb.y+h + 1` | `ceil(bbox 아래 + 16)` | 원래 아래 |

- 불변식: 보정 후 ViewBox ⊇ 원래 ViewBox (줄어드는 변 없음).
- `changed = false`이면 파일은 바이트 단위로 그대로.
- `changed = true`이면 루트 태그의 `viewBox`와 `max-width: Npx`(있을 때)만 바뀐다.
