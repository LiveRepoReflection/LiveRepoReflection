package network_path

import (
	"container/heap"
	"math"
)

// Global variable for congestion factor.
var congestionFactor float64

// ProcessRequest computes the minimum possible latency from source to destination
// in the given graph with adjusted edge costs due to the current congestionFactor.
// If the minimum latency is within the given deadline, it returns the latency as an integer;
// otherwise, it returns -1.
func ProcessRequest(graph [][]int, request []int) int {
	if len(request) != 3 {
		return -1
	}

	source := request[0]
	destination := request[1]
	deadline := float64(request[2])

	if source == destination {
		if 0 <= deadline {
			return 0
		}
		return -1
	}

	n := len(graph)
	dist := make([]float64, n)
	for i := 0; i < n; i++ {
		dist[i] = math.Inf(1)
	}
	dist[source] = 0

	pq := &PriorityQueue{}
	heap.Init(pq)
	heap.Push(pq, &Item{node: source, cost: 0})

	for pq.Len() > 0 {
		current := heap.Pop(pq).(*Item)
		curNode := current.node
		curCost := current.cost

		// If we reached destination, check against the deadline.
		if curNode == destination {
			if curCost <= deadline {
				return int(curCost)
			}
			return -1
		}

		// Skip this item if a better cost has already been found.
		if curCost > dist[curNode] {
			continue
		}

		// Process each neighbor (neighbors are stored as pairs: [neighbor, cost]).
		neighbors := graph[curNode]
		for i := 0; i < len(neighbors); i += 2 {
			neighbor := neighbors[i]
			edgeCost := float64(neighbors[i+1]) * congestionFactor
			nextCost := curCost + edgeCost
			if nextCost < dist[neighbor] {
				dist[neighbor] = nextCost
				heap.Push(pq, &Item{node: neighbor, cost: nextCost})
			}
		}
	}

	if dist[destination] <= deadline {
		return int(dist[destination])
	}
	return -1
}

// Item represents a node in the priority queue with its current computed cost.
type Item struct {
	node int
	cost float64
}

// PriorityQueue implements heap.Interface and holds Items.
type PriorityQueue []*Item

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
	item := x.(*Item)
	*pq = append(*pq, item)
}

func (pq *PriorityQueue) Pop() interface{} {
	old := *pq
	n := len(old)
	item := old[n-1]
	*pq = old[0 : n-1]
	return item
}