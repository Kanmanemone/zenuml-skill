# 기타 — 정제 단계

## 인프라

### [**PaymentGateway**](../src/Missing.kt)

<div class="resp"><span class="label">책임</span> 결제를 요청한다.</div>

⚠️ 원본 파일에서 PaymentGateway 선언을 찾지 못해 구체화하지 않음

<div class="stages">

<input type="radio" name="PaymentGateway" id="PaymentGateway-1" class="s1" checked>

<div class="stage s1">

<div class="head"><span class="name">1/1단계: 사용 상황</span><span class="nav">←</span><span class="nav">→</span></div>

</div>

<div class="scroller">

<div class="pane p1">

<div class="scene"><p>주문 금액을 실제로 받아야 할 때 쓰인다.</p></div>

</div>

</div>

</div>

### [**LegacyBridge(java)**](../src/Legacy.java)

<div class="stages">

<input type="radio" name="LegacyBridge" id="LegacyBridge-1" class="s1" checked>
<input type="radio" name="LegacyBridge" id="LegacyBridge-2" class="s2">

<div class="stage s1">

<div class="head"><span class="name">1/2단계: 사용 상황</span><span class="nav">←</span><label class="nav" for="LegacyBridge-2">→</label></div>

</div>

<div class="stage s2">

<div class="head"><span class="name">2/2단계: 원본</span><label class="nav" for="LegacyBridge-1">←</label><span class="nav">→</span></div>

</div>

<div class="scroller">

<div class="pane p1">

<div class="scene"><p>구조 뷰에 사용 상황이 명시되지 않음</p></div>

</div>

<div class="pane p2">

<div class="code">

```java
class LegacyBridge {
    void send(String id) {}
}
```

</div>

</div>

</div>

</div>

### [**formatTotal**](../src/Util.kt)

<div class="resp"><span class="label">책임</span> 합계를 글로 바꾼다.</div>

<div class="stages">

<input type="radio" name="formatTotal" id="formatTotal-1" class="s1" checked>
<input type="radio" name="formatTotal" id="formatTotal-2" class="s2">

<div class="stage s1">

<div class="head"><span class="name">1/2단계: 사용 상황</span><span class="nav">←</span><label class="nav" for="formatTotal-2">→</label></div>

</div>

<div class="stage s2">

<div class="head"><span class="name">2/2단계: 원본</span><label class="nav" for="formatTotal-1">←</label><span class="nav">→</span></div>

</div>

<div class="scroller">

<div class="pane p1">

<div class="scene"><p>영수증이나 기록에 금액을 &lt;원&gt; 단위 글로 남길 때 쓰인다.</p></div>

</div>

<div class="pane p2">

<div class="code">

```kotlin
/** 합계를 사람이 읽는 글로 바꾼다. */
fun formatTotal(total: BigDecimal): String =
    "합계: " + total.setScale(2).toPlainString() + " {원}"
```

</div>

</div>

</div>

</div>

### **AuditLog**

<div class="resp"><span class="label">책임</span> 주문 기록을 남긴다.</div>

⚠️ 원본 위치가 없어 구체화하지 않음

<div class="stages">

<input type="radio" name="AuditLog" id="AuditLog-1" class="s1" checked>

<div class="stage s1">

<div class="head"><span class="name">1/1단계: 사용 상황</span><span class="nav">←</span><span class="nav">→</span></div>

</div>

<div class="scroller">

<div class="pane p1">

<div class="scene"><p>주문 처리가 끝난 뒤 나중에 확인할 기록이 필요할 때 쓰인다.</p></div>

</div>

</div>

</div>

<details class="zenuml-stepwise-style">
<summary>이 문서에 적용되지 못한 &lt;style&gt; 코드 (<a href="https://github.github.com/gfm/#disallowed-raw-html-extension-">관련 GFM 공식 문서</a>)</summary>

<style>
.zenuml-stepwise-style { display: none; }
.resp { margin: 0 0 .6em; padding: .4em .8em; border-left: 3px solid rgba(128,128,128,.5); background: rgba(128,128,128,.08); border-radius: 0 4px 4px 0; }
.resp .label { font-weight: 600; margin-right: .4em; opacity: .75; }
.legend { border: 1px solid rgba(128,128,128,.4); border-radius: 6px; padding: .4em .8em; margin-bottom: 1em; }
.stages { border: 1px solid rgba(128,128,128,.4); border-radius: 6px; padding: 0 1em; margin-bottom: 1em; }
.stages > input { position: absolute; opacity: 0; pointer-events: none; }
.stages > .stage { display: none; }
.stages > input.s1:checked ~ .stage.s1 { display: block; }
.stages > input.s2:checked ~ .stage.s2 { display: block; }
.stages > input.s3:checked ~ .stage.s3 { display: block; }
.stages > input.s4:checked ~ .stage.s4 { display: block; }
.stages > input.s5:checked ~ .stage.s5 { display: block; }
.stages > input.s6:checked ~ .stage.s6 { display: block; }
.stages > input.s1:checked ~ .scroller > .pane.p1 { display: block; }
.stages > input.s2:checked ~ .scroller > .pane.p2 { display: block; }
.stages > input.s3:checked ~ .scroller > .pane.p3 { display: block; }
.stages > input.s4:checked ~ .scroller > .pane.p4 { display: block; }
.stages > input.s5:checked ~ .scroller > .pane.p5 { display: block; }
.stages > input.s6:checked ~ .scroller > .pane.p6 { display: block; }
.stages .head { display: flex; align-items: center; gap: .4em; padding: .5em 0 .2em; font-weight: 600; }
.stages .head .name { flex: 1; }
.stages .nav { display: inline-block; width: 2.2em; height: 1.8em; line-height: 1.8em; text-align: center; border: 1px solid rgba(128,128,128,.5); border-radius: 4px; font-weight: 400; cursor: pointer; user-select: none; }
.stages span.nav { opacity: .3; cursor: default; }
.stages .note { padding: 0 0 .5em; opacity: .8; }
.stages .scene { padding: .5em 0 1em; max-width: 65ch; }
.stages > .scroller { max-height: min(30lh, 70vh); overflow: auto; margin-bottom: 1em; }
.stages > .scroller > .pane { display: none; }
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
.stages pre.diff .del { background: oklch(0.7 0.15 25 / 10%); box-shadow: inset 4px 0 0 oklch(0.62 0.17 18); }
</style>

</details>
