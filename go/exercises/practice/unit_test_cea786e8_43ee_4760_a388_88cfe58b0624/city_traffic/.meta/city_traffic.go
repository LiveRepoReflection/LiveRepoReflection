package city_traffic

import (
	"container/heap"
	"math"
)

// Edge represents a road between two intersections with an associated travel cost.
type Edge struct {
	to   int
	cost int
}

// MinTravelTime computes the minimum travel time from the start intersection to the end intersection,
// given a network of roads and the option to install traffic lights at up to maxLights intersections
// (excluding start and end). When both ends of a road have a traffic light installed, the travel time on
// that road is halved (using integer division). Additionally, whenever passing through an intersection that
// has a traffic light installed, an additional waiting time equal to lightCost is incurred.
func MinTravelTime(n int, roads [][]int, lightCost int, start int, end int, maxLights int) int {
	// Build graph as an adjacency list.
	graph := make([][]Edge, n)
	for _, r := range roads {
		u, v, c := r[0], r[1], r[2]
		graph[u] = append(graph[u], Edge{to: v, cost: c})
		graph[v] = append(graph[v], Edge{to: u, cost: c})
	}

	// State: the current node, number of installed traffic lights (used), and whether the current node
	// is equipped (1) or not (0). The equipped flag is used to determine if the outgoing edge can be discounted.
	// Start and end are not allowed to have lights installed.
	// dist[node][used][equipped] is the minimal cost to reach that state.
	maxEquips := maxLights + 1
	dist := make([][][]int, n)
	for i := 0; i < n; i++ {
		dist[i] = make([][]int, maxEquips)
		for j := 0; j < maxEquips; j++ {
			dist[i][j] = []int{math.MaxInt64, math.MaxInt64}
		}
	}

	// Start from the starting intersection; start is never equipped.
	dist[start][0][0] = 0

	// Priority queue for Dijkstra's algorithm.
	pq := &StatePQ{}
	heap.Init(pq)
	heap.Push(pq, State{node: start, used: 0, equipped: 0, cost: 0})

	for pq.Len() > 0 {
		cur := heap.Pop(pq).(State)
		// Skip if we already found a better path to this state.
		if cur.cost > dist[cur.node][cur.used][cur.equipped] {
			continue
		}
		// If we have reached the destination, return the accumulated cost.
		// Destination is not allowed to be equipped.
		if cur.node == end {
			return cur.cost
		}
		// Explore all adjacent roads.
		for _, edge := range graph[cur.node] {
			next := edge.to

			// Option 1: Do not install a traffic light at the next intersection.
			// The travel cost is the full edge cost regardless of the current node's status.
			newCost := cur.cost + edge.cost
			if newCost < dist[next][cur.used][0] {
				dist[next][cur.used][0] = newCost
				heap.Push(pq, State{node: next, used: cur.used, equipped: 0, cost: newCost})
			}

			// Option 2: Install a traffic light at the next intersection,
			// if next is not the start or the end and if we have remaining installations.
			if next != start && next != end && cur.used < maxLights {
				// If current node is equipped, then the road cost is discounted to half.
				travelCost := edge.cost
				if cur.equipped == 1 {
					travelCost = edge.cost / 2
				}
				// Add waiting cost at the intersection once it gets equipped.
				newCost2 := cur.cost + travelCost + lightCost
				if newCost2 < dist[next][cur.used+1][1] {
					dist[next][cur.used+1][1] = newCost2
					heap.Push(pq, State{node: next, used: cur.used + 1, equipped: 1, cost: newCost2})
				}
			}
		}
	}

	// As per problem constraints, at least one path exists.
	return -1
}

// State represents a node in the graph along with the current number of installed traffic lights and
// whether this node itself is equipped with a traffic light.
type State struct {
	node     int // current intersection id
	used     int // number of traffic lights installed so far
	equipped int // 0 if not equipped, 1 if equipped
	cost     int // total cost to reach this state
}

// StatePQ implements a priority queue for States based on their cost.
type StatePQ []State

func (pq StatePQ) Len() int { return len(pq) }
func (pq StatePQ) Less(i, j int) bool {
	return pq[i].cost < pq[j].cost
}
func (pq StatePQ) Swap(i, j int) { pq[i], pq[j] = pq[j], pq[i] }

func (pq *StatePQ) Push(x interface{}) {
	*pq = append(*pq, x.(State))
}

func (pq *StatePQ) Pop() interface{} {
	old := *pq
	n := len(old)
	item := old[n-1]
	*pq = old[0 : n-1]
	return item
}