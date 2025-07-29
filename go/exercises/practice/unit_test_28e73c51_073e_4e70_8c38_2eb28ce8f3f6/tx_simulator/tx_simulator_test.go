package tx_simulator

import (
	"reflect"
	"testing"
)

func TestSimulateTransactions(t *testing.T) {
	tests := []struct {
		name           string
		n              int
		transactions   []Transaction
		nodeBehaviors  map[int][]string
		expectedResult map[string]bool
	}{
		{
			name: "Basic Example",
			n:    3,
			transactions: []Transaction{
				{ID: "T1", InvolvedNodes: []int{0, 1}, Operation: "read"},
				{ID: "T2", InvolvedNodes: []int{1, 2}, Operation: "write"},
				{ID: "T3", InvolvedNodes: []int{0, 2}, Operation: "process"},
			},
			nodeBehaviors: map[int][]string{
				1: {"write"},
				0: {"process"},
			},
			expectedResult: map[string]bool{
				"T1": true,
				"T2": false,
				"T3": false,
			},
		},
		{
			name: "All Transactions Succeed",
			n:    5,
			transactions: []Transaction{
				{ID: "T1", InvolvedNodes: []int{0, 1, 2}, Operation: "read"},
				{ID: "T2", InvolvedNodes: []int{2, 3, 4}, Operation: "write"},
				{ID: "T3", InvolvedNodes: []int{0, 4}, Operation: "process"},
			},
			nodeBehaviors: map[int][]string{},
			expectedResult: map[string]bool{
				"T1": true,
				"T2": true,
				"T3": true,
			},
		},
		{
			name: "All Transactions Fail",
			n:    4,
			transactions: []Transaction{
				{ID: "T1", InvolvedNodes: []int{0, 1}, Operation: "read"},
				{ID: "T2", InvolvedNodes: []int{1, 2}, Operation: "write"},
				{ID: "T3", InvolvedNodes: []int{2, 3}, Operation: "process"},
			},
			nodeBehaviors: map[int][]string{
				0: {"read"},
				1: {"write"},
				2: {"process"},
			},
			expectedResult: map[string]bool{
				"T1": false,
				"T2": false,
				"T3": false,
			},
		},
		{
			name: "Mixed Success and Failure",
			n:    6,
			transactions: []Transaction{
				{ID: "T1", InvolvedNodes: []int{0, 1, 2}, Operation: "read"},
				{ID: "T2", InvolvedNodes: []int{3, 4, 5}, Operation: "write"},
				{ID: "T3", InvolvedNodes: []int{0, 3}, Operation: "update"},
				{ID: "T4", InvolvedNodes: []int{1, 4}, Operation: "delete"},
				{ID: "T5", InvolvedNodes: []int{2, 5}, Operation: "insert"},
			},
			nodeBehaviors: map[int][]string{
				1: {"read"},
				3: {"write"},
				0: {"update"},
				4: {"delete"},
			},
			expectedResult: map[string]bool{
				"T1": false,
				"T2": false,
				"T3": false,
				"T4": false,
				"T5": true,
			},
		},
		{
			name: "Single Node Transactions",
			n:    3,
			transactions: []Transaction{
				{ID: "T1", InvolvedNodes: []int{0}, Operation: "read"},
				{ID: "T2", InvolvedNodes: []int{1}, Operation: "write"},
				{ID: "T3", InvolvedNodes: []int{2}, Operation: "process"},
			},
			nodeBehaviors: map[int][]string{
				1: {"write"},
			},
			expectedResult: map[string]bool{
				"T1": true,
				"T2": false,
				"T3": true,
			},
		},
		{
			name: "Complex Behaviors",
			n:    5,
			transactions: []Transaction{
				{ID: "T1", InvolvedNodes: []int{0, 1, 2, 3, 4}, Operation: "complex"},
				{ID: "T2", InvolvedNodes: []int{0, 2, 4}, Operation: "read"},
				{ID: "T3", InvolvedNodes: []int{1, 3}, Operation: "write"},
				{ID: "T4", InvolvedNodes: []int{0, 1, 2, 3}, Operation: "update"},
			},
			nodeBehaviors: map[int][]string{
				0: {"complex"},
				1: {"update"},
				3: {"write", "update"},
				4: {"read"},
			},
			expectedResult: map[string]bool{
				"T1": false,
				"T2": false,
				"T3": false,
				"T4": false,
			},
		},
		{
			name: "Empty Transactions",
			n:    3,
			transactions: []Transaction{},
			nodeBehaviors: map[int][]string{
				0: {"read"},
				1: {"write"},
			},
			expectedResult: map[string]bool{},
		},
		{
			name: "Node Behaviors Not Found",
			n:    3,
			transactions: []Transaction{
				{ID: "T1", InvolvedNodes: []int{0, 1}, Operation: "read"},
				{ID: "T2", InvolvedNodes: []int{1, 2}, Operation: "write"},
			},
			nodeBehaviors: map[int][]string{
				5: {"read"}, // Node ID out of range
				6: {"write"}, // Node ID out of range
			},
			expectedResult: map[string]bool{
				"T1": true,
				"T2": true,
			},
		},
		{
			name: "Transaction With No Nodes",
			n:    3,
			transactions: []Transaction{
				{ID: "T1", InvolvedNodes: []int{}, Operation: "read"},
			},
			nodeBehaviors: map[int][]string{},
			expectedResult: map[string]bool{
				"T1": true, // No nodes means no NACKs
			},
		},
		{
			name: "Single Node System",
			n:    1,
			transactions: []Transaction{
				{ID: "T1", InvolvedNodes: []int{0}, Operation: "read"},
				{ID: "T2", InvolvedNodes: []int{0}, Operation: "write"},
			},
			nodeBehaviors: map[int][]string{
				0: {"write"},
			},
			expectedResult: map[string]bool{
				"T1": true,
				"T2": false,
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := SimulateTransactions(tt.n, tt.transactions, tt.nodeBehaviors)
			if !reflect.DeepEqual(result, tt.expectedResult) {
				t.Errorf("SimulateTransactions() = %v, want %v", result, tt.expectedResult)
			}
		})
	}
}

