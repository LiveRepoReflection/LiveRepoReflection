package median_tracker

import (
	"math"
	"sort"
	"sync"
	"testing"
)

// tolerance to compare float64 values
const tolerance = 1e-6

func floatsEqual(a, b float64) bool {
	return math.Abs(a-b) < tolerance
}

// computeMedian computes median from a given slice of ints.
func computeMedian(nums []int) float64 {
	n := len(nums)
	if n == 0 {
		return 0.0
	}
	sort.Ints(nums)
	if n%2 == 1 {
		return float64(nums[n/2])
	}
	return float64(nums[n/2-1]+nums[n/2]) / 2.0
}

func TestSequentialMedian(t *testing.T) {
	// Using two sources.
	tracker := NewMedianTracker(2)

	// each pair holds: sourceID, value, expected median after addition.
	tests := []struct {
		sourceID      int
		value         int
		expectedMedian float64
	}{
		{0, 1, 1.0},    // [1]
		{1, 3, 2.0},    // [1,3] -> (1+3)/2 = 2.0
		{0, 5, 3.0},    // [1,3,5] -> 3
		{1, 4, 3.5},    // [1,3,4,5] -> (3+4)/2 = 3.5
		{0, 2, 3.0},    // [1,2,3,4,5] -> 3
	}

	for i, tt := range tests {
		tracker.AddValue(tt.sourceID, tt.value)
		got := tracker.GetMedian()
		if !floatsEqual(got, tt.expectedMedian) {
			t.Errorf("After addition %d: expected median %f, got %f", i+1, tt.expectedMedian, got)
		}
	}
}

func TestConcurrentMedian(t *testing.T) {
	numSources := 10
	// each source will add 100 values
	valuesPerSource := 100

	tracker := NewMedianTracker(numSources)

	// store all values for median computation.
	allValues := make([]int, 0, numSources*valuesPerSource)
	var mu sync.Mutex

	var wg sync.WaitGroup

	// Each source adds values concurrently.
	for s := 0; s < numSources; s++ {
		wg.Add(1)
		go func(sourceID int) {
			defer wg.Done()
			for v := 1; v <= valuesPerSource; v++ {
				// Create a value based on sourceID and iteration number to vary data.
				value := sourceID*valuesPerSource + v
				tracker.AddValue(sourceID, value)
				// record the value for verification; protect via mutex.
				mu.Lock()
				allValues = append(allValues, value)
				mu.Unlock()
			}
		}(s)
	}

	wg.Wait()

	// Compute expected median from collected values.
	expectedMedian := computeMedian(allValues)
	gotMedian := tracker.GetMedian()

	if !floatsEqual(gotMedian, expectedMedian) {
		t.Errorf("Concurrent test: expected median %f, got %f", expectedMedian, gotMedian)
	}
}

func TestMedianWithNegativeValues(t *testing.T) {
	// Test scenario with negative integers.
	tracker := NewMedianTracker(3)

	// Data: mixed negatives and positives.
	data := []struct {
		sourceID      int
		value         int
		expectedMedian float64
	}{
		{0, -5, -5.0},              // [-5]
		{1, -10, -7.5},             // [-10, -5] -> (-10 + -5)/2 = -7.5
		{2, 0, -5.0},               // [-10, -5, 0] -> -5
		{0, 10, -2.5},              // [-10, -5, 0, 10] -> (-5 + 0)/2 = -2.5
		{1, 5, 0.0},                // [-10, -5, 0, 5, 10] -> 0
		{2, -2, -1.0},              // [-10, -5, -2, 0, 5, 10] -> (-2+0)/2 = -1.0
	}

	for i, d := range data {
		tracker.AddValue(d.sourceID, d.value)
		got := tracker.GetMedian()
		if !floatsEqual(got, d.expectedMedian) {
			t.Errorf("After addition %d: expected median %f, got %f", i+1, d.expectedMedian, got)
		}
	}
}

func TestHighVolumeConcurrent(t *testing.T) {
	// Test with a high volume of data from multiple sources to check stability
	numSources := 50
	valuesPerSource := 1000

	tracker := NewMedianTracker(numSources)
	var wg sync.WaitGroup

	// Using a slice of slices to collect values from each source.
	allValues := make([]int, 0, numSources*valuesPerSource)
	var mu sync.Mutex

	for s := 0; s < numSources; s++ {
		wg.Add(1)
		go func(sourceID int) {
			defer wg.Done()
			for v := 0; v < valuesPerSource; v++ {
				// Generate value that can be positive or negative.
				value := (sourceID - numSources/2) * v
				tracker.AddValue(sourceID, value)
				mu.Lock()
				allValues = append(allValues, value)
				mu.Unlock()
			}
		}(s)
	}

	wg.Wait()
	expectedMedian := computeMedian(allValues)
	gotMedian := tracker.GetMedian()

	if !floatsEqual(gotMedian, expectedMedian) {
		t.Errorf("High volume concurrent test: expected median %f, got %f", expectedMedian, gotMedian)
	}
}