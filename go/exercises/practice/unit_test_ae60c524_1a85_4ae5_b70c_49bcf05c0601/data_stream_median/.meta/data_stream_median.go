package data_stream_median

import (
	"math/rand"
	"sort"
	"sync"
	"time"
)

// LimitedMemoryMedian maintains an approximate median of a data stream using reservoir sampling.
type LimitedMemoryMedian struct {
	capacity  int
	epsilon   float64
	count     int
	reservoir []float64
	mu        sync.Mutex
}

// NewLimitedMemoryMedian initializes the data structure with a maximum capacity and an epsilon.
// capacity: maximum number of values to store in memory.
// epsilon: allowed relative error for the median approximation.
func NewLimitedMemoryMedian(capacity int, epsilon float64) *LimitedMemoryMedian {
	// Seed the random number generator.
	rand.Seed(time.Now().UnixNano())
	return &LimitedMemoryMedian{
		capacity:  capacity,
		epsilon:   epsilon,
		reservoir: make([]float64, 0, capacity),
	}
}

// Add incorporates a new value into the data stream.
// Uses reservoir sampling: if the reservoir is not full, simply append. Otherwise,
// replace an existing element with probability (capacity/total elements seen).
func (l *LimitedMemoryMedian) Add(value float64) {
	l.mu.Lock()
	defer l.mu.Unlock()

	l.count++
	if len(l.reservoir) < l.capacity {
		l.reservoir = append(l.reservoir, value)
	} else {
		// Randomly decide if we should replace an element in the reservoir.
		index := rand.Intn(l.count)
		if index < l.capacity {
			l.reservoir[index] = value
		}
	}
}

// Median returns the approximate median of all the values seen so far.
// The returned value is computed from the reservoir sample. When the total
// number of added elements is less than or equal to the capacity, the median is exact.
func (l *LimitedMemoryMedian) Median() float64 {
	l.mu.Lock()
	defer l.mu.Unlock()

	// Copy reservoir to avoid modifying the underlying data.
	sample := make([]float64, len(l.reservoir))
	copy(sample, l.reservoir)
	sort.Float64s(sample)
	n := len(sample)
	if n == 0 {
		// As per constraint, Median() is only called after at least one Add, so this returns 0 by default.
		return 0
	} else if n%2 == 1 {
		return sample[n/2]
	} else {
		return (sample[(n/2)-1] + sample[n/2]) / 2.0
	}
}