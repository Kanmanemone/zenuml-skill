@Service
class OrderService(
    private val inventory: InventoryRepository,
    private val payments: PaymentGateway,
) {
    fun place(order: Order): Receipt {
        ⟨주문이 비었는지 확인하고 합계를 구함⟩
        inventory.reserve(order.id)
        payments.charge(order.id, total)
        AuditLog.record(⟨주문 번호와 formatTotal(total)로 만든 글⟩)
        return Receipt(order.id, total)
    }

    class Validator {
        fun check(order: Order): Boolean = ...
    }
}
