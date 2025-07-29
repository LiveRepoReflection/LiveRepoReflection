package quantum_network

import (
	"container/heap"
	"math"
)

type Node struct {
	id           int
	minLinks     int
	minCoherence int
}

type PriorityQueue []*Node

func (pq PriorityQueue) Len() int { return len(pq) }

func (pq PriorityQueue) Less(i, j int) bool {
	if pq[i].minLinks == pq[j].minLinks {
		return pq[i].minCoherence > pq[j].minCoherence
	}
	return pq[i].minLinks < pq[j].minLinks
}

func (pq PriorityQueue) Swap(i, j int) {
	pq[i], pq[j] = pq[j], pq[i]
}

func (pq *PriorityQueue) Push(x interface{}) {
	*pq = append(*pq, x.(*Node))
}

func (pq *PriorityQueue) Pop() interface{} {
	old := *pq
	n := len(old)
	item := old[n-1]
	*pq = old[0 : n-1]
	return item
}

func MinEntangledLinks(n int, entanglementMatrix [][]bool, coherenceLevels []int, source int, destination int) int {
	if source == destination {
		return 0
	}

	visited := make([]bool, n)
	links := make([]int, n)
	coherences := make([]int, n)
	for i := range links {
		links[i] = math.MaxInt32
		coherences[i] = -1
	}
	links[source] = 0
	coherences[source] = coherenceLevels[source]

	pq := make(PriorityQueue, 0)
	heap.Push(&pq, &Node{
		id:           source,
		minLinks:     0,
		minCoherence: coherenceLevels[source],
	})

	for pq.Len() > 0 {
		current := heap.Pop(&pq).(*Node)
		if current.id == destination {
			return current.minLinks
		}

		if visited[current.id] {
			continue
		}
		visited[current.id] = true

		for neighbor := 0; neighbor < n; neighbor++ {
			if !entanglementMatrix[current.id][neighbor] || current.id == neighbor {
				continue
			}

			newLinks := current.minLinks + 1
			newMinCoherence := current.minCoherence
			if coherenceLevels[neighbor] < newMinCoherence {
				newMinCoherence = coherenceLevels[neighbor]
			}

			if newLinks < links[neighbor] || 
			   (newLinks == links[neighbor] && newMinCoherence > coherences[neighbor]) {
				links[neighbor] = newLinks
				coherences[neighbor] = newMinCoherence
				heap.Push(&pq, &Node{
					id:           neighbor,
					minLinks:     newLinks,
					minCoherence: newMinCoherence,
				})
			}
		}
	}

	if links[destination] == math.MaxInt32 {
		return -1
	}
	return links[destination]
}