# 기타 — 정제 단계

## 인프라

### PaymentGateway

<div class="resp"><span class="label">책임</span> 결제를 요청한다.</div>

⚠️ 원본 파일에서 PaymentGateway 선언을 찾지 못해 구체화하지 않음

<div class="stages">

<input type="radio" name="PaymentGateway" id="PaymentGateway-1" class="s1" checked>

<div class="stage s1">

<div class="head"><span class="name">1단계: 꾸며낸 뼈대 (1/1)</span><span class="nav">←</span><span class="nav">→</span></div>

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

<div class="resp"><span class="label">책임</span> 합계를 글로 바꾼다.</div>

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

<div class="code">

```kotlin
fun formatTotal(order: Order): String = ""
```

</div>

</div>

<div class="stage s2">

<div class="head"><span class="name">2단계: 선언의 종류 (2/7)</span><label class="nav" for="formatTotal-1">←</label><label class="nav" for="formatTotal-3">→</label></div>

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

<div class="code">

```kotlin
fun formatTotal(total: BigDecimal): String =
    "합계: " + total.setScale(2).toPlainString() + " {원}"
```

</div>

</div>

<div class="stage s7">

<div class="head"><span class="name">7단계: 원본 (7/7)</span><label class="nav" for="formatTotal-6">←</label><span class="nav">→</span></div>

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

<div class="resp"><span class="label">책임</span> 주문 기록을 남긴다.</div>

⚠️ 원본 위치가 없어 구체화하지 않음

<div class="stages">

<input type="radio" name="AuditLog" id="AuditLog-1" class="s1" checked>

<div class="stage s1">

<div class="head"><span class="name">1단계: 꾸며낸 뼈대 (1/1)</span><span class="nav">←</span><span class="nav">→</span></div>

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
.resp { margin: 0 0 .6em; padding: .4em .8em; border-left: 3px solid rgba(128,128,128,.5); background: rgba(128,128,128,.08); border-radius: 0 4px 4px 0; }
.resp .label { font-weight: 600; margin-right: .4em; opacity: .75; }
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
