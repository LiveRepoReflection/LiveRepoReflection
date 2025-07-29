package network

import (
	"container/heap"
	"math"
)

// Edge represents a directed edge in the network
type Edge struct {
	Destination     int
	MinCapacity     float64
	MaxCapacity     float64
	CurrentCapacity float64
}

// CapacityUpdate represents an update to the capacity of an edge
type CapacityUpdate struct {
	Source      int
	Destination int
	NewCapacity float64
}

// NetworkState represents the current state of the network
type NetworkState struct {
	Graph              map[int][]Edge
	FlowPaths          []Path
	CurrentFlow        map[EdgeID]float64
	TotalFlow          float64
	PathFlows          []float64
	Source             int
	Destination        int
	NumNodes           int
	AdjacencyList      map[int][]EdgeInfo
	ResidualCapacities map[EdgeID]float64
}

// Path represents a path from source to destination
type Path struct {
	Edges    []EdgeID
	Capacity float64
}

// EdgeID uniquely identifies an edge in the graph
type EdgeID struct {
	Source      int
	Destination int
}

// EdgeInfo contains information about an edge
type EdgeInfo struct {
	Destination int
	EdgeID      EdgeID
}

// PriorityQueue implements a priority queue of nodes for Dijkstra's algorithm
type PriorityQueue []*PriorityQueueItem

// PriorityQueueItem represents an item in the priority queue
type PriorityQueueItem struct {
	Node     int
	Priority float64
	Index    int
}

// Implement heap.Interface methods for PriorityQueue
func (pq PriorityQueue) Len() int { return len(pq) }

func (pq PriorityQueue) Less(i, j int) bool {
	return pq[i].Priority > pq[j].Priority // Max heap (for capacity)
}

func (pq PriorityQueue) Swap(i, j int) {
	pq[i], pq[j] = pq[j], pq[i]
	pq[i].Index = i
	pq[j].Index = j
}

func (pq *PriorityQueue) Push(x interface{}) {
	n := len(*pq)
	item := x.(*PriorityQueueItem)
	item.Index = n
	*pq = append(*pq, item)
}

func (pq *PriorityQueue) Pop() interface{} {
	old := *pq
	n := len(old)
	item := old[n-1]
	old[n-1] = nil  // avoid memory leak
	item.Index = -1 // for safety
	*pq = old[0 : n-1]
	return item
}

// CongestionControl implements the network congestion control algorithm
func CongestionControl(numNodes int, graph map[int][]Edge, source int, destination int, updates <-chan CapacityUpdate) float64 {
	// Initialize the network state
	state := initializeNetworkState(numNodes, graph, source, destination)

	// Process capacity updates if any
	if updates != nil {
		select {
		case update := <-updates:
			applyCapacityUpdate(&state, update)
		default:
			// No updates available, continue
		}
	}

	// Find all available paths and their capacities
	findAugmentingPaths(&state)

	// Optimize flow distribution
	optimizeFlowDistribution(&state)

	return state.TotalFlow
}

// initializeNetworkState creates and initializes the network state
func initializeNetworkState(numNodes int, graph map[int][]Edge, source int, destination int) NetworkState {
	state := NetworkState{
		Graph:              make(map[int][]Edge),
		FlowPaths:          []Path{},
		CurrentFlow:        make(map[EdgeID]float64),
		PathFlows:          []float64{},
		Source:             source,
		Destination:        destination,
		NumNodes:           numNodes,
		AdjacencyList:      make(map[int][]EdgeInfo),
		ResidualCapacities: make(map[EdgeID]float64),
	}

	// Deep copy the graph to avoid modifying the original
	for node, edges := range graph {
		state.Graph[node] = make([]Edge, len(edges))
		copy(state.Graph[node], edges)

		// Build adjacency list and initialize residual capacities
		for _, edge := range edges {
			edgeID := EdgeID{Source: node, Destination: edge.Destination}
			state.AdjacencyList[node] = append(state.AdjacencyList[node], EdgeInfo{
				Destination: edge.Destination,
				EdgeID:      edgeID,
			})
			state.ResidualCapacities[edgeID] = edge.CurrentCapacity
		}
	}

	return state
}

// applyCapacityUpdate updates the network state with a new capacity update
func applyCapacityUpdate(state *NetworkState, update CapacityUpdate) {
	// Update the graph with the new capacity
	for i, edge := range state.Graph[update.Source] {
		if edge.Destination == update.Destination {
			state.Graph[update.Source][i].CurrentCapacity = update.NewCapacity
			break
		}
	}

	// Reset flows and update residual capacities
	edgeID := EdgeID{Source: update.Source, Destination: update.Destination}
	state.ResidualCapacities[edgeID] = update.NewCapacity

	// Reset all flows since we need to recompute them
	state.CurrentFlow = make(map[EdgeID]float64)
	state.TotalFlow = 0
	state.FlowPaths = []Path{}
	state.PathFlows = []float64{}
}

// findAugmentingPaths finds all paths from source to destination in the residual network
func findAugmentingPaths(state *NetworkState) {
	// Reset paths and flows
	state.FlowPaths = []Path{}
	state.PathFlows = []float64{}

	// Use a modified Edmonds-Karp algorithm to find multiple paths
	maxPaths := 10 // Limit the number of paths to consider for efficiency
	pathCount := 0

	// Continue finding paths until we can't find any more or we've found enough
	for pathCount < maxPaths {
		path, capacity := findWidestAugmentingPath(state)
		if len(path) == 0 || capacity <= 0 {
			break
		}

		// Add the path to our collection
		state.FlowPaths = append(state.FlowPaths, Path{
			Edges:    path,
			Capacity: capacity,
		})
		state.PathFlows = append(state.PathFlows, 0) // Initialize flow on this path to 0

		// Update residual capacities for this path (subtract capacity from forward edges)
		for _, edgeID := range path {
			state.ResidualCapacities[edgeID] -= capacity
		}

		pathCount++
	}
}

