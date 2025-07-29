package optimal_meeting

import (
	"container/heap"
	"math"
)

type Edge struct {
	To     int
	Weight int
}

// minHeapItem represents an item in the priority queue
type minHeapItem struct {
	vertex   int
	distance int
}

// minHeap implements heap.Interface
type minHeap []minHeapItem

func (h minHeap) Len() int           { return len(h) }
func (h minHeap) Less(i, j int) bool { return h[i].distance < h[j].distance }
func (h minHeap) Swap(i, j int)      { h[i], h[j] = h[j], h[i] }

func (h *minHeap) Push(x interface{}) {
	*h = append(*h, x.(minHeapItem))
}

func (h *minHeap) Pop() interface{} {
	old := *h
	n := len(old)
	item := old[n-1]
	*h = old[0 : n-1]
	return item
}

// dijkstra implements Dijkstra's algorithm to find shortest paths from source
func dijkstra(graph map[int][]Edge, source int) map[int]int {
	distances := make(map[int]int)
	for vertex := range graph {
		distances[vertex] = math.MaxInt32
	}
	distances[source] = 0

	pq := &minHeap{{vertex: source, distance: 0}}
	heap.Init(pq)

	for pq.Len() > 0 {
		current := heap.Pop(pq).(minHeapItem)
		vertex := current.vertex
		distance := current.distance

		if distance > distances[vertex] {
			continue
		}

		for _, edge := range graph[vertex] {
			newDist := distance + edge.Weight
			if newDist < distances[edge.To] {
				distances[edge.To] = newDist
				heap.Push(pq, minHeapItem{vertex: edge.To, distance: newDist})
			}
		}
	}

	return distances
}

// isConnected checks if all friends can reach each other in the graph
func isConnected(graph map[int][]Edge, friends []int) bool {
	if len(friends) <= 1 {
		return true
	}

	distances := dijkstra(graph, friends[0])
	for _, friend := range friends[1:] {
		if distances[friend] == math.MaxInt32 {
			return false
		}
	}
	return true
}

func OptimalMeetingPoint(graph map[int][]Edge, friendLocations []int) int {
	if len(graph) == 0 || len(friendLocations) == 0 {
		return -1
	}

	// Check if all friends can reach each other
	if !isConnected(graph, friendLocations) {
		return -1
	}

	// Special case: single friend
	if len(friendLocations) == 1 {
		return friendLocations[0]
	}

	bestLocation := -1
	minMaxDistance := math.MaxInt32

	// Try each vertex as a meeting point
	for vertex := range graph {
		maxDistance := 0
		// Calculate distances from current vertex to all friends
		distances := dijkstra(graph, vertex)

		// Find maximum distance to any friend
		for _, friend := range friendLocations {
			if distances[friend] > maxDistance {
				maxDistance = distances[friend]
			}
		}

		// Update best location if current vertex gives better result
		if maxDistance < minMaxDistance {
			minMaxDistance = maxDistance
			bestLocation = vertex
		}
	}

	return bestLocation
}