package dynamicgraph

import (
	"container/heap"
	"math"
)

// DynamicGraph represents a dynamic weighted directed graph with
// operations for adding/removing nodes and edges and finding shortest paths.
type DynamicGraph struct {
	nodes      map[int]bool            // Map to track existing nodes
	outEdges   map[int]map[int]int     // Map from source node to map of (destination node -> weight)
	inEdges    map[int]map[int]struct{} // Map from destination node to set of source nodes (for efficient node removal)
}

// NewDynamicGraph creates a new empty dynamic graph.
func NewDynamicGraph() *DynamicGraph {
	return &DynamicGraph{
		nodes:      make(map[int]bool),
		outEdges:   make(map[int]map[int]int),
		inEdges:    make(map[int]map[int]struct{}),
	}
}

// AddNode adds a new node with the given ID to the graph.
// If the node already exists, the operation is ignored.
func (g *DynamicGraph) AddNode(nodeID int) {
	if !g.nodes[nodeID] {
		g.nodes[nodeID] = true
		g.outEdges[nodeID] = make(map[int]int)
		g.inEdges[nodeID] = make(map[int]struct{})
	}
}

// RemoveNode removes a node with the given ID from the graph.
// All edges connected to this node are also removed.
// If the node doesn't exist, the operation is ignored.
func (g *DynamicGraph) RemoveNode(nodeID int) {
	if !g.nodes[nodeID] {
		return
	}

	// Remove all outgoing edges
	for destID := range g.outEdges[nodeID] {
		delete(g.inEdges[destID], nodeID)
	}
	delete(g.outEdges, nodeID)

	// Remove all incoming edges
	for srcID := range g.inEdges[nodeID] {
		delete(g.outEdges[srcID], nodeID)
	}
	delete(g.inEdges, nodeID)

	// Remove the node itself
	delete(g.nodes, nodeID)
}

// AddEdge adds a directed edge from source to destination with the given weight.
// If the edge already exists, its weight is updated.
// If either node doesn't exist, the operation is ignored.
func (g *DynamicGraph) AddEdge(sourceNodeID, destinationNodeID, weight int) {
	if !g.nodes[sourceNodeID] || !g.nodes[destinationNodeID] {
		return
	}

	g.outEdges[sourceNodeID][destinationNodeID] = weight
	g.inEdges[destinationNodeID][sourceNodeID] = struct{}{}
}

// RemoveEdge removes the directed edge from source to destination.
// If the edge doesn't exist or either node doesn't exist, the operation is ignored.
func (g *DynamicGraph) RemoveEdge(sourceNodeID, destinationNodeID int) {
	if !g.nodes[sourceNodeID] || !g.nodes[destinationNodeID] {
		return
	}

	delete(g.outEdges[sourceNodeID], destinationNodeID)
	delete(g.inEdges[destinationNodeID], sourceNodeID)
}

// ShortestPath calculates the shortest path distance from startNodeID to endNodeID.
// It uses the Bellman-Ford algorithm to handle negative edge weights.
// If no path exists, it returns math.MaxInt.
// If either node doesn't exist, it returns math.MaxInt.
func (g *DynamicGraph) ShortestPath(startNodeID, endNodeID int) int {
	if !g.nodes[startNodeID] || !g.nodes[endNodeID] {
		return math.MaxInt
	}

	// For small graphs or when startNodeID and endNodeID are close,
	// Dijkstra's algorithm tends to be faster
	if g.shouldUseDijkstra(startNodeID, endNodeID) {
		return g.dijkstraShortestPath(startNodeID, endNodeID)
	}
	
	// For larger graphs or when there are negative weights,
	// use Bellman-Ford algorithm
	return g.bellmanFordShortestPath(startNodeID, endNodeID)
}

// shouldUseDijkstra determines whether Dijkstra's algorithm should be used
// based on heuristics like graph size and presence of negative weights
func (g *DynamicGraph) shouldUseDijkstra(startNodeID, endNodeID int) bool {
	// Check if there are any negative weights in the graph
	for _, edges := range g.outEdges {
		for _, weight := range edges {
			if weight < 0 {
				return false // Negative weight found, use Bellman-Ford
			}
		}
	}
	
	return true // No negative weights, Dijkstra is safe to use
}

