# Quickstart: 정제 단계 코드 구체화 확인

## 블록 구조를 아는 언어 검증 (2026-11-18, 아래의 모든 앞선 절차보다 우선)

`python specs/010-stepwise-code-convergence/test_learning_stages.py`로 확인한다.

- **규격 표시 노드**: `class&nbsp;NiaAppState`, `enum&nbsp;class&nbsp;TopLevelDestination`, `♻️&nbsp;fun&nbsp;NiaNavHost` 라벨을 각각 실제 이름으로 읽고, 같은 이름의 선언 범위와 마지막 장면이 일치한다. 표시어 없는 기존 라벨도 그대로 읽는다(FR-021, SC-015).

- **언어별 시험 원본**: Java·TypeScript·JavaScript·Go·Rust·C#·Swift·C++·Python마다 한 파일에 머리(`import` 등)와 선언 둘 이상이 든 원본을 둔다. 노드 이름과 같은 선언의 원본 범위가 기대 범위와 글자까지 같다. 안에 블록이 든 선언은 트리가 있고, 자동 입력으로 만든 모든 장면을 연 결과가 원본 범위와 같다.
- **잘못 자르지 않음**: 짝이 맞지 않는 범위가 나오는 원본(예: `)` 뒤라 나눗셈으로 읽히는 JavaScript 정규식 `if (ok) /}/.test(text)`가 함수 안에 든 원본. 값 자리의 정규식 `const re = /}"/`는 가려지므로 범위가 맞게 잘린다)에서는 그 노드가 `원본 파일에서 <이름> 선언 범위를 블록 구조로 확인하지 못해 구체화하지 않음`이 된다.
- **Java 선언 노드**: 이전 절의 `Shapes.java` 안 `Circle`은 이제 `class Circle` 범위를 원본으로 갖는다. 기존 fixture의 `LegacyBridge`(`src/Legacy.java`)도 `class LegacyBridge` 범위가 원본이 된다.
- **Kotlin 불변**: Kotlin 노드의 상자는 바꾸기 전과 글자까지 같다.

## 원본 언어와 파일 단위 노드 검증 (2026-11-18)

`python specs/010-stepwise-code-convergence/test_learning_stages.py`로 확인한다. 시험은 임시 폴더에 작은 구조 뷰와 원본을 만들어 돌린다. 기대 결과는 다음과 같다.

- **XML 파일 단위 노드**(노드 `ColorsXml`, 표시 이름 `colors.xml`, 원본 `colors.xml`): `skip_reason` 없음, `range.whole_file` 참, `tree` null. 문서에 `⚠️` 줄이 없다. 장면은 사용 상황과 원본 둘이고, 원본 장면의 코드 블록은 `xml`이며 파일 전체와 같다. `build`의 `verified`에 든다.
- **Kotlin 파일 단위 노드**(노드 `ColorKt`, 표시 이름 `Color.kt`, 원본은 `package`·`import`와 최상위 `val` 여럿): 원본 범위가 파일 전체이고, 스코프 목록에서 `package`·`import` 줄은 루트의 자기 줄(`-`)이며, 최상위 `val`들이 루트 자식이다. 윤곽 장면에 `package`·`import`가 보이고, 마지막 장면은 파일 전체와 같다.
- **Kotlin이 아닌 선언 노드**(Java 파일 `Shapes.java` 안의 노드 `Circle`): `skip_reason`은 `Kotlin이 아닌 원본은 파일 단위 노드만 원본 범위를 정할 수 있어 구체화하지 않음`이다.
- **Kotlin 파일 이름 노드인데 같은 이름의 선언도 있음**(`Order.kt` 안 `class Order`, 노드 `Order`): 지금처럼 선언 범위다(`whole_file` 없음).
- **기존 결과 불변**: 저장소 fixture로 만든 문서에서 노드 이름과 같은 Kotlin 선언을 찾는 노드의 상자는 바꾸기 전과 글자까지 같다(SC-013). 바뀌는 것은 Kotlin이 아닌 선언 노드 `LegacyBridge`(`src/Legacy.java`)의 이유 줄뿐이며, 새 contract 문구(`Kotlin이 아닌 원본은 파일 단위 노드만 원본 범위를 정할 수 있어 구체화하지 않음`)가 된다.
- swemo 구조 뷰(Color.kt·Theme.kt·colors.xml이 든 designsystem 그룹)를 사용자 환경에서 다시 만들면 `colors.xml`과 `ColorKt`에 `⚠️` 줄이 없다. `colors.xml`이 이미 지워졌으면 `원본을 읽을 수 없어 구체화하지 않음`이 나오는 것이 맞다.

