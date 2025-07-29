package intergalacticrouter

import (
	"container/heap"
)

// Custom priority queue implementation for Dijkstra's algorithm
type pathNode struct {
	planet    string
	maxRisk   int
	hops      int
	path      []string
	priority  int // Combined priority based on risk and hops
}

type priorityQueue []*pathNode

func (pq priorityQueue) Len() int { return len(pq) }

func (pq priorityQueue) Less(i, j int) bool {
	// First compare by maxRisk, then by hops if risks are equal
	if pq[i].maxRisk == pq[j].maxRisk {
		return pq[i].hops < pq[j].hops
	}
	return pq[i].maxRisk < pq[j].maxRisk
}

func (pq priorityQueue) Swap(i, j int) {
	pq[i], pq[j] = pq[j], pq[i]
}

func (pq *priorityQueue) Push(x interface{}) {
	item := x.(*pathNode)
	*pq = append(*pq, item)
}

func (pq *priorityQueue) Pop() interface{} {
	old := *pq
	n := len(old)
	item := old[n-1]
	*pq = old[0 : n-1]
	return item
}

func FindSafestRoute(graph map[string]map[string][]int, startPlanet string, endPlanet string, maxHops int) ([]string, int) {
	// Handle special cases
	if startPlanet == endPlanet {
		if maxHops >= 0 {
			return []string{startPlanet}, 0
		}
		return []string{}, -1
	}

	// Verify start and end planets exist in the graph
	if _, exists := graph[startPlanet]; !exists {
		return []string{}, -1
	}
	if _, exists := graph[endPlanet]; !exists {
		return []string{}, -1
	}

	// Initialize priority queue
	pq := make(priorityQueue, 0)
	heap.Init(&pq)

	// Initialize visited map to track visited planets with their risks
	visited := make(map[string]map[int]bool)

	// Add start node to priority queue
	heap.Push(&pq, &pathNode{
		planet:    startPlanet,
		maxRisk:   0,
		hops:      0,
		path:      []string{startPlanet},
		priority:  0,
	})

	for pq.Len() > 0 {
		current := heap.Pop(&pq).(*pathNode)

		// Skip if we've exceeded maxHops
		if current.hops > maxHops {
			continue
		}

		// Check if we've reached the destination
		if current.planet == endPlanet {
			return current.path, current.maxRisk
		}

		// Initialize visited map for current planet if not exists
		if _, exists := visited[current.planet]; !exists {
			visited[current.planet] = make(map[int]bool)
		}

		// Skip if we've visited this planet with a better or equal risk and hops
		if visited[current.planet][current.maxRisk] && current.hops >= maxHops {
			continue
		}
		visited[current.planet][current.maxRisk] = true

		// Explore neighbors
		for nextPlanet, risks := range graph[current.planet] {
			for _, risk := range risks {
				newMaxRisk := risk
				if current.maxRisk > risk {
					newMaxRisk = current.maxRisk
				}

				// Create new path
				newPath := make([]string, len(current.path))
				copy(newPath, current.path)
				newPath = append(newPath, nextPlanet)

				heap.Push(&pq, &pathNode{
					planet:    nextPlanet,
					maxRisk:   newMaxRisk,
					hops:      current.hops + 1,
					path:      newPath,
					priority:  newMaxRisk,
				})
			}
		}
	}

	// No valid path found
	return []string{}, -1
}