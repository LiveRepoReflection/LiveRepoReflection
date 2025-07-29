package path_finder

import (
	"container/heap"
)

type Edge struct {
	to   int
	time int
	cost int
}

type State struct {
	node int
	time int
	cost int
}

type PQ []State

func (pq PQ) Len() int { return len(pq) }
func (pq PQ) Less(i, j int) bool { return pq[i].time < pq[j].time }
func (pq PQ) Swap(i, j int) { pq[i], pq[j] = pq[j], pq[i] }

func (pq *PQ) Push(x interface{}) {
	*pq = append(*pq, x.(State))
}

func (pq *PQ) Pop() interface{} {
	old := *pq
	n := len(old)
	item := old[n-1]
	*pq = old[0 : n-1]
	return item
}

func isDominated(existingStates []State, newState State) bool {
	for _, s := range existingStates {
		if s.cost <= newState.cost && s.time <= newState.time {
			return true
		}
	}
	return false
}

func addState(states []State, newState State) []State {
	filtered := []State{}
	for _, s := range states {
		if !(newState.cost <= s.cost && newState.time <= s.time) {
			filtered = append(filtered, s)
		}
	}
	return append(filtered, newState)
}

// findBestRoutes processes multiple route requests and returns an array of
// shortest travel times that satisfy both the maxTime and maxCost constraints.
// If the route doesn't exist, the corresponding result is -1.
func findBestRoutes(N int, pathways [][4]int, requests [][4]int) []int {
	// Build graph adjacency list.
	graph := make([][]Edge, N)
	for _, p := range pathways {
		u := p[0]
		v := p[1]
		t := p[2]
		c := p[3]
		graph[u] = append(graph[u], Edge{v, t, c})
		graph[v] = append(graph[v], Edge{u, t, c})
	}

	results := make([]int, len(requests))
	
	// Process each request independently.
	for i, req := range requests {
		start := req[0]
		end := req[1]
		maxTime := req[2]
		maxCost := req[3]
		
		if start == end {
			results[i] = 0
			continue
		}
		
		// bestStates[node] stores non-dominated states (time, cost) for that node.
		bestStates := make([][]State, N)
		pq := &PQ{}
		heap.Init(pq)
		initial := State{start, 0, 0}
		heap.Push(pq, initial)
		bestStates[start] = append(bestStates[start], initial)
		
		ans := -1
		for pq.Len() > 0 {
			cur := heap.Pop(pq).(State)
			
			// When destination reached, this is guaranteed minimal travel time due to PQ order.
			if cur.node == end {
				ans = cur.time
				break
			}
			
			// Explore each neighboring edge.
			for _, edge := range graph[cur.node] {
				newTime := cur.time + edge.time
				newCost := cur.cost + edge.cost
				if newTime > maxTime || newCost > maxCost {
					continue
				}
				nextState := State{edge.to, newTime, newCost}
				if isDominated(bestStates[edge.to], nextState) {
					continue
				}
				bestStates[edge.to] = addState(bestStates[edge.to], nextState)
				heap.Push(pq, nextState)
			}
		}
		results[i] = ans
	}
	return results
}