## 스코프 트리 정제 검증 (2026-11-17, 아래의 모든 앞선 절차보다 우선)

1. **자동 테스트**: 저장소 루트에서 `python specs/010-stepwise-code-convergence/test_learning_stages.py`를 실행한다. 확인하는 것은 다음과 같다.
   - 트리: 블록 문장, 한 줄 인자 묶기, 체인 고리, 외길 병합, 주석·어노테이션·raw string이 한 노드에 머묾
   - 불변식: 모든 줄이 한 곳에만 속함, 스코프 목록에 원본의 각 줄이 한 번만 나옴(SC-009 a)
   - `outline.json` 거부(오류가 여럿이면 줄도 여럿, 그리고 틀린 스코프만 고치면 통과함, SC-009 f)
   - 번호와 순서(FR-005c), 윤곽에 모든 단계가 들여 써져 보임(FR-004)
   - 장면마다 새로 드러난 줄이 그 단계의 노드 줄과 붙는 선언과 정확히 같음(SC-010)
   - fixture와 샘플 전부에서 모두 연 장면이 원본과 같음(FR-010)
   - 깊이 1 노드는 장면 종류·순서가 같고 묶음이 4개 이하임
   - 본문 없는 선언 묶기, 루트의 외길 병합
   - 결정성: 같은 원본으로 `prepare`를 두 번 실행한 스코프 목록 출력, 그리고 같은 `outline.json`으로 `build`를 두 번 실행한 문서가 글자까지 같음(SC-004)
   - 원본 없는 노드, 숨기기(펼치기를 끄면 윤곽 다음이 원본), 책임 줄(기존 회귀)
   - 붙는 선언 좁히기(2026-11-18, SC-012): 여러 줄 비공개 멤버는 루트 자식 스코프가 되고 붙는 선언에는 한 줄 선언만 있음, 한 줄 비공개 멤버는 처음 쓰이는 단계에 그대로 붙음, 기존 fixture의 기대 문서가 바뀌지 않음
   - 샘플은 테스트 안의 합성 Kotlin이다(호출 인자 목록 → 람다 → 체인 → 그리기 블록의 여러 겹). 사용자 프로젝트 코드는 fixture로 복사하지 않는다.
2. **실제 예제 — swemo-ui-bulleted-list-testbed**: `.zenuml/swemo-ui-bulleted-list-testbed.architecture.md`로 prepare → 격리된 상황 작성 → 메인 에이전트가 `outline.json` 작성 → build를 실행한다. `verified`가 구체화하는 노드 수와 같아야 하고, 구조 뷰의 SHA256은 전후가 같아야 한다. 다음을 기록해 research S8에 덧붙인다.
   - prepare 출력의 노드 블록 글자 수(읽기), `outline.json` 글자 수(쓰기)
   - BulletedListTextField의 장면별 새 줄 수
   - 작업자 호출 수(상황 서브에이전트 1)
   - (2026-11-18) MemoViewModel의 장면별 새 줄 수, 그리고 붙는 선언이 모두 한 줄인지. 다른 노드의 결과 문서가 바뀌지 않았는지는 바꾸기 전 문서와 비교한다
3. **미리보기**: 에디터에서 윤곽의 들여 쓴 번호, 앞뒤 넘기기, 달라진 줄 표시를 직접 확인한다.

## 단위 펼치기 검증 (아래의 모든 앞선 절차보다 우선)

저장소 루트에서 `python specs/010-stepwise-code-convergence/test_learning_stages.py`를 실행한다. 기본 정의의 종류와 순서, 단위 계산(비공개 멤버·상태·매개변수 붙이기, 본문 없는 선언 묶기, 4개 상한), fixture 원본 전부에서 모두 펼친 장면 = 원본, 펼치기 입력 검증의 거부, 접기와 원본 장면, 원본 없는 노드의 상황 장면, 1단계 프롬프트에 `click` 줄이 없음, 숨기기, 문서의 책임 줄을 확인한다.

