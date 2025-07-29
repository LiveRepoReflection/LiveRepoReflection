package data_stream_median

import (
	"math"
	"sort"
	"testing"
)

// exactMedian computes the true median of a slice of float64 numbers.
func exactMedian(values []float64) float64 {
	copied := make([]float64, len(values))
	copy(copied, values)
	sort.Float64s(copied)
	n := len(copied)
	if n%2 == 1 {
		return copied[n/2]
	}
	return (copied[(n/2)-1] + copied[n/2]) / 2.0
}

// withinEpsilon checks whether the approximate median is within the specified relative error (epsilon) of the exact median.
func withinEpsilon(approx, exact, epsilon float64) bool {
	diff := math.Abs(approx - exact)
	return diff <= epsilon*math.Abs(exact)
}

func TestMedianApproximation(t *testing.T) {
	testCases := []struct {
		name     string
		capacity int
		epsilon  float64
		input    []float64
	}{
		{
			name:     "single_element",
			capacity: 5,
			epsilon:  0.01,
			input:    []float64{10.0},
		},
		{
			name:     "odd_count",
			capacity: 10,
			epsilon:  0.05,
			input:    []float64{100, 50, 70},
		},
		{
			name:     "even_count",
			capacity: 10,
			epsilon:  0.1,
			input:    []float64{1, 2, 3, 4},
		},
		{
			name:     "large_dataset",
			capacity: 50,
			epsilon:  0.2,
			input: func() []float64 {
				var arr []float64
				for i := 1; i <= 100; i++ {
					arr = append(arr, float64(i))
				}
				return arr
			}(),
		},
		{
			name:     "similar_values",
			capacity: 5,
			epsilon:  0.05,
			input:    []float64{10000, 10000.5, 10000.2, 10000.7, 10000.3},
		},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			mm := NewLimitedMemoryMedian(tc.capacity, tc.epsilon)
			for _, v := range tc.input {
				mm.Add(v)
			}
			approx := mm.Median()
			trueMedian := exactMedian(tc.input)
			if !withinEpsilon(approx, trueMedian, tc.epsilon) {
				t.Errorf("Test case %s: approximate median %v not within epsilon %v of true median %v", tc.name, approx, tc.epsilon, trueMedian)
			}
		})
	}
}

func TestOrderIndependence(t *testing.T) {
	input := []float64{10, 20, 30, 40, 50, 60, 70, 80, 90, 100}
	order1 := []float64{10, 20, 30, 40, 50, 60, 70, 80, 90, 100}
	order2 := []float64{100, 10, 90, 20, 80, 30, 70, 40, 60, 50}
	capacity := 10
	epsilon := 0.05

	mm1 := NewLimitedMemoryMedian(capacity, epsilon)
	for _, v := range order1 {
		mm1.Add(v)
	}
	mm2 := NewLimitedMemoryMedian(capacity, epsilon)
	for _, v := range order2 {
		mm2.Add(v)
	}

	approx1 := mm1.Median()
	approx2 := mm2.Median()
	trueMedian := exactMedian(input)

	if !withinEpsilon(approx1, trueMedian, epsilon) {
		t.Errorf("OrderIndependence (order1): approximate median %v not within epsilon %v of true median %v", approx1, epsilon, trueMedian)
	}
	if !withinEpsilon(approx2, trueMedian, epsilon) {
		t.Errorf("OrderIndependence (order2): approximate median %v not within epsilon %v of true median %v", approx2, epsilon, trueMedian)
	}
}

func BenchmarkMedian(b *testing.B) {
	// Generate a dataset of 1000 elements.
	var input []float64
	for i := 1; i <= 1000; i++ {
		input = append(input, float64(i))
	}
	capacity := 100
	epsilon := 0.1

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		mm := NewLimitedMemoryMedian(capacity, epsilon)
		for _, v := range input {
			mm.Add(v)
		}
		_ = mm.Median()
	}
}