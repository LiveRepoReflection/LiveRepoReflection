package data_routing

import (
	"container/heap"
	"math"
)

type tuple struct {
	dataCenterID int
	serverID     int
}

type pathItem struct {
	dataCenterID int
	latency      int
	path         []int
	index       int
}

type priorityQueue []*pathItem

func (pq priorityQueue) Len() int { return len(pq) }

func (pq priorityQueue) Less(i, j int) bool {
	return pq[i].latency < pq[j].latency
}

func (pq priorityQueue) Swap(i, j int) {
	pq[i], pq[j] = pq[j], pq[i]
	pq[i].index = i
	pq[j].index = j
}

func (pq *priorityQueue) Push(x interface{}) {
	n := len(*pq)
	item := x.(*pathItem)
	item.index = n
	*pq = append(*pq, item)
}

func (pq *priorityQueue) Pop() interface{} {
	old := *pq
	n := len(old)
	item := old[n-1]
	old[n-1] = nil
	item.index = -1
	*pq = old[0 : n-1]
	return item
}

var GetCongestionLatency = func(dataCenterID int, path []int) int {
	return 0
}

func FindOptimalPath(network map[int]map[int]int, bandwidth map[int]map[int]int, source tuple, destination tuple) []int {
	if source.dataCenterID == destination.dataCenterID {
		return []int{source.dataCenterID}
	}

	visited := make(map[int]bool)
	pq := make(priorityQueue, 0)
	heap.Init(&pq)

	initialPath := []int{source.dataCenterID}
	heap.Push(&pq, &pathItem{
		dataCenterID: source.dataCenterID,
		latency:      0,
		path:         initialPath,
	})

	minLatency := make(map[int]int)
	for dc := range network {
		minLatency[dc] = math.MaxInt32
	}
	minLatency[source.dataCenterID] = 0

	for pq.Len() > 0 {
		current := heap.Pop(&pq).(*pathItem)

		if current.dataCenterID == destination.dataCenterID {
			return current.path
		}

		if visited[current.dataCenterID] {
			continue
		}
		visited[current.dataCenterID] = true

		for neighbor, latency := range network[current.dataCenterID] {
			if visited[neighbor] {
				continue
			}

			if bandwidth[current.dataCenterID][neighbor] <= 0 {
				continue
			}

			newPath := make([]int, len(current.path)+1)
			copy(newPath, current.path)
			newPath[len(newPath)-1] = neighbor

			congestion := GetCongestionLatency(neighbor, newPath)
			totalLatency := current.latency + latency + congestion

			if totalLatency < minLatency[neighbor] {
				minLatency[neighbor] = totalLatency
				heap.Push(&pq, &pathItem{
					dataCenterID: neighbor,
					latency:      totalLatency,
					path:         newPath,
				})
			}
		}
	}

	return []int{}
}