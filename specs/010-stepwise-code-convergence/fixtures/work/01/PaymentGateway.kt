class PaymentGateway {
    fun pay(order: Order) {
        LegacyBridge().forward(order)
    }
}
