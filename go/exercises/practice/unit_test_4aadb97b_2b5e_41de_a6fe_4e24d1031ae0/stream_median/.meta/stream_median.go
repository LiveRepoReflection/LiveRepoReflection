package stream_median

import (
	"container/heap"
)

// MinHeap implements heap.Interface for min heap
type MinHeap []int

func (h MinHeap) Len() int           { return len(h) }
func (h MinHeap) Less(i, j int) bool { return h[i] < h[j] }
func (h MinHeap) Swap(i, j int)      { h[i], h[j] = h[j], h[i] }

func (h *MinHeap) Push(x interface{}) {
	*h = append(*h, x.(int))
}

func (h *MinHeap) Pop() interface{} {
	old := *h
	n := len(old)
	x := old[n-1]
	*h = old[0 : n-1]
	return x
}

// MaxHeap implements heap.Interface for max heap
type MaxHeap []int

func (h MaxHeap) Len() int           { return len(h) }
func (h MaxHeap) Less(i, j int) bool { return h[i] > h[j] }
func (h MaxHeap) Swap(i, j int)      { h[i], h[j] = h[j], h[i] }

func (h *MaxHeap) Push(x interface{}) {
	*h = append(*h, x.(int))
}

func (h *MaxHeap) Pop() interface{} {
	old := *h
	n := len(old)
	x := old[n-1]
	*h = old[0 : n-1]
	return x
}

// StreamMedian maintains two heaps to calculate median
type StreamMedian struct {
	minHeap *MinHeap
	maxHeap *MaxHeap
}

// NewStreamMedian creates a new StreamMedian instance
func NewStreamMedian() *StreamMedian {
	min := &MinHeap{}
	max := &MaxHeap{}
	heap.Init(min)
	heap.Init(max)
	return &StreamMedian{
		minHeap: min,
		maxHeap: max,
	}
}

// ProcessData adds a new number to the data stream
func (sm *StreamMedian) ProcessData(num int) {
	if sm.maxHeap.Len() == 0 || num <= (*sm.maxHeap)[0] {
		heap.Push(sm.maxHeap, num)
	} else {
		heap.Push(sm.minHeap, num)
	}

	// Balance the heaps
	if sm.maxHeap.Len() > sm.minHeap.Len()+1 {
		val := heap.Pop(sm.maxHeap)
		heap.Push(sm.minHeap, val)
	} else if sm.minHeap.Len() > sm.maxHeap.Len() {
		val := heap.Pop(sm.minHeap)
		heap.Push(sm.maxHeap, val)
	}
}

// GetMedian returns the current median value
func (sm *StreamMedian) GetMedian() float64 {
	if sm.maxHeap.Len() == 0 {
		return 0.0
	}

	if sm.maxHeap.Len() == sm.minHeap.Len() {
		return float64((*sm.maxHeap)[0]+(*sm.minHeap)[0]) / 2.0
	}
	return float64((*sm.maxHeap)[0])
}