package dist_shortest_path

import (
	"container/heap"
	"errors"
	"math"
)

// Item represents a node in the priority queue.
type Item struct {
	node  string
	cost  float64
	index int
}

// PriorityQueue implements heap.Interface and holds Items.
type PriorityQueue []*Item

func (pq PriorityQueue) Len() int { 
	return len(pq) 
}

func (pq PriorityQueue) Less(i, j int) bool { 
	return pq[i].cost < pq[j].cost 
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
	old[n-1] = nil
	item.index = -1
	*pq = old[0 : n-1]
	return item
}

// FindShortestPath computes the shortest path between sourceNodeID and destinationNodeID.
// It uses Dijkstra's algorithm on the provided graphData, which represents a map of node IDs
// to their neighbors and the corresponding edge weights.
func FindShortestPath(sourceNodeID string, destinationNodeID string, graphData map[string]map[string]float64) ([]string, float64, error) {
	if sourceNodeID == destinationNodeID {
		return []string{sourceNodeID}, 0.0, nil
	}

	// Validate existence of source and destination in graphData.
	if _, ok := graphData[sourceNodeID]; !ok {
		return []string{}, -1.0, errors.New("source node not found")
	}
	if _, ok := graphData[destinationNodeID]; !ok {
		return []string{}, -1.0, errors.New("destination node not found")
	}

	// Initialize the distance to all nodes as infinity and the source as zero.
	dist := make(map[string]float64)
	prev := make(map[string]string)
	for node := range graphData {
		dist[node] = math.Inf(1)
	}
	dist[sourceNodeID] = 0.0

	// Priority queue to hold nodes to be processed.
	pq := make(PriorityQueue, 0)
	heap.Init(&pq)
	heap.Push(&pq, &Item{node: sourceNodeID, cost: 0.0})

	// Process nodes in the priority queue.
	for pq.Len() > 0 {
		item := heap.Pop(&pq).(*Item)
		current := item.node
		currentCost := item.cost

		// If we have reached the destination, we can stop early.
		if current == destinationNodeID {
			break
		}

		// Iterate through all neighbors and update the cost if a shorter path is found.
		for neighbor, weight := range graphData[current] {
			alt := currentCost + weight
			if alt < dist[neighbor] {
				dist[neighbor] = alt
				prev[neighbor] = current
				heap.Push(&pq, &Item{node: neighbor, cost: alt})
			}
		}
	}

	// If the destination was not reached, return error.
	if math.IsInf(dist[destinationNodeID], 1) {
		return []string{}, -1.0, errors.New("no path found")
	}

	// Reconstruct the shortest path by tracing predecessors.
	path := []string{}
	for at := destinationNodeID; at != ""; at = prev[at] {
		path = append([]string{at}, path...)
		if at == sourceNodeID {
			break
		}
	}

	return path, dist[destinationNodeID], nil
}