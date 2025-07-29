package city_pathing

import (
	"container/heap"
	"errors"
	"math"
)

// PathFinder implementation using Dijkstra's algorithm with priority queue
type PathFinder struct {
	graph *CityGraph
	api   TrafficAPI
}

func (pf *PathFinder) FindPath(start int, destinations []int) ([]int, int, error) {
	if len(destinations) == 0 {
		return nil, 0, errors.New("no destinations provided")
	}

	// Get current traffic signal states
	signals := pf.api.GetSignalStates()

	// Handle single destination case
	if len(destinations) == 1 {
		return pf.findSinglePath(start, destinations[0], signals)
	}

	// For multiple destinations, find optimal sequence
	return pf.findMultiPath(start, destinations, signals)
}

func (pf *PathFinder) findSinglePath(start, end int, signals map[int]string) ([]int, int, error) {
	// Check if nodes exist
	if !pf.graph.HasIntersection(start) || !pf.graph.HasIntersection(end) {
		return nil, 0, errors.New("invalid intersection")
	}

	// Dijkstra's algorithm implementation
	dist := make(map[int]int)
	prev := make(map[int]int)
	pq := make(PriorityQueue, 0)
	heap.Init(&pq)

	// Initialize distances
	for node := range pf.graph.intersections {
		if node == start {
			dist[node] = 0
		} else {
			dist[node] = math.MaxInt32
		}
		heap.Push(&pq, &Item{value: node, priority: dist[node]})
	}

	for pq.Len() > 0 {
		current := heap.Pop(&pq).(*Item).value

		if current == end {
			break
		}

		for neighbor, road := range pf.graph.roads[current] {
			// Calculate travel time considering traffic signals
			travelTime := road.length
			if signal, exists := signals[current]; exists {
				travelTime += getSignalDelay(signal)
			}
			travelTime += road.conditions // Add road condition impact

			if alt := dist[current] + travelTime; alt < dist[neighbor] {
				dist[neighbor] = alt
				prev[neighbor] = current
				pq.updatePriority(neighbor, alt)
			}
		}
	}

	// Reconstruct path
	if dist[end] == math.MaxInt32 {
		return nil, 0, errors.New("no path found")
	}

	path := []int{}
	for at := end; at != 0; at = prev[at] {
		path = append([]int{at}, path...)
	}

	return path, dist[end], nil
}

func (pf *PathFinder) findMultiPath(start int, destinations []int, signals map[int]string) ([]int, int, error) {
	// Simplified approach: visit destinations in order
	// For a complete solution, this would implement TSP with priorities
	totalPath := []int{start}
	totalTime := 0

	current := start
	for _, dest := range destinations {
		path, time, err := pf.findSinglePath(current, dest, signals)
		if err != nil {
			return nil, 0, err
		}

		// Skip the first node (current) to avoid duplication
		totalPath = append(totalPath, path[1:]...)
		totalTime += time
		current = dest
	}

	return totalPath, totalTime, nil
}

func getSignalDelay(signal string) int {
	switch signal {
	case "red":
		return 60 // 60 seconds delay
	case "yellow":
		return 10 // 10 seconds delay
	default:
		return 0
	}
}

// PriorityQueue implementation for Dijkstra's algorithm
type Item struct {
	value    int
	priority int
	index    int
}

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
	item.index = -1
	*pq = old[0 : n-1]
	return item
}

func (pq *PriorityQueue) updatePriority(value int, priority int) {
	for _, item := range *pq {
		if item.value == value {
			item.priority = priority
			heap.Fix(pq, item.index)
			break
		}
	}
}

// CityGraph methods
func (cg *CityGraph) AddIntersection(id int) {
	if cg.intersections == nil {
		cg.intersections = make(map[int]struct{})
	}
	cg.intersections[id] = struct{}{}
}

func (cg *CityGraph) HasIntersection(id int) bool {
	_, exists := cg.intersections[id]
	return exists
}

func (cg *CityGraph) AddRoad(from, to, length int, oneWay bool) {
	if cg.roads == nil {
		cg.roads = make(map[int]map[int]Road)
	}
	if _, exists := cg.roads[from]; !exists {
		cg.roads[from] = make(map[int]Road)
	}
	cg.roads[from][to] = Road{length: length, isOneWay: oneWay}

	if !oneWay {
		if _, exists := cg.roads[to]; !exists {
			cg.roads[to] = make(map[int]Road)
		}
		cg.roads[to][from] = Road{length: length, isOneWay: oneWay}
	}
}

func (cg *CityGraph) UpdateRoadCondition(from, to, condition int) {
	if road, exists := cg.roads[from][to]; exists {
		road.conditions = condition
		cg.roads[from][to] = road
	}
	if road, exists := cg.roads[to][from]; exists {
		road.conditions = condition
		cg.roads[to][from] = road
	}
}