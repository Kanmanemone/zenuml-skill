@Service
class OrderService {
    fun handle(order: Order) {
        ⟨주문을 검증하고, 재고를 잡고, 결제하고, 합계를 글로 바꿔 기록함⟩
    }

    class Validator {
        ...
    }
}