// dijkstraShortestPath implements Dijkstra's algorithm for finding shortest paths
func (g *DynamicGraph) dijkstraShortestPath(startNodeID, endNodeID int) int {
	// Initialize distance map
	distances := make(map[int]int)
	for nodeID := range g.nodes {
		distances[nodeID] = math.MaxInt
	}
	distances[startNodeID] = 0

	// Initialize priority queue
	pq := make(PriorityQueue, 0)
	heap.Init(&pq)
	heap.Push(&pq, &Item{value: startNodeID, priority: 0})

	// Keep track of visited nodes
	visited := make(map[int]bool)

	// Dijkstra's algorithm
	for pq.Len() > 0 {
		item := heap.Pop(&pq).(*Item)
		nodeID := item.value

		// If we've reached the end node, return the distance
		if nodeID == endNodeID {
			return distances[nodeID]
		}

		// Skip if already visited or if the item is outdated
		if visited[nodeID] || item.priority > distances[nodeID] {
			continue
		}
		visited[nodeID] = true

		// Check all neighbors
		for neighborID, weight := range g.outEdges[nodeID] {
			// Calculate new potential distance
			newDist := distances[nodeID]
			if newDist != math.MaxInt { // Prevent integer overflow
				newDist += weight
			}

			// Update distance if better
			if newDist < distances[neighborID] {
				distances[neighborID] = newDist
				heap.Push(&pq, &Item{value: neighborID, priority: newDist})
			}
		}
	}

	// If we get here, there's no path to endNodeID
	return math.MaxInt
}

// bellmanFordShortestPath implements the Bellman-Ford algorithm for finding shortest paths
// with possible negative edge weights
func (g *DynamicGraph) bellmanFordShortestPath(startNodeID, endNodeID int) int {
	// Initialize distance map
	distances := make(map[int]int)
	for nodeID := range g.nodes {
		distances[nodeID] = math.MaxInt
	}
	distances[startNodeID] = 0

	// Count the number of nodes for iteration limit
	nodeCount := len(g.nodes)

	// Build a list of all edges for easier iteration
	type edge struct {
		from, to, weight int
	}
	edges := make([]edge, 0)
	for from, toMap := range g.outEdges {
		for to, weight := range toMap {
			edges = append(edges, edge{from, to, weight})
		}
	}

	// Bellman-Ford algorithm
	// Relax all edges |V|-1 times
	for i := 0; i < nodeCount-1; i++ {
		updated := false
		for _, e := range edges {
			if distances[e.from] == math.MaxInt {
				continue // Can't relax edges from unreachable nodes
			}
			
			newDist := distances[e.from] + e.weight
			if newDist < distances[e.to] {
				distances[e.to] = newDist
				updated = true
			}
		}
		
		// Early termination if no updates were made in this round
		if !updated {
			break
		}
	}

	// Check for negative weight cycles
	// This is optional given the problem statement says there are no negative cycles
	for _, e := range edges {
		if distances[e.from] != math.MaxInt && 
		   distances[e.from] + e.weight < distances[e.to] {
			// Negative weight cycle detected
			// As per the problem statement, we assume no negative cycles
			// But in a real implementation, you might want to handle this case
		}
	}

	// Return the distance to the end node
	if distances[endNodeID] == math.MaxInt {
		return math.MaxInt // No path found
	}
	return distances[endNodeID]
}

// Item is a node with its priority (distance) for the priority queue
type Item struct {
	value    int // Node ID
	priority int // Distance from start node
	index    int // Index in the heap
}

// PriorityQueue implements heap.Interface and holds Items
type PriorityQueue []*Item

func (pq PriorityQueue) Len() int { return len(pq) }

// Less compares priorities (distances)
// We use less than for a min-heap (smaller distances have higher priority)
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
	old[n-1] = nil  // Avoid memory leak
	item.index = -1 // For safety
	*pq = old[0 : n-1]
	return item
}