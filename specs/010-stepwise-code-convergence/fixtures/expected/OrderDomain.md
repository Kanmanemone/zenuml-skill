# 주문 도메인 — 정제 단계

### OrderService

<div class="stages">

<input type="radio" name="OrderService" id="OrderService-1" class="s1" checked>
<input type="radio" name="OrderService" id="OrderService-2" class="s2">
<input type="radio" name="OrderService" id="OrderService-3" class="s3">
<input type="radio" name="OrderService" id="OrderService-4" class="s4">
<input type="radio" name="OrderService" id="OrderService-5" class="s5">
<input type="radio" name="OrderService" id="OrderService-6" class="s6">
<input type="radio" name="OrderService" id="OrderService-7" class="s7">

<div class="stage s1">

<div class="head"><span class="name">1단계: 꾸며낸 뼈대 (1/7)</span><span class="nav">←</span><label class="nav" for="OrderService-2">→</label></div>

<div class="code">

```kotlin
class OrderService {
    fun handle(order: Order) {
        Validator().verify(order)
        InventoryRepository().hold(order)
        PaymentGateway().pay(order)
        formatTotal(order)
        AuditLog().write(order)
    }
}
```

</div>

</div>

<div class="stage s2">

<div class="head"><span class="name">2단계: 선언의 종류 (2/7)</span><label class="nav" for="OrderService-1">←</label><label class="nav" for="OrderService-3">→</label></div>

<div class="code">

```kotlin
@Service
class OrderService {
    fun handle(order: Order) {
        ⟨주문을 검증하고, 재고를 잡고, 결제하고, 합계를 글로 바꿔 기록함⟩
    }

    class Validator {
        ...
    }
}
```

<pre class="diff" aria-hidden="true"><code><span class="add">@Service</span>
<span>class OrderService {</span>
<span>    fun handle(order: Order) {</span>
<span class="mod">        ⟨주문을 검증하고, 재고를 잡고, 결제하고, 합계를 글로 바꿔 기록함⟩</span>
<span class="mod">    }</span>
<span class="mod"></span>
<span class="mod">    class Validator {</span>
<span class="mod">        ...</span>
<span>    }</span>
<span>}</span>
</code></pre>

</div>

</div>

<div class="stage s3">

<div class="head"><span class="name">3단계: 의존 연결 (3/7)</span><label class="nav" for="OrderService-2">←</label><label class="nav" for="OrderService-4">→</label></div>

<div class="code">

```kotlin
@Service
class OrderService(
    private val inventory: InventoryRepository,
    private val payments: PaymentGateway,
) {
    fun handle(order: Order) {
        ⟨주문을 검증하고, 재고를 잡고, 결제하고, 합계를 글로 바꿔 기록함⟩
    }

    class Validator {
        ...
    }
}
```

<pre class="diff" aria-hidden="true"><code><span>@Service</span>
<span class="mod">class OrderService(</span>
<span class="add">    private val inventory: InventoryRepository,</span>
<span class="add">    private val payments: PaymentGateway,</span>
<span class="add">) {</span>
<span>    fun handle(order: Order) {</span>
<span>        ⟨주문을 검증하고, 재고를 잡고, 결제하고, 합계를 글로 바꿔 기록함⟩</span>
<span>    }</span>
<span></span>
<span>    class Validator {</span>
<span>        ...</span>
<span>    }</span>
<span>}</span>
</code></pre>

</div>

</div>

<div class="stage s4">

<div class="head"><span class="name">4단계: 공개 시그니처 (4/7)</span><label class="nav" for="OrderService-3">←</label><label class="nav" for="OrderService-5">→</label></div>

<div class="code">

```kotlin
@Service
class OrderService(
    private val inventory: InventoryRepository,
    private val payments: PaymentGateway,
) {
    fun place(order: Order): Receipt {
        ⟨주문을 검증하고, 재고를 잡고, 결제하고, 합계를 글로 바꿔 기록함⟩
    }

    class Validator {
        fun check(order: Order): Boolean = ...
    }
}
```

