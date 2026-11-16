# 기타 — 정제 단계

## 인프라

### PaymentGateway

⚠️ 원본 파일에서 PaymentGateway 선언을 찾지 못해 구체화하지 않음

<div class="stages">

<input type="radio" name="PaymentGateway" id="PaymentGateway-1" class="s1" checked>

<div class="stage s1">

<div class="head"><span class="name">1단계: 꾸며낸 뼈대 (1/1)</span><span class="nav">←</span><span class="nav">→</span></div>
<div class="note">원본과 같아진 것: 없음(노드 이름만 구조 뷰와 같음)</div>

<div class="code">

```kotlin
class PaymentGateway {
    fun pay(order: Order) {
        LegacyBridge().forward(order)
    }
}
```

</div>

</div>

</div>

### LegacyBridge(java)

⚠️ 원본이 Kotlin이 아니어서 구체화하지 않음

<div class="stages">

<input type="radio" name="LegacyBridge" id="LegacyBridge-1" class="s1" checked>

<div class="stage s1">

<div class="head"><span class="name">1단계: 꾸며낸 뼈대 (1/1)</span><span class="nav">←</span><span class="nav">→</span></div>
<div class="note">원본과 같아진 것: 없음(노드 이름만 구조 뷰와 같음)</div>

<div class="code">

```kotlin
class LegacyBridge {
    fun forward(order: Order) {}
}
```

</div>

</div>

</div>

### formatTotal

<div class="stages">

<input type="radio" name="formatTotal" id="formatTotal-1" class="s1" checked>
<input type="radio" name="formatTotal" id="formatTotal-2" class="s2">
<input type="radio" name="formatTotal" id="formatTotal-3" class="s3">
<input type="radio" name="formatTotal" id="formatTotal-4" class="s4">
<input type="radio" name="formatTotal" id="formatTotal-5" class="s5">
<input type="radio" name="formatTotal" id="formatTotal-6" class="s6">
<input type="radio" name="formatTotal" id="formatTotal-7" class="s7">

<div class="stage s1">

<div class="head"><span class="name">1단계: 꾸며낸 뼈대 (1/7)</span><span class="nav">←</span><label class="nav" for="formatTotal-2">→</label></div>
<div class="note">원본과 같아진 것: 없음(노드 이름만 구조 뷰와 같음)</div>

<div class="code">

```kotlin
fun formatTotal(order: Order): String = ""
```

</div>

</div>

<div class="stage s2">

<div class="head"><span class="name">2단계: 선언의 종류 (2/7)</span><label class="nav" for="formatTotal-1">←</label><label class="nav" for="formatTotal-3">→</label></div>
<div class="note">원본과 같아진 것: 각 노드가 실제로 무엇인지 — 노드 자체의 선언에 딸린 것 전부: 클래스·인터페이스·객체·함수 등 선언의 종류, 수식어(가시성·data·abstract 등), 상속·구현 관계, 그 선언에 붙은 어노테이션</div>

<div class="code">

```kotlin
fun formatTotal(order: Order): String = ⟨합계를 글로 바꿈⟩
```

</div>

</div>

<div class="stage s3">

<div class="head"><span class="name">3단계: 의존 연결 (3/7)</span><label class="nav" for="formatTotal-2">←</label><label class="nav" for="formatTotal-4">→</label></div>
<div class="note">이 단계에서는 달라진 것이 없음</div>

<div class="code">

```kotlin
fun formatTotal(order: Order): String = ⟨합계를 글로 바꿈⟩
```

</div>

</div>

<div class="stage s4">

<div class="head"><span class="name">4단계: 공개 시그니처 (4/7)</span><label class="nav" for="formatTotal-3">←</label><label class="nav" for="formatTotal-5">→</label></div>
<div class="note">원본과 같아진 것: 밖에서 보이는 멤버의 실제 이름·매개변수·반환 타입, 그리고 그것이 쓰는 데이터 타입의 이름</div>

