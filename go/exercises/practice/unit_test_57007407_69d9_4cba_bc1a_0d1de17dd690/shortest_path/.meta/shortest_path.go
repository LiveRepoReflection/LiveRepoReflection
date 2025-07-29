package shortest_path

import (
	"container/heap"
	"fmt"
	"math"
	"sync"
)

type Pathfinder interface {
	AddLocation(id int)
	AddRoad(from int, to int, cost int)
	UpdateRoadCost(from int, to int, newCost int)
	FindShortestPath(start int, end int, avoid []int) ([]int, int)
}

type pathfinder struct {
	mu    sync.RWMutex
	nodes map[int]struct{}
	// edges[from][to] = cost
	edges map[int]map[int]int
}

func NewPathfinder() Pathfinder {
	return &pathfinder{
		nodes: make(map[int]struct{}),
		edges: make(map[int]map[int]int),
	}
}

func (pf *pathfinder) AddLocation(id int) {
	pf.mu.Lock()
	defer pf.mu.Unlock()
	// If the node doesn't exist, add it and initialize its adjacency list.
	if _, exists := pf.nodes[id]; !exists {
		pf.nodes[id] = struct{}{}
		pf.edges[id] = make(map[int]int)
	}
}

func (pf *pathfinder) AddRoad(from int, to int, cost int) {
	pf.mu.Lock()
	defer pf.mu.Unlock()
	// Check that both nodes exist.
	if _, exists := pf.nodes[from]; !exists {
		return
	}
	if _, exists := pf.nodes[to]; !exists {
		return
	}
	// Create or update the bidirectional edge.
	if pf.edges[from] == nil {
		pf.edges[from] = make(map[int]int)
	}
	pf.edges[from][to] = cost

	if pf.edges[to] == nil {
		pf.edges[to] = make(map[int]int)
	}
	pf.edges[to][from] = cost
}

func (pf *pathfinder) UpdateRoadCost(from int, to int, newCost int) {
	pf.mu.Lock()
	defer pf.mu.Unlock()
	// Only update if both nodes exist and the road exists.
	if _, exists := pf.nodes[from]; !exists {
		return
	}
	if _, exists := pf.nodes[to]; !exists {
		return
	}
	if _, exists := pf.edges[from][to]; !exists {
		return
	}
	pf.edges[from][to] = newCost
	pf.edges[to][from] = newCost
}

func (pf *pathfinder) FindShortestPath(start int, end int, avoid []int) ([]int, int) {
	pf.mu.RLock()
	defer pf.mu.RUnlock()

	// Check if start and end exist.
	if _, exists := pf.nodes[start]; !exists {
		return []int{}, -1
	}
	if _, exists := pf.nodes[end]; !exists {
		return []int{}, -1
	}

	// Build avoid set
	avoidSet := make(map[int]bool)
	for _, id := range avoid {
		avoidSet[id] = true
	}
	// If start or end is in avoid list, then no valid path.
	if avoidSet[start] || avoidSet[end] {
		return []int{}, -1
	}

	// Initialize distances and predecessors.
	const INF = math.MaxInt64
	dist := make(map[int]int)
	prev := make(map[int]int)
	for node := range pf.nodes {
		dist[node] = INF
	}
	dist[start] = 0

	// Priority queue for dijkstra
	pq := &PriorityQueue{}
	heap.Init(pq)
	heap.Push(pq, &Item{node: start, cost: 0})

	visited := make(map[int]bool)

	for pq.Len() > 0 {
		current := heap.Pop(pq).(*Item)
		u := current.node
		if visited[u] {
			continue
		}
		visited[u] = true

		// If we reached the end, we can break.
		if u == end {
			break
		}
		// Iterate through neighbors.
		for v, cost := range pf.edges[u] {
			// Skip nodes to avoid.
			if avoidSet[v] {
				continue
			}

			if !visited[v] && dist[u] != INF && dist[u]+cost < dist[v] {
				dist[v] = dist[u] + cost
				prev[v] = u
				heap.Push(pq, &Item{node: v, cost: dist[v]})
			}
		}
	}

	// If end is unreachable.
	if dist[end] == INF {
		return []int{}, -1
	}

	// Reconstruct path.
	path := []int{}
	for at := end; ; {
		path = append([]int{at}, path...)
		if at == start {
			break
		}
		parent, ok := prev[at]
		if !ok {
			// This should not happen.
			return []int{}, -1
		}
		at = parent
	}
	return path, dist[end]
}

// Item is something we manage in a priority queue.
type Item struct {
	node int
	cost int
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

// For debugging purposes if needed.
func (pf *pathfinder) String() string {
	pf.mu.RLock()
	defer pf.mu.RUnlock()
	result := ""
	for from, neighbors := range pf.edges {
		for to, cost := range neighbors {
			result += fmt.Sprintf("%d -> %d cost %d\n", from, to, cost)
		}
	}
	return result
}