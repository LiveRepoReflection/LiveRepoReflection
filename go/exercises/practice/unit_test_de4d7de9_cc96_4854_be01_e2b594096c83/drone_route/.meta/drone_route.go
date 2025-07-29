package drone_route

import (
	"container/heap"
	"math"
)

// edge represents a directed edge from one node to another with weight w.
type edge struct {
	to int
	w  int
}

// state represents a node in the search state defined by the current node, remaining battery and total elapsed cost.
type state struct {
	cost  int
	node  int
	fuel  int
	index int // index is needed by heap.Interface but is not used explicitly.
}

// stateHeap implements heap.Interface for state.
type stateHeap []*state

func (h stateHeap) Len() int { return len(h) }
func (h stateHeap) Less(i, j int) bool {
	return h[i].cost < h[j].cost
}
func (h stateHeap) Swap(i, j int) {
	h[i], h[j] = h[j], h[i]
	h[i].index = i
	h[j].index = j
}
func (h *stateHeap) Push(x interface{}) {
	n := len(*h)
	item := x.(*state)
	item.index = n
	*h = append(*h, item)
}
func (h *stateHeap) Pop() interface{} {
	old := *h
	n := len(old)
	item := old[n-1]
	item.index = -1
	*h = old[0 : n-1]
	return item
}

// MinRouteTime finds the minimum time required for a drone to travel from S to D.
// Returns -1 if no valid route exists.
func MinRouteTime(n int, edges [][]int, S int, D int, B int, R int) int {
	// Build graph
	graph := make([][]edge, n)
	for _, e := range edges {
		if len(e) < 3 {
			continue
		}
		u, v, w := e[0], e[1], e[2]
		graph[u] = append(graph[u], edge{to: v, w: w})
	}

	// If start equals destination, no travel needed.
	if S == D {
		return 0
	}

	// Create a 2D slice to record the minimal cost to get to a given node with given fuel remaining.
	// We use n x (B+1) dimensions.
	costs := make([][]int, n)
	for i := 0; i < n; i++ {
		costs[i] = make([]int, B+1)
		for j := 0; j <= B; j++ {
			costs[i][j] = math.MaxInt64
		}
	}
	// Start with full battery at node S.
	costs[S][B] = 0

	// Priority queue for Dijkstra's algorithm.
	pq := &stateHeap{}
	heap.Init(pq)
	heap.Push(pq, &state{
		cost: 0,
		node: S,
		fuel: B,
	})

	// Dijkstra's algorithm state expansion.
	for pq.Len() > 0 {
		cur := heap.Pop(pq).(*state)
		// If we reached destination, return the cost.
		if cur.node == D {
			return cur.cost
		}
		// If we have already found a better route to this state, skip.
		if cur.cost > costs[cur.node][cur.fuel] {
			continue
		}

		// Option 1: Recharge at the current station, if not fully charged.
		if cur.fuel < B {
			newFuel := B
			newCost := cur.cost + R
			// If recharging yields a better cost at node cur.node with full battery, push it.
			if newCost < costs[cur.node][newFuel] {
				costs[cur.node][newFuel] = newCost
				heap.Push(pq, &state{
					cost: newCost,
					node: cur.node,
					fuel: newFuel,
				})
			}
		}

		// Option 2: Take an outgoing edge if there is enough fuel.
		for _, ed := range graph[cur.node] {
			if cur.fuel >= ed.w {
				newFuel := cur.fuel - ed.w
				newCost := cur.cost + ed.w
				// If we find a cheaper way to get to ed.to with newFuel remaining, update.
				if newCost < costs[ed.to][newFuel] {
					costs[ed.to][newFuel] = newCost
					heap.Push(pq, &state{
						cost: newCost,
						node: ed.to,
						fuel: newFuel,
					})
				}
			}
		}
	}

	// Destination unreachable under given constraints.
	return -1
}