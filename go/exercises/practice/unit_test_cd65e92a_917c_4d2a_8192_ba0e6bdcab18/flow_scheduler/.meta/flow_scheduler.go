package flow_scheduler

import (
	"math"
)

type Edge struct {
	to     int
	rev    int
	cap    int
	flow   int
}

type MaxFlow struct {
	size  int
	graph [][]Edge
}

func NewMaxFlow(size int) *MaxFlow {
	return &MaxFlow{
		size:  size,
		graph: make([][]Edge, size),
	}
}

func (mf *MaxFlow) AddEdge(from, to, cap int) {
	forward := Edge{to: to, rev: len(mf.graph[to]), cap: cap, flow: 0}
	backward := Edge{to: from, rev: len(mf.graph[from]), cap: 0, flow: 0}
	mf.graph[from] = append(mf.graph[from], forward)
	mf.graph[to] = append(mf.graph[to], backward)
}

func (mf *MaxFlow) bfs(level []int, s, t int) bool {
	for i := range level {
		level[i] = -1
	}
	level[s] = 0
	queue := []int{s}

	for len(queue) > 0 {
		v := queue[0]
		queue = queue[1:]

		for _, e := range mf.graph[v] {
			if e.cap-e.flow > 0 && level[e.to] < 0 {
				level[e.to] = level[v] + 1
				queue = append(queue, e.to)
			}
		}
	}
	return level[t] != -1
}

func (mf *MaxFlow) dfs(iter, level []int, v, t, flow int) int {
	if v == t {
		return flow
	}

	for i := iter[v]; i < len(mf.graph[v]); i++ {
		e := &mf.graph[v][i]
		if e.cap-e.flow > 0 && level[v] < level[e.to] {
			d := mf.dfs(iter, level, e.to, t, min(flow, e.cap-e.flow))
			if d > 0 {
				e.flow += d
				mf.graph[e.to][e.rev].flow -= d
				return d
			}
		}
	}
	return 0
}

func (mf *MaxFlow) MaxFlow(s, t int) int {
	flow := 0
	level := make([]int, mf.size)
	iter := make([]int, mf.size)

	for mf.bfs(level, s, t) {
		for i := range iter {
			iter[i] = 0
		}
		for {
			f := mf.dfs(iter, level, s, t, math.MaxInt)
			if f == 0 {
				break
			}
			flow += f
		}
	}
	return flow
}

func MaxSatisfiedRequests(n, m int, edges [][3]int, k int, requests [][3]int) int {
	maxRequests := 0

	for mask := 1; mask < (1 << k); mask++ {
		mf := NewMaxFlow(n + 2)
		source := n
		sink := n + 1

		for _, edge := range edges {
			mf.AddEdge(edge[0], edge[1], edge[2])
		}

		totalFlow := 0
		count := 0

		for i := 0; i < k; i++ {
			if mask&(1<<i) != 0 {
				req := requests[i]
				mf.AddEdge(source, req[0], req[2])
				mf.AddEdge(req[1], sink, req[2])
				totalFlow += req[2]
				count++
			}
		}

		flow := mf.MaxFlow(source, sink)
		if flow == totalFlow && count > maxRequests {
			maxRequests = count
		}
	}

	return maxRequests
}

func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}