<pre class="diff" aria-hidden="true"><code><span>@Service</span>
<span>class OrderService(</span>
<span>    private val inventory: InventoryRepository,</span>
<span>    private val payments: PaymentGateway,</span>
<span>) {</span>
<span class="mod">    fun place(order: Order): Receipt {</span>
<span>        ⟨주문을 검증하고, 재고를 잡고, 결제하고, 합계를 글로 바꿔 기록함⟩</span>
<span>    }</span>
<span></span>
<span>    class Validator {</span>
<span class="mod">        fun check(order: Order): Boolean = ...</span>
<span>    }</span>
<span>}</span>
</code></pre>

</div>

</div>

<div class="stage s5">

<div class="head"><span class="name">5단계: 핵심 흐름 (5/7)</span><label class="nav" for="OrderService-4">←</label><label class="nav" for="OrderService-6">→</label></div>

<div class="code">

```kotlin
@Service
class OrderService(
    private val inventory: InventoryRepository,
    private val payments: PaymentGateway,
) {
    fun place(order: Order): Receipt {
        ⟨주문이 비었는지 확인하고 합계를 구함⟩
        inventory.reserve(order.id)
        payments.charge(order.id, total)
        AuditLog.record(⟨주문 번호와 formatTotal(total)로 만든 글⟩)
        return Receipt(order.id, total)
    }

    class Validator {
        fun check(order: Order): Boolean = ...
    }
}
```

<pre class="diff" aria-hidden="true"><code><span>@Service</span>
<span>class OrderService(</span>
<span>    private val inventory: InventoryRepository,</span>
<span>    private val payments: PaymentGateway,</span>
<span>) {</span>
<span>    fun place(order: Order): Receipt {</span>
<span class="mod">        ⟨주문이 비었는지 확인하고 합계를 구함⟩</span>
<span class="add">        inventory.reserve(order.id)</span>
<span class="add">        payments.charge(order.id, total)</span>
<span class="add">        AuditLog.record(⟨주문 번호와 formatTotal(total)로 만든 글⟩)</span>
<span class="add">        return Receipt(order.id, total)</span>
<span>    }</span>
<span></span>
<span>    class Validator {</span>
<span>        fun check(order: Order): Boolean = ...</span>
<span>    }</span>
<span>}</span>
</code></pre>

</div>

</div>

<div class="stage s6">

<div class="head"><span class="name">6단계: 나머지 로직 (6/7)</span><label class="nav" for="OrderService-5">←</label><label class="nav" for="OrderService-7">→</label></div>

<div class="code">

```kotlin
@Service
class OrderService(
    private val inventory: InventoryRepository,
    private val payments: PaymentGateway,
) {
    fun place(order: Order): Receipt {
        require(order.lines.isNotEmpty()) { "빈 주문 {${order.id}}" }
        val total = order.lines.sumOf { it.price }
        inventory.reserve(order.id)
        payments.charge(order.id, total)
        AuditLog.record("주문 ${order.id}: ${formatTotal(total)}")
        return Receipt(order.id, total)
    }

    class Validator {
        fun check(order: Order): Boolean = order.lines.all { it.price > BigDecimal.ZERO }
    }
}
```

<pre class="diff" aria-hidden="true"><code><span>@Service</span>
<span>class OrderService(</span>
<span>    private val inventory: InventoryRepository,</span>
<span>    private val payments: PaymentGateway,</span>
<span>) {</span>
<span>    fun place(order: Order): Receipt {</span>
<span class="mod">        require(order.lines.isNotEmpty()) { "빈 주문 {${order.id}}" }</span>
<span class="add">        val total = order.lines.sumOf { it.price }</span>
<span>        inventory.reserve(order.id)</span>
<span>        payments.charge(order.id, total)</span>
<span class="mod">        AuditLog.record("주문 ${order.id}: ${formatTotal(total)}")</span>
<span>        return Receipt(order.id, total)</span>
<span>    }</span>
<span></span>
<span>    class Validator {</span>
<span class="mod">        fun check(order: Order): Boolean = order.lines.all { it.price &gt; BigDecimal.ZERO }</span>
<span>    }</span>
<span>}</span>
</code></pre>

