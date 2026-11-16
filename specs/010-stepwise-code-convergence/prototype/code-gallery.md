# 긴 원본 예제 (상자 높이 상한: 30줄 또는 화면 70%)

원본은 116줄입니다. 상자 안에서 세로로 스크롤한 뒤 ← → 로 넘겨 보세요. 상자 높이는 지금 보이는 단계의 길이를 따릅니다(상한 안에서).

## OrderService.kt

<div class="stages">

<input type="radio" name="orderservice" id="orderservice-1" class="s1" checked>
<input type="radio" name="orderservice" id="orderservice-2" class="s2">
<input type="radio" name="orderservice" id="orderservice-3" class="s3">

<div class="stage s1">

<div class="head"><span class="name">1단계: 꾸며낸 뼈대 (1/3) — 5줄</span><span class="nav">←</span><label class="nav" for="orderservice-2">→</label></div>

<div class="code">

```kotlin
class OrderService {
    fun order() {
        // 주문 처리
    }
}
```

</div>

</div>

<div class="stage s2">

<div class="head"><span class="name">2단계: 공개 시그니처 (2/3) — 54줄</span><label class="nav" for="orderservice-1">←</label><label class="nav" for="orderservice-3">→</label></div>

<div class="code">

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

<pre class="diff" aria-hidden="true"><code><span class="mod">package com.shop.order</span>
<span class="mod"></span>
<span class="add">class OrderService(private val inventory: InventoryRepository) {</span>
<span class="add">    fun step01(order: Order): Order {</span>
<span>        // 주문 처리</span>
<span class="add">        return order</span>
<span>    }</span>
<span class="add"></span>
<span class="add">    fun step02(order: Order): Order {</span>
<span class="add">        // 주문 처리</span>
<span class="add">        return order</span>
<span class="add">    }</span>
<span class="add"></span>
<span class="add">    fun step03(order: Order): Order {</span>
<span class="add">        // 주문 처리</span>
<span class="add">        return order</span>
<span class="add">    }</span>
<span class="add"></span>
<span class="add">    fun step04(order: Order): Order {</span>
<span class="add">        // 주문 처리</span>
<span class="add">        return order</span>
<span class="add">    }</span>
<span class="add"></span>
<span class="add">    fun step05(order: Order): Order {</span>
<span class="add">        // 주문 처리</span>
<span class="add">        return order</span>
<span class="add">    }</span>
<span class="add"></span>
<span class="add">    fun step06(order: Order): Order {</span>
<span class="add">        // 주문 처리</span>
<span class="add">        return order</span>
<span class="add">    }</span>
<span class="add"></span>
<span class="add">    fun step07(order: Order): Order {</span>
<span class="add">        // 주문 처리</span>
<span class="add">        return order</span>
<span class="add">    }</span>
<span class="add"></span>
<span class="add">    fun step08(order: Order): Order {</span>
<span class="add">        // 주문 처리</span>
<span class="add">        return order</span>
<span class="add">    }</span>
<span class="add"></span>
<span class="add">    fun step09(order: Order): Order {</span>
<span class="add">        // 주문 처리</span>
<span class="add">        return order</span>
<span class="add">    }</span>
<span class="add"></span>
<span class="add">    fun step10(order: Order): Order {</span>
<span class="add">        // 주문 처리</span>
<span class="add">        return order</span>
<span class="add">    }</span>
<span class="add"></span>
<span>}</span>
</code></pre>

</div>

</div>

<div class="stage s3">

<div class="head"><span class="name">3단계: 원본 (3/3) — 116줄</span><label class="nav" for="orderservice-2">←</label><span class="nav">→</span></div>

<div class="code">