실제 예제는 `.zenuml/nia-bookmarks-mvvm.architecture.md`로 prepare → 격리된 상황 작성 → `outline.json` 작성 → build를 실행한다. 마지막 `verified`는 7이어야 하고, 구조 뷰의 SHA256은 전후가 같아야 한다. 에디터에서 앞뒤 버튼과 문단·코드 렌더링은 직접 확인한다.


## 학습 단계 개편 검증 (2026-11-16, 아래 legacy 절차보다 우선)

저장소 루트에서 `python specs/010-stepwise-code-convergence/test_learning_stages.py`를 실행한다. 새 기본 정의의 상황 장면→실제 선언, 직접 의존별 반복, 숨기기, HTML 이스케이프, 원본 없는 노드의 상황 장면, 문장 장면 다음 코드의 시작 파일, 노드별 원본 검증을 확인한다. 같은 테스트가 아래 기존 fixture를 legacy 7단계로 실행해 원본 구간과 마지막 단계 회귀도 확인한다. 기존 Q1~Q8의 7단계 기대값은 legacy 정의에 한정된다.

실제 예제는 `.zenuml/nia-bookmarks-mvvm.architecture.md`로 prepare→격리된 상황 작성→begin/apply→build를 실행한다. `others.md`의 첫 장면에는 책임 한 줄을 되풀이하지 않는 상황 문단만 있고, 다음 장면은 실제 선언이어야 한다. 연결 장면은 노드마다 직접 상대 하나만 더한다. 마지막 `verified`는 7이어야 한다. 구조 뷰의 SHA256과 원본 저장소의 기존 변경 상태가 실행 전후 같아야 한다. 에디터에서 앞뒤 버튼과 문단 렌더링은 직접 확인한다.

## 준비

- Python 3.9 이상(`python3`, `python`, `py -3` 중 하나)
- VS Code 1.146 이상(Markdown 미리보기)
- 고정 입력은 `specs/010-stepwise-code-convergence/fixtures/`에 둔다.
  - `view.architecture.md`: 노드 7개로 이뤄진 구조 뷰다.
    - 그룹: 최상위 그룹 2개(노드 3개, 2개)와 그룹 없는 노드 1개로 나뉜다.
    - 링크(노드별 원본 위치)는 다음과 같다.

      | 노드 수 | 링크가 가리키는 곳 |
      |---|---|
      | 2 | 같은 파일 `Order.kt` 안의 서로 다른 클래스 |
      | 1 | `Order.kt` 안 클래스의 중첩 클래스 |
      | 1 | 표현식 본문 함수(`fun f() = …`)가 있는 다른 `.kt` 파일 |
      | 1 | 링크 없음 |
      | 1 | `.java` 파일 |
      | 1 | 그 파일에 같은 이름의 선언이 없는 `.kt` 파일 |
  - `src/`: 위 링크가 가리키는 원본이다. 다음 경우를 하나씩 담는다.
    - KDoc과 어노테이션이 붙은 선언
    - 문자열 안에 `{`가 든 함수
    - `"""` 문자열
    - CRLF 파일
  - `work/`: 손으로 쓴 단계 파일이다.
    - 1단계 노드 파일과 2…6단계 노드 파일
    - 2단계에는 `⟨설명⟩`과 `...` 보조 표기를 넣는다.
    - 한 단계는 어떤 노드에서 일부러 바꾸지 않는다.
  - `expected/`: 기대 결과다. `original/*.kt`(잘라낸 원본 범위)와 문서를 둔다.

명령은 저장소 루트에서 실행한다. `<py>`는 찾은 인터프리터이고, `S`는 `.agents/skills/revealing-code-step-by-step/scripts/stages.py`이다.

## Q1. prepare — 원본 범위·이유·문서 나누기 (FR-002, FR-015c, FR-017, FR-020)

```text
<py> S prepare specs/010-stepwise-code-convergence/fixtures/view.architecture.md
```

**기대 결과**:

- **원본 범위**: `fixtures/view.stages/work/original/`의 파일 4개가 `fixtures/expected/original/`과 바이트 단위로 같다.
  - 같은 파일 `Order.kt`의 두 클래스는 각자 자기 선언만 담는다.
  - 중첩 클래스는 들여쓴 그대로 잘린다.
  - 바깥 클래스의 범위에는 중첩 클래스가 들어 있고, `work/manifest.json`의 `contains`에 그 Id가 있다.
  - KDoc과 어노테이션은 범위에 들어간다.
  - 문자열 안의 `{`나 `"""` 때문에 끝이 어긋나지 않는다.
- **구체화하지 않는 노드**: 링크 없음, `.java`, 선언 없음 노드가 contract 2절 표의 `skip_reason`을 갖는다.
- **문서 나누기**: 문서는 `<노드 3개 그룹 Id>.md`와 `others.md` 둘로 정해진다.
- **1단계 프롬프트**: `work/stage1-prompt.md`에 1단계 정의, 노드 7개의 `<id> (<이름>) → <절대 경로>` 줄, 구조 뷰 내용 전부가 들어 있다.
- **다시 실행**: 한 번 더 실행하면 이전 `work/` 내용이 남지 않는다.

## Q2. begin — 복사와 거부 (FR-013)

Q1 뒤에 `fixtures/work/01/*`를 산출 폴더의 `work/01/`로 복사하고 다음을 실행한다.

```text
<py> S begin specs/010-stepwise-code-convergence/fixtures/view.stages 2
<py> S begin specs/010-stepwise-code-convergence/fixtures/view.stages 2
```

**기대 결과**:

- 첫 실행은 구체화하는 노드마다 `work/02/<id>.kt`를 1단계와 똑같이 만들고, 그 코드와 원본 범위를 `=====` 머리 아래에 출력한다. `OrderService` 머리에는 `안에 든 노드: Validator`가 붙는다.
- 두 번째 실행은 종료 코드 2로 끝난다.
- `begin … 1`과 `begin … 7`도 종료 코드 2로 끝난다.
- `work/01/`의 파일 하나를 지우고 산출 폴더를 다시 만든 뒤 `begin … 2`를 실행하면, 종료 코드 2로 끝나고 빠진 경로가 출력된다.

## Q2a. apply — 한 번에 바꾸기와 경고 (R11)

Q2 뒤에 `work/edits.txt`에 블록 두 개를 적는다. 하나는 `OrderService.kt`에 있는 글을, 하나는 `Validator.kt`에 없는 글을 바꾼다. 그다음 `apply … 2`를 실행한다.

**기대 결과**:

- 종료 코드 2로 끝나고 두 번째 블록이 실패했다고 출력된다. 두 파일 모두 바뀌지 않았다.
- 두 번째 블록을 지우고 다시 실행하면 종료 코드 0이고, `changed`에 `OrderService`가 있다. `work/edits.txt`는 지워졌다.
- `begin … 3`을 실행하고 `OrderService.kt`의 원본 줄 하나(예: `@Service`)를 지우는 블록을 `apply … 3`으로 적용하면 `warnings`에 그 줄이 나온다.
- `begin … 4`를 실행한 뒤 `apply … 3`을 실행하면 종료 코드 2로 끝난다.

## Q3. build — 문서 바이트 비교 (FR-010, FR-014~016)

`fixtures/work/`의 나머지 단계 파일을 산출 폴더에 복사한 뒤 실행한다.

```text
<py> S build specs/010-stepwise-code-convergence/fixtures/view.stages
```

**기대 결과**:

- 종료 코드는 0이고, `verified`는 4다.
- 각 문서가 `fixtures/expected/`의 같은 이름 파일과 바이트 단위로 같다.
- 일부러 바꾸지 않은 단계는 `unchanged`에 나오고, 문서의 그 단계에 `이 단계에서는 달라진 것이 없음`이 붙는다.
- diff 층(`pre.diff`)의 줄 수는 코드 줄 수와 같다. 줄 종류(`add`·`mod`·`del`)는 fixture에서 일부러 넣은 추가·변경·삭제와 일치한다.
- 분리 확인: 문서에서 `pre.diff` 요소들과 wrapper 안의 두 번째 `<style>`을 지운 결과가 `fixtures/expected/<문서>.base.md`와 바이트 단위로 같다. `.base.md`는 같은 wrapper와 기본 CSS만 가진 diff 층 없는 기대 문서다.
- 구체화하지 않는 노드는 `⚠️` 이유 줄과 1단계 하나만 갖는다.