</div>

</div>

<div class="stage s7">

<div class="head"><span class="name">7단계: 원본 (7/7)</span><label class="nav" for="OrderService-6">←</label><span class="nav">→</span></div>

<div class="code">

```kotlin
/**
 * 주문을 만들고 재고를 예약한다. 본문의 { 는 주석이라 세지 않는다.
 */
@Service
class OrderService(
    private val inventory: InventoryRepository,
    private val payments: PaymentGateway,
) {
    fun place(order: Order): Receipt {
        require(order.lines.isNotEmpty()) { "빈 주문 {${order.id}}" }
        val total = order.lines.sumOf { it.price }
        inventory.reserve(order.id)
        payments.charge(order.id, total)
        AuditLog.record("주문 ${order.id}: ${formatTotal(total)}")
        return Receipt(order.id, total)
    }

    class Validator {
        // 주문 줄이 모두 양수 가격인지 본다
        fun check(order: Order): Boolean = order.lines.all { it.price > BigDecimal.ZERO }
    }
}
```

<pre class="diff" aria-hidden="true"><code><span class="add">/**</span>
<span class="add"> * 주문을 만들고 재고를 예약한다. 본문의 { 는 주석이라 세지 않는다.</span>
<span class="add"> */</span>
<span>@Service</span>
<span>class OrderService(</span>
<span>    private val inventory: InventoryRepository,</span>
<span>    private val payments: PaymentGateway,</span>
<span>) {</span>
<span>    fun place(order: Order): Receipt {</span>
<span>        require(order.lines.isNotEmpty()) { "빈 주문 {${order.id}}" }</span>
<span>        val total = order.lines.sumOf { it.price }</span>
<span>        inventory.reserve(order.id)</span>
<span>        payments.charge(order.id, total)</span>
<span>        AuditLog.record("주문 ${order.id}: ${formatTotal(total)}")</span>
<span>        return Receipt(order.id, total)</span>
<span>    }</span>
<span></span>
<span>    class Validator {</span>
<span class="add">        // 주문 줄이 모두 양수 가격인지 본다</span>
<span>        fun check(order: Order): Boolean = order.lines.all { it.price &gt; BigDecimal.ZERO }</span>
<span>    }</span>
<span>}</span>
</code></pre>

</div>

</div>

</div>

### Validator

<div class="stages">

<input type="radio" name="Validator" id="Validator-1" class="s1" checked>
<input type="radio" name="Validator" id="Validator-2" class="s2">
<input type="radio" name="Validator" id="Validator-3" class="s3">
<input type="radio" name="Validator" id="Validator-4" class="s4">
<input type="radio" name="Validator" id="Validator-5" class="s5">
<input type="radio" name="Validator" id="Validator-6" class="s6">
<input type="radio" name="Validator" id="Validator-7" class="s7">

<div class="stage s1">

<div class="head"><span class="name">1단계: 꾸며낸 뼈대 (1/7)</span><span class="nav">←</span><label class="nav" for="Validator-2">→</label></div>

<div class="code">

```kotlin
class Validator {
    fun verify(order: Order) {}
}
```

</div>

</div>

<div class="stage s2">

<div class="head"><span class="name">2단계: 선언의 종류 (2/7)</span><label class="nav" for="Validator-1">←</label><label class="nav" for="Validator-3">→</label></div>

<div class="code">

```kotlin
    class Validator {
        ...
    }
```

<pre class="diff" aria-hidden="true"><code><span class="mod">    class Validator {</span>
<span class="mod">        ...</span>
<span class="mod">    }</span>
</code></pre>

</div>

</div>

<div class="stage s3">

<div class="head"><span class="name">3단계: 의존 연결 (3/7)</span><label class="nav" for="Validator-2">←</label><label class="nav" for="Validator-4">→</label></div>
<div class="note">이 단계에서는 달라진 것이 없음</div>

<div class="code">

```kotlin
    class Validator {
        ...
    }
```

</div>

</div>

<div class="stage s4">

