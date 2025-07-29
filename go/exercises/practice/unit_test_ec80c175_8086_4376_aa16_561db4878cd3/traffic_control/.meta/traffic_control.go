package traffic_control

import (
	"container/heap"
	"math"
	"math/rand"
	"time"
)

// SimulatedAnnealing constants
const (
	initialTemperature = 1000.0
	coolingRate        = 0.995
	minTemperature     = 0.1
	iterationsPerTemp  = 20
)

// OptimalTrafficLightControl optimizes traffic light timings to minimize average travel time
//
// Parameters:
// - n: Number of intersections
// - m: Number of roads
// - roads: Array of road connections [u, v, t] where u and v are intersections and t is travel time
// - k: Number of trips
// - trips: Array of trips [start, end]
// - cycleLength: Total duration of a traffic light cycle (green + red)
//
// Returns:
// - schedule: Array of green light durations for each intersection
func OptimalTrafficLightControl(n, m int, roads [][]int, k int, trips [][]int, cycleLength int) []int {
	// Create graph representation
	graph := buildGraph(n, roads)
	
	// Initialize random number generator
	rng := rand.New(rand.NewSource(time.Now().UnixNano()))
	
	// Initialize initial schedule with reasonable values
	bestSchedule := make([]int, n)
	for i := range bestSchedule {
		bestSchedule[i] = cycleLength / 2 // Start with equal green/red times
	}
	
	// Calculate initial cost
	bestCost := evaluateSchedule(bestSchedule, n, graph, trips, cycleLength)
	
	// Initialize simulated annealing parameters
	temperature := initialTemperature
	
	// If we have no trips, there's nothing to optimize
	if k == 0 {
		return bestSchedule
	}
	
	// Store the most used intersections to focus optimization on them
	intersectionUsage := analyzeTrafficDensity(n, graph, trips)
	
	// Run simulated annealing
	for temperature > minTemperature {
		for iter := 0; iter < iterationsPerTemp; iter++ {
			// Create a new candidate solution by modifying the best solution
			candidateSchedule := make([]int, n)
			copy(candidateSchedule, bestSchedule)
			
			// Modify the schedule:
			// Prioritize adjusting more frequently used intersections
			modifiedIntersection := selectIntersectionToModify(n, intersectionUsage, rng)
			
			// Determine how much to change the green time by
			changeAmount := 1 + rng.Intn(5)
			if rng.Float64() < 0.5 {
				changeAmount = -changeAmount
			}
			
			// Apply the change, ensuring it stays within valid bounds
			candidateSchedule[modifiedIntersection] = clamp(
				candidateSchedule[modifiedIntersection]+changeAmount,
				1, cycleLength-1,
			)
			
			// Evaluate the candidate solution
			candidateCost := evaluateSchedule(candidateSchedule, n, graph, trips, cycleLength)
			
			// Determine if we should accept this solution
			if acceptSolution(bestCost, candidateCost, temperature, rng) {
				bestSchedule = candidateSchedule
				bestCost = candidateCost
			}
		}
		
		// Cool down
		temperature *= coolingRate
	}
	
	// Try to further refine the solution with hill climbing
	bestSchedule = localSearch(bestSchedule, n, graph, trips, cycleLength, intersectionUsage)
	
	return bestSchedule
}

// buildGraph converts the edge list representation to an adjacency list
func buildGraph(n int, roads [][]int) [][][]int {
	graph := make([][][]int, n)
	
	// Initialize empty adjacency lists
	for i := 0; i < n; i++ {
		graph[i] = make([][]int, 0)
	}
	
	// Add each road to the graph (bidirectional)
	for _, road := range roads {
		u, v, t := road[0], road[1], road[2]
		graph[u] = append(graph[u], []int{v, t})
		graph[v] = append(graph[v], []int{u, t})
	}
	
	return graph
}

// evaluateSchedule calculates the average travel time for all trips with the given schedule
func evaluateSchedule(schedule []int, n int, graph [][][]int, trips [][]int, cycleLength int) float64 {
	totalTravelTime := 0.0
	
	for _, trip := range trips {
		start, end := trip[0], trip[1]
		travelTime := findShortestPathWithLights(n, graph, start, end, schedule, cycleLength)
		totalTravelTime += travelTime
	}
	
	if len(trips) == 0 {
		return 0
	}
	
	return totalTravelTime / float64(len(trips))
}

// findShortestPathWithLights calculates the shortest path from start to end considering traffic lights
func findShortestPathWithLights(n int, graph [][][]int, start, end int, schedule []int, cycleLength int) float64 {
	// Set up distance array
	dist := make([]float64, n)
	for i := range dist {
		dist[i] = math.Inf(1)
	}
	dist[start] = 0
	
	// Priority queue for Dijkstra's algorithm
	pq := &PriorityQueue{}
	heap.Init(pq)
	heap.Push(pq, &Item{value: start, priority: 0})
	
	// Set to track visited nodes
	visited := make(map[int]bool)
	
	// Dijkstra's algorithm
	for pq.Len() > 0 {
		item := heap.Pop(pq).(*Item)
		u := item.value
		
		// Skip if we've already processed this node
		if visited[u] {
			continue
		}
		visited[u] = true
		
		// If we've reached the destination, we're done
		if u == end {
			break
		}
		
		// Check all neighbors
		for _, edge := range graph[u] {
			v, weight := edge[0], float64(edge[1])
			
			// Calculate waiting time due to traffic lights
			waitTime := 0.0
			
			// Only calculate traffic light wait time if we're not at the destination
			if v != end {
				// Calculate when we arrive at the intersection
				arrivalTime := dist[u] + weight
				
				// Calculate what part of the cycle we're in when we arrive
				cyclePosition := int(arrivalTime) % cycleLength
				greenDuration := schedule[v]
				
				// If we arrive during the red period, calculate waiting time
				if cyclePosition >= greenDuration {
					// Wait for the next green light
					waitTime = float64(cycleLength - cyclePosition + greenDuration)
				}
			}
			
			// Relaxation step
			newDist := dist[u] + weight + waitTime
			if newDist < dist[v] {
				dist[v] = newDist
				heap.Push(pq, &Item{value: v, priority: newDist})
			}
		}
	}
	
	return dist[end]
}

