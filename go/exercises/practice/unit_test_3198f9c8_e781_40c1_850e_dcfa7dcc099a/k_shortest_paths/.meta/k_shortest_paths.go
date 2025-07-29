package k_shortest_paths

import (
	"container/heap"
	"sort"
)

type Item struct {
	cost int
	node int
}

// PriorityQueue implements a min-heap for Items.
type PriorityQueue []Item

func (pq PriorityQueue) Len() int { 
	return len(pq)
}

func (pq PriorityQueue) Less(i, j int) bool {
	return pq[i].cost < pq[j].cost
}

func (pq PriorityQueue) Swap(i, j int) {
	pq[i], pq[j] = pq[j], pq[i]
}

func (pq *PriorityQueue) Push(x interface{}) {
	*pq = append(*pq, x.(Item))
}

func (pq *PriorityQueue) Pop() interface{} {
	n := len(*pq)
	item := (*pq)[n-1]
	*pq = (*pq)[:n-1]
	return item
}

// KShortestPaths finds the k-shortest paths from start to end in a directed weighted graph.
// The graph is represented as an adjacency list where graph[i] is a slice of [2]int elements,
// with the first element being the destination node and the second element being the edge weight.
func KShortestPaths(n int, graph [][][2]int, start int, end int, k int) []int {
	results := []int{}
	count := make([]int, n)

	pq := &PriorityQueue{}
	heap.Init(pq)
	heap.Push(pq, Item{cost: 0, node: start})

	for pq.Len() > 0 && count[end] < k {
		curr := heap.Pop(pq).(Item)
		count[curr.node]++
		if curr.node == end {
			results = append(results, curr.cost)
		}
		if count[curr.node] > k {
			continue
		}
		for _, edge := range graph[curr.node] {
			nextNode := edge[0]
			edgeWeight := edge[1]
			heap.Push(pq, Item{cost: curr.cost + edgeWeight, node: nextNode})
		}
	}

	sort.Ints(results)
	return results
}