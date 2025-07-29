package efficient_pathfinder

import (
	"container/heap"
	"errors"
	"math"
	"sync"
)

type Edge struct {
	to   int
	cost int64
}

type Pathfinder struct {
	size    int
	edges   [][]Edge
	lock    sync.RWMutex
}

func NewPathfinder(size int) *Pathfinder {
	return &Pathfinder{
		size:  size,
		edges: make([][]Edge, size),
	}
}

func (pf *Pathfinder) Update(op string, u, v int, cost int64) error {
	if u < 0 || u >= pf.size || v < 0 || v >= pf.size {
		return errors.New("invalid node ID")
	}

	if cost < 0 && op != "remove" {
		return errors.New("negative edge cost")
	}

	pf.lock.Lock()
	defer pf.lock.Unlock()

	switch op {
	case "add":
		pf.addEdge(u, v, cost)
	case "update":
		pf.updateEdge(u, v, cost)
	case "remove":
		pf.removeEdge(u, v)
	default:
		return errors.New("invalid operation")
	}
	return nil
}

func (pf *Pathfinder) addEdge(u, v int, cost int64) {
	// Check if edge already exists
	for i, e := range pf.edges[u] {
		if e.to == v {
			if cost < e.cost {
				pf.edges[u][i].cost = cost
			}
			return
		}
	}
	pf.edges[u] = append(pf.edges[u], Edge{v, cost})
}

func (pf *Pathfinder) updateEdge(u, v int, cost int64) {
	for i, e := range pf.edges[u] {
		if e.to == v {
			pf.edges[u][i].cost = cost
			return
		}
	}
	pf.edges[u] = append(pf.edges[u], Edge{v, cost})
}

func (pf *Pathfinder) removeEdge(u, v int) {
	for i, e := range pf.edges[u] {
		if e.to == v {
			pf.edges[u] = append(pf.edges[u][:i], pf.edges[u][i+1:]...)
			return
		}
	}
}

func (pf *Pathfinder) Query(s, d int) int64 {
	if s < 0 || s >= pf.size || d < 0 || d >= pf.size {
		return -1
	}
	if s == d {
		return 0
	}

	pf.lock.RLock()
	defer pf.lock.RUnlock()

	dist := make([]int64, pf.size)
	for i := range dist {
		dist[i] = math.MaxInt64
	}
	dist[s] = 0

	h := &minHeap{}
	heap.Init(h)
	heap.Push(h, heapItem{node: s, distance: 0})

	for h.Len() > 0 {
		current := heap.Pop(h).(heapItem)
		if current.node == d {
			return current.distance
		}

		if current.distance > dist[current.node] {
			continue
		}

		for _, edge := range pf.edges[current.node] {
			newDist := current.distance + edge.cost
			if newDist < dist[edge.to] {
				dist[edge.to] = newDist
				heap.Push(h, heapItem{node: edge.to, distance: newDist})
			}
		}
	}

	return -1
}

type heapItem struct {
	node     int
	distance int64
}

type minHeap []heapItem

func (h minHeap) Len() int           { return len(h) }
func (h minHeap) Less(i, j int) bool { return h[i].distance < h[j].distance }
func (h minHeap) Swap(i, j int)      { h[i], h[j] = h[j], h[i] }

func (h *minHeap) Push(x interface{}) {
	*h = append(*h, x.(heapItem))
}

func (h *minHeap) Pop() interface{} {
	old := *h
	n := len(old)
	x := old[n-1]
	*h = old[0 : n-1]
	return x
}