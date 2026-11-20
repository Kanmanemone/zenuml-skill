# 주문 도메인 — 정제 단계

### OrderService

<div class="resp"><span class="label">책임</span> 주문을 받아 처리한다.</div>

<div class="stages">

<input type="radio" name="OrderService" id="OrderService-1" class="s1" checked>
<input type="radio" name="OrderService" id="OrderService-2" class="s2">
<input type="radio" name="OrderService" id="OrderService-3" class="s3">
<input type="radio" name="OrderService" id="OrderService-4" class="s4">
<input type="radio" name="OrderService" id="OrderService-5" class="s5">
<input type="radio" name="OrderService" id="OrderService-6" class="s6">

<div class="stage s1">

<div class="head"><span class="name">1단계: 사용 상황 (1/6)</span><span class="nav">←</span><label class="nav" for="OrderService-2">→</label></div>

<div class="scene"><p>고객이 장바구니를 확정해 결제 버튼을 누를 때 쓰인다.</p></div>

</div>

<div class="stage s2">

<div class="head"><span class="name">2단계: 윤곽 (2/6)</span><label class="nav" for="OrderService-1">←</label><label class="nav" for="OrderService-3">→</label></div>

<div class="code">

```kotlin
/**
 * 주문을 만들고 재고를 예약한다. 본문의 { 는 주석이라 세지 않는다.
 */
@Service
class OrderService(
    ...
) {
    ⟨1. 주문 하나를 처리해 영수증을 돌려준다.⟩
        ⟨2. 재고를 잡은 다음 결제를 청구한다.⟩
        ⟨3. 처리한 주문을 감사 기록에 남긴다.⟩

    ⟨4. 주문 줄의 가격이 올바른지 따로 확인한다.⟩
}
```

</div>

</div>

<div class="stage s3">

<div class="head"><span class="name">3단계: 펼치기 1/4 — 주문 하나를 처리해 영수증을 돌려준다. (3/6)</span><label class="nav" for="OrderService-2">←</label><label class="nav" for="OrderService-4">→</label></div>

<div class="code">

```kotlin
/**
 * 주문을 만들고 재고를 예약한다. 본문의 { 는 주석이라 세지 않는다.
 */
@Service
class OrderService(
    ...
) {
    fun place(order: Order): Receipt {
        require(order.lines.isNotEmpty()) { "빈 주문 {${order.id}}" }
        val total = order.lines.sumOf { it.price }
        ⟨2. 재고를 잡은 다음 결제를 청구한다.⟩
        ⟨3. 처리한 주문을 감사 기록에 남긴다.⟩
        return Receipt(order.id, total)
    }

    ⟨4. 주문 줄의 가격이 올바른지 따로 확인한다.⟩
}
```

</div>

</div>

<div class="stage s4">

<div class="head"><span class="name">4단계: 펼치기 2/4 — 재고를 잡은 다음 결제를 청구한다. (4/6)</span><label class="nav" for="OrderService-3">←</label><label class="nav" for="OrderService-5">→</label></div>

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
        ⟨3. 처리한 주문을 감사 기록에 남긴다.⟩
        return Receipt(order.id, total)
    }

    ⟨4. 주문 줄의 가격이 올바른지 따로 확인한다.⟩
}
```

</div>

</div>

<div class="stage s5">

<div class="head"><span class="name">5단계: 펼치기 3/4 — 처리한 주문을 감사 기록에 남긴다. (5/6)</span><label class="nav" for="OrderService-4">←</label><label class="nav" for="OrderService-6">→</label></div>

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

    ⟨4. 주문 줄의 가격이 올바른지 따로 확인한다.⟩
}
```

</div>

</div>

<div class="stage s6">

<div class="head"><span class="name">6단계: 펼치기 4/4 — 주문 줄의 가격이 올바른지 따로 확인한다. (6/6)</span><label class="nav" for="OrderService-5">←</label><span class="nav">→</span></div>

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

</div>

</div>

</div>

### Validator

<div class="resp"><span class="label">책임</span> 주문이 올바른지 본다.</div>

<div class="stages">

<input type="radio" name="Validator" id="Validator-1" class="s1" checked>
<input type="radio" name="Validator" id="Validator-2" class="s2">