<div class="code">

```kotlin
fun formatTotal(total: BigDecimal): String =
    ⟨합계를 글로 바꿈⟩
```

</div>

</div>

<div class="stage s5">

<div class="head"><span class="name">5단계: 핵심 흐름 (5/7)</span><label class="nav" for="formatTotal-4">←</label><label class="nav" for="formatTotal-6">→</label></div>
<div class="note">이 단계에서는 달라진 것이 없음</div>

<div class="code">

```kotlin
fun formatTotal(total: BigDecimal): String =
    ⟨합계를 글로 바꿈⟩
```

</div>

</div>

<div class="stage s6">

<div class="head"><span class="name">6단계: 나머지 로직 (6/7)</span><label class="nav" for="formatTotal-5">←</label><label class="nav" for="formatTotal-7">→</label></div>
<div class="note">원본과 같아진 것: 남은 본문 전부와 숨은 멤버(비공개 함수·프로퍼티, 그 어노테이션 포함), 오류 처리, 분기</div>

<div class="code">

```kotlin
fun formatTotal(total: BigDecimal): String =
    "합계: " + total.setScale(2).toPlainString() + " {원}"
```

</div>

</div>

<div class="stage s7">

<div class="head"><span class="name">7단계: 원본 (7/7)</span><label class="nav" for="formatTotal-6">←</label><span class="nav">→</span></div>
<div class="note">원본과 같아진 것: 전부 — 원본 범위의 주석·빈 줄·들여쓰기까지</div>

<div class="code">

```kotlin
/** 합계를 사람이 읽는 글로 바꾼다. */
fun formatTotal(total: BigDecimal): String =
    "합계: " + total.setScale(2).toPlainString() + " {원}"
```

</div>

</div>

</div>

### AuditLog

⚠️ 원본 위치가 없어 구체화하지 않음

<div class="stages">

<input type="radio" name="AuditLog" id="AuditLog-1" class="s1" checked>

<div class="stage s1">

<div class="head"><span class="name">1단계: 꾸며낸 뼈대 (1/1)</span><span class="nav">←</span><span class="nav">→</span></div>
<div class="note">원본과 같아진 것: 없음(노드 이름만 구조 뷰와 같음)</div>

<div class="code">

```kotlin
class AuditLog {
    fun write(order: Order) {}
}
```

</div>

</div>

</div>

<style>
.stages { border: 1px solid rgba(128,128,128,.4); border-radius: 6px; padding: 0 1em; margin-bottom: 1em; }
.stages > input { position: absolute; opacity: 0; pointer-events: none; }
.stages > .stage { display: none; }
.stages > input.s1:checked ~ .stage.s1 { display: block; }
.stages > input.s2:checked ~ .stage.s2 { display: block; }
.stages > input.s3:checked ~ .stage.s3 { display: block; }
.stages > input.s4:checked ~ .stage.s4 { display: block; }
.stages > input.s5:checked ~ .stage.s5 { display: block; }
.stages > input.s6:checked ~ .stage.s6 { display: block; }
.stages > input.s7:checked ~ .stage.s7 { display: block; }
.stages .head { display: flex; align-items: center; gap: .4em; padding: .5em 0 .2em; font-weight: 600; }
.stages .head .name { flex: 1; }
.stages .nav { display: inline-block; width: 2.2em; height: 1.8em; line-height: 1.8em; text-align: center; border: 1px solid rgba(128,128,128,.5); border-radius: 4px; font-weight: 400; cursor: pointer; user-select: none; }
.stages span.nav { opacity: .3; cursor: default; }
.stages .note { padding: 0 0 .5em; opacity: .8; }
.stages .code { max-height: min(30lh, 70vh); overflow: auto; margin-bottom: 1em; }
.stages .code pre { margin: 0; overflow: visible; width: max-content; min-width: 100%; box-sizing: border-box; }
.stages .code pre, .stages .code pre code { white-space: pre; word-break: normal; }
</style>
