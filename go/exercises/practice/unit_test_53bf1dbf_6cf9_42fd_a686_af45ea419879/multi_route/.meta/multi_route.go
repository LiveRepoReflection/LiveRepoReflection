package multi_route

import (
	"container/heap"
	"math"
)

// FindShortestPath finds the shortest path from any of the source nodes to the destination node
// 
// Parameters:
// - N: The total number of nodes in the system (1 <= N <= 100,000)
// - K: The number of source nodes (1 <= K <= N)
// - sources: A slice of K distinct integers representing the IDs of the source nodes
// - destination: An integer representing the ID of the destination node
// - edges: A slice of edges, each represented by [node1, node2, latency]
//
// Returns:
// - The minimum latency required to reach the destination node from any of the sources.
// - If no path exists from any source to the destination, returns -1.
func FindShortestPath(N int, K int, sources []int, destination int, edges [][]int) int {
	// Validate inputs
	if N <= 0 || K <= 0 || K > N || destination < 0 || destination >= N {
		return -1
	}

	// Check if destination is one of the sources
	for _, src := range sources {
		if src < 0 || src >= N {
			return -1 // Source node out of range
		}
		if src == destination {
			return 0 // If destination is a source, distance is 0
		}
	}

	// Build adjacency list representation of the graph
	graph := make([][]edge, N)
	for _, e := range edges {
		if len(e) != 3 || e[0] < 0 || e[0] >= N || e[1] < 0 || e[1] >= N || e[2] < 0 {
			return -1 // Invalid edge
		}
		
		// Skip self-loops
		if e[0] == e[1] {
			continue
		}
		
		// Add bidirectional edges
		graph[e[0]] = append(graph[e[0]], edge{to: e[1], weight: e[2]})
		graph[e[1]] = append(graph[e[1]], edge{to: e[0], weight: e[2]})
	}

	// Use Dijkstra's algorithm with multiple sources
	// By treating all sources as having distance 0 initially
	return dijkstraMultiSource(graph, sources, destination)
}

// edge represents a weighted edge in the graph
type edge struct {
	to     int
	weight int
}

// item is an element in the priority queue
type item struct {
	node     int
	distance int
	index    int // index in the heap
}

// A priorityQueue implements heap.Interface and holds items.
type priorityQueue []*item

func (pq priorityQueue) Len() int { return len(pq) }

func (pq priorityQueue) Less(i, j int) bool {
	return pq[i].distance < pq[j].distance
}

func (pq priorityQueue) Swap(i, j int) {
	pq[i], pq[j] = pq[j], pq[i]
	pq[i].index = i
	pq[j].index = j
}

func (pq *priorityQueue) Push(x interface{}) {
	n := len(*pq)
	item := x.(*item)
	item.index = n
	*pq = append(*pq, item)
}

func (pq *priorityQueue) Pop() interface{} {
	old := *pq
	n := len(old)
	item := old[n-1]
	old[n-1] = nil  // avoid memory leak
	item.index = -1 // for safety
	*pq = old[0 : n-1]
	return item
}

// dijkstraMultiSource implements Dijkstra's algorithm with multiple source nodes
func dijkstraMultiSource(graph [][]edge, sources []int, destination int) int {
	n := len(graph)
	
	// Initialize distances to infinity
	dist := make([]int, n)
	for i := range dist {
		dist[i] = math.MaxInt32
	}
	
	// Create priority queue and initialize with all source nodes
	pq := make(priorityQueue, 0)
	
	// Add all source nodes to priority queue with distance 0
	for _, src := range sources {
		dist[src] = 0
		heap.Push(&pq, &item{node: src, distance: 0})
	}
	
	// Dijkstra's algorithm
	for pq.Len() > 0 {
		u := heap.Pop(&pq).(*item)
		
		// If we've reached the destination, return the distance
		if u.node == destination {
			return u.distance
		}
		
		// If we've already found a better path to this node, skip it
		if u.distance > dist[u.node] {
			continue
		}
		
		// Check all neighbors of u
		for _, e := range graph[u.node] {
			v := e.to
			weight := e.weight
			
			// If we found a better path to v, update its distance
			if newDist := u.distance + weight; newDist < dist[v] {
				dist[v] = newDist
				heap.Push(&pq, &item{node: v, distance: newDist})
			}
		}
	}
	
	// If we've exhausted all reachable nodes and haven't found the destination
	if dist[destination] == math.MaxInt32 {
		return -1 // No path found
	}
	
	return dist[destination]
}