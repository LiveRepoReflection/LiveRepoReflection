package concurrent_path

import (
	"container/heap"
	"errors"
	"sync"
)

type Edge struct {
	To     int
	Weight int
}

type Node struct {
	ID       int
	Distance int
	Index    int
}

type PriorityQueue []*Node

func (pq PriorityQueue) Len() int { return len(pq) }

func (pq PriorityQueue) Less(i, j int) bool {
	return pq[i].Distance < pq[j].Distance
}

func (pq PriorityQueue) Swap(i, j int) {
	pq[i], pq[j] = pq[j], pq[i]
	pq[i].Index = i
	pq[j].Index = j
}

func (pq *PriorityQueue) Push(x interface{}) {
	n := len(*pq)
	node := x.(*Node)
	node.Index = n
	*pq = append(*pq, node)
}

func (pq *PriorityQueue) Pop() interface{} {
	old := *pq
	n := len(old)
	node := old[n-1]
	old[n-1] = nil
	node.Index = -1
	*pq = old[0 : n-1]
	return node
}

func FindShortestPath(numNodes int, graph map[int][]Edge, source int, destination int) ([]int, error) {
	if source < 0 || source >= numNodes || destination < 0 || destination >= numNodes {
		return nil, errors.New("invalid source or destination node")
	}

	if source == destination {
		return []int{source}, nil
	}

	distances := make([]int, numNodes)
	previous := make([]int, numNodes)
	for i := range distances {
		distances[i] = -1
		previous[i] = -1
	}
	distances[source] = 0

	pq := make(PriorityQueue, 0)
	heap.Init(&pq)
	heap.Push(&pq, &Node{ID: source, Distance: 0})

	var mu sync.Mutex
	var wg sync.WaitGroup
	visited := make([]bool, numNodes)

	processNode := func(node *Node) {
		defer wg.Done()

		mu.Lock()
		if visited[node.ID] {
			mu.Unlock()
			return
		}
		visited[node.ID] = true
		mu.Unlock()

		edges := graph[node.ID]
		for _, edge := range edges {
			wg.Add(1)
			go func(edge Edge) {
				defer wg.Done()

				newDist := distances[node.ID] + edge.Weight
				mu.Lock()
				if distances[edge.To] == -1 || newDist < distances[edge.To] {
					distances[edge.To] = newDist
					previous[edge.To] = node.ID
					heap.Push(&pq, &Node{ID: edge.To, Distance: newDist})
				}
				mu.Unlock()
			}(edge)
		}
	}

	for pq.Len() > 0 {
		node := heap.Pop(&pq).(*Node)
		if node.ID == destination {
			break
		}

		wg.Add(1)
		go processNode(node)
		wg.Wait()
	}

	if distances[destination] == -1 {
		return []int{}, nil
	}

	path := make([]int, 0)
	current := destination
	for current != -1 {
		path = append(path, current)
		current = previous[current]
	}

	for i, j := 0, len(path)-1; i < j; i, j = i+1, j-1 {
		path[i], path[j] = path[j], path[i]
	}

	return path, nil
}