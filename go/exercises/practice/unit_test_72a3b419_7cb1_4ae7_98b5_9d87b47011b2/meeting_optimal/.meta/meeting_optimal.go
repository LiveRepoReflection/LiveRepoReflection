package meeting_optimal

import (
	"container/heap"
	"math"
)

const INF = math.MaxInt64

type Edge struct {
	to, weight int
}

func MeetingOptimal(n int, edges [][]int, locations []int) int {
	// Build adjacency list
	graph := make([][]Edge, n)
	for _, e := range edges {
		u, v, w := e[0], e[1], e[2]
		graph[u] = append(graph[u], Edge{to: v, weight: w})
		graph[v] = append(graph[v], Edge{to: u, weight: w})
	}

	// Get unique sources from locations
	uniqueSourcesMap := make(map[int]struct{})
	for _, loc := range locations {
		if loc >= 0 && loc < n {
			uniqueSourcesMap[loc] = struct{}{}
		}
	}
	if len(uniqueSourcesMap) == 0 {
		return -1
	}
	uniqueSources := make([]int, 0, len(uniqueSourcesMap))
	for src := range uniqueSourcesMap {
		uniqueSources = append(uniqueSources, src)
	}

	// Initialize arrays to track maximum distance and reachability count for each node
	globalMax := make([]int, n)
	reachableCount := make([]int, n)
	for i := 0; i < n; i++ {
		globalMax[i] = 0
		reachableCount[i] = 0
	}

	// Run Dijkstra for each unique source and update globalMax and reachableCount
	for _, src := range uniqueSources {
		dist := make([]int, n)
		for i := 0; i < n; i++ {
			dist[i] = INF
		}
		dist[src] = 0
		pq := &PriorityQueue{}
		heap.Init(pq)
		heap.Push(pq, &Item{node: src, dist: 0})

		for pq.Len() > 0 {
			cur := heap.Pop(pq).(*Item)
			u := cur.node
			d := cur.dist
			if d > dist[u] {
				continue
			}
			for _, edge := range graph[u] {
				v := edge.to
				newDist := d + edge.weight
				if newDist < dist[v] {
					dist[v] = newDist
					heap.Push(pq, &Item{node: v, dist: newDist})
				}
			}
		}

		// Update global metrics for all nodes reachable from this source.
		for v := 0; v < n; v++ {
			if dist[v] < INF {
				reachableCount[v]++
				if dist[v] > globalMax[v] {
					globalMax[v] = dist[v]
				}
			}
		}
	}

	// Find candidate meeting point: node that is reachable from all sources
	// and minimizes the maximum distance. Tie-break on smallest index.
	bestNode := -1
	bestMax := INF
	required := len(uniqueSources)
	for v := 0; v < n; v++ {
		if reachableCount[v] == required {
			if globalMax[v] < bestMax {
				bestMax = globalMax[v]
				bestNode = v
			}
		}
	}
	return bestNode
}

type Item struct {
	node int
	dist int
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