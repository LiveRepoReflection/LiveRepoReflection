package decentralized_consensus

import (
	"math/rand"
	"testing"
)

func TestSimulateConsensus(t *testing.T) {
	tests := []struct {
		name                   string
		n                      int
		k                      int
		r                      int
		initialValues          []int64
		messageLossProbability float64
		expectedConsensus      bool
	}{
		{
			name:                   "Single node always reaches consensus",
			n:                      1,
			k:                      0, // doesn't matter for single node
			r:                      1,
			initialValues:          []int64{42},
			messageLossProbability: 0,
			expectedConsensus:      true,
		},
		{
			name:                   "Two nodes with same value already in consensus",
			n:                      2,
			k:                      1,
			r:                      1,
			initialValues:          []int64{10, 10},
			messageLossProbability: 0,
			expectedConsensus:      true,
		},
		{
			name:                   "Two nodes reach consensus with no message loss",
			n:                      2,
			k:                      1,
			r:                      2,
			initialValues:          []int64{5, 10},
			messageLossProbability: 0,
			expectedConsensus:      true,
		},
		{
			name:                   "Three nodes reach consensus with no message loss",
			n:                      3,
			k:                      2,
			r:                      3,
			initialValues:          []int64{1, 5, 9},
			messageLossProbability: 0,
			expectedConsensus:      true,
		},
		{
			name:                   "Five nodes with high variance values",
			n:                      5,
			k:                      3,
			r:                      10,
			initialValues:          []int64{1, 10, 100, 1000, 10000},
			messageLossProbability: 0,
			expectedConsensus:      true,
		},
		{
			name:                   "Ten nodes with low message loss",
			n:                      10,
			k:                      5,
			r:                      20,
			initialValues:          []int64{1, 2, 3, 4, 5, 6, 7, 8, 9, 10},
			messageLossProbability: 0.1,
			expectedConsensus:      true,
		},
		{
			name:                   "Five nodes with high message loss probability may not reach consensus",
			n:                      5,
			k:                      1,
			r:                      3,
			initialValues:          []int64{1, 5, 10, 15, 20},
			messageLossProbability: 0.9,
			expectedConsensus:      false,
		},
		{
			name:                   "Large network test",
			n:                      100,
			k:                      10,
			r:                      20,
			initialValues:          generateSequentialValues(100),
			messageLossProbability: 0.2,
			expectedConsensus:      true,
		},
		{
			name:                   "Extreme values test",
			n:                      10,
			k:                      5,
			r:                      15,
			initialValues:          []int64{-9223372036854775808, 0, 9223372036854775807, 1, -1, 1000000, -1000000, 5, -5, 42},
			messageLossProbability: 0.1,
			expectedConsensus:      true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Use a deterministic seed for reproducible tests
			rand.Seed(42)
			
			result := SimulateConsensus(tt.n, tt.k, tt.r, tt.initialValues, tt.messageLossProbability)
			
			if result != tt.expectedConsensus {
				t.Errorf("SimulateConsensus(%d, %d, %d, %v, %f) = %v, want %v",
					tt.n, tt.k, tt.r, tt.initialValues, tt.messageLossProbability, result, tt.expectedConsensus)
			}
		})
	}
}

func TestSimulateConsensusEdgeCases(t *testing.T) {
	// Test with minimum valid values
	t.Run("Minimum valid values", func(t *testing.T) {
		rand.Seed(42)
		result := SimulateConsensus(1, 0, 1, []int64{1}, 0)
		if !result {
			t.Errorf("Expected consensus for minimum valid values")
		}
	})

	// Test with varying values requiring an even number median calculation
	t.Run("Even number median calculation", func(t *testing.T) {
		rand.Seed(42)
		result := SimulateConsensus(4, 2, 5, []int64{1, 3, 5, 7}, 0)
		// We expect consensus because the smaller of the two middle values (3) is chosen
		if !result {
			t.Errorf("Expected consensus for even number median calculation")
		}
	})

	// Test where all nodes have the same initial value except one
	t.Run("All same except one", func(t *testing.T) {
		rand.Seed(42)
		result := SimulateConsensus(5, 3, 10, []int64{10, 10, 10, 10, 100}, 0)
		if !result {
			t.Errorf("Expected consensus when all nodes have same value except one")
		}
	})
}

func BenchmarkSimulateConsensus(b *testing.B) {
	benchmarks := []struct {
		name                   string
		n                      int
		k                      int
		r                      int
		messageLossProbability float64
	}{
		{"Small network (10 nodes)", 10, 5, 10, 0.1},
		{"Medium network (50 nodes)", 50, 10, 20, 0.1},
		{"Large network (200 nodes)", 200, 20, 20, 0.1},
	}

	for _, bm := range benchmarks {
		b.Run(bm.name, func(b *testing.B) {
			initialValues := generateRandomValues(bm.n)
			rand.Seed(42) // Use a fixed seed for reproducibility
			
			b.ResetTimer()
			for i := 0; i < b.N; i++ {
				SimulateConsensus(bm.n, bm.k, bm.r, initialValues, bm.messageLossProbability)
			}
		})
	}
}

// Helper functions
func generateSequentialValues(n int) []int64 {
	values := make([]int64, n)
	for i := 0; i < n; i++ {
		values[i] = int64(i + 1)
	}
	return values
}

func generateRandomValues(n int) []int64 {
	values := make([]int64, n)
	for i := 0; i < n; i++ {
		values[i] = int64(rand.Intn(1000))
	}
	return values
}