package transaction_ordering

import (
	"testing"
	"time"
)

func TestTransactionProcessing(t *testing.T) {
	tests := []struct {
		name             string
		transactions     []Transaction
		initialBalances  map[int]int
		expectedRejected []Transaction
		expectedBalances map[int]int
	}{
		{
			name: "basic transactions",
			transactions: []Transaction{
				{From: 1, To: 2, Amount: 100, Timestamp: time.Unix(1678886400, 0)},
				{From: 2, To: 3, Amount: 50, Timestamp: time.Unix(1678886401, 0)},
			},
			initialBalances:  map[int]int{1: 1000, 2: 500, 3: 300},
			expectedRejected: []Transaction{},
			expectedBalances: map[int]int{1: 900, 2: 550, 3: 350},
		},
		{
			name: "insufficient funds",
			transactions: []Transaction{
				{From: 1, To: 2, Amount: 100, Timestamp: time.Unix(1678886400, 0)},
				{From: 1, To: 3, Amount: 1000, Timestamp: time.Unix(1678886401, 0)},
			},
			initialBalances: map[int]int{1: 100, 2: 0, 3: 0},
			expectedRejected: []Transaction{
				{From: 1, To: 3, Amount: 1000, Timestamp: time.Unix(1678886401, 0)},
			},
			expectedBalances: map[int]int{1: 0, 2: 100, 3: 0},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			processor := NewTransactionProcessor(tt.initialBalances)
			rejected := processor.Process(tt.transactions)

			if len(rejected) != len(tt.expectedRejected) {
				t.Fatalf("expected %d rejected transactions, got %d", len(tt.expectedRejected), len(rejected))
			}

			for i := range rejected {
				if rejected[i] != tt.expectedRejected[i] {
					t.Errorf("rejected transaction %d mismatch:\nexpected %v\ngot %v", i, tt.expectedRejected[i], rejected[i])
				}
			}

			balances := processor.GetBalances()
			for acc, expected := range tt.expectedBalances {
				if balances[acc] != expected {
					t.Errorf("account %d balance mismatch: expected %d, got %d", acc, expected, balances[acc])
				}
			}
		})
	}
}