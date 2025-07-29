Okay, here's a challenging Python coding problem designed with the criteria you specified:

**Problem Title:** Distributed Transaction Orchestration

**Problem Description:**

Imagine you are building a distributed e-commerce platform.  A single order fulfillment process involves multiple independent microservices: `InventoryService`, `PaymentService`, `ShippingService`, and `NotificationService`.  Each service has its own database and operates independently.

To ensure data consistency across these services when an order is placed, you need to implement a distributed transaction orchestration mechanism.  This means that if any service fails during the order fulfillment process, all preceding operations must be rolled back (compensated) to maintain data integrity.

**Your Task:**

Write a Python program that simulates this distributed transaction orchestration using the Saga pattern.

Specifically, you must implement the following functions:

1.  `place_order(order_id: str, items: list, user_id: str, payment_info: dict, shipping_address: dict) -> bool`:
    *   This is the main function that initiates the order fulfillment process.
    *   It takes an `order_id` (unique string), a list of `items` (each item is a dictionary with 'item_id' and 'quantity'), `user_id` (string), `payment_info` (dictionary), and `shipping_address` (dictionary) as input.
    *   It orchestrates the calls to the microservices in the following order:
        *   `reserve_inventory(order_id, items)`
        *   `process_payment(order_id, user_id, payment_info, total_amount)` (calculate `total_amount` based on `items` – assume a simple pricing lookup is available through `get_item_price(item_id)`)
        *   `schedule_shipping(order_id, shipping_address)`
        *   `send_confirmation_notification(order_id, user_id)`
    *   If *any* of these steps fail (return `False`), the function must trigger the compensation logic to rollback the completed steps in *reverse* order of execution.
    *   The function must return `True` if the order is successfully placed and fulfilled, and `False` otherwise.

2.  `reserve_inventory(order_id: str, items: list) -> bool`:
    *   Simulates reserving the specified `items` in the `InventoryService`.
    *   For simplicity, assume a global `inventory` dictionary that maps `item_id` to available quantity.
    *   If sufficient quantity is available for all items, decrement the `inventory` and return `True`.
    *   If insufficient quantity is available for any item, return `False`.
    *   **Compensation:** `compensate_inventory_reservation(order_id, items)` must restore the inventory.

3.  `process_payment(order_id: str, user_id: str, payment_info: dict, amount: float) -> bool`:
    *   Simulates processing the payment in the `PaymentService`.
    *   For simplicity, assume a global `payment_records` dictionary that stores payment status for each `order_id`.
    *   Always return `True` unless the `order_id` is in the `blacklist_order_ids` set, in which case return `False` to simulate a payment failure.
    *   Set `payment_records[order_id] = 'processed'` if successful.
    *   **Compensation:** `refund_payment(order_id, user_id, amount)` must simulate refunding the payment.

4.  `schedule_shipping(order_id: str, shipping_address: dict) -> bool`:
    *   Simulates scheduling the shipping in the `ShippingService`.
    *   Always return `True` unless the `order_id` is in the `shipping_error_order_ids` set, in which case return `False` to simulate a shipping scheduling failure.
    *   **Compensation:** `cancel_shipping(order_id)` must simulate canceling the shipping.

5.  `send_confirmation_notification(order_id: str, user_id: str) -> bool`:
    *   Simulates sending a confirmation notification to the user in the `NotificationService`.
    *   Always return `True`.
    *   **Compensation:** `resend_confirmation_notification(order_id, user_id)` - In this case, compensation is to simply resend the notification after a brief delay.

**Compensation Functions (Implement these as well):**

*   `compensate_inventory_reservation(order_id: str, items: list) -> None`
*   `refund_payment(order_id: str, user_id: str, amount: float) -> None`
*   `cancel_shipping(order_id: str) -> None`
*   `resend_confirmation_notification(order_id: str, user_id: str) -> None`

**Constraints and Considerations:**

*   **Atomicity:** The `place_order` function must behave atomically – either the entire order fulfillment succeeds, or all changes are rolled back.
*   **Idempotency:** The compensation functions should be idempotent.  They might be called multiple times, and the result should be the same as if they were called only once.  (Hint: Use `order_id` to track compensation status).
*   **Concurrency:** Assume that multiple orders can be placed concurrently.  You need to ensure thread safety (using locks) when accessing shared resources like `inventory` and `payment_records`.  Assume the global variables are accessed by multiple threads, so incorporate thread safety mechanisms.
*   **Logging:**  Implement basic logging to track the progress of each step and any compensations that are performed.
*   **Error Handling:** Implement robust error handling to catch exceptions and ensure that compensations are triggered appropriately.

**Global Variables (Shared Resources - protected by locks):**

```python
inventory = {}  # item_id: quantity
payment_records = {}  # order_id: 'processed' or None
item_prices = {} # item_id: price
blacklist_order_ids = set() #order_id : Set of order ids that will cause payment failure
shipping_error_order_ids = set() # Set of order ids that will cause shipping failure
inventory_lock = threading.Lock()
payment_lock = threading.Lock()
shipping_lock = threading.Lock()
notification_lock = threading.Lock()
```

**Example Usage:**

```python
order_id = "order123"
items = [{"item_id": "item1", "quantity": 2}, {"item_id": "item2", "quantity": 1}]
user_id = "user456"
payment_info = {"credit_card": "..."}
shipping_address = {"street": "...", "city": "..."}

success = place_order(order_id, items, user_id, payment_info, shipping_address)

if success:
    print(f"Order {order_id} placed successfully!")
else:
    print(f"Order {order_id} failed.")
```

**Difficulty:** Hard (LeetCode Hard level)

This problem tests your understanding of distributed systems concepts, the Saga pattern, concurrency control, error handling, and idempotency, along with your Python programming skills. Good luck!
