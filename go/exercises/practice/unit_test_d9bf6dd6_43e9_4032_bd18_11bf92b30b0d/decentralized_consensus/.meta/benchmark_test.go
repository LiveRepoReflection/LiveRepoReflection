package decentralized_consensus

import (
	"math/rand"
	"testing"
	"time"
)

func BenchmarkMedianCalculation(b *testing.B) {
	// Generate test data
	sizes := []int{10, 100, 1000, 10000}
	
	for _, size := range sizes {
		values := generateRandomInt64Slice(size)
		
		b.Run("SortMedian-"+string(rune(size)), func(b *testing.B) {
			for i := 0; i < b.N; i++ {
				calculateMedian(values)
			}
		})
		
		b.Run("EfficientMedian-"+string(rune(size)), func(b *testing.B) {
			for i := 0; i < b.N; i++ {
				efficientMedian(values)
			}
		})
	}
}

func TestMedianImplementationsEquivalence(t *testing.T) {
	rand.Seed(time.Now().UnixNano())
	
	// Test with different sizes of slices
	sizes := []int{1, 2, 3, 10, 100, 1000}
	
	for _, size := range sizes {
		for i := 0; i < 10; i++ { // Run multiple tests per size
			values := generateRandomInt64Slice(size)
			
			sortMedian := calculateMedian(values)
			efficientMedian := efficientMedian(values)
			
			if sortMedian != efficientMedian {
				t.Errorf("Median implementations differ: sort-based=%d, quickselect=%d for size %d",
					sortMedian, efficientMedian, size)
				t.Logf("Values: %v", values)
			}
		}
	}
}

func generateRandomInt64Slice(size int) []int64 {
	result := make([]int64, size)
	for i := 0; i < size; i++ {
		result[i] = rand.Int63n(1000000) - 500000 // Range from -500,000 to 499,999
	}
	return result
}