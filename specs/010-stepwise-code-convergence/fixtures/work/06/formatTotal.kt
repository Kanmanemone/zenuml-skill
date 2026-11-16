fun formatTotal(total: BigDecimal): String =
    "합계: " + total.setScale(2).toPlainString() + " {원}"
