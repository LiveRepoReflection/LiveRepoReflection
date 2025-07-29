package optimal_paths

import (
	"container/heap"
)

type Edge struct {
	Dest int
	Cost int
}

type Graph map[int][]Edge

type item struct {
	node  int
	cost  int
	index int
}

type PriorityQueue []*item

func (pq PriorityQueue) Len() int {
	return len(pq)
}

func (pq PriorityQueue) Less(i, j int) bool {
	return pq[i].cost < pq[j].cost
}

func (pq PriorityQueue) Swap(i, j int) {
	pq[i], pq[j] = pq[j], pq[i]
	pq[i].index = i
	pq[j].index = j
}

func (pq *PriorityQueue) Push(x interface{}) {
	n := len(*pq)
	it := x.(*item)
	it.index = n
	*pq = append(*pq, it)
}

func (pq *PriorityQueue) Pop() interface{} {
	old := *pq
	n := len(old)
	it := old[n-1]
	it.index = -1
	*pq = old[0 : n-1]
	return it
}

func FindOptimalPath(graph Graph, startServerID int, endServerID int, unavailableServerIDs []int) ([]int, int) {
	unavailableSet := make(map[int]bool)
	for _, id := range unavailableServerIDs {
		unavailableSet[id] = true
	}

	if unavailableSet[startServerID] || unavailableSet[endServerID] {
		return []int{}, -1
	}

	if startServerID == endServerID {
		return []int{startServerID}, 0
	}

	dist := make(map[int]int)
	prev := make(map[int]int)
	const maxInt = int(^uint(0) >> 1)

	// Initialize distances for nodes present in the graph.
	for node := range graph {
		dist[node] = maxInt
		// Also initialize distances for destination nodes that might not be keys in the graph.
		for _, edge := range graph[node] {
			if _, ok := dist[edge.Dest]; !ok {
				dist[edge.Dest] = maxInt
			}
		}
	}

	dist[startServerID] = 0

	pq := &PriorityQueue{}
	heap.Init(pq)
	heap.Push(pq, &item{
		node: startServerID,
		cost: 0,
	})

	for pq.Len() > 0 {
		current := heap.Pop(pq).(*item)
		if current.node == endServerID {
			break
		}

		// Skip outdated distance entries.
		if current.cost > dist[current.node] {
			continue
		}

		// Process neighbors
		for _, edge := range graph[current.node] {
			if unavailableSet[edge.Dest] {
				continue
			}
			alt := current.cost + edge.Cost
			if alt < dist[edge.Dest] {
				dist[edge.Dest] = alt
				prev[edge.Dest] = current.node
				heap.Push(pq, &item{
					node: edge.Dest,
					cost: alt,
				})
			}
		}
	}

	finalCost, ok := dist[endServerID]
	if !ok || finalCost == maxInt {
		return []int{}, -1
	}

	path := []int{}
	for at := endServerID; ; {
		path = append([]int{at}, path...)
		if at == startServerID {
			break
		}
		atPrev, exists := prev[at]
		if !exists {
			return []int{}, -1
		}
		at = atPrev
	}
	return path, finalCost
}