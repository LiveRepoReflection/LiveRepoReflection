package trade_network

import (
	"container/heap"
	"math"
)

type edge struct {
	to, rev, cap, cost int
}

type mcmf struct {
	n   int
	g   [][]edge
	pot []int
	dist []int
	prevV []int
	prevE []int
}

func newMCMF(n int) *mcmf {
	return &mcmf{
		n:    n,
		g:    make([][]edge, n),
		pot:  make([]int, n),
		dist: make([]int, n),
		prevV: make([]int, n),
		prevE: make([]int, n),
	}
}

func (m *mcmf) addEdge(from, to, cap, cost int) {
	m.g[from] = append(m.g[from], edge{to: to, rev: len(m.g[to]), cap: cap, cost: cost})
	m.g[to] = append(m.g[to], edge{to: from, rev: len(m.g[from]) - 1, cap: 0, cost: -cost})
}

type item struct {
	node, dist int
	index int
}

type priorityQueue []*item

func (pq priorityQueue) Len() int { return len(pq) }
func (pq priorityQueue) Less(i, j int) bool { return pq[i].dist < pq[j].dist }
func (pq priorityQueue) Swap(i, j int) { 
	pq[i], pq[j] = pq[j], pq[i]
	pq[i].index = i
	pq[j].index = j
}

func (pq *priorityQueue) Push(x interface{}) {
	n := len(*pq)
	it := x.(*item)
	it.index = n
	*pq = append(*pq, it)
}

func (pq *priorityQueue) Pop() interface{} {
	old := *pq
	n := len(old)
	it := old[n-1]
	old[n-1] = nil
	it.index = -1
	*pq = old[0 : n-1]
	return it
}

func (m *mcmf) minCostFlow(s, t, f int) (int, int) {
	res := 0
	inf := math.MaxInt32
	// initialize potential to 0 for all nodes
	for i := 0; i < m.n; i++ {
		m.pot[i] = 0
	}
	flow := 0
	for f > 0 {
		// Dijkstra to find shortest path from s to t in residual graph
		for i := 0; i < m.n; i++ {
			m.dist[i] = inf
		}
		m.dist[s] = 0
		pq := &priorityQueue{}
		heap.Init(pq)
		heap.Push(pq, &item{node: s, dist: 0})
		for pq.Len() > 0 {
			it := heap.Pop(pq).(*item)
			v := it.node
			if m.dist[v] < it.dist {
				continue
			}
			for i, e := range m.g[v] {
				if e.cap > 0 && m.dist[e.to] > m.dist[v] + e.cost + m.pot[v] - m.pot[e.to] {
					m.dist[e.to] = m.dist[v] + e.cost + m.pot[v] - m.pot[e.to]
					m.prevV[e.to] = v
					m.prevE[e.to] = i
					heap.Push(pq, &item{node: e.to, dist: m.dist[e.to]})
				}
			}
		}
		if m.dist[t] == inf {
			break
		}
		// update potentials for all nodes
		for v := 0; v < m.n; v++ {
			if m.dist[v] < inf {
				m.pot[v] += m.dist[v]
			}
		}
		// add as much flow as possible along the found path
		addFlow := f
		for v := t; v != s; v = m.prevV[v] {
			if addFlow > m.g[m.prevV[v]][m.prevE[v]].cap {
				addFlow = m.g[m.prevV[v]][m.prevE[v]].cap
			}
		}
		f -= addFlow
		flow += addFlow
		res += addFlow * m.pot[t]
		for v := t; v != s; v = m.prevV[v] {
			e := &m.g[m.prevV[v]][m.prevE[v]]
			e.cap -= addFlow
			m.g[v][e.rev].cap += addFlow
		}
	}
	return flow, res
}

// MinCostTrade computes the minimal total cost of trading goods across the network.
// It processes each good individually and sums the cost.
func MinCostTrade(numPlanets int, numGoods int, demandSupply [][]int, wormholes [][]int, penalty int) int {
	totalCost := 0
	// For each good, build network and compute min cost flow.
	for g := 0; g < numGoods; g++ {
		n := numPlanets + 2
		S := numPlanets
		T := numPlanets + 1
		mcmfNet := newMCMF(n)
		totalDemand := 0
		// For each planet, add supply edge if negative supply, and demand edge if positive.
		for i := 0; i < numPlanets; i++ {
			val := demandSupply[i][g]
			if val < 0 {
				// Supply available: add edge from S -> i with capacity = -val.
				mcmfNet.addEdge(S, i, -val, 0)
			} else if val > 0 {
				// Demand: add edge from i -> T with capacity = val.
				mcmfNet.addEdge(i, T, val, 0)
				totalDemand += val
			}
		}
		// Add penalty edge from S -> T to allow unmet demand at cost penalty per unit.
		mcmfNet.addEdge(S, T, totalDemand, penalty)
		// Add wormhole edges for this good.
		// Each wormhole format: [source, destination, cost, cap_good0, cap_good1, ..., cap_good_(numGoods-1)]
		for _, wh := range wormholes {
			if len(wh) < 3+numGoods {
				continue
			}
			u := wh[0]
			v := wh[1]
			cost := wh[2]
			capacity := wh[3+g]
			if capacity > 0 {
				mcmfNet.addEdge(u, v, capacity, cost)
			}
		}
		// The required flow is totalDemand.
		_, cost := mcmfNet.minCostFlow(S, T, totalDemand)
		totalCost += cost
	}
	return totalCost
}