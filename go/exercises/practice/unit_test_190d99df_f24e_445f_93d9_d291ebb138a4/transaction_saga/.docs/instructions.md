## Problem: Distributed Transaction Orchestrator

You are tasked with building a simplified distributed transaction orchestrator for a microservices architecture. This orchestrator is responsible for ensuring data consistency across multiple independent services when a single logical operation requires modifications to data in several of them. Think of it as a lightweight implementation of the Saga pattern with compensation transactions.

**Scenario:**

Imagine an e-commerce system composed of three microservices: `OrderService`, `PaymentService`, and `InventoryService`. When a user places an order, the following steps need to occur atomically:

1.  `OrderService` creates a new order record.
2.  `PaymentService` processes the payment.
3.  `InventoryService` reserves the ordered items (reducing the available quantity).

If any of these steps fail, all preceding steps must be compensated (rolled back) to maintain data consistency.

**Your Task:**

Implement a `TransactionOrchestrator` in Go that can manage distributed transactions across these three services (represented by function calls). The orchestrator should:

1.  **Define a transaction:** A transaction consists of a list of actions (forward operations) and their corresponding compensation actions (rollback operations).
2.  **Execute the transaction:** Execute the forward actions in sequence. If any action fails (returns an error), execute the compensation actions for all previously successful actions in reverse order.
3.  **Handle failures gracefully:** Implement proper error handling and logging.  If a compensation action fails, log the error and continue with the remaining compensation actions. The orchestrator should return an error indicating overall transaction failure, even if some compensation actions also failed.
4.  **Concurrency:**  The transaction orchestrator must be concurrency-safe. Multiple transactions can be executed simultaneously.

**Constraints and Requirements:**

*   **Service Interaction:** You are provided with stub functions representing the interactions with the services: `CreateOrder`, `ProcessPayment`, and `ReserveInventory`.  These functions can simulate success or failure based on predefined conditions.
*   **Idempotency:** Assume that the compensation actions (e.g., `CancelOrder`, `RefundPayment`, `ReleaseInventory`) are idempotent. They can be safely retried multiple times without unintended side effects.
*   **Timeouts:**  Implement timeouts for both forward and compensation actions.  If an action takes longer than the specified timeout, consider it a failure and proceed with the compensation phase.
*   **Logging:** The orchestrator should log the start and completion (success or failure) of each action (forward and compensation). Use a structured logging library of your choice (e.g., `log`, `logrus`, `zap`).
*   **Scalability:** While this is a single-process implementation, consider the design implications for a distributed environment.  How would you adapt your design for a real-world distributed system with multiple orchestrator instances? (This aspect will not be explicitly tested but should inform your design choices).
*   **Error Handling:** Use the `errors` package to create and wrap errors, providing context about where the error occurred.  This will help with debugging and troubleshooting.

**Stub Functions (Provided):**

```go
package main

import (
	"context"
	"errors"
	"time"
)

// Simulate service interactions
var (
	ErrOrderCreationFailed  = errors.New("order creation failed")
	ErrPaymentFailed        = errors.New("payment processing failed")
	ErrInventoryReservationFailed = errors.New("inventory reservation failed")
	ErrOrderCancellationFailed = errors.New("order cancellation failed")
	ErrPaymentRefundFailed = errors.New("payment refund failed")
	ErrInventoryReleaseFailed = errors.New("inventory release failed")

	SimulatePaymentFailure = false
	SimulateInventoryFailure = false
)

// CreateOrder simulates creating an order.
func CreateOrder(ctx context.Context, orderID string) error {
	// Simulate potential failure during order creation
	return nil
}

// CancelOrder simulates cancelling an order.
func CancelOrder(ctx context.Context, orderID string) error {
	// Simulate potential failure during order cancellation
	return nil
}

// ProcessPayment simulates processing a payment.
func ProcessPayment(ctx context.Context, orderID string, amount float64) error {
	if SimulatePaymentFailure {
		return ErrPaymentFailed
	}
	return nil
}

// RefundPayment simulates refunding a payment.
func RefundPayment(ctx context.Context, orderID string, amount float64) error {
	// Simulate potential failure during payment refund
	return nil
}

// ReserveInventory simulates reserving inventory.
func ReserveInventory(ctx context.Context, orderID string, items []string) error {
	if SimulateInventoryFailure {
		return ErrInventoryReservationFailed
	}
	return nil
}

// ReleaseInventory simulates releasing reserved inventory.
func ReleaseInventory(ctx context.Context, orderID string, items []string) error {
	// Simulate potential failure during inventory release
	return nil
}
```

**Example Transaction:**

```go
orderID := "order123"
amount := 100.0
items := []string{"item1", "item2"}

transaction := []Action{
    {
        Name: "CreateOrder",
        Forward: func(ctx context.Context) error {
            return CreateOrder(ctx, orderID)
        },
        Compensation: func(ctx context.Context) error {
            return CancelOrder(ctx, orderID)
        },
        Timeout: 5 * time.Second,
    },
    {
        Name: "ProcessPayment",
        Forward: func(ctx context.Context) error {
            return ProcessPayment(ctx, orderID, amount)
        },
        Compensation: func(ctx context.Context) error {
            return RefundPayment(ctx, orderID, amount)
        },
        Timeout: 5 * time.Second,
    },
    {
        Name: "ReserveInventory",
        Forward: func(ctx context.Context) error {
            return ReserveInventory(ctx, orderID, items)
        },
        Compensation: func(ctx context.Context) error {
            return ReleaseInventory(ctx, orderID, items)
        },
        Timeout: 5 * time.Second,
    },
}
```

**Deliverables:**

1.  Go code implementing the `TransactionOrchestrator` with the required functionality.
2.  A clear explanation of your design choices, particularly concerning concurrency, error handling, and scalability.
3.  Demonstration of how to use your `TransactionOrchestrator` with the provided stub functions and the example transaction.

This problem requires a deep understanding of concurrency, error handling, and distributed systems principles, making it a challenging task suitable for a high-level programming competition. Good luck!