func TestEdgeCases(t *testing.T) {
	t.Run("Zero Nodes", func(t *testing.T) {
		result := SimulateTransactions(0, []Transaction{
			{ID: "T1", InvolvedNodes: []int{}, Operation: "read"},
		}, map[int][]string{})
		expected := map[string]bool{"T1": true}
		if !reflect.DeepEqual(result, expected) {
			t.Errorf("SimulateTransactions() = %v, want %v", result, expected)
		}
	})

	t.Run("Invalid Node IDs in Transaction", func(t *testing.T) {
		result := SimulateTransactions(2, []Transaction{
			{ID: "T1", InvolvedNodes: []int{0, 1}, Operation: "read"},
			{ID: "T2", InvolvedNodes: []int{2, 3}, Operation: "write"}, // Invalid node IDs
		}, map[int][]string{})
		expected := map[string]bool{"T1": true, "T2": true}
		if !reflect.DeepEqual(result, expected) {
			t.Errorf("SimulateTransactions() = %v, want %v", result, expected)
		}
	})

	t.Run("Duplicate Transaction IDs", func(t *testing.T) {
		result := SimulateTransactions(3, []Transaction{
			{ID: "T1", InvolvedNodes: []int{0, 1}, Operation: "read"},
			{ID: "T1", InvolvedNodes: []int{1, 2}, Operation: "write"}, // Duplicate ID
		}, map[int][]string{})
		// Last one wins
		expected := map[string]bool{"T1": true}
		if !reflect.DeepEqual(result, expected) {
			t.Errorf("SimulateTransactions() = %v, want %v", result, expected)
		}
	})

	t.Run("Duplicate Node IDs in Transaction", func(t *testing.T) {
		result := SimulateTransactions(3, []Transaction{
			{ID: "T1", InvolvedNodes: []int{0, 0, 1}, Operation: "read"}, // Duplicate node ID
		}, map[int][]string{})
		expected := map[string]bool{"T1": true}
		if !reflect.DeepEqual(result, expected) {
			t.Errorf("SimulateTransactions() = %v, want %v", result, expected)
		}
	})
}

func BenchmarkSimulateTransactions(b *testing.B) {
	n := 10
	transactions := make([]Transaction, 0, 100)
	for i := 0; i < 100; i++ {
		nodes := []int{i % n, (i + 1) % n, (i + 2) % n}
		transactions = append(transactions, Transaction{
			ID:            "T" + string(rune(i)),
			InvolvedNodes: nodes,
			Operation:     "op" + string(rune(i%5)),
		})
	}
	nodeBehaviors := map[int][]string{
		0: {"op1", "op3"},
		3: {"op0", "op2"},
		5: {"op4"},
		8: {"op1", "op3", "op4"},
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		SimulateTransactions(n, transactions, nodeBehaviors)
	}
}