package microservice_route

import (
	"container/heap"
	"math"
)

// state represents a node in the priority queue with its current cost.
type state struct {
	node int
	cost int
}

// priorityQueue implements heap.Interface and holds states.
type priorityQueue []state

func (pq priorityQueue) Len() int { return len(pq) }

func (pq priorityQueue) Less(i, j int) bool {
	return pq[i].cost < pq[j].cost
}

func (pq priorityQueue) Swap(i, j int) {
	pq[i], pq[j] = pq[j], pq[i]
}

func (pq *priorityQueue) Push(x interface{}) {
	*pq = append(*pq, x.(state))
}

func (pq *priorityQueue) Pop() interface{} {
	old := *pq
	n := len(old)
	item := old[n-1]
	*pq = old[0 : n-1]
	return item
}

// MinCommunicationTime computes the minimum expected communication time from source to destination.
// If there is no route, it returns -1.
func MinCommunicationTime(N int, latency [][]int, K int, source int, destination int) int {
	// Special case: if source is destination, cost is zero.
	if source == destination {
		return 0
	}

	// Initialize distances as infinity.
	dist := make([]int, N)
	for i := 0; i < N; i++ {
		dist[i] = math.MaxInt64
	}
	dist[source] = 0

	// Priority queue with initial state.
	pq := &priorityQueue{}
	heap.Init(pq)
	heap.Push(pq, state{node: source, cost: 0})

	for pq.Len() > 0 {
		curr := heap.Pop(pq).(state)
		// If we reached destination, return cost.
		if curr.node == destination {
			return curr.cost
		}
		// If current cost is greater than recorded, continue.
		if curr.cost > dist[curr.node] {
			continue
		}
		// Explore neighbors.
		for next := 0; next < N; next++ {
			if latency[curr.node][next] == -1 {
				continue
			}
			// Compute additional overhead:
			// If next is destination, no overhead is added.
			// Otherwise, add overhead K because next becomes an intermediate microservice.
			additionalOverhead := 0
			if next != destination {
				additionalOverhead = K
			}
			newCost := curr.cost + latency[curr.node][next] + additionalOverhead
			if newCost < dist[next] {
				dist[next] = newCost
				heap.Push(pq, state{node: next, cost: newCost})
			}
		}
	}

	// If destination unreachable, return -1.
	return -1
}