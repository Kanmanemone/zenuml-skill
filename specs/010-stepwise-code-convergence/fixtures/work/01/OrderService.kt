class OrderService {
    fun handle(order: Order) {
        Validator().verify(order)
        InventoryRepository().hold(order)
        PaymentGateway().pay(order)
        formatTotal(order)
        AuditLog().write(order)
    }
}
