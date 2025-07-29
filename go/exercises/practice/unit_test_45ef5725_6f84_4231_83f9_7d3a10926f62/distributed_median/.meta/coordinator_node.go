package distributed_median

import (
	"container/heap"
	"sort"
)

type CoordinatorNode struct {
	allNumbers []int
}

func NewCoordinatorNode() *CoordinatorNode {
	return &CoordinatorNode{
		allNumbers: make([]int, 0),
	}
}

func (c *CoordinatorNode) ReceiveWorkerBuffer(buffer []int) {
	c.allNumbers = append(c.allNumbers, buffer...)
}

func (c *CoordinatorNode) CalculateMedian() float64 {
	if len(c.allNumbers) == 0 {
		return 0.0
	}

	// For small datasets, use simple sorting
	if len(c.allNumbers) <= 1000 {
		sort.Ints(c.allNumbers)
		return calculateMedianFromSorted(c.allNumbers)
	}

	// For large datasets, use two heaps for more efficient median calculation
	return c.calculateMedianWithHeaps()
}

func (c *CoordinatorNode) calculateMedianWithHeaps() float64 {
	lowerHalf := &MaxHeap{}
	upperHalf := &MinHeap{}
	heap.Init(lowerHalf)
	heap.Init(upperHalf)

	for _, num := range c.allNumbers {
		if lowerHalf.Len() == 0 || num <= (*lowerHalf)[0] {
			heap.Push(lowerHalf, num)
		} else {
			heap.Push(upperHalf, num)
		}

		// Balance the heaps
		if lowerHalf.Len() > upperHalf.Len()+1 {
			heap.Push(upperHalf, heap.Pop(lowerHalf))
		} else if upperHalf.Len() > lowerHalf.Len() {
			heap.Push(lowerHalf, heap.Pop(upperHalf))
		}
	}

	if lowerHalf.Len() == upperHalf.Len() {
		return float64((*lowerHalf)[0]+(*upperHalf)[0]) / 2.0
	}
	return float64((*lowerHalf)[0])
}

func calculateMedianFromSorted(nums []int) float64 {
	n := len(nums)
	if n%2 == 1 {
		return float64(nums[n/2])
	}
	return float64(nums[n/2-1]+nums[n/2]) / 2.0
}

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