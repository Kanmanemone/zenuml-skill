# navigation3-sample

Navigation 3 (`androidx.navigation3`) 학습용 최소 샘플 앱. 첨부된 아키텍처 뷰(Now in
Android의 navigation3 구조)를 참고해, Hilt/멀티모듈/적응형 레이아웃 같은 부가 요소는
전부 빼고 핵심 개념만 남겼습니다. 화면(엔트리)은 총 3개: Home, Settings, Detail.

## 구조 대응표

원본(NIA) 구조의 개념을 그대로 축소해 옮겼습니다.

| 원본 (PDF)                    | 이 샘플                                  | 역할                                   |
|--------------------------------|-------------------------------------------|----------------------------------------|
| `NiaNavKey`                    | `navigation/AppNavKey.kt`                  | 모든 목적지 키의 계약 (`isTopLevel`)   |
| `NiaNavigatorState`            | `navigation/AppNavigatorState.kt`          | 탭별 백 스택 데이터 보관               |
| `NiaNavigator`                 | `navigation/AppNavigator.kt`               | `navigate()` / `pop()` 연산            |
| `ForYouEntryProvider` 등        | `entries/HomeEntryProvider.kt` 등 3개 파일 | `entry<Route> { }`로 화면 등록         |
| `NiaNavDisplay`                | `ui/AppNavDisplay.kt`                      | `entryProviderBuilders`를 모아 androidx `NavDisplay` 호출 |
| `NiaApp`                       | `ui/App.kt`                                | 탭 전환 버튼 + `AppNavDisplay` 배치    |
| `MainActivity`                 | `MainActivity.kt`                          | 상태/네비게이터 생성 후 `App` 호출     |

Hilt 멀티바인딩으로 모으던 `entryProviderBuilders (Set)`은 여기서는 그냥
`AppNavDisplay.kt`에서 만든 `List`로 대체했습니다 (DI 없이도 같은 조립 패턴을
보여주는 것이 목적).

## 빌드에 관한 안내

이 세션(샌드박스 환경)은 네트워크 정책상 `dl.google.com`(Android SDK, AGP/androidx
Maven 아티팩트 다운로드 경로)에 접근할 수 없어, 여기서 `./gradlew assembleDebug`를
직접 실행해 컴파일을 검증하지 못했습니다. Android Studio에서 열거나 정상적인
네트워크 환경에서 `./gradlew assembleDebug`를 실행해 확인해 주세요. 버전 조합
(AGP 8.7.3 / Kotlin 2.1.0 / Compose BOM 2025.06.01 / navigation3 1.1.5)이 맞지
않으면 Android Studio가 업그레이드를 제안합니다.