<div class="stage s1">

<div class="head"><span class="name">1단계: 사용 상황 (1/2)</span><span class="nav">←</span><label class="nav" for="Validator-2">→</label></div>

<div class="scene"><p>주문을 접수하기 전에 쓰인다.</p></div>

</div>

<div class="stage s2">

<div class="head"><span class="name">2단계: 원본 (2/2)</span><label class="nav" for="Validator-1">←</label><span class="nav">→</span></div>

<div class="code">

```kotlin
    class Validator {
        // 주문 줄이 모두 양수 가격인지 본다
        fun check(order: Order): Boolean = order.lines.all { it.price > BigDecimal.ZERO }
    }
```

</div>

</div>

</div>

### InventoryRepository

<div class="resp"><span class="label">책임</span> 재고를 예약한다.</div>

<div class="stages">

<input type="radio" name="InventoryRepository" id="InventoryRepository-1" class="s1" checked>
<input type="radio" name="InventoryRepository" id="InventoryRepository-2" class="s2">
<input type="radio" name="InventoryRepository" id="InventoryRepository-3" class="s3">
<input type="radio" name="InventoryRepository" id="InventoryRepository-4" class="s4">

<div class="stage s1">

<div class="head"><span class="name">1단계: 사용 상황 (1/4)</span><span class="nav">←</span><label class="nav" for="InventoryRepository-2">→</label></div>

<div class="scene"><p>주문이 확정되어 물건을 따로 떼어 둬야 할 때 쓰인다.</p></div>

</div>

<div class="stage s2">

<div class="head"><span class="name">2단계: 윤곽 (2/4)</span><label class="nav" for="InventoryRepository-1">←</label><label class="nav" for="InventoryRepository-3">→</label></div>

<div class="code">

```kotlin
class InventoryRepository {
    fun reserve(id: String) {
        ⟨1. 잘못된 주문 번호를 오류로 알린다.⟩
        ⟨2. 주문 번호를 예약 목록에 남긴다.⟩
    }
}
```

</div>

</div>

<div class="stage s3">

<div class="head"><span class="name">3단계: 펼치기 1/2 — 잘못된 주문 번호를 오류로 알린다. (3/4)</span><label class="nav" for="InventoryRepository-2">←</label><label class="nav" for="InventoryRepository-4">→</label></div>

<div class="code">

```kotlin
class InventoryRepository {
    fun reserve(id: String) {
        val note = """
            예약 { $id }
        """.trimIndent()
        if (id.first() == '{') error(note)
        ⟨2. 주문 번호를 예약 목록에 남긴다.⟩
    }
}
```

</div>

</div>

<div class="stage s4">

<div class="head"><span class="name">4단계: 펼치기 2/2 — 주문 번호를 예약 목록에 남긴다. (4/4)</span><label class="nav" for="InventoryRepository-3">←</label><span class="nav">→</span></div>

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

<details class="zenuml-stepwise-style">
<summary>이 문서에 적용되지 못한 &lt;style&gt; 코드 (<a href="https://github.github.com/gfm/#disallowed-raw-html-extension-">관련 GFM 공식 문서</a>)</summary>

<style>
.zenuml-stepwise-style { display: none; }
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
.stages .head { display: flex; align-items: center; gap: .4em; padding: .5em 0 .2em; font-weight: 600; }
.stages .head .name { flex: 1; }
.stages .nav { display: inline-block; width: 2.2em; height: 1.8em; line-height: 1.8em; text-align: center; border: 1px solid rgba(128,128,128,.5); border-radius: 4px; font-weight: 400; cursor: pointer; user-select: none; }
.stages span.nav { opacity: .3; cursor: default; }
.stages .note { padding: 0 0 .5em; opacity: .8; }
.stages .scene { padding: .5em 0 1em; max-width: 65ch; }
.stages .code { max-height: min(30lh, 70vh); overflow: auto; margin-bottom: 1em; }
.stages .code pre { margin: 0; overflow: visible; width: max-content; min-width: 100%; box-sizing: border-box; }
.stages .code pre, .stages .code pre code { white-space: pre; word-break: normal; }
</style>

</details>
