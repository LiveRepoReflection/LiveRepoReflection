package traffic_optimizer

import (
	"container/heap"
	"math"
)

// RoadSegment represents a directed edge in the graph.
type RoadSegment struct {
	ToNode           int
	BaseTravelTime   float64
	Capacity         int
	CongestionFactor float64
	TrafficVolume    int
}

// VehicleRoute represents a vehicle's journey from a start to an end node.
type VehicleRoute struct {
	StartNode int
	EndNode   int
	Path      []int
}

// item represents a node in the priority queue used in Dijkstra's algorithm.
type item struct {
	node     int
	priority float64
	index    int
}

// priorityQueue implements heap.Interface and holds items.
type priorityQueue []*item

func (pq priorityQueue) Len() int { return len(pq) }

func (pq priorityQueue) Less(i, j int) bool {
	return pq[i].priority < pq[j].priority
}

func (pq priorityQueue) Swap(i, j int) {
	pq[i], pq[j] = pq[j], pq[i]
	pq[i].index = i
	pq[j].index = j
}

func (pq *priorityQueue) Push(x interface{}) {
	n := len(*pq)
	it := x.(*item)
	it.index = n
	*pq = append(*pq, it)
}

func (pq *priorityQueue) Pop() interface{} {
	old := *pq
	n := len(old)
	it := old[n-1]
	old[n-1] = nil
	it.index = -1
	*pq = old[0 : n-1]
	return it
}

// dijkstra computes the shortest path from start to end using current edge costs.
// The cost for an edge is calculated as:
//    cost = BaseTravelTime * (1 + CongestionFactor * ((TrafficVolume+1)/Capacity)^2)
// The function does not update the TrafficVolume.
func dijkstra(graph map[int][]RoadSegment, start, end int) (path []int, totalCost float64) {
	dist := make(map[int]float64)
	prev := make(map[int]int)
	visited := make(map[int]bool)

	// initialize distances to Infinity
	for node := range graph {
		dist[node] = math.Inf(1)
	}
	dist[start] = 0

	pq := &priorityQueue{}
	heap.Init(pq)
	heap.Push(pq, &item{node: start, priority: 0})

	for pq.Len() > 0 {
		currentItem := heap.Pop(pq).(*item)
		u := currentItem.node

		if visited[u] {
			continue
		}
		visited[u] = true

		if u == end {
			break
		}

		// Explore neighbors of u
		for _, seg := range graph[u] {
			v := seg.ToNode
			// Compute cost if one more vehicle is added to this edge (simulate usage)
			edgeCost := seg.BaseTravelTime * (1 + seg.CongestionFactor*math.Pow(float64(seg.TrafficVolume+1)/float64(seg.Capacity), 2))
			alt := dist[u] + edgeCost
			if alt < dist[v] {
				dist[v] = alt
				prev[v] = u
				heap.Push(pq, &item{node: v, priority: alt})
			}
		}
	}

	// if destination is unreachable, return empty path and infinite cost
	if _, ok := dist[end]; !ok || math.IsInf(dist[end], 1) {
		return []int{}, math.Inf(1)
	}

	// Reconstruct path from end to start
	var reversePath []int
	for at := end; ; {
		reversePath = append(reversePath, at)
		if at == start {
			break
		}
		at = prev[at]
	}
	// reverse the path to get the correct order
	for i, j := 0, len(reversePath)-1; i < j; i, j = i+1, j-1 {
		reversePath[i], reversePath[j] = reversePath[j], reversePath[i]
	}

	return reversePath, dist[end]
}

// updateTrafficVolume updates the graph by incrementing the TrafficVolume on the edge from 'from' to 'to'.
func updateTrafficVolume(graph map[int][]RoadSegment, from, to int) {
	segments := graph[from]
	for i := range segments {
		if segments[i].ToNode == to {
			graph[from][i].TrafficVolume++
			return
		}
	}
}

// resetTrafficVolume resets the TrafficVolume of all road segments in the graph to 0.
func resetTrafficVolume(graph map[int][]RoadSegment) {
	for node, segments := range graph {
		for i := range segments {
			graph[node][i].TrafficVolume = 0
		}
	}
}

// OptimizeTrafficFlow iteratively adjusts vehicle routes to minimize overall average commute time.
// It runs for the specified number of iterations and returns the final assignment of vehicle routes
// along with the average commute time.
func OptimizeTrafficFlow(graph map[int][]RoadSegment, vehicleRoutes []VehicleRoute, iterations int) ([]VehicleRoute, float64) {
	var finalRoutes []VehicleRoute
	var avgCommuteTime float64

	// Iteratively compute routes
	for iter := 0; iter < iterations; iter++ {
		// Reset traffic volumes at the beginning of each iteration.
		resetTrafficVolume(graph)
		totalCommuteTime := 0.0
		iterationRoutes := make([]VehicleRoute, len(vehicleRoutes))
		// Process each vehicle sequentially so each sees updated traffic volumes.
		for i, vehicle := range vehicleRoutes {
			path, cost := dijkstra(graph, vehicle.StartNode, vehicle.EndNode)
			// If no path is found, assign an empty route and cost zero.
			if len(path) == 0 {
				iterationRoutes[i] = VehicleRoute{
					StartNode: vehicle.StartNode,
					EndNode:   vehicle.EndNode,
					Path:      []int{},
				}
				continue
			}
			// Update traffic volume along the chosen path.
			for j := 0; j < len(path)-1; j++ {
				updateTrafficVolume(graph, path[j], path[j+1])
			}
			iterationRoutes[i] = VehicleRoute{
				StartNode: vehicle.StartNode,
				EndNode:   vehicle.EndNode,
				Path:      path,
			}
			totalCommuteTime += cost
		}
		avgCommuteTime = totalCommuteTime / float64(len(vehicleRoutes))
		// Save the current iteration's routes as the latest assignment.
		finalRoutes = iterationRoutes
	}
	return finalRoutes, avgCommuteTime
}