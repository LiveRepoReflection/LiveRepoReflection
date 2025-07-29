package optimal_cdn

import (
	"container/heap"
	"errors"
	"fmt"
	"math"
)

// OptimalCDNPlacement calculates the optimal placement of CDN servers
// to minimize the total cost of server placement and latency.
func OptimalCDNPlacement(
	n, m, k, p int, // Number of cities, connections, users, maximum servers
	c, t int, // Server placement cost, latency threshold
	connections [][3]int, // Connections between cities with latency
	users [][2]int, // User locations and request rates
	originLatencies []int, // Latencies to the origin server
) (int, error) {
	// Validate input
	if err := validateInput(n, m, k, p, c, t, connections, users, originLatencies); err != nil {
		return 0, err
	}

	// Build the graph as an adjacency list
	graph := buildGraph(n, connections)

	// Calculate the shortest path from each city to every other city
	shortestPaths := calculateAllShortestPaths(n, graph)

	// Calculate the latency cost for each user to each potential server location
	// and to the origin server
	userLatencyCosts := calculateUserLatencyCosts(n, k, t, shortestPaths, users, originLatencies)

	// Find the optimal server placement
	return findOptimalPlacement(n, k, p, c, userLatencyCosts)
}

// validateInput checks if the input parameters are valid
func validateInput(
	n, m, k, p int,
	c, t int,
	connections [][3]int,
	users [][2]int,
	originLatencies []int,
) error {
	if n <= 0 || m < 0 || k < 0 || p < 0 || c <= 0 || t <= 0 {
		return errors.New("invalid input parameters: all parameters must be positive except m, k, p which can be zero")
	}

	if len(originLatencies) != n {
		return errors.New("invalid origin latencies: length does not match number of cities")
	}

	if originLatencies[0] != 0 {
		return errors.New("invalid origin latency: latency from origin to itself must be 0")
	}

	for i, conn := range connections {
		if conn[0] < 0 || conn[0] >= n || conn[1] < 0 || conn[1] >= n {
			return fmt.Errorf("invalid connection %d: city IDs must be between 0 and %d", i, n-1)
		}
		if conn[2] <= 0 {
			return fmt.Errorf("invalid connection %d: latency must be positive", i)
		}
	}

	for i, user := range users {
		if user[0] < 0 || user[0] >= n {
			return fmt.Errorf("invalid user %d: city ID must be between 0 and %d", i, n-1)
		}
		if user[1] <= 0 {
			return fmt.Errorf("invalid user %d: request rate must be positive", i)
		}
	}

	return nil
}

// buildGraph constructs an adjacency list representation of the network
func buildGraph(n int, connections [][3]int) [][]Edge {
	graph := make([][]Edge, n)
	for _, conn := range connections {
		city1, city2, latency := conn[0], conn[1], conn[2]
		// Add both directions since the graph is undirected
		graph[city1] = append(graph[city1], Edge{To: city2, Latency: latency})
		graph[city2] = append(graph[city2], Edge{To: city1, Latency: latency})
	}
	return graph
}

// Edge represents a connection between cities with a latency cost
type Edge struct {
	To      int
	Latency int
}

// calculateAllShortestPaths calculates the shortest path from each city to every other city
func calculateAllShortestPaths(n int, graph [][]Edge) [][]int {
	shortestPaths := make([][]int, n)
	for i := 0; i < n; i++ {
		shortestPaths[i] = dijkstra(n, graph, i)
	}
	return shortestPaths
}

// dijkstra calculates the shortest path from a source city to all other cities
func dijkstra(n int, graph [][]Edge, source int) []int {
	dist := make([]int, n)
	for i := range dist {
		dist[i] = math.MaxInt32
	}
	dist[source] = 0

	pq := make(PriorityQueue, 0)
	heap.Init(&pq)
	heap.Push(&pq, &Item{value: source, priority: 0})

	for pq.Len() > 0 {
		item := heap.Pop(&pq).(*Item)
		u := item.value

		// If the distance is worse than what we already have, skip
		if item.priority > dist[u] {
			continue
		}

		for _, edge := range graph[u] {
			v := edge.To
			latency := edge.Latency
			if alt := dist[u] + latency; alt < dist[v] {
				dist[v] = alt
				heap.Push(&pq, &Item{value: v, priority: alt})
			}
		}
	}

	// If a city is not reachable, we set its distance to -1
	for i := range dist {
		if dist[i] == math.MaxInt32 {
			dist[i] = -1
		}
	}

	return dist
}

// Item is a priority queue item for Dijkstra's algorithm
type Item struct {
	value    int
	priority int
	index    int
}

// PriorityQueue implements heap.Interface and holds Items
type PriorityQueue []*Item

func (pq PriorityQueue) Len() int { return len(pq) }

func (pq PriorityQueue) Less(i, j int) bool {
	return pq[i].priority < pq[j].priority
}

func (pq PriorityQueue) Swap(i, j int) {
	pq[i], pq[j] = pq[j], pq[i]
	pq[i].index = i
	pq[j].index = j
}

func (pq *PriorityQueue) Push(x interface{}) {
	n := len(*pq)
	item := x.(*Item)
	item.index = n
	*pq = append(*pq, item)
}

