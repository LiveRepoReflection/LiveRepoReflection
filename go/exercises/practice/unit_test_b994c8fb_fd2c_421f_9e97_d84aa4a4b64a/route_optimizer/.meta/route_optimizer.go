package route_optimizer

import (
	"container/heap"
	"math"
)

type Connection struct {
	Dest      string
	Latency   int
	Bandwidth int
}

type Path struct {
	nodes     []string
	latency   int
	bandwidth int
}

type PriorityQueue []*Path

func (pq PriorityQueue) Len() int { return len(pq) }

func (pq PriorityQueue) Less(i, j int) bool {
	return pq[i].latency < pq[j].latency
}

func (pq PriorityQueue) Swap(i, j int) {
	pq[i], pq[j] = pq[j], pq[i]
}

func (pq *PriorityQueue) Push(x interface{}) {
	item := x.(*Path)
	*pq = append(*pq, item)
}

func (pq *PriorityQueue) Pop() interface{} {
	old := *pq
	n := len(old)
	item := old[n-1]
	*pq = old[0 : n-1]
	return item
}

func FindOptimalPath(graph map[string][]Connection, source, destination string, minBandwidth int) []string {
	if source == destination {
		return []string{source}
	}

	visited := make(map[string]bool)
	pq := make(PriorityQueue, 0)
	heap.Init(&pq)

	initialPath := &Path{
		nodes:     []string{source},
		latency:   0,
		bandwidth: math.MaxInt32,
	}
	heap.Push(&pq, initialPath)

	for pq.Len() > 0 {
		currentPath := heap.Pop(&pq).(*Path)
		lastNode := currentPath.nodes[len(currentPath.nodes)-1]

		if lastNode == destination {
			return currentPath.nodes
		}

		if visited[lastNode] {
			continue
		}
		visited[lastNode] = true

		for _, conn := range graph[lastNode] {
			if visited[conn.Dest] {
				continue
			}

			newBandwidth := min(currentPath.bandwidth, conn.Bandwidth)
			if newBandwidth < minBandwidth {
				continue
			}

			newNodes := make([]string, len(currentPath.nodes)+1)
			copy(newNodes, currentPath.nodes)
			newNodes[len(newNodes)-1] = conn.Dest

			newPath := &Path{
				nodes:     newNodes,
				latency:   currentPath.latency + conn.Latency,
				bandwidth: newBandwidth,
			}

			heap.Push(&pq, newPath)
		}
	}

	return []string{}
}

func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}