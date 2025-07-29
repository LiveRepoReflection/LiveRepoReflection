package dynamic_route

import (
	"container/heap"
	"math"
)

type Edge struct {
	node   int
	weight int
}

type Graph [][]Edge

type Item struct {
	node     int
	distance int
	time     int
	index    int
}

type PriorityQueue []*Item

func (pq PriorityQueue) Len() int { return len(pq) }

func (pq PriorityQueue) Less(i, j int) bool {
	return pq[i].distance < pq[j].distance
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

func FindOptimalRoute(N, T int, snapshots [][][]int, start, end, startTime, endTime int) int {
	if start == end {
		return 0
	}
	if startTime > endTime {
		return -1
	}

	// Build the temporal graph
	temporalGraph := make([]Graph, T)
	for t := 0; t < T; t++ {
		graph := make(Graph, N)
		for _, edge := range snapshots[t] {
			u, v, w := edge[0], edge[1], edge[2]
			graph[u] = append(graph[u], Edge{v, w})
			graph[v] = append(graph[v], Edge{u, w})
		}
		temporalGraph[t] = graph
	}

	// Initialize distances
	distances := make([][]int, N)
	for i := range distances {
		distances[i] = make([]int, T)
		for j := range distances[i] {
			distances[i][j] = math.MaxInt32
		}
	}
	distances[start][startTime] = 0

	pq := make(PriorityQueue, 0)
	heap.Push(&pq, &Item{
		node:     start,
		distance: 0,
		time:     startTime,
	})

	for pq.Len() > 0 {
		current := heap.Pop(&pq).(*Item)
		currentNode := current.node
		currentTime := current.time
		currentDist := current.distance

		if currentNode == end {
			return currentDist
		}

		if currentTime >= T || currentTime > endTime {
			continue
		}

		if currentDist > distances[currentNode][currentTime] {
			continue
		}

		// Option 1: Move to next timestamp without moving
		if currentTime+1 < T && currentTime+1 <= endTime {
			if distances[currentNode][currentTime+1] > currentDist {
				distances[currentNode][currentTime+1] = currentDist
				heap.Push(&pq, &Item{
					node:     currentNode,
					distance: currentDist,
					time:     currentTime + 1,
				})
			}
		}

		// Option 2: Traverse edges available at current timestamp
		for _, edge := range temporalGraph[currentTime][currentNode] {
			nextNode := edge.node
			newDist := currentDist + edge.weight
			if newDist < distances[nextNode][currentTime] {
				distances[nextNode][currentTime] = newDist
				heap.Push(&pq, &Item{
					node:     nextNode,
					distance: newDist,
					time:     currentTime,
				})
			}
		}
	}

	return -1
}