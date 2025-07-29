package concurrentmedian

import (
	"container/heap"
	"sync"
)

// MedianCalculator maintains the running median of a stream of numbers
type MedianCalculator struct {
	minHeap *MinHeap // stores the larger half of numbers
	maxHeap *MaxHeap // stores the smaller half of numbers
	mutex   sync.RWMutex
}

// NewMedianCalculator creates a new MedianCalculator
func NewMedianCalculator() *MedianCalculator {
	return &MedianCalculator{
		minHeap: &MinHeap{},
		maxHeap: &MaxHeap{},
	}
}

// Insert adds a new number to the stream
func (mc *MedianCalculator) Insert(num int) {
	mc.mutex.Lock()
	defer mc.mutex.Unlock()

	// Insert into appropriate heap
	if mc.maxHeap.Len() == 0 || num < -mc.maxHeap.Peek() {
		heap.Push(mc.maxHeap, -num)
	} else {
		heap.Push(mc.minHeap, num)
	}

	// Rebalance heaps if necessary
	if mc.maxHeap.Len() > mc.minHeap.Len()+1 {
		heap.Push(mc.minHeap, -heap.Pop(mc.maxHeap).(int))
	} else if mc.minHeap.Len() > mc.maxHeap.Len() {
		heap.Push(mc.maxHeap, -heap.Pop(mc.minHeap).(int))
	}
}

// GetMedian returns the current median of the stream
func (mc *MedianCalculator) GetMedian() float64 {
	mc.mutex.RLock()
	defer mc.mutex.RUnlock()

	if mc.maxHeap.Len() == 0 {
		return 0.0
	}

	if mc.maxHeap.Len() > mc.minHeap.Len() {
		return float64(-mc.maxHeap.Peek())
	}

	return float64(-mc.maxHeap.Peek()+mc.minHeap.Peek()) / 2.0
}

// MinHeap implements a min heap
type MinHeap []int

func (h MinHeap) Len() int           { return len(h) }
func (h MinHeap) Less(i, j int) bool { return h[i] < h[j] }
func (h MinHeap) Swap(i, j int)      { h[i], h[j] = h[j], h[i] }
func (h *MinHeap) Push(x interface{}) { *h = append(*h, x.(int)) }
func (h *MinHeap) Pop() interface{} {
	old := *h
	n := len(old)
	x := old[n-1]
	*h = old[0 : n-1]
	return x
}
func (h *MinHeap) Peek() int {
	if len(*h) == 0 {
		return 0
	}
	return (*h)[0]
}

// MaxHeap implements a max heap (stored as negative values)
type MaxHeap []int

func (h MaxHeap) Len() int           { return len(h) }
func (h MaxHeap) Less(i, j int) bool { return h[i] < h[j] }
func (h MaxHeap) Swap(i, j int)      { h[i], h[j] = h[j], h[i] }
func (h *MaxHeap) Push(x interface{}) { *h = append(*h, x.(int)) }
func (h *MaxHeap) Pop() interface{} {
	old := *h
	n := len(old)
	x := old[n-1]
	*h = old[0 : n-1]
	return x
}
func (h *MaxHeap) Peek() int {
	if len(*h) == 0 {
		return 0
	}
	return (*h)[0]
}