package network_latency

import (
	"container/heap"
	"math"
)

// Item represents a single element in the priority queue.
type Item struct {
	node     int
	distance int
	index    int
}

// PriorityQueue implements heap.Interface and holds Items.
type PriorityQueue []*Item

func (pq PriorityQueue) Len() int { return len(pq) }

// Less prioritizes lower distances.
func (pq PriorityQueue) Less(i, j int) bool {
	return pq[i].distance < pq[j].distance
}

func (pq PriorityQueue) Swap(i, j int) {
	pq[i], pq[j] = pq[j], pq[i]
	pq[i].index = i
	pq[j].index = j
}

// Push pushes an element into the queue.
func (pq *PriorityQueue) Push(x interface{}) {
	n := len(*pq)
	item := x.(*Item)
	item.index = n
	*pq = append(*pq, item)
}

// Pop removes and returns the element with the smallest distance.
func (pq *PriorityQueue) Pop() interface{} {
	old := *pq
	n := len(old)
	item := old[n-1]
	item.index = -1 // for safety
	*pq = old[0 : n-1]
	return item
}

// update modifies the priority of an Item in the queue.
func (pq *PriorityQueue) update(item *Item, distance int) {
	item.distance = distance
	heap.Fix(pq, item.index)
}

// MaxNetworkLatency calculates the maximum distance from any node to its nearest service node.
// N is the number of nodes, graph is the adjacency list where graph[i] contains pairs [neighbor, cost],
// and serviceNodes is the list of nodes that are service centers.
func MaxNetworkLatency(N int, graph [][][2]int, serviceNodes []int) int {
	// Initialize distance slice with infinity.
	distances := make([]int, N)
	for i := 0; i < N; i++ {
		distances[i] = math.MaxInt64
	}

	// Priority queue for multi-source Dijkstra.
	pq := make(PriorityQueue, 0, N)
	heap.Init(&pq)

	// Add all service nodes to the queue with distance 0.
	for _, node := range serviceNodes {
		if node >= 0 && node < N {
			distances[node] = 0
			heap.Push(&pq, &Item{
				node:     node,
				distance: 0,
			})
		}
	}

	// Multi-source Dijkstra.
	for pq.Len() > 0 {
		item := heap.Pop(&pq).(*Item)
		u := item.node
		currDist := item.distance

		// Ignore if a better distance was already found.
		if currDist > distances[u] {
			continue
		}

		// Relaxation step.
		for _, edge := range graph[u] {
			v := edge[0]
			cost := edge[1]
			if distances[u]+cost < distances[v] {
				distances[v] = distances[u] + cost
				heap.Push(&pq, &Item{
					node:     v,
					distance: distances[v],
				})
			}
		}
	}

	// Compute maximum distance from any node to a service node.
	maxLatency := 0
	for _, d := range distances {
		if d > maxLatency {
			maxLatency = d
		}
	}

	return maxLatency
}