## Q4. build — 누락과 불일치 (FR-010)

1. `work/04/`의 파일 하나를 지우고 `build`를 실행한다. 종료 코드 2로 끝나고 빠진 파일이 출력된다.
2. 파일을 되돌린다. 그다음 `fixtures/src/`의 원본 하나에서 그 노드 범위 안의 글자 하나를 바꾸고 `build`를 실행한다. 종료 코드 3으로 끝나고, 그 노드와 첫 번째로 다른 줄 번호가 출력된다. 확인한 뒤 원본을 되돌린다.

## Q5. 단계 정의 고치기 (US3, FR-009, SC-006)

`stages.md`를 임시로 고친다. 중간에 `데이터 모양` 단계를 하나 넣고, `의존 연결`과 `공개 시그니처`의 순서를 바꾼다. 그다음 8단계에 맞춘 작업 파일로 Q1~Q3을 다시 돌린다.

**기대 결과**:

- 제목이 `1단계: 꾸며낸 뼈대 (1/8)` … `8단계: 원본 (8/8)` 순서로 바뀐 정의를 따른다.
- 고친 곳은 `stages.md` 하나뿐이다.
- 확인한 뒤 `stages.md`를 되돌린다.

## Q5a. 단계 보이기와 결과 위치 설정 (FR-009a, FR-019a)

`settings.jsonc`를 임시로 고친다. `"의존 연결": false`, `"꾸며낸 뼈대": false`, `"원본": false`, `"없는 단계": true`로 하고, `output.directory`는 `./out`으로 한다. 그다음 `prepare`를 실행한다.

**기대 결과**:

- 산출 폴더가 `fixtures/out/view.stages/`다. `fixtures/` 안의 다른 파일은 그대로다.
- 출력 `stages`의 상태는 다음과 같다.
  - "꾸며낸 뼈대": `work: 1`, `visible: false`
  - "의존 연결": 목록에 없다.
  - "공개 시그니처": `merged`에 "의존 연결"이 있다.
  - "원본": `visible: true`
  - 화면 번호: 보이는 단계끼리 `1/5` … `5/5`로 매겨진다.
- `notices`에 두 줄이 있다. "원본"은 항상 보인다는 알림과, "없는 단계"는 단계 정의에 없어 무시했다는 알림이다.
- `--show=의존 연결`을 더해 다시 실행하면 "의존 연결"이 목록에 돌아온다. `settings.jsonc`는 바뀌지 않는다.
- 확인한 뒤 `settings.jsonc`를 되돌린다.

## Q6. VS Code 미리보기 (FR-015~016, FR-015e)

`fixtures/view.stages/`의 문서를 미리보기로 열고 다음을 확인한다.

- 노드마다 상자가 하나씩 있고, ← →로 넘길 수 있다. 처음과 끝에서는 버튼이 흐리고, 넘길 때 애니메이션이 없다.
- 제목은 `2단계: 선언의 종류 (2/7)` 형식이고, 그 아래에 단계 설명은 없다.
- 노드 제목과 상자 사이에 회색 띠로 `책임` 한 줄이 있고, 단계를 넘겨도 그대로다. 책임이 `설명에 명시되지 않음`인 노드에는 띠가 없다(FR-015e).
- 상자 높이는 현재 단계 길이를 따르고, 상한을 넘으면 상자 안에서 세로로 스크롤된다. 스크롤하는 동안 제목이 보인다.
- 긴 줄은 줄바꿈되지 않고 코드 열만 가로로 스크롤된다. 편집기의 자동 줄바꿈을 켜도 같다.
- 달라진 줄이 VS Code의 git 변경 표시처럼 보인다. 추가는 초록, 변경은 파랑이고, 지워진 자리에는 빨간 삼각형이 있다. 막대와 줄 배경은 코드의 해당 줄과 같은 높이에 있고, 가로·세로로 스크롤해도 줄을 따라간다. 색칠 위의 코드도 선택·복사할 수 있다(research R7의 확인 (a)(b)).
- diff 층을 지운 문서(`*.base.md`)를 미리보기로 열면, 기존 상자가 색칠만 빠진 채 똑같이 동작한다(research R7의 확인 (c)).
- Kotlin 구문 색칠이 보인다.
- 넘겨 보기를 지원하지 않는 곳에서의 모습(FR-015b): 문서 끝 wrapper 안의 두 `<style>`을 지운 사본을 미리보기로 열면 모든 단계가 순서대로 나열되고, 코드는 그대로 보인다. GitHub에서는 wrapper를 펼치지 않는 한 CSS 원문이 보이지 않는다(FR-022).

