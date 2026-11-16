@Service
class OrderService(
    private val inventory: InventoryRepository,
    private val payments: PaymentGateway,
) {
    fun place(order: Order): Receipt {
        ⟨주문을 검증하고, 재고를 잡고, 결제하고, 합계를 글로 바꿔 기록함⟩
    }

    class Validator {
        fun check(order: Order): Boolean = ...
    }
}
