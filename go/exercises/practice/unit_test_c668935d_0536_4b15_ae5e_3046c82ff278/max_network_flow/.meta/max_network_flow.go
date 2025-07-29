package max_network_flow

import (
	"container/list"
	"math"
)

type Edge struct {
	to     int
	rev    int
	cap    int
	flow   int
}

func MaxFlow(n int, edges [][]int, source int, sink int) int {
	if source < 0 || source >= n || sink < 0 || sink >= n {
		return -1
	}
	if source == sink {
		return 0
	}

	// Build adjacency list
	graph := make([][]Edge, n)
	for _, e := range edges {
		from, to, cap := e[0], e[1], e[2]
		if cap <= 0 {
			continue
		}
		// Add forward edge
		forwardEdge := Edge{
			to:  to,
			rev: len(graph[to]),
			cap: cap,
		}
		// Add reverse edge
		reverseEdge := Edge{
			to:  from,
			rev: len(graph[from]),
			cap: 0,
		}
		graph[from] = append(graph[from], forwardEdge)
		graph[to] = append(graph[to], reverseEdge)
	}

	// Dinic's algorithm
	maxFlow := 0
	level := make([]int, n)

	for {
		// BFS to build level graph
		for i := range level {
			level[i] = -1
		}
		level[source] = 0
		queue := list.New()
		queue.PushBack(source)

		for queue.Len() > 0 {
			u := queue.Remove(queue.Front()).(int)
			for _, edge := range graph[u] {
				if level[edge.to] < 0 && edge.flow < edge.cap {
					level[edge.to] = level[u] + 1
					queue.PushBack(edge.to)
				}
			}
		}

		if level[sink] < 0 {
			break
		}

		// DFS to find blocking flow
		ptr := make([]int, n)
		for {
			flow := dfs(graph, level, ptr, source, sink, math.MaxInt32)
			if flow == 0 {
				break
			}
			maxFlow += flow
		}
	}

	return maxFlow
}

func dfs(graph [][]Edge, level []int, ptr []int, u int, sink int, flow int) int {
	if u == sink {
		return flow
	}

	for ; ptr[u] < len(graph[u]); ptr[u]++ {
		edge := &graph[u][ptr[u]]
		if level[edge.to] == level[u]+1 && edge.flow < edge.cap {
			minFlow := min(flow, edge.cap-edge.flow)
			flowFound := dfs(graph, level, ptr, edge.to, sink, minFlow)
			if flowFound > 0 {
				edge.flow += flowFound
				graph[edge.to][edge.rev].flow -= flowFound
				return flowFound
			}
		}
	}

	return 0
}

func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}