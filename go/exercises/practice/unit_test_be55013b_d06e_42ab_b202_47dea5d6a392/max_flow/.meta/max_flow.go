package max_flow

import (
	"errors"
	"math"
)

// Edge represents a directed edge in the network
type Edge struct {
	from     int
	to       int
	capacity int
}

// Internal representation of an edge in the residual graph
type flowEdge struct {
	to        int
	capacity  int
	flow      int
	reverseID int
}

// MaxFlow calculates the maximum flow from source to sink in a flow network
// using the Edmonds-Karp algorithm (Ford-Fulkerson with BFS)
func MaxFlow(n int, edges []Edge, source int, sink int) (int, error) {
	// Validate input
	if n <= 0 {
		return 0, errors.New("number of nodes must be positive")
	}
	if source < 0 || source >= n {
		return 0, errors.New("source node index out of range")
	}
	if sink < 0 || sink >= n {
		return 0, errors.New("sink node index out of range")
	}
	if source == sink {
		return 0, nil // No flow is possible if source and sink are the same
	}

	// Check edges for validity
	for _, edge := range edges {
		if edge.from < 0 || edge.from >= n {
			return 0, errors.New("edge source index out of range")
		}
		if edge.to < 0 || edge.to >= n {
			return 0, errors.New("edge destination index out of range")
		}
		if edge.capacity < 0 {
			return 0, errors.New("edge capacity cannot be negative")
		}
	}

	// Initialize residual graph
	graph := make([][]flowEdge, n)
	
	// Add edges to the residual graph
	for _, edge := range edges {
		// Add the forward edge
		fromID := len(graph[edge.from])
		toID := len(graph[edge.to])
		
		graph[edge.from] = append(graph[edge.from], flowEdge{
			to:        edge.to,
			capacity:  edge.capacity,
			flow:      0,
			reverseID: toID,
		})
		
		// Add the reverse edge with zero capacity (for the residual graph)
		graph[edge.to] = append(graph[edge.to], flowEdge{
			to:        edge.from,
			capacity:  0,
			flow:      0,
			reverseID: fromID,
		})
	}
	
	// Implement Edmonds-Karp algorithm
	maxFlow := 0
	
	for {
		// Find an augmenting path using BFS
		parent, bottleneck := bfs(graph, source, sink)
		
		// If no path was found, we're done
		if bottleneck <= 0 {
			break
		}
		
		// Update flow along the path
		maxFlow += bottleneck
		v := sink
		for v != source {
			u := parent[v].node
			edgeID := parent[v].edgeID
			
			// Update forward edge
			graph[u][edgeID].flow += bottleneck
			
			// Update reverse edge
			reverseID := graph[u][edgeID].reverseID
			graph[v][reverseID].flow -= bottleneck
			
			v = u
		}
	}
	
	return maxFlow, nil
}

// parentInfo stores information about the parent node in the BFS path
type parentInfo struct {
	node   int // Parent node
	edgeID int // Edge ID in the parent's adjacency list
}

// bfs performs breadth-first search to find an augmenting path
// returns a map of parent nodes and the bottleneck capacity along the path
func bfs(graph [][]flowEdge, source, sink int) ([]parentInfo, int) {
	n := len(graph)
	visited := make([]bool, n)
	parent := make([]parentInfo, n)
	
	// Initialize all parent entries
	for i := range parent {
		parent[i] = parentInfo{node: -1, edgeID: -1}
	}
	
	// Create a queue for BFS
	queue := make([]int, 0, n)
	queue = append(queue, source)
	visited[source] = true
	
	// Track the bottleneck capacity along the path to each node
	pathCapacity := make([]int, n)
	pathCapacity[source] = math.MaxInt32
	
	// BFS to find augmenting path
	for len(queue) > 0 {
		u := queue[0]
		queue = queue[1:]
		
		// Check all adjacent edges
		for i, edge := range graph[u] {
			v := edge.to
			residualCapacity := edge.capacity - edge.flow
			
			// If there's available capacity and node hasn't been visited
			if residualCapacity > 0 && !visited[v] {
				parent[v] = parentInfo{node: u, edgeID: i}
				pathCapacity[v] = min(pathCapacity[u], residualCapacity)
				visited[v] = true
				queue = append(queue, v)
				
				// If we reached the sink, we're done
				if v == sink {
					return parent, pathCapacity[sink]
				}
			}
		}
	}
	
	// No augmenting path found
	return parent, 0
}

// min returns the minimum of two integers
func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}