## Q7. 끝까지 실행 (US1, US2, SC-001~003, SC-007, SC-008)

실제 구조 뷰 `.zenuml/swemo-architecture.architecture.md`로 스킬을 요청한다(예: "이 구조 뷰로 정제 단계 코드 만들어줘").

**기대 결과**:

- **1단계 격리(SC-002)**: 대화 기록의 1단계 서브에이전트 프롬프트는 `stage1-prompt.md`를 읽고 따르라는 한 줄뿐이고, 그 파일에는 구조 뷰 내용, 1단계 정의, 규칙, 쓸 경로만 있다. 서브에이전트는 그 파일 말고는 Read하지 않았고, Grep·Glob·Bash·웹 도구를 호출하지 않았다.
- **중간 단계**: 메인 에이전트는 작업 파일을 따로 읽지 않고, 단계마다 `begin` 한 번, `edits.txt` 쓰기와 `apply`(경고를 고치는 데 쓴 것 포함)만 했다.
- **응답**: 채팅 응답이 `build`의 `reply`와 같다.
- **1단계 내용(SC-001)**: 노드 이름이 모두 그대로 나오고, 구조 뷰의 의존이 모두 코드에 드러난다.
- **2단계부터**: 아직 드러나지 않은 본문이 지어낸 코드가 아니라 `⟨설명⟩`이나 `...`이다.
- **이름 맞추기**: 이름이 드러난 단계에서 다른 노드의 호출 이름도 같이 바뀐다(FR-011a).
- **마지막 단계(SC-003)**: `build`가 종료 코드 0으로 끝나고, `verified`가 구체화한 노드 수와 같다.
- **원본 보존(SC-008)**: `git -C ../swemo status`와 구조 뷰 파일의 `git diff`가 비어 있다.
- **단계 내용**: 몇 개 노드를 넘겨 보며 눈으로 확인한다.
  - 각 단계가 정의된 측면만 바꿨다(FR-011).
  - 구체화 사다리를 내려간 곳이 없다(FR-012, FR-012a).

## Q8. 같은 이름의 선언 고르기 (FR-002)

오버로드만 담은 구조 뷰 `fixtures/overload.architecture.md`(노드 `Screen`, `ScreenViewModel`)와 원본 `fixtures/src/Screen.kt`(공개 `fun Screen(vm)`과 `private fun Screen(state, ...)`)를 쓴다.

```text
<py> S prepare specs/010-stepwise-code-convergence/fixtures/overload.architecture.md
<py> S prepare specs/010-stepwise-code-convergence/fixtures/overload.architecture.md --pick=Screen:1
```

**기대 결과**:

- 첫 실행: `Screen` 노드에 `candidates` 2개(3–7줄 공개, 9–15줄 비공개)와 `--pick으로 하나를 골라야 함` 사유가 있다.
- 두 번째 실행: `Screen`의 `range`가 3–7줄이다. `work/original/Screen.kt`는 `fixtures/expected/original/overload-Screen.kt`와 바이트 단위로 같다.
- 그다음 `fixtures/work-overload/01/*`를 `work/01/`에 복사하고 `begin 2`~`begin 6`, `build`를 실행한다. 종료 코드는 0이고 `verified`는 1이다(`ScreenViewModel`은 링크가 없어 구체화하지 않음).
- 확인한 뒤 `fixtures/overload.stages/`를 지운다.

## 2026-11-23 변화 0단계 확인

