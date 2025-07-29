package cdn_placement

import (
	"container/heap"
	"math"
	"sort"
)

// OptimalNetworkPlacement determines the optimal placement of content replicas on nodes
// to minimize the average latency for content requests.
//
// Parameters:
// - n: number of nodes in the network
// - edges: list of edges, each represented as [node1, node2, latency]
// - storageCapacity: array where storageCapacity[i] is the storage capacity of node i
// - requestFrequencies: 2D array where requestFrequencies[i][0] is the node requesting content
//   and requestFrequencies[i][1] is the frequency of requests from that node
// - contentSize: size of the content to be replicated
// - maxReplicas: maximum number of content replicas allowed
//
// Returns:
// - A list of node indices where content replicas should be placed
func OptimalNetworkPlacement(n int, edges [][]int, storageCapacity []int, 
                            requestFrequencies [][]int, contentSize int, 
                            maxReplicas int) []int {
	// Filter out nodes with insufficient storage capacity
	eligibleNodes := make([]int, 0, n)
	for i := 0; i < n; i++ {
		if storageCapacity[i] >= contentSize {
			eligibleNodes = append(eligibleNodes, i)
		}
	}

	// If no nodes have sufficient storage, return empty list
	if len(eligibleNodes) == 0 {
		return []int{}
	}

	// Limit maxReplicas to the number of eligible nodes
	if maxReplicas > len(eligibleNodes) {
		maxReplicas = len(eligibleNodes)
	}

	// Build the graph as an adjacency list for shortest path calculations
	graph := buildGraph(n, edges)

	// Create frequency map for easier access
	freqMap := make(map[int]int)
	totalFrequency := 0
	for _, req := range requestFrequencies {
		node, freq := req[0], req[1]
		freqMap[node] = freq
		totalFrequency += freq
	}

	// If n is small enough, we can use brute force to find the optimal placement
	if len(eligibleNodes) <= 20 && maxReplicas <= 5 {
		return bruteForceOptimalPlacement(n, graph, eligibleNodes, freqMap, maxReplicas)
	}

	// Otherwise, use a greedy approximation algorithm
	return greedyOptimalPlacement(n, graph, eligibleNodes, freqMap, maxReplicas)
}

// buildGraph creates an adjacency list representation of the network
func buildGraph(n int, edges [][]int) [][]Edge {
	graph := make([][]Edge, n)
	
	// Initialize the graph with empty adjacency lists
	for i := range graph {
		graph[i] = make([]Edge, 0)
	}

	// Add each edge to the graph (undirected, so add both directions)
	for _, edge := range edges {
		from, to, latency := edge[0], edge[1], edge[2]
		
		// Check if this edge already exists with a different latency
		existingEdgeIdx := -1
		for i, e := range graph[from] {
			if e.To == to {
				existingEdgeIdx = i
				break
			}
		}
		
		// If edge exists and current latency is lower, update it
		if existingEdgeIdx >= 0 {
			if latency < graph[from][existingEdgeIdx].Latency {
				graph[from][existingEdgeIdx].Latency = latency
				
				// Update the reverse edge too
				for i, e := range graph[to] {
					if e.To == from {
						graph[to][i].Latency = latency
						break
					}
				}
			}
		} else {
			// Add new edge in both directions
			graph[from] = append(graph[from], Edge{To: to, Latency: latency})
			graph[to] = append(graph[to], Edge{To: from, Latency: latency})
		}
	}
	
	return graph
}

// Edge represents a connection between two nodes with a latency
type Edge struct {
	To      int
	Latency int
}

// bruteForceOptimalPlacement finds the optimal placement by checking all possible combinations
func bruteForceOptimalPlacement(n int, graph [][]Edge, eligibleNodes []int, 
                              freqMap map[int]int, maxReplicas int) []int {
	best := struct {
		placement []int
		latency   float64
	}{
		placement: []int{},
		latency:   math.MaxFloat64,
	}

	// Helper function to compute combinations
	var generateCombinations func([]int, int, int, []int)
	generateCombinations = func(arr []int, start, size int, current []int) {
		if len(current) == size {
			// Calculate average latency for current placement
			avgLatency := calculateAverageLatencyForPlacement(n, graph, freqMap, current)
			
			// Update best if this placement is better
			if avgLatency < best.latency {
				best.latency = avgLatency
				best.placement = make([]int, len(current))
				copy(best.placement, current)
			}
			return
		}

		// Generate combinations
		for i := start; i < len(arr); i++ {
			current = append(current, arr[i])
			generateCombinations(arr, i+1, size, current)
			current = current[:len(current)-1] // backtrack
		}
	}

	// Try all possible numbers of replicas from 1 to maxReplicas
	for k := 1; k <= maxReplicas; k++ {
		generateCombinations(eligibleNodes, 0, k, []int{})
	}

	return best.placement
}

