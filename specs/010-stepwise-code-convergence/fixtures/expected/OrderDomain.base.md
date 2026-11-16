# 주문 도메인 — 정제 단계

### OrderService

<div class="resp"><span class="label">책임</span> 주문을 받아 처리한다.</div>

<div class="stages">

<input type="radio" name="OrderService" id="OrderService-1" class="s1" checked>
<input type="radio" name="OrderService" id="OrderService-2" class="s2">
<input type="radio" name="OrderService" id="OrderService-3" class="s3">
<input type="radio" name="OrderService" id="OrderService-4" class="s4">
<input type="radio" name="OrderService" id="OrderService-5" class="s5">

<div class="stage s1">

<div class="head"><span class="name">1단계: 사용 상황 (1/5)</span><span class="nav">←</span><label class="nav" for="OrderService-2">→</label></div>

<div class="scene"><p>고객이 장바구니를 확정해 결제 버튼을 누를 때 쓰인다.</p></div>

</div>

<div class="stage s2">

<div class="head"><span class="name">2단계: 윤곽 (2/5)</span><label class="nav" for="OrderService-1">←</label><label class="nav" for="OrderService-3">→</label></div>

<div class="code">

```kotlin
/**
 * 주문을 만들고 재고를 예약한다. 본문의 { 는 주석이라 세지 않는다.
 */
@Service
class OrderService(
    ...
) {
    ⟨주문을 확인하고 재고와 결제를 거쳐 영수증을 낸다⟩
    ⟨주문 줄의 가격이 올바른지 따로 확인한다⟩
}
```

</div>

</div>

<div class="stage s3">

<div class="head"><span class="name">3단계: 펼치기 1/2 — 주문을 확인하고 재고와 결제를 거쳐 영수증을 낸다 (3/5)</span><label class="nav" for="OrderService-2">←</label><label class="nav" for="OrderService-4">→</label></div>

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
        ⟨주문이 비었는지 확인하고 합계를 구한다⟩
        inventory.reserve(order.id)
        payments.charge(order.id, total)
        AuditLog.record("주문 ${order.id}: ${formatTotal(total)}")
        return Receipt(order.id, total)
    }

    ⟨주문 줄의 가격이 올바른지 따로 확인한다⟩
}
```

</div>

</div>

<div class="stage s4">

<div class="head"><span class="name">4단계: 펼치기 2/2 — 주문 줄의 가격이 올바른지 따로 확인한다 (4/5)</span><label class="nav" for="OrderService-3">←</label><label class="nav" for="OrderService-5">→</label></div>

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
        ⟨주문이 비었는지 확인하고 합계를 구한다⟩
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

<div class="stage s5">

<div class="head"><span class="name">5단계: 원본 (5/5)</span><label class="nav" for="OrderService-4">←</label><span class="nav">→</span></div>

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
<input type="radio" name="Validator" id="Validator-3" class="s3">

<div class="stage s1">

<div class="head"><span class="name">1단계: 사용 상황 (1/3)</span><span class="nav">←</span><label class="nav" for="Validator-2">→</label></div>

<div class="scene"><p>주문을 접수하기 전에 쓰인다.</p></div>

</div>

<div class="stage s2">

<div class="head"><span class="name">2단계: 윤곽 (2/3)</span><label class="nav" for="Validator-1">←</label><label class="nav" for="Validator-3">→</label></div>

<div class="code">

```kotlin
    class Validator {
        ⟨모든 주문 줄의 가격이 0보다 큰지 본다⟩
    }
```

</div>

</div>

<div class="stage s3">

<div class="head"><span class="name">3단계: 펼치기 1/1 — 모든 주문 줄의 가격이 0보다 큰지 본다 (3/3)</span><label class="nav" for="Validator-2">←</label><span class="nav">→</span></div>

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

<div class="stage s1">

<div class="head"><span class="name">1단계: 사용 상황 (1/3)</span><span class="nav">←</span><label class="nav" for="InventoryRepository-2">→</label></div>

<div class="scene"><p>주문이 확정되어 물건을 따로 떼어 둬야 할 때 쓰인다.</p></div>

</div>

<div class="stage s2">

<div class="head"><span class="name">2단계: 윤곽 (2/3)</span><label class="nav" for="InventoryRepository-1">←</label><label class="nav" for="InventoryRepository-3">→</label></div>

<div class="code">

```kotlin
class InventoryRepository {
    ⟨주문 번호로 재고를 떼어 두고 이미 쓴 번호를 기억한다⟩
}
```

</div>

</div>

<div class="stage s3">

<div class="head"><span class="name">3단계: 펼치기 1/1 — 주문 번호로 재고를 떼어 두고 이미 쓴 번호를 기억한다 (3/3)</span><label class="nav" for="InventoryRepository-2">←</label><span class="nav">→</span></div>

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
