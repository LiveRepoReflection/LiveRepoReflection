package flight_planner

import (
	"container/heap"
	"math"
)

type Flight struct {
	U int
	V int
	C int
	K int
	I int
}

func MinCost(numCities int, flights []Flight, source, dest, passengers int) int {
	graph := make([][]Flight, numCities)
	for _, f := range flights {
		graph[f.U] = append(graph[f.U], f)
	}

	dist := make([]int, numCities)
	for i := 0; i < numCities; i++ {
		dist[i] = math.MaxInt64
	}
	dist[source] = 0

	pq := &PriorityQueue{}
	heap.Init(pq)
	heap.Push(pq, &Node{city: source, cost: 0})

	for pq.Len() > 0 {
		current := heap.Pop(pq).(*Node)
		city := current.city
		currCost := current.cost

		if currCost > dist[city] {
			continue
		}

		if city == dest {
			return currCost
		}

		for _, edge := range graph[city] {
			if edge.K < passengers {
				continue
			}
			edgeCost := edge.C + passengers*edge.I
			newCost := currCost + edgeCost
			if newCost < dist[edge.V] {
				dist[edge.V] = newCost
				heap.Push(pq, &Node{city: edge.V, cost: newCost})
			}
		}
	}
	if dist[dest] == math.MaxInt64 {
		return -1
	}
	return dist[dest]
}

type Node struct {
	city int
	cost int
}

type PriorityQueue []*Node

func (pq PriorityQueue) Len() int { return len(pq) }
func (pq PriorityQueue) Less(i, j int) bool {
	return pq[i].cost < pq[j].cost
}
func (pq PriorityQueue) Swap(i, j int) {
	pq[i], pq[j] = pq[j], pq[i]
}

func (pq *PriorityQueue) Push(x interface{}) {
	*pq = append(*pq, x.(*Node))
}

func (pq *PriorityQueue) Pop() interface{} {
	old := *pq
	n := len(old)
	node := old[n-1]
	*pq = old[0 : n-1]
	return node
}