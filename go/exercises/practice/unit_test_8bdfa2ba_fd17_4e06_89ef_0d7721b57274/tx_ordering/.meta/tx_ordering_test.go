package tx_ordering

import (
	"reflect"
	"testing"
)

func TestOrderTransactions(t *testing.T) {
	tests := []struct {
		name         string
		transactions []Transaction
		expected     []Transaction
	}{
		{
			name:         "Empty transactions",
			transactions: []Transaction{},
			expected:     []Transaction{},
		},
		{
			name: "Single transaction",
			transactions: []Transaction{
				{ID: "A", Submitter: "Alice", Timestamp: 100, Priority: 1, Conflicts: []string{}},
			},
			expected: []Transaction{
				{ID: "A", Submitter: "Alice", Timestamp: 100, Priority: 1, Conflicts: []string{}},
			},
		},
		{
			name: "Order by timestamp",
			transactions: []Transaction{
				{ID: "B", Submitter: "Bob", Timestamp: 200, Priority: 1, Conflicts: []string{}},
				{ID: "A", Submitter: "Alice", Timestamp: 100, Priority: 2, Conflicts: []string{}},
				{ID: "C", Submitter: "Charlie", Timestamp: 300, Priority: 0, Conflicts: []string{}},
			},
			expected: []Transaction{
				{ID: "A", Submitter: "Alice", Timestamp: 100, Priority: 2, Conflicts: []string{}},
				{ID: "B", Submitter: "Bob", Timestamp: 200, Priority: 1, Conflicts: []string{}},
				{ID: "C", Submitter: "Charlie", Timestamp: 300, Priority: 0, Conflicts: []string{}},
			},
		},
		{
			name: "Order by priority when timestamps are equal",
			transactions: []Transaction{
				{ID: "A", Submitter: "Alice", Timestamp: 100, Priority: 2, Conflicts: []string{}},
				{ID: "B", Submitter: "Bob", Timestamp: 100, Priority: 1, Conflicts: []string{}},
				{ID: "C", Submitter: "Charlie", Timestamp: 100, Priority: 3, Conflicts: []string{}},
			},
			expected: []Transaction{
				{ID: "B", Submitter: "Bob", Timestamp: 100, Priority: 1, Conflicts: []string{}},
				{ID: "A", Submitter: "Alice", Timestamp: 100, Priority: 2, Conflicts: []string{}},
				{ID: "C", Submitter: "Charlie", Timestamp: 100, Priority: 3, Conflicts: []string{}},
			},
		},
		{
			name: "Order by ID lexicographically when timestamps and priorities are equal",
			transactions: []Transaction{
				{ID: "C", Submitter: "Charlie", Timestamp: 100, Priority: 1, Conflicts: []string{}},
				{ID: "A", Submitter: "Alice", Timestamp: 100, Priority: 1, Conflicts: []string{}},
				{ID: "B", Submitter: "Bob", Timestamp: 100, Priority: 1, Conflicts: []string{}},
			},
			expected: []Transaction{
				{ID: "A", Submitter: "Alice", Timestamp: 100, Priority: 1, Conflicts: []string{}},
				{ID: "B", Submitter: "Bob", Timestamp: 100, Priority: 1, Conflicts: []string{}},
				{ID: "C", Submitter: "Charlie", Timestamp: 100, Priority: 1, Conflicts: []string{}},
			},
		},
		{
			name: "Handle conflicts with same timestamp and priority",
			transactions: []Transaction{
				{ID: "B", Submitter: "Alice", Timestamp: 100, Priority: 1, Conflicts: []string{"A"}},
				{ID: "A", Submitter: "Bob", Timestamp: 100, Priority: 1, Conflicts: []string{"B"}},
				{ID: "C", Submitter: "Charlie", Timestamp: 200, Priority: 0, Conflicts: []string{}},
			},
			expected: []Transaction{
				{ID: "A", Submitter: "Bob", Timestamp: 100, Priority: 1, Conflicts: []string{"B"}},
				{ID: "B", Submitter: "Alice", Timestamp: 100, Priority: 1, Conflicts: []string{"A"}},
				{ID: "C", Submitter: "Charlie", Timestamp: 200, Priority: 0, Conflicts: []string{}},
			},
		},
		{
			name: "One-way conflict with same timestamp and priority",
			transactions: []Transaction{
				{ID: "B", Submitter: "Alice", Timestamp: 100, Priority: 1, Conflicts: []string{"A"}},
				{ID: "A", Submitter: "Bob", Timestamp: 100, Priority: 1, Conflicts: []string{}},
				{ID: "C", Submitter: "Charlie", Timestamp: 200, Priority: 0, Conflicts: []string{}},
			},
			expected: []Transaction{
				{ID: "A", Submitter: "Bob", Timestamp: 100, Priority: 1, Conflicts: []string{}},
				{ID: "B", Submitter: "Alice", Timestamp: 100, Priority: 1, Conflicts: []string{"A"}},
				{ID: "C", Submitter: "Charlie", Timestamp: 200, Priority: 0, Conflicts: []string{}},
			},
		},
		{
			name: "Complex conflict scenario",
			transactions: []Transaction{
				{ID: "C", Submitter: "Charlie", Timestamp: 100, Priority: 1, Conflicts: []string{"A", "D"}},
				{ID: "A", Submitter: "Alice", Timestamp: 100, Priority: 1, Conflicts: []string{"B"}},
				{ID: "B", Submitter: "Bob", Timestamp: 100, Priority: 1, Conflicts: []string{"C"}},
				{ID: "D", Submitter: "Dave", Timestamp: 100, Priority: 1, Conflicts: []string{"B"}},
				{ID: "E", Submitter: "Eve", Timestamp: 150, Priority: 2, Conflicts: []string{}},
			},
			expected: []Transaction{
				{ID: "A", Submitter: "Alice", Timestamp: 100, Priority: 1, Conflicts: []string{"B"}},
				{ID: "B", Submitter: "Bob", Timestamp: 100, Priority: 1, Conflicts: []string{"C"}},
				{ID: "C", Submitter: "Charlie", Timestamp: 100, Priority: 1, Conflicts: []string{"A", "D"}},
				{ID: "D", Submitter: "Dave", Timestamp: 100, Priority: 1, Conflicts: []string{"B"}},
				{ID: "E", Submitter: "Eve", Timestamp: 150, Priority: 2, Conflicts: []string{}},
			},
		},
		{
			name: "Duplicate transaction IDs",
			transactions: []Transaction{
				{ID: "A", Submitter: "Alice", Timestamp: 100, Priority: 1, Conflicts: []string{}},
				{ID: "A", Submitter: "Alice", Timestamp: 200, Priority: 1, Conflicts: []string{}},
				{ID: "B", Submitter: "Bob", Timestamp: 150, Priority: 1, Conflicts: []string{}},
			},
			expected: []Transaction{
				{ID: "A", Submitter: "Alice", Timestamp: 100, Priority: 1, Conflicts: []string{}},
				{ID: "B", Submitter: "Bob", Timestamp: 150, Priority: 1, Conflicts: []string{}},
				{ID: "A", Submitter: "Alice", Timestamp: 200, Priority: 1, Conflicts: []string{}},
			},
		},
		{
			name: "Mix of all ordering rules",
			transactions: []Transaction{
				{ID: "D", Submitter: "Dave", Timestamp: 300, Priority: 2, Conflicts: []string{}},
				{ID: "B", Submitter: "Bob", Timestamp: 200, Priority: 1, Conflicts: []string{"C"}},
				{ID: "A", Submitter: "Alice", Timestamp: 100, Priority: 3, Conflicts: []string{}},
				{ID: "C", Submitter: "Charlie", Timestamp: 200, Priority: 1, Conflicts: []string{"B"}},
				{ID: "E", Submitter: "Eve", Timestamp: 100, Priority: 1, Conflicts: []string{}},
				{ID: "F", Submitter: "Frank", Timestamp: 100, Priority: 1, Conflicts: []string{}},
			},
			expected: []Transaction{
				{ID: "E", Submitter: "Eve", Timestamp: 100, Priority: 1, Conflicts: []string{}},
				{ID: "F", Submitter: "Frank", Timestamp: 100, Priority: 1, Conflicts: []string{}},
				{ID: "A", Submitter: "Alice", Timestamp: 100, Priority: 3, Conflicts: []string{}},
				{ID: "B", Submitter: "Bob", Timestamp: 200, Priority: 1, Conflicts: []string{"C"}},
				{ID: "C", Submitter: "Charlie", Timestamp: 200, Priority: 1, Conflicts: []string{"B"}},
				{ID: "D", Submitter: "Dave", Timestamp: 300, Priority: 2, Conflicts: []string{}},
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := OrderTransactions(tt.transactions)
			if !reflect.DeepEqual(result, tt.expected) {
				t.Errorf("OrderTransactions() = %v, want %v", result, tt.expected)
			}
		})
	}
}

