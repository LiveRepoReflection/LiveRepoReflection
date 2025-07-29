package median_tracker

import (
	"container/heap"
	"sync"
)

// minHeap implements a min-heap of integers.
type minHeap []int

func (h minHeap) Len() int           { return len(h) }
func (h minHeap) Less(i, j int) bool { return h[i] < h[j] }
func (h minHeap) Swap(i, j int)      { h[i], h[j] = h[j], h[i] }

func (h *minHeap) Push(x interface{}) {
	*h = append(*h, x.(int))
}

func (h *minHeap) Pop() interface{} {
	old := *h
	n := len(old)
	x := old[n-1]
	*h = old[0 : n-1]
	return x
}

// maxHeap implements a max-heap of integers using the min-heap interface by storing negative values.
type maxHeap []int

func (h maxHeap) Len() int           { return len(h) }
func (h maxHeap) Less(i, j int) bool { return h[i] < h[j] }
func (h maxHeap) Swap(i, j int)      { h[i], h[j] = h[j], h[i] }

func (h *maxHeap) Push(x interface{}) {
	*h = append(*h, x.(int))
}

func (h *maxHeap) Pop() interface{} {
	old := *h
	n := len(old)
	x := old[n-1]
	*h = old[0 : n-1]
	return x
}

// MedianTracker is the interface for tracking the median of a stream of integers.
type MedianTracker interface {
	AddValue(sourceID int, value int)
	GetMedian() float64
}

// medianTracker implements the MedianTracker interface using a max-heap and min-heap.
type medianTracker struct {
	minH minHeap
	maxH maxHeap
	lock sync.Mutex
}

// NewMedianTracker returns a new instance of MedianTracker.
// The numSources parameter is kept for compatibility with the interface and potential extensions.
func NewMedianTracker(numSources int) MedianTracker {
	mt := &medianTracker{
		minH: minHeap{},
		maxH: maxHeap{},
	}
	heap.Init(&mt.minH)
	heap.Init(&mt.maxH)
	return mt
}

// AddValue adds a value from a specific source to the tracker.
// It is safe for concurrent use.
func (mt *medianTracker) AddValue(sourceID int, value int) {
	mt.lock.Lock()
	defer mt.lock.Unlock()

	if mt.maxH.Len() == 0 || value <= -mt.maxH[0] {
		heap.Push(&mt.maxH, -value)
	} else {
		heap.Push(&mt.minH, value)
	}

	// Rebalance the heaps if the sizes differ by more than one.
	if mt.maxH.Len() > mt.minH.Len()+1 {
		v := -heap.Pop(&mt.maxH).(int)
		heap.Push(&mt.minH, v)
	} else if mt.minH.Len() > mt.maxH.Len()+1 {
		v := heap.Pop(&mt.minH).(int)
		heap.Push(&mt.maxH, -v)
	}
}

// GetMedian returns the current median of all values added.
// It is safe for concurrent use.
func (mt *medianTracker) GetMedian() float64 {
	mt.lock.Lock()
	defer mt.lock.Unlock()

	if mt.maxH.Len() == 0 && mt.minH.Len() == 0 {
		return 0.0
	}

	if mt.maxH.Len() == mt.minH.Len() {
		return (float64(-mt.maxH[0]) + float64(mt.minH[0])) / 2.0
	} else if mt.maxH.Len() > mt.minH.Len() {
		return float64(-mt.maxH[0])
	} else {
		return float64(mt.minH[0])
	}
}