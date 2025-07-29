package consensus_route

import (
	"container/heap"
)

// Item represents an element in the priority queue.
type Item struct {
	node     int   // current node id
	priority int   // cumulative latency to reach this node
	path     []int // the route taken to reach this node, including the node
	index    int   // the index of the item in the heap
}

// PriorityQueue implements heap.Interface and holds Items.
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

// FindOptimalRoute returns the optimal route from originNode to a node from consistentNodes with the lowest latency,
// ensuring that the total latency does not exceed maxLatency. If no such route exists, it returns nil.
func FindOptimalRoute(N int, graph map[int]map[int]int, primaryNode int, originNode int, maxLatency int, consistentNodes []int) []int {
	// If the origin node is already consistent, return a route containing only the origin.
	for _, n := range consistentNodes {
		if n == originNode {
			return []int{originNode}
		}
	}

	// Build a set for quick lookup of consistent nodes.
	consistentSet := make(map[int]bool)
	for _, n := range consistentNodes {
		consistentSet[n] = true
	}

	// Define an "infinite" latency threshold; any latency beyond maxLatency is unusable.
	INF := maxLatency + 1

	// Initialize distances for all nodes. distances[node] will hold the lowest latency found to reach that node.
	distances := make([]int, N)
	for i := 0; i < N; i++ {
		distances[i] = INF
	}
	distances[originNode] = 0

	// PriorityQueue for Dijkstra's algorithm.
	pq := &PriorityQueue{}
	heap.Init(pq)
	heap.Push(pq, &Item{
		node:     originNode,
		priority: 0,
		path:     []int{originNode},
	})

	// bestRoute records the best route to any consistent node found so far.
	var bestRoute []int
	bestLatency := INF

	for pq.Len() > 0 {
		item := heap.Pop(pq).(*Item)
		curNode := item.node
		curLatency := item.priority

		// If a route to a consistent node has already been found with better latency, we can potentially prune worse paths.
		if curLatency > bestLatency {
			continue
		}

		// If the current node is consistent, update the bestRoute if the latency is lower.
		if consistentSet[curNode] {
			if curLatency < bestLatency {
				bestLatency = curLatency
				bestRoute = item.path
			}
			// If the next item in the queue has a latency not less than the best found, no further improvement is possible.
			if pq.Len() > 0 {
				nextItem := (*pq)[0]
				if nextItem.priority >= bestLatency {
					break
				}
			}
		}

		// Expand to neighbors.
		neighbors, exists := graph[curNode]
		if !exists {
			continue
		}
		for neighbor, edgeLatency := range neighbors {
			newLatency := curLatency + edgeLatency
			// Skip if the new computed latency exceeds maxLatency.
			if newLatency > maxLatency {
				continue
			}
			// If a better route is found for the neighbor, update its distance and push it to the queue.
			if newLatency < distances[neighbor] {
				distances[neighbor] = newLatency
				newPath := append([]int{}, item.path...)
				newPath = append(newPath, neighbor)
				heap.Push(pq, &Item{
					node:     neighbor,
					priority: newLatency,
					path:     newPath,
				})
			}
		}
	}

	if bestRoute == nil || bestLatency > maxLatency {
		return nil
	}
	return bestRoute
}