func TestLargeNumberOfTransactions(t *testing.T) {
	// Test with a large number of transactions to check for performance issues
	if testing.Short() {
		t.Skip("Skipping large transaction test in short mode")
	}

	var transactions []Transaction
	for i := 1000; i >= 1; i-- {
		tx := Transaction{
			ID:        string(rune(64 + i)), // Convert to letters A-Z and beyond
			Timestamp: int64(i * 10),
			Priority:  uint64(i % 5),
		}
		transactions = append(transactions, tx)
	}

	// This is mainly to check that the function completes in a reasonable time
	result := OrderTransactions(transactions)
	if len(result) != len(transactions) {
		t.Errorf("Expected %d transactions, got %d", len(transactions), len(result))
	}
}

func TestConflictResolution(t *testing.T) {
	// Create a scenario with many conflicts to test the conflict resolution logic
	var transactions []Transaction
	
	// All transactions have the same timestamp and priority
	for i := 0; i < 20; i++ {
		conflicts := make([]string, 0)
		// Each transaction conflicts with 5 others
		for j := 1; j <= 5; j++ {
			conflictID := string(rune(65 + ((i + j) % 20)))
			conflicts = append(conflicts, conflictID)
		}
		
		tx := Transaction{
			ID:        string(rune(65 + i)), // A to T
			Timestamp: 100,
			Priority:  1,
			Conflicts: conflicts,
		}
		transactions = append(transactions, tx)
	}

	result := OrderTransactions(transactions)
	
	// Check that the result has the correct number of transactions
	if len(result) != len(transactions) {
		t.Errorf("Expected %d transactions, got %d", len(transactions), len(result))
	}
	
	// Verify that the transactions are sorted lexicographically by ID
	for i := 1; i < len(result); i++ {
		if result[i-1].ID > result[i].ID {
			t.Errorf("Transactions not correctly ordered: %s should come before %s", result[i].ID, result[i-1].ID)
		}
	}
}

func BenchmarkOrderTransactions(b *testing.B) {
	// Prepare a decent sized set of transactions for benchmarking
	var transactions []Transaction
	for i := 0; i < 1000; i++ {
		conflicts := make([]string, 0)
		if i > 0 && i < 999 {
			conflicts = append(conflicts, string(rune(64+i-1)), string(rune(64+i+1)))
		}
		
		tx := Transaction{
			ID:        string(rune(64 + i%26)) + string(rune(64 + i/26)), // Create IDs like AA, AB, etc.
			Timestamp: int64(i % 100 * 10),
			Priority:  uint64(i % 5),
			Conflicts: conflicts,
		}
		transactions = append(transactions, tx)
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		OrderTransactions(transactions)
	}
}