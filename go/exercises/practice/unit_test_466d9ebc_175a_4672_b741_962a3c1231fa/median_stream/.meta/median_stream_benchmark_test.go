package medianstream

import (
	"fmt"
	"math/rand"
	"testing"
)

func BenchmarkAddValue(b *testing.B) {
	sizes := []int{1000, 10000, 100000}
	
	for _, size := range sizes {
		b.Run(fmt.Sprintf("Size-%d", size), func(b *testing.B) {
			ms := New()
			
			// Pre-populate with size elements
			for i := 0; i < size; i++ {
				ms.AddValue(fmt.Sprintf("source%d", i%100), i)
			}
			
			// Reset timer for the actual benchmark
			b.ResetTimer()
			
			for i := 0; i < b.N; i++ {
				ms.AddValue("benchmark-source", rand.Intn(100000))
			}
		})
	}
}

func BenchmarkGetMedian(b *testing.B) {
	sizes := []int{1000, 10000, 100000, 1000000}
	
	for _, size := range sizes {
		b.Run(fmt.Sprintf("Size-%d", size), func(b *testing.B) {
			ms := New()
			
			// Pre-populate with size elements
			for i := 0; i < size; i++ {
				ms.AddValue(fmt.Sprintf("source%d", i%100), rand.Intn(100000))
			}
			
			// Reset timer for the actual benchmark
			b.ResetTimer()
			
			for i := 0; i < b.N; i++ {
				_ = ms.GetMedian()
			}
		})
	}
}

func BenchmarkMixedOperations(b *testing.B) {
	ms := New()
	
	// Pre-populate with some elements
	for i := 0; i < 10000; i++ {
		ms.AddValue(fmt.Sprintf("source%d", i%100), rand.Intn(100000))
	}
	
	// Reset timer for the actual benchmark
	b.ResetTimer()
	
	b.Run("90%Add-10%Get", func(b *testing.B) {
		for i := 0; i < b.N; i++ {
			if rand.Intn(10) < 9 {
				ms.AddValue(fmt.Sprintf("source%d", i%100), rand.Intn(100000))
			} else {
				_ = ms.GetMedian()
			}
		}
	})
	
	b.Run("50%Add-50%Get", func(b *testing.B) {
		for i := 0; i < b.N; i++ {
			if rand.Intn(2) == 0 {
				ms.AddValue(fmt.Sprintf("source%d", i%100), rand.Intn(100000))
			} else {
				_ = ms.GetMedian()
			}
		}
	})
	
	b.Run("10%Add-90%Get", func(b *testing.B) {
		for i := 0; i < b.N; i++ {
			if rand.Intn(10) < 1 {
				ms.AddValue(fmt.Sprintf("source%d", i%100), rand.Intn(100000))
			} else {
				_ = ms.GetMedian()
			}
		}
	})
}