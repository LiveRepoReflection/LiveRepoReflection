## Problem: Scalable Transaction Reconciliation

**Description:**

You are building a financial reconciliation system for a high-volume transaction platform. The platform processes millions of transactions daily across various sources (e.g., bank transfers, credit card payments, cryptocurrency exchanges). Your task is to efficiently reconcile these transactions to identify discrepancies and potential fraud.

**Input:**

You will receive two sets of transaction records:

1.  **Expected Transactions:** A stream of expected transactions from the platform's internal ledger. Each transaction record contains:
    *   `transaction_id` (unique string): A unique identifier for the transaction.
    *   `timestamp` (integer): Unix timestamp of when the transaction was initiated.
    *   `amount` (decimal): The expected transaction amount.
    *   `currency` (string): The currency of the transaction (e.g., "USD", "EUR", "BTC").
    *   `source` (string): The source of the transaction (e.g., "BankA", "CreditCardB", "ExchangeC").
    *   `type` (string): The transaction type (e.g., "deposit", "withdrawal", "payment").

2.  **Observed Transactions:** A stream of observed transaction records from external sources (e.g., bank statements, payment gateway reports, exchange APIs). Each transaction record contains the same fields as the expected transactions, but the values might differ.

**Output:**

Identify and report the following types of discrepancies:

1.  **Missing Transactions:** Transactions present in the `Expected Transactions` stream but not found in the `Observed Transactions` stream within a specified time window.
2.  **Unexpected Transactions:** Transactions present in the `Observed Transactions` stream but not found in the `Expected Transactions` stream within a specified time window.
3.  **Amount Mismatches:** Transactions where the `transaction_id` matches in both streams, but the `amount` differs beyond a certain tolerance.
4.  **Currency Mismatches:** Transactions where the `transaction_id` matches in both streams, but the `currency` differs.
5.  **Type Mismatches:** Transactions where the `transaction_id` matches in both streams, but the `type` differs.

Your solution should output a list of discrepancy records. Each discrepancy record should contain:

*   `discrepancy_type` (string): One of "Missing", "Unexpected", "AmountMismatch", "CurrencyMismatch", "TypeMismatch".
*   `transaction_id` (string): The `transaction_id` of the involved transaction.
*   `expected_record` (dictionary): The corresponding record from the `Expected Transactions` stream (or `None` if the transaction is unexpected).
*   `observed_record` (dictionary): The corresponding record from the `Observed Transactions` stream (or `None` if the transaction is missing).
*   `details` (string): A description of the discrepancy (e.g., "Expected amount: 100.00, Observed amount: 99.50").

**Constraints:**

*   **Scalability:** The system must handle millions of transactions per day.
*   **Real-time or Near Real-time:** Discrepancies should be detected and reported as quickly as possible.  A reasonable latency is within a few minutes.
*   **Memory Efficiency:** Memory usage should be minimized, as the entire dataset cannot be held in memory simultaneously.
*   **Time Window:** Transactions are considered matching if their timestamps are within a specified `time_window` (in seconds) of each other. This accounts for potential timing differences between systems.
*   **Amount Tolerance:** Amounts are considered matching if the absolute difference is less than or equal to a specified `amount_tolerance`.
*   **Handling Late Arriving Data:**  Transactions might arrive out of order or with significant delays. The system should be able to handle late-arriving data gracefully, without causing incorrect discrepancies.
*   **Multiple Sources:** The `Observed Transactions` might come from multiple independent sources, each with its own data format and arrival rate.
*   **Currency Conversion:** (Optional, but adds complexity) Handle transactions in different currencies by using a currency conversion API.

**Example:**

```
Expected Transaction:
{
    "transaction_id": "tx123",
    "timestamp": 1678886400,
    "amount": 100.00,
    "currency": "USD",
    "source": "BankA",
    "type": "deposit"
}

Observed Transaction:
{
    "transaction_id": "tx123",
    "timestamp": 1678886410,
    "amount": 99.50,
    "currency": "USD",
    "source": "BankA",
    "type": "deposit"
}

time_window = 60 seconds
amount_tolerance = 1.00

Output Discrepancy:
{
    "discrepancy_type": "AmountMismatch",
    "transaction_id": "tx123",
    "expected_record": { ... },
    "observed_record": { ... },
    "details": "Expected amount: 100.00, Observed amount: 99.50"
}
```

**Bonus Challenges:**

*   Implement a mechanism to automatically resolve minor discrepancies (e.g., small amount differences).
*   Provide a user interface to view and manage detected discrepancies.
*   Integrate with an alerting system to notify relevant stakeholders about critical discrepancies.
*   Implement currency conversion to allow comparison of transactions with different currencies.

This problem requires careful consideration of data structures, algorithms, and system design to achieve the required scalability, efficiency, and accuracy. Good luck!
