/** 합계를 사람이 읽는 글로 바꾼다. */
fun formatTotal(total: BigDecimal): String =
    "합계: " + total.setScale(2).toPlainString() + " {원}"