**준비**: git이 있어야 한다. 자동 확인은 `python -m unittest specs/010-stepwise-code-convergence/test_learning_stages.py`에 들어 있다(임시 저장소를 만들어 노드 하나를 고치고 하나를 지운다. git이 없으면 skip).

**기대 결과**:

- `--base` 없이 돌린 기존 fixture의 결과는 기존 기대 결과와 비교해 사라진 자리 표시(`del`/`del-after` 클래스)와 그 CSS만 다르다(SC-019).
- `--base`를 준 실행에서 고친 노드에만 0단계가 하나 있고, 두 복원이 변경 후·변경 전 범위와 같다. 지운 노드는 `### 🗑️` 제목이고, 마지막 단계가 변경 전 범위와 같다. 다른 노드의 1단계 이후는 `--base` 없는 결과와 같다(SC-020).
- 같은 실행의 스코프 목록에 고친 노드의 변경 전 줄이 없고, outline 항목은 지운 노드만큼만 늘어난다(SC-021).

**수동 확인**: 실제 저장소(예: swemo, `--base=5ee6b90 --head=26035c6`)로 만든 문서를 VS Code 미리보기로 연다. 1단계에서 ←를 누르면 0단계가 나오고, 0단계의 ←는 비활성이며, →를 누르면 1단계로 돌아온다. 초록·파랑·빨강 배경과 막대가 보인다.

## 2026-11-23 공유 스크롤 상자 확인

**자동**: 테스트 파일 전체를 실행한다. 확인하는 것은 두 가지다.
- 상자마다 `scroller`가 하나이고 단계마다 `pane`이 하나다.
- 문서의 fence 내용이 단계 장면과 차례대로 같다.

기존 기대 결과는 다시 만든다. `git diff`의 차이가 상자 구조(제목과 장면의 자리)와 CSS뿐이고 fence 안 글자는 같은지 확인한다(SC-022).

**수동**: swemo 샘플을 다시 만들어 VS Code 미리보기로 연다. `CategorySelector`에서 코드를 아래로 스크롤한 뒤 →를 누르면 같은 위치에서 보인다. ←도 같다. 짧은 단계로 가면 그 끝에서 멈춘다. 제목과 버튼은 스크롤해도 보인다.

## 2026-11-24 -1단계 확인

```
python specs/010-stepwise-code-convergence/test_learning_stages.py
```

- `--base`를 준 실행에서 고친 노드에만 -1단계가 하나 있다. 그 fence는 `work/before/<id>.kt`와 같고 색칠 층이 없다. 0단계의 ←는 -1단계로 간다. 지운 노드와 바뀌지 않은 노드에는 -1단계가 없다(SC-023).

**수동 확인**: 0단계 확인과 같은 문서를 VS Code 미리보기로 연다. 0단계에서 ←를 누르면 -1단계(변경 전 코드, 색 없음)가 나오고, -1단계의 ←는 비활성이며, →를 누르면 0단계로 돌아온다.

## 2026-11-24 노드 제목의 변화 표시와 링크 확인

```
python specs/010-stepwise-code-convergence/test_learning_stages.py
```

- 변화 fixture: 고친 노드 ♻️, 지운 노드 🗑️, 바뀌지 않은 노드 이모지 없음, 범례 상자 하나, 링크 있는 제목의 href가 결과 폴더에서 구조 뷰 링크와 같은 파일을 가리킨다(SC-024).
- 비교 기준 없는 기대 결과 파일의 diff는 노드 제목과 `.legend` CSS 줄뿐이다.

**수동 확인**: swemo `5ee6b90 → 26035c6` 결과를 VS Code 미리보기로 연다. 맨 위 상자에 범례와 비교 기준이 있고, 노드 제목의 이모지가 구조 뷰와 맞으며, 굵은 노드 이름을 누르면 원본 파일이 열린다.

## 2026-11-24 단계 제목의 번호 확인

```
python specs/010-stepwise-code-convergence/test_learning_stages.py
```

- fixture 문서의 단계 제목이 `3/6단계: 펼치기 — 1. …`처럼 시작하고 끝에 `(k/n)`이 없다(SC-025).

**수동 확인**: swemo 문서의 제목이 `07/22단계: 펼치기 — 5. …`이고, 0단계·-1단계 제목은 전과 같다.
