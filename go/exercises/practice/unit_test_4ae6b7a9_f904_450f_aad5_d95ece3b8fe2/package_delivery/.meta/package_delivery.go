package packagedelivery

import (
	"container/heap"
	"fmt"
	"math"
)

// OptimalDeliveryCost calculates the minimum total cost to deliver all packages
// respecting hub capacities and optimizing for total cost
func OptimalDeliveryCost(hubs []Hub, routes []Route, packages []Package) int {
	// Handle edge cases
	if len(packages) == 0 {
		return 0
	}
	if len(hubs) == 0 {
		return 0
	}

	// Build hub map for quick lookups
	hubMap := make(map[int]*HubInfo)
	for _, hub := range hubs {
		hubMap[hub.ID] = &HubInfo{
			ID:             hub.ID,
			Capacity:       hub.Capacity,
			ProcessingCost: hub.ProcessingCost,
			OutgoingRoutes: make(map[int]int),
		}
	}

	// Check if all source and destination hubs exist
	for _, pkg := range packages {
		if _, exists := hubMap[pkg.SourceHubID]; !exists {
			return -1
		}
		if _, exists := hubMap[pkg.DestinationHubID]; !exists {
			return -1
		}
	}

	// Initialize the graph with routes
	for _, route := range routes {
		sourceHub, exists := hubMap[route.SourceHubID]
		if !exists {
			return -1
		}
		if _, exists := hubMap[route.DestinationHubID]; !exists {
			return -1
		}
		sourceHub.OutgoingRoutes[route.DestinationHubID] = route.CostPerPackage
	}

	// Count packages per source hub to check capacity constraints
	packagesPerHub := make(map[int]int)
	for _, pkg := range packages {
		packagesPerHub[pkg.SourceHubID]++
	}

	// Check initial capacity constraints
	for hubID, count := range packagesPerHub {
		if hubMap[hubID].Capacity < count {
			return -1
		}
	}

	// Group packages by source-destination pairs to process them more efficiently
	packageGroups := make(map[string][]Package)
	for _, pkg := range packages {
		key := fmt.Sprintf("%d-%d", pkg.SourceHubID, pkg.DestinationHubID)
		packageGroups[key] = append(packageGroups[key], pkg)
	}

	// Find the shortest path for each package and calculate total cost
	totalCost := 0
	// For each source-destination pair, find the best path and calculate costs
	for _, pkgGroup := range packageGroups {
		if len(pkgGroup) == 0 {
			continue
		}

		pkg := pkgGroup[0]
		numPackages := len(pkgGroup)

		// Packages already at destination just need processing
		if pkg.SourceHubID == pkg.DestinationHubID {
			totalCost += numPackages * hubMap[pkg.SourceHubID].ProcessingCost
			continue
		}

		// Find the best path for this package group
		path, pathCost := findShortestPath(hubMap, pkg.SourceHubID, pkg.DestinationHubID)
		if pathCost == math.MaxInt32 {
			return -1 // No path found
		}

		// Calculate total cost including transportation and processing
		for _, hubID := range path {
			totalCost += numPackages * hubMap[hubID].ProcessingCost
		}
		totalCost += numPackages * pathCost
	}

	return totalCost
}

// HubInfo extends Hub with additional routing information
type HubInfo struct {
	ID             int
	Capacity       int
	ProcessingCost int
	OutgoingRoutes map[int]int // Maps destination hub ID to cost per package
}

// findShortestPath uses Dijkstra's algorithm to find the shortest path and cost
// between source and destination hubs
func findShortestPath(hubMap map[int]*HubInfo, sourceID, destID int) ([]int, int) {
	// Initialize distances to all nodes as infinity
	distances := make(map[int]int)
	prev := make(map[int]int)
	for id := range hubMap {
		distances[id] = math.MaxInt32
	}
	distances[sourceID] = 0

	// Initialize priority queue
	pq := make(PriorityQueue, 0)
	heap.Init(&pq)
	heap.Push(&pq, &Item{
		hubID:    sourceID,
		priority: 0,
	})

	// Track visited nodes to avoid cycles
	visited := make(map[int]bool)

	// Dijkstra's algorithm
	for pq.Len() > 0 {
		current := heap.Pop(&pq).(*Item)
		currentID := current.hubID

		// Skip if already visited or if we've reached the destination
		if visited[currentID] {
			continue
		}
		visited[currentID] = true

		// If we've reached the destination, we can stop
		if currentID == destID {
			break
		}

		// Check all neighbors
		for neighborID, cost := range hubMap[currentID].OutgoingRoutes {
			if !visited[neighborID] {
				newDist := distances[currentID] + cost
				if newDist < distances[neighborID] {
					distances[neighborID] = newDist
					prev[neighborID] = currentID
					heap.Push(&pq, &Item{
						hubID:    neighborID,
						priority: newDist,
					})
				}
			}
		}
	}

	// If destination is unreachable
	if distances[destID] == math.MaxInt32 {
		return nil, math.MaxInt32
	}

	// Reconstruct the path
	path := []int{}
	current := destID
	for current != sourceID {
		path = append([]int{current}, path...)
		current = prev[current]
	}
	path = append([]int{sourceID}, path...)

	return path, distances[destID]
}

// Item is an item in the priority queue for Dijkstra's algorithm
type Item struct {
	hubID    int
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
	old[n-1] = nil
	item.index = -1
	*pq = old[0 : n-1]
	return item
}