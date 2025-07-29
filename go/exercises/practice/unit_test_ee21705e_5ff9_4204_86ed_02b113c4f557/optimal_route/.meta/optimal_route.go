package optimalroute

import (
	"container/heap"
	"math"
)

// RouteResult represents the result of finding an optimal route for a truck
type RouteResult struct {
	TruckID     int
	Route       []int
	TotalCost   float64
	Incomplete  bool
}

// Edge represents a directed edge in the city's road network
type Edge struct {
	To         int
	TravelTime int
	TollCost   int
}

// OptimalRoutePlanner finds the optimal route for each truck
func OptimalRoutePlanner(graphEdges [][4]int, truckRoutes []TruckRoute, maxTravelTime int, timeTollWeight float64) []RouteResult {
	// Create an adjacency list representation of the graph
	graph := make(map[int][]Edge)
	for _, edge := range graphEdges {
		from, to, travelTime, tollCost := edge[0], edge[1], edge[2], edge[3]
		graph[from] = append(graph[from], Edge{To: to, TravelTime: travelTime, TollCost: tollCost})
	}

	results := make([]RouteResult, 0, len(truckRoutes))

	// Process each truck
	for _, truck := range truckRoutes {
		result := processTruck(graph, truck, maxTravelTime, timeTollWeight)
		results = append(results, result)
	}

	return results
}

// processTruck finds the optimal route for a single truck
func processTruck(graph map[int][]Edge, truck TruckRoute, maxTravelTime int, timeTollWeight float64) RouteResult {
	result := RouteResult{
		TruckID: truck.truckID,
	}

	// Edge case: No delivery locations, just return the start depot
	if len(truck.deliveryPoints) == 0 {
		result.Route = []int{truck.startDepot}
		result.TotalCost = 0
		return result
	}

	// Initialize variables for the complete route and total cost
	completeRoute := []int{truck.startDepot}
	totalTravelTime := 0
	totalTollCost := 0

	// Current position starts at the depot
	currentPosition := truck.startDepot

	// Visit each delivery location in order
	for _, destination := range truck.deliveryPoints {
		// Find the shortest path from currentPosition to destination
		path, travelTime, tollCost, reachable := findShortestPath(graph, currentPosition, destination, timeTollWeight)
		
		if !reachable {
			// If any destination is unreachable, mark the route as incomplete
			result.Incomplete = true
			result.TotalCost = math.Inf(1)
			return result
		}

		// Check if adding this path would exceed the maximum travel time
		if totalTravelTime+travelTime > maxTravelTime {
			result.Incomplete = true
			result.TotalCost = math.Inf(1)
			return result
		}

		// Update the running totals
		totalTravelTime += travelTime
		totalTollCost += tollCost

		// Add the path to the complete route, excluding the first node (as it's already in the route)
		if len(path) > 1 {
			completeRoute = append(completeRoute, path[1:]...)
		}

		// Update current position
		currentPosition = destination
	}

	// Calculate the total cost
	totalCost := float64(totalTravelTime) + (timeTollWeight * float64(totalTollCost))

	result.Route = completeRoute
	result.TotalCost = totalCost
	return result
}

// PathNode represents a node in the priority queue for Dijkstra's algorithm
type PathNode struct {
	nodeID    int
	cost      float64
	index     int // Index in the heap
}

// PathPriorityQueue is a min-heap of PathNodes
type PathPriorityQueue []*PathNode

// Required methods for the heap.Interface
func (pq PathPriorityQueue) Len() int { return len(pq) }

func (pq PathPriorityQueue) Less(i, j int) bool {
	return pq[i].cost < pq[j].cost
}

func (pq PathPriorityQueue) Swap(i, j int) {
	pq[i], pq[j] = pq[j], pq[i]
	pq[i].index = i
	pq[j].index = j
}

func (pq *PathPriorityQueue) Push(x interface{}) {
	n := len(*pq)
	node := x.(*PathNode)
	node.index = n
	*pq = append(*pq, node)
}

func (pq *PathPriorityQueue) Pop() interface{} {
	old := *pq
	n := len(old)
	node := old[n-1]
	old[n-1] = nil  // avoid memory leak
	node.index = -1 // for safety
	*pq = old[0 : n-1]
	return node
}

// findShortestPath uses Dijkstra's algorithm to find the shortest path between two nodes
// Returns the path, travel time, toll cost, and a boolean indicating if the destination is reachable
func findShortestPath(graph map[int][]Edge, start, end int, timeTollWeight float64) ([]int, int, int, bool) {
	// Edge case: start and end are the same node
	if start == end {
		return []int{start}, 0, 0, true
	}

	// Initialize distances and previous nodes
	dist := make(map[int]float64)
	prev := make(map[int]int)
	travelTimes := make(map[int]int)
	tollCosts := make(map[int]int)
	
	// Initialize the priority queue
	pq := make(PathPriorityQueue, 0)
	heap.Init(&pq)

	// Push the start node onto the queue
	startNode := &PathNode{
		nodeID: start,
		cost:   0,
	}
	heap.Push(&pq, startNode)
	dist[start] = 0
	travelTimes[start] = 0
	tollCosts[start] = 0

	// Dijkstra's algorithm
	for pq.Len() > 0 {
		// Get the node with the smallest distance
		current := heap.Pop(&pq).(*PathNode)
		currentID := current.nodeID

		// If we've reached the destination, we're done
		if currentID == end {
			break
		}

		// If the current cost is greater than the known distance, skip
		if current.cost > dist[currentID] {
			continue
		}

		// Check all neighbors of the current node
		for _, edge := range graph[currentID] {
			neighborID := edge.To
			
			// Calculate the cost to reach the neighbor
			newTravelTime := travelTimes[currentID] + edge.TravelTime
			newTollCost := tollCosts[currentID] + edge.TollCost
			newCost := float64(newTravelTime) + (timeTollWeight * float64(newTollCost))

			// If this is a better path, update the distance
			if _, exists := dist[neighborID]; !exists || newCost < dist[neighborID] {
				dist[neighborID] = newCost
				prev[neighborID] = currentID
				travelTimes[neighborID] = newTravelTime
				tollCosts[neighborID] = newTollCost

				// Add the neighbor to the priority queue
				neighborNode := &PathNode{
					nodeID: neighborID,
					cost:   newCost,
				}
				heap.Push(&pq, neighborNode)
			}
		}
	}

	// Check if we found a path to the destination
	if _, exists := dist[end]; !exists {
		return nil, 0, 0, false
	}

	// Reconstruct the path
	path := []int{}
	current := end
	for current != start {
		path = append([]int{current}, path...)
		current = prev[current]
	}
	path = append([]int{start}, path...)

	return path, travelTimes[end], tollCosts[end], true
}