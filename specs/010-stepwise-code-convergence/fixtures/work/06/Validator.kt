    class Validator {
        fun check(order: Order): Boolean = order.lines.all { it.price > BigDecimal.ZERO }
    }
