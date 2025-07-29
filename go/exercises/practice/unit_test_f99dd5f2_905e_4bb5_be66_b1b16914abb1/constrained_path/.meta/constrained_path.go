package constrained_path

import (
	"container/heap"
	"math"
)

type Edge struct {
	dest   int
	cost   int
	risk   int
}

type NodeState struct {
	node     int
	totalCost int
	totalRisk int
}

type PriorityQueue []*NodeState

func (pq PriorityQueue) Len() int { return len(pq) }

func (pq PriorityQueue) Less(i, j int) bool {
	return pq[i].totalCost < pq[j].totalCost
}

func (pq PriorityQueue) Swap(i, j int) {
	pq[i], pq[j] = pq[j], pq[i]
}

func (pq *PriorityQueue) Push(x interface{}) {
	item := x.(*NodeState)
	*pq = append(*pq, item)
}

func (pq *PriorityQueue) Pop() interface{} {
	old := *pq
	n := len(old)
	item := old[n-1]
	*pq = old[0 : n-1]
	return item
}

func FindConstrainedPath(n int, edges [][]int, start int, destination int, maxRisk int) int {
	// Build adjacency list
	graph := make([][]Edge, n)
	for _, e := range edges {
		src, dest, cost, risk := e[0], e[1], e[2], e[3]
		graph[src] = append(graph[src], Edge{dest, cost, risk})
	}

	// Initialize minCost matrix: minCost[node][risk] = min cost to reach node with exactly risk
	minCost := make([][]int, n)
	for i := range minCost {
		minCost[i] = make([]int, maxRisk+1)
		for j := range minCost[i] {
			minCost[i][j] = math.MaxInt32
		}
	}
	minCost[start][0] = 0

	pq := make(PriorityQueue, 0)
	heap.Push(&pq, &NodeState{node: start, totalCost: 0, totalRisk: 0})

	for pq.Len() > 0 {
		current := heap.Pop(&pq).(*NodeState)

		if current.node == destination {
			return current.totalCost
		}

		if current.totalCost > minCost[current.node][current.totalRisk] {
			continue
		}

		for _, edge := range graph[current.node] {
			newRisk := current.totalRisk + edge.risk
			newCost := current.totalCost + edge.cost

			if newRisk > maxRisk {
				continue
			}

			if newCost < minCost[edge.dest][newRisk] {
				minCost[edge.dest][newRisk] = newCost
				heap.Push(&pq, &NodeState{
					node:      edge.dest,
					totalCost: newCost,
					totalRisk: newRisk,
				})
			}
		}
	}

	// Check if we found any path to destination within risk limit
	minPathCost := math.MaxInt32
	for risk := 0; risk <= maxRisk; risk++ {
		if minCost[destination][risk] < minPathCost {
			minPathCost = minCost[destination][risk]
		}
	}

	if minPathCost != math.MaxInt32 {
		return minPathCost
	}
	return -1
}