package networkrouter

import (
	"container/heap"
	"math"
)

type Node struct {
	ID int
}

type Edge struct {
	Source      int
	Destination int
	Latency     int
	Bandwidth   int
}

type ContentRequest struct {
	UserID            int
	ContentID         int
	SourceServer      int
	DestinationServer int
	BandwidthRequired int
}

type NetworkGraph struct {
	Nodes []Node
	Edges []Edge
}

// Helper struct to store path information during search
type pathNode struct {
	nodeID    int
	latency   int
	bandwidth int
	path      []int
}

// Priority queue implementation for Dijkstra's algorithm
type priorityQueue []*pathNode

func (pq priorityQueue) Len() int           { return len(pq) }
func (pq priorityQueue) Less(i, j int) bool { return pq[i].latency < pq[j].latency }
func (pq priorityQueue) Swap(i, j int)      { pq[i], pq[j] = pq[j], pq[i] }
func (pq *priorityQueue) Push(x interface{}) { *pq = append(*pq, x.(*pathNode)) }
func (pq *priorityQueue) Pop() interface{} {
	old := *pq
	n := len(old)
	item := old[n-1]
	*pq = old[0 : n-1]
	return item
}

// findPath finds the optimal path considering bandwidth constraints
func findPath(graph NetworkGraph, start, end int, requiredBandwidth int, usedBandwidth map[string]int) ([]int, bool) {
	// Initialize distances
	distances := make(map[int]int)
	paths := make(map[int][]int)
	pq := &priorityQueue{}
	heap.Init(pq)

	// Initialize start node
	heap.Push(pq, &pathNode{
		nodeID:    start,
		latency:   0,
		bandwidth: math.MaxInt32,
		path:      []int{start},
	})
	distances[start] = 0

	// Create adjacency list for faster lookup
	adjList := make(map[int][]Edge)
	for _, edge := range graph.Edges {
		adjList[edge.Source] = append(adjList[edge.Source], edge)
	}

	for pq.Len() > 0 {
		current := heap.Pop(pq).(*pathNode)

		if current.nodeID == end {
			return current.path, true
		}

		// Skip if we've found a better path already
		if current.latency > distances[current.nodeID] {
			continue
		}

		// Process neighbors
		for _, edge := range adjList[current.nodeID] {
			remainingBandwidth := edge.Bandwidth - usedBandwidth[getEdgeKey(edge.Source, edge.Destination)]
			if remainingBandwidth < requiredBandwidth {
				continue
			}

			newLatency := current.latency + edge.Latency
			if dist, exists := distances[edge.Destination]; !exists || newLatency < dist {
				distances[edge.Destination] = newLatency
				newPath := make([]int, len(current.path))
				copy(newPath, current.path)
				newPath = append(newPath, edge.Destination)
				paths[edge.Destination] = newPath

				heap.Push(pq, &pathNode{
					nodeID:    edge.Destination,
					latency:   newLatency,
					bandwidth: min(current.bandwidth, remainingBandwidth),
					path:      newPath,
				})
			}
		}
	}

	return nil, false
}

func getEdgeKey(src, dst int) string {
	return string(rune(src)) + "-" + string(rune(dst))
}

func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}

// OptimizeNetwork implements the main network optimization logic
func OptimizeNetwork(networkGraph NetworkGraph, requests []ContentRequest) (map[int][]int, []int) {
	routedRequests := make(map[int][]int)
	rejectedRequests := []int{}
	usedBandwidth := make(map[string]int)

	// Sort requests by bandwidth required (larger requests first)
	sortedRequests := make([]ContentRequest, len(requests))
	copy(sortedRequests, requests)
	for i := 0; i < len(sortedRequests)-1; i++ {
		for j := i + 1; j < len(sortedRequests); j++ {
			if sortedRequests[i].BandwidthRequired < sortedRequests[j].BandwidthRequired {
				sortedRequests[i], sortedRequests[j] = sortedRequests[j], sortedRequests[i]
			}
		}
	}

	// Process each request
	for _, request := range sortedRequests {
		path, found := findPath(networkGraph, request.SourceServer, request.DestinationServer,
			request.BandwidthRequired, usedBandwidth)

		if !found {
			rejectedRequests = append(rejectedRequests, request.UserID)
			continue
		}

		// Update bandwidth usage for the path
		for i := 0; i < len(path)-1; i++ {
			edgeKey := getEdgeKey(path[i], path[i+1])
			usedBandwidth[edgeKey] += request.BandwidthRequired
		}

		routedRequests[request.UserID] = path
	}

	return routedRequests, rejectedRequests
}