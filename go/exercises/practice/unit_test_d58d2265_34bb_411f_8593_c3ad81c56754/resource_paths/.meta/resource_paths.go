package resource_paths

import (
	"container/heap"
	"math"
)

type state struct {
	node int
	cost int
	res  int
}

// statePQ is a priority queue of states ordered by cost.
type statePQ []state

func (pq statePQ) Len() int { return len(pq) }
func (pq statePQ) Less(i, j int) bool {
	return pq[i].cost < pq[j].cost
}
func (pq statePQ) Swap(i, j int) { pq[i], pq[j] = pq[j], pq[i] }

func (pq *statePQ) Push(x interface{}) {
	*pq = append(*pq, x.(state))
}

func (pq *statePQ) Pop() interface{} {
	old := *pq
	n := len(old)
	x := old[n-1]
	*pq = old[0 : n-1]
	return x
}

// ResourcePaths computes the shortest distances from any source to every node
// subject to the constraint that the cumulative resource consumption along the
// path is less than or equal to the capacity of the destination node.
func ResourcePaths(n int, edges [][]int, sources []int, capacity []int) []int {
	// Build the graph: graph[u] contains edges represented as {v, w, c}
	graph := make([][][3]int, n)
	for _, edge := range edges {
		u, v, w, c := edge[0], edge[1], edge[2], edge[3]
		graph[u] = append(graph[u], [3]int{v, w, c})
	}

	// For each node, maintain a frontier of states (cost, res consumed)
	frontier := make([][]state, n)
	// Answer array: store minimal cost from any source to node, initially infinity
	ans := make([]int, n)
	for i := 0; i < n; i++ {
		ans[i] = math.MaxInt64
	}

	pq := &statePQ{}
	heap.Init(pq)

	// Multi-source: push each source state (with cost 0 and resource usage 0)
	for _, s := range sources {
		// Only add if the source satisfies its own resource capacity.
		if 0 <= capacity[s] {
			st := state{node: s, cost: 0, res: 0}
			heap.Push(pq, st)
			frontier[s] = append(frontier[s], st)
			if 0 < ans[s] {
				ans[s] = 0
			}
		}
	}

	// Dijkstra-like multi-criteria search using a priority queue.
	for pq.Len() > 0 {
		cur := heap.Pop(pq).(state)
		// If the cost is already greater than the best recorded answer, we can skip.
		if cur.cost > ans[cur.node] {
			continue
		}

		// Relax all outgoing edges from current node.
		for _, edge := range graph[cur.node] {
			v, w, c := edge[0], edge[1], edge[2]
			newRes := cur.res + c
			if newRes > capacity[v] {
				continue // resource constraint would be violated at node v.
			}
			newCost := cur.cost + w
			newState := state{node: v, cost: newCost, res: newRes}
			// Check if newState is dominated by any existing state in frontier[v].
			dominate := false
			newFrontier := []state{}
			for _, exist := range frontier[v] {
				// If an existing state has cost <= newCost and res <= newRes, newState is dominated.
				if exist.cost <= newCost && exist.res <= newRes {
					dominate = true
					break
				}
				// If newState dominates an existing state, do not include the existing one.
				if newCost <= exist.cost && newRes <= exist.res {
					// Skip adding exist in newFrontier.
					continue
				}
				newFrontier = append(newFrontier, exist)
			}
			if dominate {
				continue
			}
			// Add new state to the frontier.
			newFrontier = append(newFrontier, newState)
			frontier[v] = newFrontier
			// Update answer if this is a better cost.
			if newCost < ans[v] {
				ans[v] = newCost
			}
			heap.Push(pq, newState)
		}
	}

	// Replace math.MaxInt64 with -1 for unreachable nodes.
	for i := 0; i < n; i++ {
		if ans[i] == math.MaxInt64 {
			ans[i] = -1
		}
	}
	return ans
}