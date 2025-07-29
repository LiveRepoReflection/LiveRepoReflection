package traffic_reconfig

import (
	"errors"
)

type Edge struct {
	to     int
	rev    int
	cap    int
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
	forward := Edge{to: to, cap: cap, rev: len(mf.graph[to])}
	backward := Edge{to: from, cap: 0, rev: len(mf.graph[from])}
	mf.graph[from] = append(mf.graph[from], forward)
	mf.graph[to] = append(mf.graph[to], backward)
}

func (mf *MaxFlow) bfsLevel(source, sink int, level []int) bool {
	for i := range level {
		level[i] = -1
	}
	level[source] = 0
	q := []int{source}

	for len(q) > 0 {
		v := q[0]
		q = q[1:]

		for _, e := range mf.graph[v] {
			if e.cap > 0 && level[e.to] < 0 {
				level[e.to] = level[v] + 1
				q = append(q, e.to)
			}
		}
	}
	return level[sink] != -1
}

func (mf *MaxFlow) dfsFlow(v, sink, flow int, level, iter []int) int {
	if v == sink {
		return flow
	}

	for i := iter[v]; i < len(mf.graph[v]); i++ {
		e := &mf.graph[v][i]
		if e.cap > 0 && level[v] < level[e.to] {
			d := mf.dfsFlow(e.to, sink, min(flow, e.cap), level, iter)
			if d > 0 {
				e.cap -= d
				mf.graph[e.to][e.rev].cap += d
				return d
			}
		}
	}
	return 0
}

func (mf *MaxFlow) Flow(source, sink int) int {
	flow := 0
	level := make([]int, mf.size)
	iter := make([]int, mf.size)

	for mf.bfsLevel(source, sink, level) {
		for i := range iter {
			iter[i] = 0
		}
		for {
			f := mf.dfsFlow(source, sink, 1<<60, level, iter)
			if f == 0 {
				break
			}
			flow += f
		}
	}
	return flow
}

func MaxTrafficFlow(n int, edges, reducedEdges [][3]int, source, destination int) (int, error) {
	if source < 0 || source >= n || destination < 0 || destination >= n {
		return 0, errors.New("invalid source or destination node")
	}

	// Create capacity map for original edges
	originalCap := make(map[[2]int]int)
	for _, e := range edges {
		key := [2]int{e[0], e[1]}
		originalCap[key] = e[2]
	}

	// Create reduced capacity map
	reducedCap := make(map[[2]int]int)
	for _, e := range reducedEdges {
		key := [2]int{e[0], e[1]}
		if originalCap[key] < e[2] {
			return 0, errors.New("reduced capacity cannot exceed original capacity")
		}
		reducedCap[key] = e[2]
	}

	// Initialize max flow with final capacities
	mf := NewMaxFlow(n)
	for _, e := range edges {
		key := [2]int{e[0], e[1]}
		if cap, exists := reducedCap[key]; exists {
			mf.AddEdge(e[0], e[1], cap)
		} else {
			mf.AddEdge(e[0], e[1], e[2])
		}
	}

	return mf.Flow(source, destination), nil
}

func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}