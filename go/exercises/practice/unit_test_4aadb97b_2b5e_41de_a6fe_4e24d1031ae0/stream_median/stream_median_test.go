package stream_median

import (
	"math/rand"
	"testing"
	"time"
)

func TestMedianCalculator(t *testing.T) {
	t.Run("EmptyStream", func(t *testing.T) {
		sm := NewStreamMedian()
		if median := sm.GetMedian(); median != 0.0 {
			t.Errorf("Expected median 0.0 for empty stream, got %f", median)
		}
	})

	t.Run("SingleElement", func(t *testing.T) {
		sm := NewStreamMedian()
		sm.ProcessData(42)
		if median := sm.GetMedian(); median != 42.0 {
			t.Errorf("Expected median 42.0, got %f", median)
		}
	})

	t.Run("TwoElements", func(t *testing.T) {
		sm := NewStreamMedian()
		sm.ProcessData(10)
		sm.ProcessData(20)
		if median := sm.GetMedian(); median != 15.0 {
			t.Errorf("Expected median 15.0, got %f", median)
		}
	})

	t.Run("OddNumberOfElements", func(t *testing.T) {
		sm := NewStreamMedian()
		sm.ProcessData(10)
		sm.ProcessData(20)
		sm.ProcessData(30)
		if median := sm.GetMedian(); median != 20.0 {
			t.Errorf("Expected median 20.0, got %f", median)
		}
	})

	t.Run("EvenNumberOfElements", func(t *testing.T) {
		sm := NewStreamMedian()
		sm.ProcessData(10)
		sm.ProcessData(20)
		sm.ProcessData(30)
		sm.ProcessData(40)
		if median := sm.GetMedian(); median != 25.0 {
			t.Errorf("Expected median 25.0, got %f", median)
		}
	})

	t.Run("NegativeNumbers", func(t *testing.T) {
		sm := NewStreamMedian()
		sm.ProcessData(-10)
		sm.ProcessData(-20)
		sm.ProcessData(-30)
		if median := sm.GetMedian(); median != -20.0 {
			t.Errorf("Expected median -20.0, got %f", median)
		}
	})

	t.Run("MixedNumbers", func(t *testing.T) {
		sm := NewStreamMedian()
		sm.ProcessData(-10)
		sm.ProcessData(10)
		sm.ProcessData(0)
		if median := sm.GetMedian(); median != 0.0 {
			t.Errorf("Expected median 0.0, got %f", median)
		}
	})

	t.Run("LargeDataset", func(t *testing.T) {
		sm := NewStreamMedian()
		for i := 1; i <= 1001; i++ {
			sm.ProcessData(i)
		}
		if median := sm.GetMedian(); median != 501.0 {
			t.Errorf("Expected median 501.0, got %f", median)
		}
	})

	t.Run("RandomOrder", func(t *testing.T) {
		sm := NewStreamMedian()
		rand.Seed(time.Now().UnixNano())
		nums := []int{1, 2, 3, 4, 5, 6, 7, 8, 9, 10}
		rand.Shuffle(len(nums), func(i, j int) { nums[i], nums[j] = nums[j], nums[i] })
		for _, num := range nums {
			sm.ProcessData(num)
		}
		if median := sm.GetMedian(); median != 5.5 {
			t.Errorf("Expected median 5.5, got %f", median)
		}
	})
}

func BenchmarkStreamMedian(b *testing.B) {
	sm := NewStreamMedian()
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		sm.ProcessData(rand.Intn(1000))
		_ = sm.GetMedian()
	}
}