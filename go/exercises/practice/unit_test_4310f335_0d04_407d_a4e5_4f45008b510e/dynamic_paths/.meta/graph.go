package dynamic_paths

import (
	"container/heap"
	"sync"
)

type Graph struct {
	edges map[int]map[int]int
	lock  sync.RWMutex
}

func NewGraph() *Graph {
	return &Graph{
		edges: make(map[int]map[int]int),
	}
}

func (g *Graph) UpdateEdge(u, v, newTravelTime int) {
	g.lock.Lock()
	defer g.lock.Unlock()
	if newTravelTime < 0 {
		// Remove the edge if it exists.
		if neighbors, exists := g.edges[u]; exists {
			delete(neighbors, v)
			if len(neighbors) == 0 {
				delete(g.edges, u)
			}
		}
		return
	}
	// Add or update the edge with the new travel time.
	if _, exists := g.edges[u]; !exists {
		g.edges[u] = make(map[int]int)
	}
	g.edges[u][v] = newTravelTime
}

type Item struct {
	node  int
	dist  int
	index int
}

type PriorityQueue []*Item

func (pq PriorityQueue) Len() int {
	return len(pq)
}
func (pq PriorityQueue) Less(i, j int) bool {
	return pq[i].dist < pq[j].dist
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

func (g *Graph) QueryShortestPath(sources []int, destination int) int {
	g.lock.RLock()
	defer g.lock.RUnlock()

	// If destination exists in sources, return 0.
	for _, s := range sources {
		if s == destination {
			return 0
		}
	}

	distances := make(map[int]int)
	pq := &PriorityQueue{}
	heap.Init(pq)

	// Initialize the priority queue with all source nodes.
	for _, s := range sources {
		if _, exists := distances[s]; !exists || distances[s] > 0 {
			distances[s] = 0
			heap.Push(pq, &Item{node: s, dist: 0})
		}
	}

	for pq.Len() > 0 {
		item := heap.Pop(pq).(*Item)
		u := item.node
		d := item.dist

		// If the destination is reached, return the accumulated distance.
		if u == destination {
			return d
		}
		// Skip the node if a shorter path has already been discovered.
		if d > distances[u] {
			continue
		}
		neighbors, exists := g.edges[u]
		if !exists {
			continue
		}
		for v, w := range neighbors {
			newDist := d + w
			if old, found := distances[v]; !found || newDist < old {
				distances[v] = newDist
				heap.Push(pq, &Item{node: v, dist: newDist})
			}
		}
	}
	return -1
}