func (pq *PriorityQueue) Pop() interface{} {
	old := *pq
	n := len(old)
	item := old[n-1]
	old[n-1] = nil  // avoid memory leak
	item.index = -1 // for safety
	*pq = old[0 : n-1]
	return item
}

// calculateUserLatencyCosts calculates the latency cost for each user to each potential server
// and to the origin server, considering the latency threshold
func calculateUserLatencyCosts(
	n, k, t int,
	shortestPaths [][]int,
	users [][2]int,
	originLatencies []int,
) [][]int {
	// For each user, calculate the cost to route their traffic to each potential server
	// or to the origin if the latency exceeds the threshold
	userLatencyCosts := make([][]int, k)
	for i := 0; i < k; i++ {
		userCity, requestRate := users[i][0], users[i][1]
		userLatencyCosts[i] = make([]int, n)

		// Calculate the cost to the origin server (always an option)
		originCost := requestRate * originLatencies[userCity]

		for serverCity := 0; serverCity < n; serverCity++ {
			// Check if there's a path from user to server
			if shortestPaths[userCity][serverCity] == -1 {
				// If no path exists, route to origin
				userLatencyCosts[i][serverCity] = originCost
				continue
			}

			// Calculate latency cost to this server
			latency := shortestPaths[userCity][serverCity]
			if latency > t {
				// If latency exceeds threshold, route to origin
				userLatencyCosts[i][serverCity] = originCost
			} else {
				// Otherwise, use this server
				userLatencyCosts[i][serverCity] = requestRate * latency
			}
		}
	}
	return userLatencyCosts
}

// findOptimalPlacement uses dynamic programming to find the optimal placement of CDN servers
func findOptimalPlacement(n, k, p, c int, userLatencyCosts [][]int) (int, error) {
	// If we can't place any servers, all traffic goes to the origin
	if p == 0 {
		return calculateCostWithNoServers(k, userLatencyCosts), nil
	}

	// Create a bitmap of all possible server placement combinations
	// For each combination, calculate the total cost
	minCost := math.MaxInt32

	// Use a recursive approach with memoization to find the optimal solution
	memo := make(map[int]int) // key is the server bitmap, value is the cost
	minCost = findOptimalRecursive(n, k, p, c, userLatencyCosts, 0, 0, memo)

	return minCost, nil
}

// calculateCostWithNoServers calculates the cost when all traffic goes to the origin
func calculateCostWithNoServers(k int, userLatencyCosts [][]int) int {
	totalCost := 0
	for i := 0; i < k; i++ {
		// Use origin cost (server at city 0)
		totalCost += userLatencyCosts[i][0]
	}
	return totalCost
}

// findOptimalRecursive recursively explores server placement combinations with memoization
func findOptimalRecursive(
	n, k, p, c int,
	userLatencyCosts [][]int,
	serverBitmap int, // bit i is 1 if a server is placed at city i
	serversUsed int,  // number of servers used so far
	memo map[int]int, // memoization table
) int {
	// If we've already computed this state, return the memoized result
	if cost, ok := memo[serverBitmap]; ok {
		return cost
	}

	// Base case: if we've used all servers or tried all cities
	if serversUsed == p {
		// Calculate the cost with the current server placement
		return calculateCostWithServers(n, k, c, userLatencyCosts, serverBitmap, serversUsed)
	}

	// Try all possible placements for the next server
	minCost := math.MaxInt32
	
	// Option 1: Stop placing more servers
	if serversUsed > 0 { // Only if we've placed at least one server
		costWithNoMoreServers := calculateCostWithServers(n, k, c, userLatencyCosts, serverBitmap, serversUsed)
		minCost = costWithNoMoreServers
	}
	
	// Option 2: Place a server in one of the remaining cities
	for city := 0; city < n; city++ {
		// Skip if a server is already placed here
		if (serverBitmap & (1 << city)) != 0 {
			continue
		}
		
		// Place a server at this city
		newBitmap := serverBitmap | (1 << city)
		
		// Recursively calculate cost with this new placement
		cost := findOptimalRecursive(n, k, p, c, userLatencyCosts, newBitmap, serversUsed+1, memo)
		
		// Update min cost
		if cost < minCost {
			minCost = cost
		}
	}
	
	// Memoize and return the result
	memo[serverBitmap] = minCost
	return minCost
}

// calculateCostWithServers calculates the total cost with a given server placement
func calculateCostWithServers(
	n, k, c int,
	userLatencyCosts [][]int,
	serverBitmap int,
	serversUsed int,
) int {
	// Calculate server placement cost
	placementCost := serversUsed * c
	
	// Calculate latency cost
	latencyCost := 0
	
	// For each user, find the nearest server
	for i := 0; i < k; i++ {
		minLatencyCost := math.MaxInt32
		
		// Try each server location
		for city := 0; city < n; city++ {
			// Skip if no server is placed here
			if (serverBitmap & (1 << city)) == 0 {
				continue
			}
			
			// Update minimum latency cost for this user
			if userLatencyCosts[i][city] < minLatencyCost {
				minLatencyCost = userLatencyCosts[i][city]
			}
		}
		
		// If no servers are placed or all servers are unreachable
		if minLatencyCost == math.MaxInt32 {
			// Use origin server (city 0)
			minLatencyCost = userLatencyCosts[i][0]
		}
		
		latencyCost += minLatencyCost
	}
	
	return placementCost + latencyCost
}