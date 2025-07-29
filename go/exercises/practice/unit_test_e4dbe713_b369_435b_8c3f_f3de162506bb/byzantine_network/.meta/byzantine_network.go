package byzantine_network

import (
	"container/heap"
	"math"
)

type Edge struct {
	u, v int
}

type Partition struct {
	groups       [][]int
	groupSizes   []int
	groupIndices []int
	cutSize      int
}

type PriorityQueue []*Partition

func (pq PriorityQueue) Len() int { return len(pq) }

func (pq PriorityQueue) Less(i, j int) bool {
	return pq[i].cutSize < pq[j].cutSize
}

func (pq PriorityQueue) Swap(i, j int) {
	pq[i], pq[j] = pq[j], pq[i]
}

func (pq *PriorityQueue) Push(x interface{}) {
	item := x.(*Partition)
	*pq = append(*pq, item)
}

func (pq *PriorityQueue) Pop() interface{} {
	old := *pq
	n := len(old)
	item := old[n-1]
	*pq = old[0 : n-1]
	return item
}

func OptimalPartition(N int, K int, edges [][2]int, groupSizes []int) int {
	if len(groupSizes) != K {
		return -1
	}

	totalRequested := 0
	for _, size := range groupSizes {
		if size > 0 && size < 4 {
			return -1
		}
		totalRequested += size
	}
	if totalRequested > N {
		return -1
	}

	adj := make([][]int, N)
	for _, edge := range edges {
		u, v := edge[0], edge[1]
		adj[u] = append(adj[u], v)
		adj[v] = append(adj[v], u)
	}

	initialPartition := &Partition{
		groups:       make([][]int, K),
		groupSizes:   make([]int, K),
		groupIndices: make([]int, N),
		cutSize:      0,
	}

	for i := 0; i < N; i++ {
		initialPartition.groupIndices[i] = -1
	}

	pq := make(PriorityQueue, 0)
	heap.Init(&pq)
	heap.Push(&pq, initialPartition)

	minCut := math.MaxInt32

	for pq.Len() > 0 {
		current := heap.Pop(&pq).(*Partition)

		if current.cutSize >= minCut {
			continue
		}

		allAssigned := true
		for i := 0; i < N; i++ {
			if current.groupIndices[i] == -1 {
				allAssigned = false
				break
			}
		}

		if allAssigned {
			if current.cutSize < minCut {
				minCut = current.cutSize
			}
			continue
		}

		nextNode := -1
		for i := 0; i < N; i++ {
			if current.groupIndices[i] == -1 {
				nextNode = i
				break
			}
		}

		for group := 0; group < K; group++ {
			if current.groupSizes[group] >= groupSizes[group] {
				continue
			}

			newCutSize := current.cutSize
			for _, neighbor := range adj[nextNode] {
				if current.groupIndices[neighbor] != -1 && current.groupIndices[neighbor] != group {
					newCutSize++
				}
			}

			newPartition := &Partition{
				groups:       make([][]int, K),
				groupSizes:   make([]int, K),
				groupIndices: make([]int, N),
				cutSize:      newCutSize,
			}

			copy(newPartition.groupIndices, current.groupIndices)
			newPartition.groupIndices[nextNode] = group

			copy(newPartition.groupSizes, current.groupSizes)
			newPartition.groupSizes[group]++

			for i := 0; i < K; i++ {
				newPartition.groups[i] = make([]int, len(current.groups[i]))
				copy(newPartition.groups[i], current.groups[i])
			}
			newPartition.groups[group] = append(newPartition.groups[group], nextNode)

			heap.Push(&pq, newPartition)
		}
	}

	if minCut == math.MaxInt32 {
		return -1
	}
	return minCut
}