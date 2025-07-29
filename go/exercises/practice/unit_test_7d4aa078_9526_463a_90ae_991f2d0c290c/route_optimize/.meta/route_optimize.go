package route_optimize

import (
	"container/heap"
	"math"
)

type Edge struct {
	To       int
	Cost     int
	Priority int
}

type Route struct {
	nodes     []int
	totalCost int
	minPrio   int
}

type PriorityQueue []*Route

func (pq PriorityQueue) Len() int { return len(pq) }

func (pq PriorityQueue) Less(i, j int) bool {
	if pq[i].minPrio == pq[j].minPrio {
		if pq[i].totalCost == pq[j].totalCost {
			return len(pq[i].nodes) < len(pq[j].nodes)
		}
		return pq[i].totalCost < pq[j].totalCost
	}
	return pq[i].minPrio > pq[j].minPrio
}

func (pq PriorityQueue) Swap(i, j int) {
	pq[i], pq[j] = pq[j], pq[i]
}

func (pq *PriorityQueue) Push(x interface{}) {
	item := x.(*Route)
	*pq = append(*pq, item)
}

func (pq *PriorityQueue) Pop() interface{} {
	old := *pq
	n := len(old)
	item := old[n-1]
	old[n-1] = nil
	*pq = old[0 : n-1]
	return item
}

func FindOptimalRoute(graph map[int][]Edge, start int, end int, deadline int) []int {
	if start == end {
		return []int{start}
	}

	pq := make(PriorityQueue, 0)
	heap.Init(&pq)

	initialRoute := &Route{
		nodes:     []int{start},
		totalCost: 0,
		minPrio:   math.MaxInt32,
	}
	heap.Push(&pq, initialRoute)

	bestRoute := &Route{}
	found := false

	for pq.Len() > 0 {
		current := heap.Pop(&pq).(*Route)
		lastNode := current.nodes[len(current.nodes)-1]

		if lastNode == end {
			if !found || current.minPrio > bestRoute.minPrio ||
				(current.minPrio == bestRoute.minPrio && current.totalCost < bestRoute.totalCost) ||
				(current.minPrio == bestRoute.minPrio && current.totalCost == bestRoute.totalCost && len(current.nodes) < len(bestRoute.nodes)) {
				bestRoute = current
				found = true
			}
			continue
		}

		for _, edge := range graph[lastNode] {
			newTotalCost := current.totalCost + edge.Cost
			if newTotalCost > deadline {
				continue
			}

			newMinPrio := current.minPrio
			if edge.Priority < newMinPrio {
				newMinPrio = edge.Priority
			}

			newNodes := make([]int, len(current.nodes)+1)
			copy(newNodes, current.nodes)
			newNodes[len(newNodes)-1] = edge.To

			newRoute := &Route{
				nodes:     newNodes,
				totalCost: newTotalCost,
				minPrio:   newMinPrio,
			}

			heap.Push(&pq, newRoute)
		}
	}

	if found {
		return bestRoute.nodes
	}
	return []int{}
}