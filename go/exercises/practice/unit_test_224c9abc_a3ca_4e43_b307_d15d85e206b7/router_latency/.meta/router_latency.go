package router_latency

import (
	"container/heap"
	"math"
)

type Item struct {
	node     int
	distance int
}

type PriorityQueue []*Item

func (pq PriorityQueue) Len() int { return len(pq) }

func (pq PriorityQueue) Less(i, j int) bool {
	return pq[i].distance < pq[j].distance
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

func MinMaxLatency(N int, K int, edges [][3]int) int {
	if K > N {
		return -1
	}

	// Build adjacency list
	adj := make(map[int][]Item)
	for _, edge := range edges {
		u, v, w := edge[0], edge[1], edge[2]
		adj[u] = append(adj[u], Item{node: v, distance: w})
		adj[v] = append(adj[v], Item{node: u, distance: w})
	}

	// Precompute all pairs shortest paths
	dist := make([][]int, N+1)
	for i := range dist {
		dist[i] = make([]int, N+1)
		for j := range dist[i] {
			if i == j {
				dist[i][j] = 0
			} else {
				dist[i][j] = math.MaxInt32
			}
		}
	}

	for u := 1; u <= N; u++ {
		pq := make(PriorityQueue, 0)
		heap.Push(&pq, &Item{node: u, distance: 0})
		visited := make(map[int]bool)

		for pq.Len() > 0 {
			item := heap.Pop(&pq).(*Item)
			if visited[item.node] {
				continue
			}
			visited[item.node] = true

			for _, neighbor := range adj[item.node] {
				newDist := item.distance + neighbor.distance
				if newDist < dist[u][neighbor.node] {
					dist[u][neighbor.node] = newDist
					heap.Push(&pq, &Item{node: neighbor.node, distance: newDist})
				}
			}
		}
	}

	// Generate all combinations of K routers
	minMaxLatency := math.MaxInt32
	combinations := generateCombinations(N, K)

	for _, routers := range combinations {
		currentMax := 0
		for server := 1; server <= N; server++ {
			minDist := math.MaxInt32
			for _, router := range routers {
				if dist[server][router] < minDist {
					minDist = dist[server][router]
				}
			}
			if minDist > currentMax {
				currentMax = minDist
			}
		}
		if currentMax < minMaxLatency {
			minMaxLatency = currentMax
		}
	}

	return minMaxLatency
}

func generateCombinations(n, k int) [][]int {
	var result [][]int
	var backtrack func(start int, current []int)
	
	backtrack = func(start int, current []int) {
		if len(current) == k {
			temp := make([]int, k)
			copy(temp, current)
			result = append(result, temp)
			return
		}
		
		for i := start; i <= n; i++ {
			current = append(current, i)
			backtrack(i+1, current)
			current = current[:len(current)-1]
		}
	}
	
	backtrack(1, []int{})
	return result
}