```kotlin
package com.shop.order

import java.math.BigDecimal

// 이 줄은 가로 스크롤을 확인하려고 일부러 아주 길게 쓴 줄입니다 — 줄바꿈되지 않고 상자 안에서 가로로 넘어가야 하며, 이 줄의 배경도 끝까지 칠해져야 합니다.

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

<pre class="diff" aria-hidden="true"><code><span>package com.shop.order</span>
<span class="add"></span>
<span class="add">import java.math.BigDecimal</span>
<span class="add"></span>
<span class="add">// 이 줄은 가로 스크롤을 확인하려고 일부러 아주 길게 쓴 줄입니다 — 줄바꿈되지 않고 상자 안에서 가로로 넘어가야 하며, 이 줄의 배경도 끝까지 칠해져야 합니다.</span>
<span></span>
<span>class OrderService(private val inventory: InventoryRepository) {</span>
<span>    fun step01(order: Order): Order {</span>
<span class="mod">        require(order.lines.isNotEmpty()) { "step01: empty order" }</span>
<span class="mod">        val total = order.lines.sumOf { it.price * it.quantity.toBigDecimal() }</span>
<span class="add">        if (total &gt; BigDecimal("1000")) {</span>
<span class="add">            inventory.reserve(order.id, order.lines.map { it.sku })</span>
<span class="add">        }</span>
<span class="add">        val checked = order.copy(total = total, step = 1)</span>
<span class="add">        log.debug("step01 done: {}", checked.id)</span>
<span class="add">        return checked</span>
<span>    }</span>
<span></span>
<span>    fun step02(order: Order): Order {</span>
<span class="mod">        require(order.lines.isNotEmpty()) { "step02: empty order" }</span>
<span class="mod">        val total = order.lines.sumOf { it.price * it.quantity.toBigDecimal() }</span>
<span class="add">        if (total &gt; BigDecimal("2000")) {</span>
<span class="add">            inventory.reserve(order.id, order.lines.map { it.sku })</span>
<span class="add">        }</span>
<span class="add">        val checked = order.copy(total = total, step = 2)</span>
<span class="add">        log.debug("step02 done: {}", checked.id)</span>
<span class="add">        return checked</span>
<span>    }</span>
<span></span>
<span>    fun step03(order: Order): Order {</span>
<span class="mod">        require(order.lines.isNotEmpty()) { "step03: empty order" }</span>
<span class="mod">        val total = order.lines.sumOf { it.price * it.quantity.toBigDecimal() }</span>
<span class="add">        if (total &gt; BigDecimal("3000")) {</span>
<span class="add">            inventory.reserve(order.id, order.lines.map { it.sku })</span>
<span class="add">        }</span>
<span class="add">        val checked = order.copy(total = total, step = 3)</span>
<span class="add">        log.debug("step03 done: {}", checked.id)</span>
<span class="add">        return checked</span>
<span>    }</span>
<span></span>
<span>    fun step04(order: Order): Order {</span>
<span class="mod">        require(order.lines.isNotEmpty()) { "step04: empty order" }</span>
<span class="mod">        val total = order.lines.sumOf { it.price * it.quantity.toBigDecimal() }</span>
<span class="add">        if (total &gt; BigDecimal("4000")) {</span>
<span class="add">            inventory.reserve(order.id, order.lines.map { it.sku })</span>
<span class="add">        }</span>
<span class="add">        val checked = order.copy(total = total, step = 4)</span>
<span class="add">        log.debug("step04 done: {}", checked.id)</span>
<span class="add">        return checked</span>
<span>    }</span>
<span></span>
<span>    fun step05(order: Order): Order {</span>
<span class="mod">        require(order.lines.isNotEmpty()) { "step05: empty order" }</span>
<span class="mod">        val total = order.lines.sumOf { it.price * it.quantity.toBigDecimal() }</span>
<span class="add">        if (total &gt; BigDecimal("5000")) {</span>
<span class="add">            inventory.reserve(order.id, order.lines.map { it.sku })</span>
<span class="add">        }</span>
<span class="add">        val checked = order.copy(total = total, step = 5)</span>
<span class="add">        log.debug("step05 done: {}", checked.id)</span>
<span class="add">        return checked</span>
<span>    }</span>
<span></span>
<span>    fun step06(order: Order): Order {</span>
<span class="mod">        require(order.lines.isNotEmpty()) { "step06: empty order" }</span>
<span class="mod">        val total = order.lines.sumOf { it.price * it.quantity.toBigDecimal() }</span>
<span class="add">        if (total &gt; BigDecimal("6000")) {</span>
<span class="add">            inventory.reserve(order.id, order.lines.map { it.sku })</span>
<span class="add">        }</span>
<span class="add">        val checked = order.copy(total = total, step = 6)</span>
<span class="add">        log.debug("step06 done: {}", checked.id)</span>
<span class="add">        return checked</span>
<span>    }</span>
<span></span>
<span>    fun step07(order: Order): Order {</span>
<span class="mod">        require(order.lines.isNotEmpty()) { "step07: empty order" }</span>
<span class="mod">        val total = order.lines.sumOf { it.price * it.quantity.toBigDecimal() }</span>
<span class="add">        if (total &gt; BigDecimal("7000")) {</span>
<span class="add">            inventory.reserve(order.id, order.lines.map { it.sku })</span>
<span class="add">        }</span>
<span class="add">        val checked = order.copy(total = total, step = 7)</span>
<span class="add">        log.debug("step07 done: {}", checked.id)</span>
<span class="add">        return checked</span>
<span>    }</span>
<span></span>
<span>    fun step08(order: Order): Order {</span>
<span class="mod">        require(order.lines.isNotEmpty()) { "step08: empty order" }</span>
<span class="mod">        val total = order.lines.sumOf { it.price * it.quantity.toBigDecimal() }</span>
<span class="add">        if (total &gt; BigDecimal("8000")) {</span>
<span class="add">            inventory.reserve(order.id, order.lines.map { it.sku })</span>
<span class="add">        }</span>
<span class="add">        val checked = order.copy(total = total, step = 8)</span>
<span class="add">        log.debug("step08 done: {}", checked.id)</span>
<span class="add">        return checked</span>
<span>    }</span>
<span></span>
<span>    fun step09(order: Order): Order {</span>
<span class="mod">        require(order.lines.isNotEmpty()) { "step09: empty order" }</span>
<span class="mod">        val total = order.lines.sumOf { it.price * it.quantity.toBigDecimal() }</span>
<span class="add">        if (total &gt; BigDecimal("9000")) {</span>
<span class="add">            inventory.reserve(order.id, order.lines.map { it.sku })</span>
<span class="add">        }</span>
<span class="add">        val checked = order.copy(total = total, step = 9)</span>
<span class="add">        log.debug("step09 done: {}", checked.id)</span>
<span class="add">        return checked</span>
<span>    }</span>
<span></span>
<span>    fun step10(order: Order): Order {</span>
<span class="mod">        require(order.lines.isNotEmpty()) { "step10: empty order" }</span>
<span class="mod">        val total = order.lines.sumOf { it.price * it.quantity.toBigDecimal() }</span>
<span class="add">        if (total &gt; BigDecimal("10000")) {</span>
<span class="add">            inventory.reserve(order.id, order.lines.map { it.sku })</span>
<span class="add">        }</span>
<span class="add">        val checked = order.copy(total = total, step = 10)</span>
<span class="add">        log.debug("step10 done: {}", checked.id)</span>
<span class="add">        return checked</span>
<span>    }</span>
<span></span>
<span>}</span>
</code></pre>

</div>

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
