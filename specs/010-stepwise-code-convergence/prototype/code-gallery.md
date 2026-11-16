# 긴 원본 예제 (상자 높이 상한: 30줄 또는 화면 70%)

원본은 116줄입니다. 상자 안에서 세로로 스크롤한 뒤 ← → 로 넘겨 보세요. 상자 높이는 지금 보이는 단계의 길이를 따릅니다(상한 안에서).

## OrderService.kt

<div class="stages">

<input type="radio" name="orderservice" id="orderservice-1" class="s1" checked>
<input type="radio" name="orderservice" id="orderservice-2" class="s2">
<input type="radio" name="orderservice" id="orderservice-3" class="s3">

<div class="stage s1">

<div class="head"><span class="name">1단계: 꾸며낸 뼈대 (1/3) — 5줄</span><span class="nav">←</span><label class="nav" for="orderservice-2">→</label></div>

```kotlin
class OrderService {
    fun order() {
        // 주문 처리
    }
}
```

</div>

<div class="stage s2">

<div class="head"><span class="name">2단계: 공개 시그니처 (2/3) — 54줄</span><label class="nav" for="orderservice-1">←</label><label class="nav" for="orderservice-3">→</label></div>

```kotlin
package com.shop.order

class OrderService(private val inventory: InventoryRepository) {
    fun step01(order: Order): Order {
        // 주문 처리
        return order
    }

    fun step02(order: Order): Order {
        // 주문 처리
        return order
    }

    fun step03(order: Order): Order {
        // 주문 처리
        return order
    }

    fun step04(order: Order): Order {
        // 주문 처리
        return order
    }

    fun step05(order: Order): Order {
        // 주문 처리
        return order
    }

    fun step06(order: Order): Order {
        // 주문 처리
        return order
    }

    fun step07(order: Order): Order {
        // 주문 처리
        return order
    }

    fun step08(order: Order): Order {
        // 주문 처리
        return order
    }

    fun step09(order: Order): Order {
        // 주문 처리
        return order
    }

    fun step10(order: Order): Order {
        // 주문 처리
        return order
    }

}
```

</div>

<div class="stage s3">

<div class="head"><span class="name">3단계: 원본 (3/3) — 116줄</span><label class="nav" for="orderservice-2">←</label><span class="nav">→</span></div>

