# navigation3-basics-sample

Navigation 3 공식 문서(https://developer.android.com/guide/navigation/navigation-3/basics)의
예제만 그대로 따라 만든 최소 학습용 샘플. `navigation3-sample/`(Now in Android 구조를
축소한 샘플)과 달리 여기엔 NIA에서 가져온 개념(`NavKey` 커스텀 인터페이스, `Navigator`
래퍼, api/impl 모듈 분리, DI)이 전혀 없습니다 — 공식 문서가 보여주는 그대로 키(plain
object/data class) + `mutableStateListOf<Any>` 백 스택 + `entryProvider { entry<T> {} }`
+ `NavDisplay` 네 가지만 있습니다.

파일 하나(`MainActivity.kt`)에 전부 들어 있습니다. 목적이 "구조를 나누어 보여주는 것"이
아니라 "라이브러리 자체의 최소 API 표면을 보여주는 것"이라, 파일을 쪼갤 이유가 없어서
그렇게 뒀습니다.

화면 3개: `Home` → `Product(id)` / `About`. `Home`에서 두 화면 중 하나로 이동하고,
각 화면에서 뒤로가기 버튼으로 `backStack.removeLastOrNull()`을 호출해 돌아옵니다.

## 빌드에 관한 안내

`navigation3-sample/README.md`와 동일한 사유로, 이 세션은 `dl.google.com`(Android SDK,
AGP/androidx Maven 아티팩트) 접근이 막혀 있어 여기서 직접 `./gradlew assembleDebug`를
실행해 컴파일을 검증하지 못했습니다. Android Studio에서 열거나 정상 네트워크 환경에서
빌드해 확인해 주세요.
