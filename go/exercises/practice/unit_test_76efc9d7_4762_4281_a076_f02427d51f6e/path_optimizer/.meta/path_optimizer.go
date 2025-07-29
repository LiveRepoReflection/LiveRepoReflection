package path_optimizer

import (
	"container/heap"
	"math"
)

// TimeWeight represents the travel time weight available at a given timestamp.
type TimeWeight struct {
	timestamp int // Unix timestamp (seconds since epoch)
	weight    int // Travel time in seconds
}

// Edge represents a directed edge in the graph with a dynamic weight timeline.
type Edge struct {
	to             string
	weightTimeline []TimeWeight
}

// Request represents a delivery request.
type Request struct {
	from      string // Source address
	to        string // Destination address
	startTime int    // Unix timestamp (delivery must start at or after this time)
	deadline  int    // Unix timestamp (delivery must arrive by this time)
}

// Assignment represents an assigned delivery task.
type Assignment struct {
	request     Request
	startTime   int      // Actual start time of the delivery (Unix timestamp)
	arrivalTime int      // Actual arrival time of the delivery (Unix timestamp)
	path        []string // Ordered list of addresses visited on the route (including source and destination)
}

// OptimizeRoutes takes the graph and a slice of Requests, and returns a slice of Assignments.
// For each Request, a dynamic Dijkstra's algorithm is used to calculate the route based on dynamic edge weights.
// If no valid route exists that reaches the destination by its deadline, the request is skipped.
func OptimizeRoutes(graph map[string][]Edge, requests []Request) []Assignment {
	var assignments []Assignment
	for _, req := range requests {
		arrivalTime, path, ok := findDynamicShortestPath(graph, req.from, req.to, req.startTime, req.deadline)
		if ok {
			assignments = append(assignments, Assignment{
				request:     req,
				startTime:   req.startTime,
				arrivalTime: arrivalTime,
				path:        path,
			})
		}
	}
	return assignments
}

// findDynamicShortestPath implements a modified Dijkstra's algorithm that accounts for dynamic edge weights.
// It starts at source at time startTime and finds the earliest arrival time at destination that is <= deadline.
// Returns arrivalTime, the path from source to destination, and a flag indicating success.
func findDynamicShortestPath(graph map[string][]Edge, source, destination string, startTime, deadline int) (int, []string, bool) {
	// Initialize distances map and predecessor map.
	arrivalTimes := make(map[string]int)
	predecessor := make(map[string]string)
	for node := range graph {
		arrivalTimes[node] = math.MaxInt64
	}
	// It's possible that some nodes do not appear as keys; initialize source anyway.
	if _, exists := arrivalTimes[source]; !exists {
		arrivalTimes[source] = math.MaxInt64
	}

	arrivalTimes[source] = startTime

	// Priority queue for state items.
	pq := &priorityQueue{}
	heap.Init(pq)
	heap.Push(pq, &item{
		node:        source,
		arrivalTime: startTime,
	})
	visited := make(map[string]bool)

	for pq.Len() > 0 {
		current := heap.Pop(pq).(*item)
		curNode := current.node
		curTime := current.arrivalTime

		if curTime > arrivalTimes[curNode] {
			continue
		}

		// If we've reached destination and within deadline, we can finish.
		if curNode == destination && curTime <= deadline {
			return curTime, reconstructPath(predecessor, source, destination), true
		}

		// Mark visited for this state.
		visited[curNode] = true

		for _, edge := range graph[curNode] {
			// Calculate effective departure using dynamic edge weight.
			// Check if current time is valid for the edge weight timeline.
			if len(edge.weightTimeline) == 0 {
				// No timeline means impassable.
				continue
			}
			// If the current time is less than the first timestamp in timeline, the edge is impassable.
			if curTime < edge.weightTimeline[0].timestamp {
				continue
			}
			// Find the effective weight from the timeline.
			effectiveWeight := getEffectiveWeight(edge.weightTimeline, curTime)
			// If no effective weight is found, skip.
			if effectiveWeight < 0 {
				continue
			}
			nextTime := curTime + effectiveWeight
			// If nextTime exceeds deadline, no need to proceed along this edge.
			if nextTime > deadline {
				continue
			}
			// Relaxation step.
			if nextTime < arrivalTimes[edge.to] {
				arrivalTimes[edge.to] = nextTime
				predecessor[edge.to] = curNode
				heap.Push(pq, &item{
					node:        edge.to,
					arrivalTime: nextTime,
				})
			}
		}
	}

	// If destination was never reached within deadline.
	if arrivalTimes[destination] == math.MaxInt64 {
		return 0, nil, false
	}

	return arrivalTimes[destination], reconstructPath(predecessor, source, destination), arrivalTimes[destination] <= deadline
}

// getEffectiveWeight returns the travel time weight from the timeline given the departure time.
// It finds the latest timestamp that is less than or equal to time.
// If none exists, it returns -1 indicating that the edge is impassable at that time.
func getEffectiveWeight(timeline []TimeWeight, time int) int {
	low := 0
	high := len(timeline) - 1
	result := -1
	for low <= high {
		mid := (low + high) / 2
		if timeline[mid].timestamp <= time {
			result = timeline[mid].weight
			low = mid + 1
		} else {
			high = mid - 1
		}
	}
	return result
}

// reconstructPath builds the path from source to destination using the predecessor map.
func reconstructPath(predecessor map[string]string, source, destination string) []string {
	var path []string
	current := destination
	for current != source {
		path = append([]string{current}, path...)
		prev, exists := predecessor[current]
		if !exists {
			// If path cannot be reconstructed, return empty path.
			return []string{}
		}
		current = prev
	}
	path = append([]string{source}, path...)
	return path
}

// item represents a node in the priority queue.
type item struct {
	node        string
	arrivalTime int
}

// priorityQueue implements heap.Interface for items based on arrivalTime.
type priorityQueue []*item

func (pq priorityQueue) Len() int { return len(pq) }
func (pq priorityQueue) Less(i, j int) bool {
	return pq[i].arrivalTime < pq[j].arrivalTime
}
func (pq priorityQueue) Swap(i, j int) { pq[i], pq[j] = pq[j], pq[i] }

func (pq *priorityQueue) Push(x interface{}) {
	*pq = append(*pq, x.(*item))
}

func (pq *priorityQueue) Pop() interface{} {
	old := *pq
	n := len(old)
	it := old[n-1]
	*pq = old[0 : n-1]
	return it
}