<div class="head"><span class="name">4단계: 공개 시그니처 (4/7)</span><label class="nav" for="Validator-3">←</label><label class="nav" for="Validator-5">→</label></div>

<div class="code">

```kotlin
    class Validator {
        fun check(order: Order): Boolean = ...
    }
```

<pre class="diff" aria-hidden="true"><code><span>    class Validator {</span>
<span class="mod">        fun check(order: Order): Boolean = ...</span>
<span>    }</span>
</code></pre>

</div>

</div>

<div class="stage s5">

<div class="head"><span class="name">5단계: 핵심 흐름 (5/7)</span><label class="nav" for="Validator-4">←</label><label class="nav" for="Validator-6">→</label></div>
<div class="note">이 단계에서는 달라진 것이 없음</div>

<div class="code">

```kotlin
    class Validator {
        fun check(order: Order): Boolean = ...
    }
```

</div>

</div>

<div class="stage s6">

<div class="head"><span class="name">6단계: 나머지 로직 (6/7)</span><label class="nav" for="Validator-5">←</label><label class="nav" for="Validator-7">→</label></div>

<div class="code">

```kotlin
    class Validator {
        fun check(order: Order): Boolean = order.lines.all { it.price > BigDecimal.ZERO }
    }
```

<pre class="diff" aria-hidden="true"><code><span>    class Validator {</span>
<span class="mod">        fun check(order: Order): Boolean = order.lines.all { it.price &gt; BigDecimal.ZERO }</span>
<span>    }</span>
</code></pre>

</div>

</div>

<div class="stage s7">

<div class="head"><span class="name">7단계: 원본 (7/7)</span><label class="nav" for="Validator-6">←</label><span class="nav">→</span></div>

<div class="code">

```kotlin
    class Validator {
        // 주문 줄이 모두 양수 가격인지 본다
        fun check(order: Order): Boolean = order.lines.all { it.price > BigDecimal.ZERO }
    }
```

<pre class="diff" aria-hidden="true"><code><span>    class Validator {</span>
<span class="add">        // 주문 줄이 모두 양수 가격인지 본다</span>
<span>        fun check(order: Order): Boolean = order.lines.all { it.price &gt; BigDecimal.ZERO }</span>
<span>    }</span>
</code></pre>

</div>

</div>

</div>

### InventoryRepository

<div class="stages">

<input type="radio" name="InventoryRepository" id="InventoryRepository-1" class="s1" checked>
<input type="radio" name="InventoryRepository" id="InventoryRepository-2" class="s2">
<input type="radio" name="InventoryRepository" id="InventoryRepository-3" class="s3">
<input type="radio" name="InventoryRepository" id="InventoryRepository-4" class="s4">
<input type="radio" name="InventoryRepository" id="InventoryRepository-5" class="s5">
<input type="radio" name="InventoryRepository" id="InventoryRepository-6" class="s6">
<input type="radio" name="InventoryRepository" id="InventoryRepository-7" class="s7">

<div class="stage s1">

<div class="head"><span class="name">1단계: 꾸며낸 뼈대 (1/7)</span><span class="nav">←</span><label class="nav" for="InventoryRepository-2">→</label></div>

<div class="code">

```kotlin
class InventoryRepository {
    fun hold(order: Order) {}
}
```

</div>

</div>

<div class="stage s2">

<div class="head"><span class="name">2단계: 선언의 종류 (2/7)</span><label class="nav" for="InventoryRepository-1">←</label><label class="nav" for="InventoryRepository-3">→</label></div>

<div class="code">

```kotlin
class InventoryRepository {
    fun hold(order: Order) {
        ⟨재고를 잡아 둠⟩
    }
}
```

<pre class="diff" aria-hidden="true"><code><span>class InventoryRepository {</span>
<span class="mod">    fun hold(order: Order) {</span>
<span class="add">        ⟨재고를 잡아 둠⟩</span>
<span class="add">    }</span>
<span>}</span>
</code></pre>

</div>

</div>

<div class="stage s3">

<div class="head"><span class="name">3단계: 의존 연결 (3/7)</span><label class="nav" for="InventoryRepository-2">←</label><label class="nav" for="InventoryRepository-4">→</label></div>
<div class="note">이 단계에서는 달라진 것이 없음</div>

