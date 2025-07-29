package network_design

import (
	"container/heap"
)

type Edge struct {
	from   int
	to     int
	weight int
}

type MinHeap []Edge

func (h MinHeap) Len() int           { return len(h) }
func (h MinHeap) Less(i, j int) bool { return h[i].weight < h[j].weight }
func (h MinHeap) Swap(i, j int)      { h[i], h[j] = h[j], h[i] }

func (h *MinHeap) Push(x interface{}) {
	*h = append(*h, x.(Edge))
}

func (h *MinHeap) Pop() interface{} {
	old := *h
	n := len(old)
	x := old[n-1]
	*h = old[0 : n-1]
	return x
}

func MinNetworkCost(n int, cost func(int, int) int) int {
	if n <= 1 {
		return 0
	}

	visited := make([]bool, n)
	minHeap := &MinHeap{}
	heap.Init(minHeap)

	totalCost := 0
	edgesAdded := 0

	visited[0] = true
	for i := 1; i < n; i++ {
		weight := cost(0, i)
		heap.Push(minHeap, Edge{from: 0, to: i, weight: weight})
	}

	for edgesAdded < n-1 && minHeap.Len() > 0 {
		currentEdge := heap.Pop(minHeap).(Edge)

		if visited[currentEdge.to] {
			continue
		}

		visited[currentEdge.to] = true
		totalCost += currentEdge.weight
		edgesAdded++

		for i := 0; i < n; i++ {
			if !visited[i] {
				weight := cost(currentEdge.to, i)
				heap.Push(minHeap, Edge{from: currentEdge.to, to: i, weight: weight})
			}
		}
	}

	if edgesAdded != n-1 {
		return -1
	}

	return totalCost
}