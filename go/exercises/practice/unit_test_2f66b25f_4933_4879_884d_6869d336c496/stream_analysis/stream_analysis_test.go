package stream_analysis

import (
	"math"
	"sync"
	"testing"
)

// Helper function to compare floating point numbers.
func floatEquals(a, b float64) bool {
	const eps = 1e-9
	return math.Abs(a-b) < eps
}

func TestEmptyWindow(t *testing.T) {
	analyzer := NewStreamAnalyzer(10)
	
	avg := analyzer.Average()
	if !floatEquals(avg, 0.0) {
		t.Errorf("Empty window average = %f, want %f", avg, 0.0)
	}

	med := analyzer.Median()
	if !floatEquals(med, 0.0) {
		t.Errorf("Empty window median = %f, want %f", med, 0.0)
	}

	p, err := analyzer.Percentile(0.5)
	if err != nil {
		t.Errorf("Empty window Percentile(0.5) returned error: %v", err)
	}
	if !floatEquals(p, 0.0) {
		t.Errorf("Empty window Percentile(0.5) = %f, want %f", p, 0.0)
	}
}

func TestSingleElement(t *testing.T) {
	analyzer := NewStreamAnalyzer(10)
	analyzer.Ingest(5.0)

	avg := analyzer.Average()
	if !floatEquals(avg, 5.0) {
		t.Errorf("Single element average = %f, want %f", avg, 5.0)
	}

	med := analyzer.Median()
	if !floatEquals(med, 5.0) {
		t.Errorf("Single element median = %f, want %f", med, 5.0)
	}

	p, err := analyzer.Percentile(0.5)
	if err != nil {
		t.Errorf("Single element Percentile(0.5) returned error: %v", err)
	}
	if !floatEquals(p, 5.0) {
		t.Errorf("Single element Percentile(0.5) = %f, want %f", p, 5.0)
	}
}

func TestWindowSliding(t *testing.T) {
	windowSize := 5
	analyzer := NewStreamAnalyzer(windowSize)
	// Ingest more than windowSize elements; the window should always hold the last 'windowSize' elements.
	data := []float64{1, 2, 3, 4, 5, 6, 7}
	for _, d := range data {
		analyzer.Ingest(d)
	}
	// Expected window contains: 3, 4, 5, 6, 7
	expectedAvg := (3 + 4 + 5 + 6 + 7) / 5.0
	avg := analyzer.Average()
	if !floatEquals(avg, expectedAvg) {
		t.Errorf("Window sliding average = %f, want %f", avg, expectedAvg)
	}

	// Median of [3,4,5,6,7] is 5.
	med := analyzer.Median()
	if !floatEquals(med, 5.0) {
		t.Errorf("Window sliding median = %f, want %f", med, 5.0)
	}

	// For Percentile, assuming a method that returns the value at a specific rank.
	// For p = 0.25 in the sorted array [3,4,5,6,7], expected value is 4.
	p, err := analyzer.Percentile(0.25)
	if err != nil {
		t.Errorf("Percentile(0.25) returned error: %v", err)
	}
	if !floatEquals(p, 4.0) {
		t.Errorf("Percentile(0.25) = %f, want %f", p, 4.0)
	}
}

func TestPercentileInvalid(t *testing.T) {
	analyzer := NewStreamAnalyzer(10)
	analyzer.Ingest(5.0)

	_, err := analyzer.Percentile(-0.1)
	if err == nil {
		t.Errorf("Expected error for Percentile(-0.1), got nil")
	}

	_, err = analyzer.Percentile(1.1)
	if err == nil {
		t.Errorf("Expected error for Percentile(1.1), got nil")
	}
}

func TestEdgePercentiles(t *testing.T) {
	analyzer := NewStreamAnalyzer(5)
	// Ingest data in arbitrary order.
	data := []float64{10, 20, 30, 40, 50}
	for _, v := range data {
		analyzer.Ingest(v)
	}

	// Percentile at 0.0 should return the minimum value.
	minVal, err := analyzer.Percentile(0.0)
	if err != nil {
		t.Errorf("Percentile(0.0) returned error: %v", err)
	}
	if !floatEquals(minVal, 10.0) {
		t.Errorf("Percentile(0.0) = %f, want %f", minVal, 10.0)
	}

	// Percentile at 1.0 should return the maximum value.
	maxVal, err := analyzer.Percentile(1.0)
	if err != nil {
		t.Errorf("Percentile(1.0) returned error: %v", err)
	}
	if !floatEquals(maxVal, 50.0) {
		t.Errorf("Percentile(1.0) = %f, want %f", maxVal, 50.0)
	}
}

func TestConcurrentAccess(t *testing.T) {
	analyzer := NewStreamAnalyzer(1000)
	var wg sync.WaitGroup

	// Launch 100 goroutines for concurrent ingestion.
	for i := 0; i < 100; i++ {
		wg.Add(1)
		go func(start int) {
			defer wg.Done()
			for j := 0; j < 1000; j++ {
				analyzer.Ingest(float64(start*1000 + j))
			}
		}(i)
	}

	// Launch 50 goroutines for concurrent querying.
	for i := 0; i < 50; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for j := 0; j < 1000; j++ {
				_ = analyzer.Average()
				_ = analyzer.Median()
				if p, err := analyzer.Percentile(0.5); err != nil || p < 0 {
					t.Errorf("Concurrent Percentile(0.5) error: %v, value: %f", err, p)
				}
			}
		}()
	}

	wg.Wait()
}