<div class="code">

```kotlin
class InventoryRepository {
    fun hold(order: Order) {
        ⟨재고를 잡아 둠⟩
    }
}
```

</div>

</div>

<div class="stage s4">

<div class="head"><span class="name">4단계: 공개 시그니처 (4/7)</span><label class="nav" for="InventoryRepository-3">←</label><label class="nav" for="InventoryRepository-5">→</label></div>

<div class="code">

```kotlin
class InventoryRepository {
    fun reserve(id: String) {
        ⟨재고를 잡아 둠⟩
    }
}
```

<pre class="diff" aria-hidden="true"><code><span>class InventoryRepository {</span>
<span class="mod">    fun reserve(id: String) {</span>
<span>        ⟨재고를 잡아 둠⟩</span>
<span>    }</span>
<span>}</span>
</code></pre>

</div>

</div>

<div class="stage s5">

<div class="head"><span class="name">5단계: 핵심 흐름 (5/7)</span><label class="nav" for="InventoryRepository-4">←</label><label class="nav" for="InventoryRepository-6">→</label></div>
<div class="note">이 단계에서는 달라진 것이 없음</div>

<div class="code">

```kotlin
class InventoryRepository {
    fun reserve(id: String) {
        ⟨재고를 잡아 둠⟩
    }
}
```

</div>

</div>

<div class="stage s6">

<div class="head"><span class="name">6단계: 나머지 로직 (6/7)</span><label class="nav" for="InventoryRepository-5">←</label><label class="nav" for="InventoryRepository-7">→</label></div>

<div class="code">

```kotlin
class InventoryRepository {
    private val reserved = mutableSetOf<String>()

    fun reserve(id: String) {
        val note = """
            예약 { $id }
        """.trimIndent()
        if (id.first() == '{') error(note)
        reserved += id
    }
}
```

<pre class="diff" aria-hidden="true"><code><span>class InventoryRepository {</span>
<span class="add">    private val reserved = mutableSetOf&lt;String&gt;()</span>
<span class="add"></span>
<span>    fun reserve(id: String) {</span>
<span class="mod">        val note = """</span>
<span class="add">            예약 { $id }</span>
<span class="add">        """.trimIndent()</span>
<span class="add">        if (id.first() == '{') error(note)</span>
<span class="add">        reserved += id</span>
<span>    }</span>
<span>}</span>
</code></pre>

</div>

</div>

<div class="stage s7">

<div class="head"><span class="name">7단계: 원본 (7/7)</span><label class="nav" for="InventoryRepository-6">←</label><span class="nav">→</span></div>
<div class="note">이 단계에서는 달라진 것이 없음</div>

<div class="code">

```kotlin
class InventoryRepository {
    private val reserved = mutableSetOf<String>()

    fun reserve(id: String) {
        val note = """
            예약 { $id }
        """.trimIndent()
        if (id.first() == '{') error(note)
        reserved += id
    }
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

<style>
.stages .code { position: relative; }
.stages .code > pre.diff { position: absolute; top: 0; left: 0; background: transparent; pointer-events: none; color: transparent; }
.stages pre.diff code { color: transparent; background: transparent; min-width: 100%; }
.stages pre.diff span { display: inline-block; width: 100%; min-height: 1lh; vertical-align: top; position: relative; margin-left: -.6em; padding-left: .6em; }
.stages pre.diff .add { background: oklch(0.7 0.13 150 / 10%); box-shadow: inset 4px 0 0 oklch(0.74 0.13 152); }
.stages pre.diff .mod { background: oklch(0.7 0.13 245 / 10%); box-shadow: inset 4px 0 0 oklch(0.52 0.19 260); }
.stages pre.diff .del::before, .stages pre.diff .del-after::after { content: ""; position: absolute; left: 0; border: 5px solid transparent; border-left-color: oklch(0.65 0.19 25); }
.stages pre.diff .del::before { top: -5px; }
.stages pre.diff .del-after::after { bottom: -5px; }
</style>
