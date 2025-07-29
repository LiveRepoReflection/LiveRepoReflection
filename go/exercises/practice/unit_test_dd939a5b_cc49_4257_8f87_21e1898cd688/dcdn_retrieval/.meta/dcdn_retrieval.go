package dcdn_retrieval

import (
	"container/heap"
	"math"
)

// CalculateMinimumCost computes the minimum total cost for retrieving all file chunks.
// The cost is calculated as the sum of transfer cost and storage cost.
// Transfer cost for each chunk is defined as the shortest distance from the chosen source peer to the initiatingNode.
// Storage cost for a peer is calculated as sqrt(n), where n is the total number of chunks retrieved from that peer.
// If a chunk is available at the initiating node, its cost is 0.
// If any chunk is not available (or no path exists from every candidate peer), the function returns -1.
func CalculateMinimumCost(graph map[string]map[string]int, chunkLocations map[int][]string, initiatingNode string, numChunks int) float64 {
	// Check if initiatingNode is present in the graph.
	_, exists := graph[initiatingNode]
	if !exists {
		return -1.0
	}

	// Compute shortest path distance from every node to the initiatingNode using Dijkstra.
	distances := dijkstra(graph, initiatingNode)

	// Map to count how many chunks have been assigned from each peer (excluding initiatingNode).
	peerChunkCount := make(map[string]int)
	totalCost := 0.0

	// Process each chunk.
	for i := 0; i < numChunks; i++ {
		// Check if chunk i exists in the provided locations.
		locations, ok := chunkLocations[i]
		if !ok || len(locations) == 0 {
			return -1.0
		}

		// If the chunk is available locally, choose local with zero cost.
		foundLocal := false
		for _, peer := range locations {
			if peer == initiatingNode {
				foundLocal = true
				break
			}
		}
		if foundLocal {
			continue
		}

		// For chunks not available locally, select the candidate peer with minimum marginal cost.
		bestMarginalCost := math.MaxFloat64
		bestPeer := ""
		for _, peer := range locations {
			dist, ok := distances[peer]
			// If the peer is unreachable, skip.
			if !ok || math.IsInf(dist, 0) {
				continue
			}
			curCount := float64(peerChunkCount[peer])
			// Marginal storage cost for adding one chunk.
			marginalStorage := math.Sqrt(curCount+1) - math.Sqrt(curCount)
			marginalCost := dist + marginalStorage
			if marginalCost < bestMarginalCost {
				bestMarginalCost = marginalCost
				bestPeer = peer
			}
		}

		// If no candidate peer was reachable, return -1.
		if bestPeer == "" {
			return -1.0
		}

		// Add cost and update count for the selected peer.
		peerChunkCount[bestPeer]++
		totalCost += bestMarginalCost
	}

	return totalCost
}

// dijkstra computes the shortest path distances from the source node to every other node in the graph.
// The graph is an undirected graph represented as map[string]map[string]int.
// Returns a map of node -> shortest distance.
func dijkstra(graph map[string]map[string]int, source string) map[string]float64 {
	// Initialize distances.
	dist := make(map[string]float64)
	for node := range graph {
		dist[node] = math.Inf(1)
	}
	dist[source] = 0

	// PriorityQueue for Dijkstra's algorithm.
	pq := &PriorityQueue{}
	heap.Init(pq)
	heap.Push(pq, &Item{node: source, dist: 0})

	for pq.Len() > 0 {
		item := heap.Pop(pq).(*Item)
		u := item.node
		d := item.dist

		// If we have found a better path before, skip.
		if d > dist[u] {
			continue
		}

		neighbors, ok := graph[u]
		if !ok {
			continue
		}
		// For undirected graph, each edge is bidirectional.
		for v, weight := range neighbors {
			newDist := d + float64(weight)
			if newDist < dist[v] {
				dist[v] = newDist
				heap.Push(pq, &Item{node: v, dist: newDist})
			}
		}
	}

	return dist
}

// Item represents a node in the priority queue.
type Item struct {
	node string
	dist float64
}

// PriorityQueue implements heap.Interface and holds Items.
type PriorityQueue []*Item

func (pq PriorityQueue) Len() int { 
	return len(pq) 
}

func (pq PriorityQueue) Less(i, j int) bool {
	return pq[i].dist < pq[j].dist
}

func (pq PriorityQueue) Swap(i, j int) { 
	pq[i], pq[j] = pq[j], pq[i]
}

func (pq *PriorityQueue) Push(x interface{}) {
	item := x.(*Item)
	*pq = append(*pq, item)
}

func (pq *PriorityQueue) Pop() interface{} {
	old := *pq
	n := len(old)
	item := old[n-1]
	*pq = old[0 : n-1]
	return item
}