// findWidestAugmentingPath uses Dijkstra's algorithm to find the path with the highest bottleneck capacity
func findWidestAugmentingPath(state *NetworkState) ([]EdgeID, float64) {
	// Initialize data structures
	distances := make(map[int]float64)
	previous := make(map[int]EdgeID)
	visited := make(map[int]bool)

	for i := 0; i < state.NumNodes; i++ {
		distances[i] = 0 // We're finding the path with maximum capacity
	}
	distances[state.Source] = math.Inf(1) // Source has infinite capacity to itself

	// Create priority queue
	pq := make(PriorityQueue, 0)
	heap.Init(&pq)
	heap.Push(&pq, &PriorityQueueItem{
		Node:     state.Source,
		Priority: math.Inf(1),
	})

	// Dijkstra's algorithm
	for pq.Len() > 0 {
		item := heap.Pop(&pq).(*PriorityQueueItem)
		u := item.Node
		priority := item.Priority

		if visited[u] {
			continue
		}
		visited[u] = true

		if u == state.Destination {
			break
		}

		// For each neighbor of u
		edges, exists := state.AdjacencyList[u]
		if !exists {
			continue
		}

		for _, edge := range edges {
			v := edge.Destination
			edgeID := edge.EdgeID

			// Skip if no residual capacity
			if state.ResidualCapacities[edgeID] <= 0 {
				continue
			}

			// Calculate capacity through this edge
			capacity := math.Min(priority, state.ResidualCapacities[edgeID])

			if capacity > distances[v] {
				distances[v] = capacity
				previous[v] = edgeID

				heap.Push(&pq, &PriorityQueueItem{
					Node:     v,
					Priority: capacity,
				})
			}
		}
	}

	// If destination is not reachable
	if _, exists := previous[state.Destination]; !exists {
		return []EdgeID{}, 0
	}

	// Reconstruct the path
	path := []EdgeID{}
	bottleneckCapacity := distances[state.Destination]
	for u := state.Destination; u != state.Source; {
		edgeID := previous[u]
		path = append([]EdgeID{edgeID}, path...) // Prepend to path
		u = edgeID.Source
	}

	return path, bottleneckCapacity
}

// optimizeFlowDistribution optimizes the flow distribution among the available paths
func optimizeFlowDistribution(state *NetworkState) {
	// Reset all flows
	state.CurrentFlow = make(map[EdgeID]float64)
	state.TotalFlow = 0
	for i := range state.PathFlows {
		state.PathFlows[i] = 0
	}

	if len(state.FlowPaths) == 0 {
		return
	}

	// Calculate total available capacity across all paths
	totalCapacity := 0.0
	for _, path := range state.FlowPaths {
		totalCapacity += path.Capacity
	}

	// Distribute flow proportionally to path capacities for fairness
	for i, path := range state.FlowPaths {
		// Calculate proportional flow for this path
		proportionalFlow := path.Capacity / totalCapacity * totalCapacity
		flow := math.Min(path.Capacity, proportionalFlow)
		state.PathFlows[i] = flow

		// Update flows on individual edges
		for _, edgeID := range path.Edges {
			state.CurrentFlow[edgeID] += flow
		}

		state.TotalFlow += flow
	}

	// Verify that we're not exceeding any edge capacity
	edgeFlows := make(map[EdgeID]float64)
	for i, path := range state.FlowPaths {
		pathFlow := state.PathFlows[i]
		for _, edgeID := range path.Edges {
			edgeFlows[edgeID] += pathFlow
		}
	}

	// Check for congestion and adjust if necessary
	for node, edges := range state.Graph {
		for _, edge := range edges {
			edgeID := EdgeID{Source: node, Destination: edge.Destination}
			if edgeFlows[edgeID] > edge.CurrentCapacity {
				// We have congestion, scale down all flows that use this edge
				scalingFactor := edge.CurrentCapacity / edgeFlows[edgeID]
				reduceTotalFlow(state, edgeID, scalingFactor)
			}
		}
	}
}

// reduceTotalFlow reduces flows on all paths that use a congested edge
func reduceTotalFlow(state *NetworkState, congestedEdge EdgeID, scalingFactor float64) {
	// First identify which paths use the congested edge
	affectedPaths := []int{}
	for i, path := range state.FlowPaths {
		for _, edgeID := range path.Edges {
			if edgeID == congestedEdge {
				affectedPaths = append(affectedPaths, i)
				break
			}
		}
	}

	// Reduce flow on affected paths
	for _, pathIndex := range affectedPaths {
		oldFlow := state.PathFlows[pathIndex]
		newFlow := oldFlow * scalingFactor
		flowReduction := oldFlow - newFlow

		// Update path flow
		state.PathFlows[pathIndex] = newFlow

		// Update total flow
		state.TotalFlow -= flowReduction

		// Update flows on individual edges in this path
		for _, edgeID := range state.FlowPaths[pathIndex].Edges {
			state.CurrentFlow[edgeID] -= flowReduction
		}
	}
}