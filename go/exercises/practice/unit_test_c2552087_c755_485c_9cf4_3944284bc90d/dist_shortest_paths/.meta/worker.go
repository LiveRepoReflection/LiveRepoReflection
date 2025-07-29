package dist_shortest_paths

import (
	"container/heap"
	"errors"
	"fmt"
	"strconv"
	"strings"
	"sync"
)

type Worker struct {
	id      int
	graph   map[int]map[int]int
	mu      sync.RWMutex
	stopped bool
}

type Node struct {
	ID       int
	Distance int
}

type PriorityQueue []*Node

func NewWorker(id int) *Worker {
	return &Worker{
		id:    id,
		graph: make(map[int]map[int]int),
	}
}

func (w *Worker) AddNode(nodeID int, edgesStr string) error {
	w.mu.Lock()
	defer w.mu.Unlock()

	if w.stopped {
		return errors.New("worker stopped")
	}

	if _, exists := w.graph[nodeID]; !exists {
		w.graph[nodeID] = make(map[int]int)
	}

	if edgesStr == "" {
		return nil
	}

	edges := strings.Split(edgesStr, ";")
	for _, edge := range edges {
		parts := strings.Split(edge, ",")
		if len(parts) != 2 {
			return fmt.Errorf("invalid edge format: %s", edge)
		}

		neighbor, err := strconv.Atoi(parts[0])
		if err != nil {
			return fmt.Errorf("invalid neighbor ID: %v", err)
		}

		weight, err := strconv.Atoi(parts[1])
		if err != nil {
			return fmt.Errorf("invalid edge weight: %v", err)
		}

		w.graph[nodeID][neighbor] = weight
	}

	return nil
}

func (w *Worker) ComputeShortestPath(source, destination int, workers []*Worker) (int, error) {
	w.mu.RLock()
	if w.stopped {
		w.mu.RUnlock()
		return -1, errors.New("worker stopped")
	}
	w.mu.RUnlock()

	distances := make(map[int]int)
	visited := make(map[int]bool)
	pq := make(PriorityQueue, 0)
	heap.Init(&pq)

	heap.Push(&pq, &Node{ID: source, Distance: 0})
	distances[source] = 0

	for pq.Len() > 0 {
		current := heap.Pop(&pq).(*Node)
		if visited[current.ID] {
			continue
		}
		visited[current.ID] = true

		if current.ID == destination {
			return current.Distance, nil
		}

		workerIdx := current.ID % len(workers)
		workers[workerIdx].mu.RLock()
		edges, exists := workers[workerIdx].graph[current.ID]
		workers[workerIdx].mu.RUnlock()

		if !exists {
			continue
		}

		for neighbor, weight := range edges {
			if _, ok := distances[neighbor]; !ok || distances[neighbor] > current.Distance+weight {
				distances[neighbor] = current.Distance + weight
				heap.Push(&pq, &Node{ID: neighbor, Distance: distances[neighbor]})
			}
		}
	}

	return -1, nil
}

func (w *Worker) Stop() {
	w.mu.Lock()
	w.stopped = true
	w.mu.Unlock()
}

func (pq PriorityQueue) Len() int { return len(pq) }

func (pq PriorityQueue) Less(i, j int) bool {
	return pq[i].Distance < pq[j].Distance
}

func (pq PriorityQueue) Swap(i, j int) {
	pq[i], pq[j] = pq[j], pq[i]
}

func (pq *PriorityQueue) Push(x interface{}) {
	item := x.(*Node)
	*pq = append(*pq, item)
}

func (pq *PriorityQueue) Pop() interface{} {
	old := *pq
	n := len(old)
	item := old[n-1]
	*pq = old[0 : n-1]
	return item
}