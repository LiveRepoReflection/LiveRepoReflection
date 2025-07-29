package concurrentmedian

import (
	"math"
	"sync"
	"testing"
)

const float64EqualityThreshold = 1e-9

func almostEqual(a, b float64) bool {
	return math.Abs(a-b) <= float64EqualityThreshold
}

func TestMedianCalculator(t *testing.T) {
	for _, tc := range medianTestCases {
		t.Run(tc.description, func(t *testing.T) {
			calc := NewMedianCalculator()
			
			for _, num := range tc.input {
				calc.Insert(num)
			}
			
			got := calc.GetMedian()
			want := tc.expected[len(tc.expected)-1]
			
			if !almostEqual(got, want) {
				t.Errorf("GetMedian() = %v, want %v", got, want)
			}
		})
	}
}

func TestConcurrentAccess(t *testing.T) {
	calc := NewMedianCalculator()
	const goroutines = 100
	const numbersPerGoroutine = 1000
	
	var wg sync.WaitGroup
	wg.Add(goroutines)
	
	// Concurrent insertions
	for i := 0; i < goroutines; i++ {
		go func(offset int) {
			defer wg.Done()
			for j := 0; j < numbersPerGoroutine; j++ {
				calc.Insert(j + offset)
			}
		}(i * numbersPerGoroutine)
	}
	
	// Concurrent reads while inserting
	for i := 0; i < goroutines; i++ {
		go func() {
			calc.GetMedian()
		}()
	}
	
	wg.Wait()
	
	// Verify final state is valid
	median := calc.GetMedian()
	if math.IsNaN(median) {
		t.Error("Invalid median after concurrent operations")
	}
}

func BenchmarkInsert(b *testing.B) {
	calc := NewMedianCalculator()
	b.ResetTimer()
	
	for i := 0; i < b.N; i++ {
		calc.Insert(i)
	}
}

func BenchmarkGetMedian(b *testing.B) {
	calc := NewMedianCalculator()
	for i := 0; i < 1000; i++ {
		calc.Insert(i)
	}
	
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		calc.GetMedian()
	}
}

func BenchmarkConcurrentOperations(b *testing.B) {
	calc := NewMedianCalculator()
	const goroutines = 4
	
	b.ResetTimer()
	
	b.RunParallel(func(pb *testing.PB) {
		for pb.Next() {
			calc.Insert(1)
			calc.GetMedian()
		}
	})
}