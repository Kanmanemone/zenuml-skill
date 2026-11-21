# zenuml-skill Constitution

## Core Principles

### I. 오버엔지니어링 금지

- 현재 Spec이 요구하는 것만 만든다. "나중에 필요할지도 모르는" 옵션·설정·확장 지점·추상화
  계층이나, Spec에 없는 경우를 대비한 처리를 넣지 않는다.
- 요구사항을 만족하는 방법 중 가장 단순한 것, 곧 파일·개념·단계가 가장 적은 것을 고른다.
  더 복잡한 방법을 쓰려면 더 단순한 방법이 안 되는 이유를 plan.md의 Complexity Tracking에
  기록한다.
- 한 곳에서만 쓰이는 코드를 일반화된 헬퍼·클래스·모듈로 빼내지 않는다.
- 표준 라이브러리나 이미 있는 코드로 충분하면 새 의존성을 들이지 않는다.

### II. 요청은 해당 Spec에서 진행

- 요청이 기존 Spec이 다루는 내용이면 그 Spec을 업데이트하고 진행한다. 같은 내용으로 새 Spec을
  만들지 않는다.
- 어느 기존 Spec에도 해당하지 않으면 `/speckit-specify`로 새 Spec을 만들고 진행한다.

### III. 출력 변동성 수준의 수정에는 Spec Kit을 쓰지 않음

- LLM의 출력 변동성(output variability), 곧 같은 요청에도 실행마다 달라질 수 있는 수준의 차이를
  고치는 작업에는 Spec Kit을 쓰지 않고 Spec도 수정하지 않는다. 이런 차이는 요구사항의 변화가
  아니기 때문이다. 원칙 II는 이런 작업에 적용하지 않는다.

### IV. 설정 기본값은 옵션 정의 한 곳에만 둠

- 스킬 설정 옵션의 기본값은 그 스킬 `settings.schema.json`의 `default` 하나에만 둔다. 배포
  `settings.jsonc`의 값과 그 주석은 이 값과 같게 유지한다.
- spec·plan·research·data-model·contract·quickstart·tasks 같은 Spec Kit 문서와 스킬
  지침(`SKILL.md`, `references/`)은 옵션의 의미와 허용 값만 적고, 기본값을 옮겨 적지 않는다.
- 테스트는 기본값을 하드코딩하지 않고 옵션 정의의 `default`와 비교한다.
- 예외: 날짜가 붙은 결정 기록(Clarifications 세션 등)과 이미 실행한 검증 결과는 그 시점의
  사실이므로 그대로 둔다.
- 근거: 기본값이 여러 곳에 있으면 값 하나를 바꿀 때마다 여러 문서를 고쳐야 하고, 고치지 못한
  곳은 실제 값과 어긋난다. 이 규칙이 지켜지면 기본값 변경은 그 스킬의 두 설정 파일만 바꾼다.

## Governance

- 이 헌법은 다른 모든 지침·관행보다 우선한다.
- `/speckit-plan`의 Constitution Check와 코드 리뷰에서 변경이 위 원칙을 지키는지 확인하고,
  어긴 변경은 고친 뒤에 받아들인다.
- 개정은 `/speckit-constitution`으로 한다. 버전은 원칙을 없애거나 뜻을 바꾸면 MAJOR,
  원칙·섹션을 더하면 MINOR, 문구만 다듬으면 PATCH를 올린다.

**Version**: 1.2.0 | **Ratified**: 2026-11-15 | **Last Amended**: 2026-11-22