// greedyOptimalPlacement uses a greedy approach to find a good placement
func greedyOptimalPlacement(n int, graph [][]Edge, eligibleNodes []int, 
                          freqMap map[int]int, maxReplicas int) []int {
	// If only one replica is allowed, find the node that minimizes total weighted distance
	if maxReplicas == 1 {
		bestNode := -1
		minTotalWeightedDist := math.MaxFloat64
		
		for _, node := range eligibleNodes {
			// Calculate all shortest paths from this node
			dist := dijkstra(n, graph, node)
			
			// Calculate total weighted distance
			totalWeightedDist := 0.0
			for requestNode, freq := range freqMap {
				if dist[requestNode] != math.MaxInt64 {
					totalWeightedDist += float64(dist[requestNode]) * float64(freq)
				}
			}
			
			if totalWeightedDist < minTotalWeightedDist {
				minTotalWeightedDist = totalWeightedDist
				bestNode = node
			}
		}
		
		if bestNode != -1 {
			return []int{bestNode}
		}
		return []int{}
	}

	// For multiple replicas, use an incremental greedy approach
	placement := make([]int, 0, maxReplicas)
	
	// Calculate the request demand for each node (sum of frequencies)
	nodeDemand := make([]int, n)
	for node, freq := range freqMap {
		nodeDemand[node] = freq
	}
	
	// Sort eligible nodes by demand in descending order
	sort.Slice(eligibleNodes, func(i, j int) bool {
		return nodeDemand[eligibleNodes[i]] > nodeDemand[eligibleNodes[j]]
	})
	
	// Add high-demand nodes first, up to half of maxReplicas
	initialPlacement := int(math.Ceil(float64(maxReplicas) / 2.0))
	for i := 0; i < initialPlacement && i < len(eligibleNodes); i++ {
		placement = append(placement, eligibleNodes[i])
	}
	
	// Use remaining replicas to minimize latency
	remaining := maxReplicas - len(placement)
	if remaining > 0 {
		candidateNodes := make([]int, 0)
		for _, node := range eligibleNodes {
			// Check if node is already in the placement
			isAlreadyPlaced := false
			for _, placedNode := range placement {
				if placedNode == node {
					isAlreadyPlaced = true
					break
				}
			}
			
			if !isAlreadyPlaced {
				candidateNodes = append(candidateNodes, node)
			}
		}
		
		// Add remaining nodes greedily to minimize latency
		for i := 0; i < remaining && len(candidateNodes) > 0; i++ {
			bestNode := -1
			minLatency := math.MaxFloat64
			
			// Try adding each candidate and calculate the resulting latency
			for _, candidate := range candidateNodes {
				tempPlacement := append(placement, candidate)
				latency := calculateAverageLatencyForPlacement(n, graph, freqMap, tempPlacement)
				
				if latency < minLatency {
					minLatency = latency
					bestNode = candidate
				}
			}
			
			if bestNode != -1 {
				placement = append(placement, bestNode)
				
				// Remove the added node from candidates
				for i, node := range candidateNodes {
					if node == bestNode {
						candidateNodes = append(candidateNodes[:i], candidateNodes[i+1:]...)
						break
					}
				}
			}
		}
	}
	
	return placement
}

// calculateAverageLatencyForPlacement calculates the average latency for all requests
// based on the given placement of content replicas
func calculateAverageLatencyForPlacement(n int, graph [][]Edge, freqMap map[int]int, 
                                       placement []int) float64 {
	// Convert placement to a set for faster lookup
	placementSet := make(map[int]bool)
	for _, node := range placement {
		placementSet[node] = true
	}

	// If any replica is placed on a request node, the latency for that node is 0
	totalLatency := 0.0
	totalFrequency := 0
	
	// For each request node, find the shortest path to any content replica
	for node, freq := range freqMap {
		// If the node itself has a replica, latency is 0
		if placementSet[node] {
			totalFrequency += freq
			continue
		}
		
		// Find shortest path to any replica
		shortestDist := math.MaxInt64
		
		// We could run Dijkstra's once per request node, but it's more efficient
		// to run it once per replica and take the minimum distance
		for replicaNode := range placementSet {
			dist := dijkstra(n, graph, replicaNode)
			if dist[node] < shortestDist {
				shortestDist = dist[node]
			}
		}
		
		// If the node is reachable from any replica
		if shortestDist != math.MaxInt64 {
			totalLatency += float64(shortestDist) * float64(freq)
			totalFrequency += freq
		}
	}
	
	// Avoid division by zero
	if totalFrequency == 0 {
		return 0
	}
	
	return totalLatency / float64(totalFrequency)
}

// dijkstra runs Dijkstra's algorithm to find shortest paths from a source node
func dijkstra(n int, graph [][]Edge, source int) []int {
	// Initialize distances to all nodes as infinity
	dist := make([]int, n)
	for i := range dist {
		dist[i] = math.MaxInt64
	}
	dist[source] = 0

	// Priority queue for Dijkstra's algorithm
	pq := make(PriorityQueue, 0)
	heap.Init(&pq)
	heap.Push(&pq, &Item{node: source, priority: 0})

	// Process nodes in order of increasing distance
	for pq.Len() > 0 {
		item := heap.Pop(&pq).(*Item)
		u := item.node
		
		// If we've found a longer path to this node, skip
		if item.priority > dist[u] {
			continue
		}
		
		// Relax edges from this node
		for _, edge := range graph[u] {
			v := edge.To
			weight := edge.Latency
			
			// If we found a shorter path to v
			if dist[u] != math.MaxInt64 && dist[u]+weight < dist[v] {
				dist[v] = dist[u] + weight
				heap.Push(&pq, &Item{node: v, priority: dist[v]})
			}
		}
	}
	
	return dist
}

// Item is a node with a priority for the priority queue
type Item struct {
	node     int
	priority int
	index    int // Index in the heap
}

// PriorityQueue implements heap.Interface and holds Items
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