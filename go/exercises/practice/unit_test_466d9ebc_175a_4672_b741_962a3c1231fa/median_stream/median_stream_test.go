package medianstream

import (
	"fmt"
	"math"
	"math/rand"
	"runtime"
	"sync"
	"testing"
	"time"
)

func TestEmptyStream(t *testing.T) {
	ms := New()
	if got, want := ms.GetMedian(), 0.0; got != want {
		t.Errorf("Empty stream median = %f, want %f", got, want)
	}
}

func TestSingleValue(t *testing.T) {
	ms := New()
	ms.AddValue("source1", 5)
	if got, want := ms.GetMedian(), 5.0; got != want {
		t.Errorf("Single value median = %f, want %f", got, want)
	}
}

func TestOddNumberOfValues(t *testing.T) {
	ms := New()
	ms.AddValue("source1", 5)
	ms.AddValue("source1", 3)
	ms.AddValue("source2", 7)
	if got, want := ms.GetMedian(), 5.0; got != want {
		t.Errorf("Odd number median = %f, want %f", got, want)
	}
}

func TestEvenNumberOfValues(t *testing.T) {
	ms := New()
	ms.AddValue("source1", 5)
	ms.AddValue("source1", 3)
	ms.AddValue("source2", 7)
	ms.AddValue("source2", 9)
	if got, want := ms.GetMedian(), 6.0; got != want {
		t.Errorf("Even number median = %f, want %f", got, want)
	}
}

func TestMultipleSources(t *testing.T) {
	ms := New()
	ms.AddValue("source1", 1)
	ms.AddValue("source2", 2)
	ms.AddValue("source3", 3)
	ms.AddValue("source4", 4)
	ms.AddValue("source5", 5)
	if got, want := ms.GetMedian(), 3.0; got != want {
		t.Errorf("Multiple sources median = %f, want %f", got, want)
	}
}

func TestDuplicateValues(t *testing.T) {
	ms := New()
	ms.AddValue("source1", 5)
	ms.AddValue("source2", 5)
	ms.AddValue("source3", 5)
	if got, want := ms.GetMedian(), 5.0; got != want {
		t.Errorf("Duplicate values median = %f, want %f", got, want)
	}
}

func TestMixedValues(t *testing.T) {
	ms := New()
	values := []int{7, 3, 5, 9, 2, 8, 4, 6, 1}
	
	for i, val := range values {
		ms.AddValue(fmt.Sprintf("source%d", i%3+1), val)
	}
	
	if got, want := ms.GetMedian(), 5.0; got != want {
		t.Errorf("Mixed values median = %f, want %f", got, want)
	}
}

func TestStreamingMedian(t *testing.T) {
	ms := New()
	testCases := []struct {
		sourceID    string
		value       int
		wantMedian  float64
	}{
		{"source1", 5, 5.0},
		{"source2", 15, 10.0},
		{"source1", 1, 5.0},
		{"source3", 3, 4.0},
		{"source2", 2, 3.0},
		{"source1", 9, 4.0},
		{"source3", 6, 5.0},
		{"source2", 7, 5.5},
	}
	
	for i, tc := range testCases {
		ms.AddValue(tc.sourceID, tc.value)
		if got := ms.GetMedian(); math.Abs(got - tc.wantMedian) > 1e-6 {
			t.Errorf("Case %d: After adding %d from %s, median = %f, want %f", 
				i, tc.value, tc.sourceID, got, tc.wantMedian)
		}
	}
}

func TestLargeInputs(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping large input test in short mode")
	}
	
	ms := New()
	n := 10000
	
	// Add n values in ascending order
	for i := 0; i < n; i++ {
		ms.AddValue("source1", i)
	}
	
	expectedMedian := float64(n-1) / 2.0
	if got := ms.GetMedian(); math.Abs(got - expectedMedian) > 1e-6 {
		t.Errorf("Large ascending input median = %f, want %f", got, expectedMedian)
	}
	
	// Add n more values in descending order
	for i := 0; i < n; i++ {
		ms.AddValue("source2", n-i-1)
	}
	
	// Now we should have all values 0 to n-1 twice, so median is still the same
	if got := ms.GetMedian(); math.Abs(got - expectedMedian) > 1e-6 {
		t.Errorf("After adding descending values, median = %f, want %f", got, expectedMedian)
	}
}

func TestConcurrentAccess(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping concurrent access test in short mode")
	}
	
	ms := New()
	const (
		numGoroutines = 50
		numOperations = 1000
	)
	
	var wg sync.WaitGroup
	wg.Add(numGoroutines)
	
	// Seed random number generator
	rand.Seed(time.Now().UnixNano())
	
	for i := 0; i < numGoroutines; i++ {
		go func(sourceID string) {
			defer wg.Done()
			for j := 0; j < numOperations; j++ {
				value := rand.Intn(10000)
				ms.AddValue(sourceID, value)
				
				// Occasionally check the median
				if j%100 == 0 {
					_ = ms.GetMedian()
				}
			}
		}(fmt.Sprintf("source%d", i))
	}
	
	wg.Wait()
	
	// Final check - just ensure we don't crash
	_ = ms.GetMedian()
}

func TestPerformance(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping performance test in short mode")
	}
	
	ms := New()
	n := 1000000
	sources := 100
	
	// Add many values
	start := time.Now()
	for i := 0; i < n; i++ {
		sourceID := fmt.Sprintf("source%d", i%sources)
		ms.AddValue(sourceID, i)
	}
	addTime := time.Since(start)
	
	// Get median multiple times
	start = time.Now()
	iterations := 1000
	for i := 0; i < iterations; i++ {
		_ = ms.GetMedian()
	}
	getMedianTime := time.Since(start)
	
	t.Logf("Performance with %d values from %d sources:", n, sources)
	t.Logf("  AddValue: %v total (%v per operation)", addTime, addTime/time.Duration(n))
	t.Logf("  GetMedian: %v total (%v per operation)", getMedianTime, getMedianTime/time.Duration(iterations))
	
	// Check memory usage
	var m runtime.MemStats
	runtime.GC()
	runtime.ReadMemStats(&m)
	t.Logf("  Memory usage: %d MB", m.Alloc/(1024*1024))
}

func TestHighPrecisionMedian(t *testing.T) {
	ms := New()
	ms.AddValue("source1", 1)
	ms.AddValue("source2", 2)
	
	median := ms.GetMedian()
	expected := 1.5
	if math.Abs(median-expected) > 1e-6 {
		t.Errorf("High precision median = %f, want %f", median, expected)
	}
	
	// Test with larger values that could cause floating point precision issues
	ms = New()
	ms.AddValue("source1", 1000000)
	ms.AddValue("source2", 1000001)
	
	median = ms.GetMedian()
	expected = 1000000.5
	if math.Abs(median-expected) > 1e-6 {
		t.Errorf("High precision large median = %f, want %f", median, expected)
	}
}