```kotlin
package com.shop.order

import java.math.BigDecimal

class OrderService(private val inventory: InventoryRepository) {
    fun step01(order: Order): Order {
        require(order.lines.isNotEmpty()) { "step01: empty order" }
        val total = order.lines.sumOf { it.price * it.quantity.toBigDecimal() }
        if (total > BigDecimal("1000")) {
            inventory.reserve(order.id, order.lines.map { it.sku })
        }
        val checked = order.copy(total = total, step = 1)
        log.debug("step01 done: {}", checked.id)
        return checked
    }

    fun step02(order: Order): Order {
        require(order.lines.isNotEmpty()) { "step02: empty order" }
        val total = order.lines.sumOf { it.price * it.quantity.toBigDecimal() }
        if (total > BigDecimal("2000")) {
            inventory.reserve(order.id, order.lines.map { it.sku })
        }
        val checked = order.copy(total = total, step = 2)
        log.debug("step02 done: {}", checked.id)
        return checked
    }

    fun step03(order: Order): Order {
        require(order.lines.isNotEmpty()) { "step03: empty order" }
        val total = order.lines.sumOf { it.price * it.quantity.toBigDecimal() }
        if (total > BigDecimal("3000")) {
            inventory.reserve(order.id, order.lines.map { it.sku })
        }
        val checked = order.copy(total = total, step = 3)
        log.debug("step03 done: {}", checked.id)
        return checked
    }

    fun step04(order: Order): Order {
        require(order.lines.isNotEmpty()) { "step04: empty order" }
        val total = order.lines.sumOf { it.price * it.quantity.toBigDecimal() }
        if (total > BigDecimal("4000")) {
            inventory.reserve(order.id, order.lines.map { it.sku })
        }
        val checked = order.copy(total = total, step = 4)
        log.debug("step04 done: {}", checked.id)
        return checked
    }

    fun step05(order: Order): Order {
        require(order.lines.isNotEmpty()) { "step05: empty order" }
        val total = order.lines.sumOf { it.price * it.quantity.toBigDecimal() }
        if (total > BigDecimal("5000")) {
            inventory.reserve(order.id, order.lines.map { it.sku })
        }
        val checked = order.copy(total = total, step = 5)
        log.debug("step05 done: {}", checked.id)
        return checked
    }

    fun step06(order: Order): Order {
        require(order.lines.isNotEmpty()) { "step06: empty order" }
        val total = order.lines.sumOf { it.price * it.quantity.toBigDecimal() }
        if (total > BigDecimal("6000")) {
            inventory.reserve(order.id, order.lines.map { it.sku })
        }
        val checked = order.copy(total = total, step = 6)
        log.debug("step06 done: {}", checked.id)
        return checked
    }

    fun step07(order: Order): Order {
        require(order.lines.isNotEmpty()) { "step07: empty order" }
        val total = order.lines.sumOf { it.price * it.quantity.toBigDecimal() }
        if (total > BigDecimal("7000")) {
            inventory.reserve(order.id, order.lines.map { it.sku })
        }
        val checked = order.copy(total = total, step = 7)
        log.debug("step07 done: {}", checked.id)
        return checked
    }

    fun step08(order: Order): Order {
        require(order.lines.isNotEmpty()) { "step08: empty order" }
        val total = order.lines.sumOf { it.price * it.quantity.toBigDecimal() }
        if (total > BigDecimal("8000")) {
            inventory.reserve(order.id, order.lines.map { it.sku })
        }
        val checked = order.copy(total = total, step = 8)
        log.debug("step08 done: {}", checked.id)
        return checked
    }

    fun step09(order: Order): Order {
        require(order.lines.isNotEmpty()) { "step09: empty order" }
        val total = order.lines.sumOf { it.price * it.quantity.toBigDecimal() }
        if (total > BigDecimal("9000")) {
            inventory.reserve(order.id, order.lines.map { it.sku })
        }
        val checked = order.copy(total = total, step = 9)
        log.debug("step09 done: {}", checked.id)
        return checked
    }

    fun step10(order: Order): Order {
        require(order.lines.isNotEmpty()) { "step10: empty order" }
        val total = order.lines.sumOf { it.price * it.quantity.toBigDecimal() }
        if (total > BigDecimal("10000")) {
            inventory.reserve(order.id, order.lines.map { it.sku })
        }
        val checked = order.copy(total = total, step = 10)
        log.debug("step10 done: {}", checked.id)
        return checked
    }

}
```

</div>

</div>

## 다음 노드

상자 아래 문서가 바로 이어지는지 확인용 문단입니다.

<style>
.stages { border: 1px solid rgba(128,128,128,.4); border-radius: 6px; padding: 0 1em; }
.stages > input { position: absolute; opacity: 0; pointer-events: none; }
.stages > .stage { display: none; }
.stages > input.s1:checked ~ .stage.s1 { display: block; }
.stages > input.s2:checked ~ .stage.s2 { display: block; }
.stages > input.s3:checked ~ .stage.s3 { display: block; }
.stages .head { display: flex; align-items: center; gap: .4em; padding: .5em 0; font-weight: 600; }
.stages .head .name { flex: 1; }
.stages .nav { display: inline-block; width: 2.2em; height: 1.8em; line-height: 1.8em; text-align: center; border: 1px solid rgba(128,128,128,.5); border-radius: 4px; font-weight: 400; cursor: pointer; user-select: none; }
.stages span.nav { opacity: .3; cursor: default; }
.stages pre { margin-top: 0; max-height: min(30lh, 70vh); overflow: auto; }
.stages pre, .stages pre code { white-space: pre; word-break: normal; }
</style>
