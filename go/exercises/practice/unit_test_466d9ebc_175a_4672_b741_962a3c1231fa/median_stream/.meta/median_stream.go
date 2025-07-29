// Package medianstream implements a distributed median calculator for multiple data sources
package medianstream

import (
	"container/heap"
	"sync"
)

// minHeap and maxHeap are implementations of the heap interface
// to efficiently track the median of a stream of integers

type minHeap []int

func (h minHeap) Len() int            { return len(h) }
func (h minHeap) Less(i, j int) bool  { return h[i] < h[j] }
func (h minHeap) Swap(i, j int)       { h[i], h[j] = h[j], h[i] }
func (h *minHeap) Push(x interface{}) { *h = append(*h, x.(int)) }
func (h *minHeap) Pop() interface{} {
	old := *h
	n := len(old)
	x := old[n-1]
	*h = old[0 : n-1]
	return x
}

type maxHeap []int

func (h maxHeap) Len() int            { return len(h) }
func (h maxHeap) Less(i, j int) bool  { return h[i] > h[j] }
func (h maxHeap) Swap(i, j int)       { h[i], h[j] = h[j], h[i] }
func (h *maxHeap) Push(x interface{}) { *h = append(*h, x.(int)) }
func (h *maxHeap) Pop() interface{} {
	old := *h
	n := len(old)
	x := old[n-1]
	*h = old[0 : n-1]
	return x
}

// DistributedMedianStream represents the distributed median calculator system
type DistributedMedianStream struct {
	// lowerHalf is a max heap containing elements smaller than the median
	lowerHalf maxHeap
	// upperHalf is a min heap containing elements larger than the median
	upperHalf minHeap
	// totalCount tracks the total number of elements added
	totalCount int
	// mu protects the heaps and counts during concurrent operations
	mu sync.RWMutex
}

// New creates and returns a new DistributedMedianStream
func New() *DistributedMedianStream {
	return &DistributedMedianStream{
		lowerHalf: make(maxHeap, 0),
		upperHalf: make(minHeap, 0),
	}
}

// AddValue adds a new integer value from a specific source to the stream
// This method is thread-safe and can be called concurrently
func (dms *DistributedMedianStream) AddValue(sourceID string, value int) {
	dms.mu.Lock()
	defer dms.mu.Unlock()

	// Decide which heap to push the value into
	if dms.lowerHalf.Len() == 0 || value <= dms.lowerHalf[0] {
		heap.Push(&dms.lowerHalf, value)
	} else {
		heap.Push(&dms.upperHalf, value)
	}

	// Rebalance the heaps to maintain the invariant:
	// The lowerHalf has either the same number of elements as upperHalf
	// or one more element
	dms.rebalanceHeaps()

	// Increment the total count
	dms.totalCount++
}

// rebalanceHeaps adjusts the heaps to maintain the size invariant
// This method assumes the caller holds the lock
func (dms *DistributedMedianStream) rebalanceHeaps() {
	// If lowerHalf has more than one element more than upperHalf
	if dms.lowerHalf.Len() > dms.upperHalf.Len()+1 {
		// Move the largest element from lowerHalf to upperHalf
		heap.Push(&dms.upperHalf, heap.Pop(&dms.lowerHalf))
	} else if dms.lowerHalf.Len() < dms.upperHalf.Len() {
		// If upperHalf has more elements than lowerHalf
		// Move the smallest element from upperHalf to lowerHalf
		heap.Push(&dms.lowerHalf, heap.Pop(&dms.upperHalf))
	}
}

// GetMedian calculates and returns the current median of all integers received
// If no values have been received yet, returns 0.0
// This method is thread-safe and can be called concurrently
func (dms *DistributedMedianStream) GetMedian() float64 {
	dms.mu.RLock()
	defer dms.mu.RUnlock()

	// If no values, return 0.0
	if dms.totalCount == 0 {
		return 0.0
	}

	// If the number of elements is odd, the median is the top element of lowerHalf
	if dms.lowerHalf.Len() > dms.upperHalf.Len() {
		return float64(dms.lowerHalf[0])
	}

	// If the number of elements is even, the median is the average of
	// the top of lowerHalf and the top of upperHalf
	return (float64(dms.lowerHalf[0]) + float64(dms.upperHalf[0])) / 2.0
}