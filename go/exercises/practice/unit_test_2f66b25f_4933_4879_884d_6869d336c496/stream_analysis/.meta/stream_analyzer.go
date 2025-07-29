package stream_analysis

import (
	"errors"
	"math"
	"sort"
	"sync"
)

type StreamAnalyzer struct {
	capacity  int
	data      []float64
	nextIndex int
	count     int
	sum       float64
	mu        sync.RWMutex
}

// NewStreamAnalyzer creates a new StreamAnalyzer with a fixed sliding window capacity.
func NewStreamAnalyzer(capacity int) *StreamAnalyzer {
	return &StreamAnalyzer{
		capacity: capacity,
		data:     make([]float64, capacity),
	}
}

// Ingest adds a new data point to the stream and maintains the sliding window.
func (sa *StreamAnalyzer) Ingest(value float64) {
	sa.mu.Lock()
	defer sa.mu.Unlock()

	if sa.count < sa.capacity {
		sa.data[sa.count] = value
		sa.sum += value
		sa.count++
	} else {
		// Replace the oldest element.
		oldVal := sa.data[sa.nextIndex]
		sa.sum = sa.sum - oldVal + value
		sa.data[sa.nextIndex] = value
		sa.nextIndex = (sa.nextIndex + 1) % sa.capacity
	}
}

// Average returns the average of the current sliding window.
// If the window is empty, it returns 0.0.
func (sa *StreamAnalyzer) Average() float64 {
	sa.mu.RLock()
	defer sa.mu.RUnlock()

	if sa.count == 0 {
		return 0.0
	}
	return sa.sum / float64(sa.count)
}

// getSnapshot returns a copy of the current sliding window in the order of ingestion.
func (sa *StreamAnalyzer) getSnapshot() []float64 {
	sa.mu.RLock()
	defer sa.mu.RUnlock()

	if sa.count == 0 {
		return nil
	}
	snapshot := make([]float64, sa.count)
	if sa.count < sa.capacity {
		// Window is not full; copy from the beginning.
		copy(snapshot, sa.data[:sa.count])
		return snapshot
	}

	// Window is full; copy in the correct order starting from nextIndex.
	i := 0
	for j := sa.nextIndex; j < sa.capacity; j++ {
		snapshot[i] = sa.data[j]
		i++
	}
	for j := 0; j < sa.nextIndex; j++ {
		snapshot[i] = sa.data[j]
		i++
	}
	return snapshot
}

// Median computes the median of the current sliding window.
// If the window is empty, it returns 0.0.
func (sa *StreamAnalyzer) Median() float64 {
	snapshot := sa.getSnapshot()
	n := len(snapshot)
	if n == 0 {
		return 0.0
	}

	sort.Float64s(snapshot)
	mid := n / 2
	if n%2 == 1 {
		return snapshot[mid]
	}
	return (snapshot[mid-1] + snapshot[mid]) / 2.0
}

// Percentile computes the p-th percentile of the current sliding window.
// p should be in the range [0.0, 1.0]. Returns an error if p is out of range.
// If the window is empty, it returns 0.0 and no error.
func (sa *StreamAnalyzer) Percentile(p float64) (float64, error) {
	if p < 0.0 || p > 1.0 {
		return 0.0, errors.New("percentile must be between 0.0 and 1.0")
	}

	snapshot := sa.getSnapshot()
	n := len(snapshot)
	if n == 0 {
		return 0.0, nil
	}

	sort.Float64s(snapshot)
	pos := p * float64(n-1)
	index := int(math.Round(pos))
	if index < 0 {
		index = 0
	}
	if index >= n {
		index = n - 1
	}
	return snapshot[index], nil
}