// analyzeTrafficDensity returns a score for each intersection based on how frequently it's used
func analyzeTrafficDensity(n int, graph [][][]int, trips [][]int) []int {
	usage := make([]int, n)
	
	for _, trip := range trips {
		start, end := trip[0], trip[1]
		
		// Use BFS to find shortest path (ignoring traffic lights)
		path := findShortestPath(n, graph, start, end)
		
		// Increment usage counter for each intersection in the path
		for _, intersection := range path {
			usage[intersection]++
		}
	}
	
	return usage
}

// findShortestPath finds the shortest path between start and end using BFS
func findShortestPath(n int, graph [][][]int, start, end int) []int {
	// Queue for BFS
	queue := []int{start}
	
	// Track visited nodes and their previous node
	visited := make([]bool, n)
	visited[start] = true
	prev := make([]int, n)
	for i := range prev {
		prev[i] = -1
	}
	
	// BFS
	for len(queue) > 0 {
		u := queue[0]
		queue = queue[1:]
		
		if u == end {
			break
		}
		
		for _, edge := range graph[u] {
			v := edge[0]
			
			if !visited[v] {
				visited[v] = true
				prev[v] = u
				queue = append(queue, v)
			}
		}
	}
	
	// Reconstruct path
	path := []int{}
	
	// Check if end was reached
	if prev[end] != -1 || start == end {
		// Reconstruct the path from end to start
		for at := end; at != -1; at = prev[at] {
			path = append([]int{at}, path...)
		}
	}
	
	return path
}

// selectIntersectionToModify selects an intersection to modify, favoring more heavily used ones
func selectIntersectionToModify(n int, usage []int, rng *rand.Rand) int {
	// Calculate total usage
	totalUsage := 0
	for _, u := range usage {
		totalUsage += u + 1 // Add 1 to ensure even unused intersections have a chance
	}
	
	// If no usage data or all zeros, select randomly
	if totalUsage == n {
		return rng.Intn(n)
	}
	
	// Select based on weighted probability
	target := rng.Intn(totalUsage)
	cumulative := 0
	
	for i, u := range usage {
		cumulative += u + 1
		if cumulative > target {
			return i
		}
	}
	
	// Fallback (shouldn't happen)
	return rng.Intn(n)
}

// acceptSolution determines if a candidate solution should be accepted
func acceptSolution(currentCost, candidateCost, temperature float64, rng *rand.Rand) bool {
	// Always accept better solutions
	if candidateCost < currentCost {
		return true
	}
	
	// Accept worse solutions with a probability that decreases with temperature
	delta := currentCost - candidateCost
	probability := math.Exp(delta / temperature)
	
	return rng.Float64() < probability
}

// clamp ensures a value stays within the specified range
func clamp(value, min, max int) int {
	if value < min {
		return min
	}
	if value > max {
		return max
	}
	return value
}

// localSearch performs hill climbing to refine the solution
func localSearch(initialSchedule []int, n int, graph [][][]int, trips [][]int, cycleLength int, usage []int) []int {
	bestSchedule := make([]int, n)
	copy(bestSchedule, initialSchedule)
	bestCost := evaluateSchedule(bestSchedule, n, graph, trips, cycleLength)
	
	improved := true
	
	// Continue until no improvement is found
	for improved {
		improved = false
		
		// Try adjusting each intersection
		for i := 0; i < n; i++ {
			// Skip intersections with low usage to save computation
			if usage[i] <= 1 && n > 5 {
				continue
			}
			
			// Try increasing green time
			if bestSchedule[i] < cycleLength-1 {
				candidateSchedule := make([]int, n)
				copy(candidateSchedule, bestSchedule)
				candidateSchedule[i]++
				
				candidateCost := evaluateSchedule(candidateSchedule, n, graph, trips, cycleLength)
				if candidateCost < bestCost {
					bestSchedule = candidateSchedule
					bestCost = candidateCost
					improved = true
					break
				}
			}
			
			// Try decreasing green time
			if bestSchedule[i] > 1 {
				candidateSchedule := make([]int, n)
				copy(candidateSchedule, bestSchedule)
				candidateSchedule[i]--
				
				candidateCost := evaluateSchedule(candidateSchedule, n, graph, trips, cycleLength)
				if candidateCost < bestCost {
					bestSchedule = candidateSchedule
					bestCost = candidateCost
					improved = true
					break
				}
			}
		}
	}
	
	return bestSchedule
}

// Item is an item in a priority queue for Dijkstra's algorithm
type Item struct {
	value    int
	priority float64
	index    int
}

// PriorityQueue implements heap.Interface for use in Dijkstra's algorithm
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