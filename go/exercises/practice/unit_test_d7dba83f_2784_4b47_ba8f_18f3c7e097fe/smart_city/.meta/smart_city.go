package smart_city

import (
	"container/heap"
	"math"
)

type Edge struct {
	to       int
	bandwidth int
	latency  int
}

type DataSource struct {
	buildingID     int
	dataType      string
	criticality   int
	maxLatency    int
	dataSize      int
}

type Path struct {
	nodes     []int
	bandwidth int
	latency   int
}

type PriorityQueue []*DataSource

func (pq PriorityQueue) Len() int { return len(pq) }

func (pq PriorityQueue) Less(i, j int) bool {
	return pq[i].criticality > pq[j].criticality
}

func (pq PriorityQueue) Swap(i, j int) {
	pq[i], pq[j] = pq[j], pq[i]
}

func (pq *PriorityQueue) Push(x interface{}) {
	item := x.(*DataSource)
	*pq = append(*pq, item)
}

func (pq *PriorityQueue) Pop() interface{} {
	old := *pq
	n := len(old)
	item := old[n-1]
	*pq = old[0 : n-1]
	return item
}

func CalculateMaxCriticalityScore(N int, M int, channels [][4]int, dataSources [][5]interface{}, simulationTime int) int {
	// Build adjacency list
	adj := make([][]Edge, N)
	for _, ch := range channels {
		src, dest, bw, lat := ch[0], ch[1], ch[2], ch[3]
		adj[src] = append(adj[src], Edge{dest, bw, lat})
		adj[dest] = append(adj[dest], Edge{src, bw, lat})
	}

	// Convert data sources
	pq := make(PriorityQueue, 0, len(dataSources))
	sources := make([]DataSource, len(dataSources))
	for i, ds := range dataSources {
		sources[i] = DataSource{
			buildingID:  ds[0].(int),
			dataType:    ds[1].(string),
			criticality: ds[2].(int),
			maxLatency:  ds[3].(int),
			dataSize:    ds[4].(int),
		}
		pq = append(pq, &sources[i])
	}
	heap.Init(&pq)

	totalScore := 0

	for t := 0; t < simulationTime; t++ {
		// Make a copy of the original channels for this time step
		channelUsage := make(map[[2]int]int)
		for _, ch := range channels {
			src, dest := ch[0], ch[1]
			if src > dest {
				src, dest = dest, src
			}
			channelUsage[[2]int{src, dest}] = ch[2]
		}

		tempPQ := make(PriorityQueue, len(pq))
		copy(tempPQ, pq)
		heap.Init(&tempPQ)

		for tempPQ.Len() > 0 {
			ds := heap.Pop(&tempPQ).(*DataSource)
			paths := findAllPaths(adj, ds.buildingID, 0)

			// Find best path that can accommodate this data
			var bestPath *Path
			for _, path := range paths {
				if path.latency > ds.maxLatency {
					continue
				}

				if path.bandwidth < ds.dataSize {
					continue
				}

				// Check if path has enough remaining bandwidth
				pathValid := true
				for i := 0; i < len(path.nodes)-1; i++ {
					src, dest := path.nodes[i], path.nodes[i+1]
					if src > dest {
						src, dest = dest, src
					}
					if channelUsage[[2]int{src, dest}] < ds.dataSize {
						pathValid = false
						break
					}
				}

				if pathValid && (bestPath == nil || path.latency < bestPath.latency) {
					bestPath = &path
				}
			}

			if bestPath != nil {
				// Use this path and update channel usage
				for i := 0; i < len(bestPath.nodes)-1; i++ {
					src, dest := bestPath.nodes[i], bestPath.nodes[i+1]
					if src > dest {
						src, dest = dest, src
					}
					channelUsage[[2]int{src, dest}] -= ds.dataSize
				}
				totalScore += ds.criticality
			}
		}
	}

	return totalScore
}

func findAllPaths(adj [][]Edge, start, end int) []Path {
	var paths []Path
	visited := make([]bool, len(adj))
	currentPath := []int{start}
	findPathsDFS(adj, start, end, visited, currentPath, math.MaxInt32, 0, &paths)
	return paths
}

func findPathsDFS(adj [][]Edge, current, end int, visited []bool, currentPath []int, minBandwidth int, totalLatency int, paths *[]Path) {
	if current == end {
		*paths = append(*paths, Path{
			nodes:     append([]int{}, currentPath...),
			bandwidth: minBandwidth,
			latency:   totalLatency,
		})
		return
	}

	visited[current] = true

	for _, edge := range adj[current] {
		if !visited[edge.to] {
			newMinBandwidth := min(minBandwidth, edge.bandwidth)
			newTotalLatency := totalLatency + edge.latency
			findPathsDFS(adj, edge.to, end, visited, append(currentPath, edge.to), newMinBandwidth, newTotalLatency, paths)
		}
	}

	visited[current] = false
}

func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}