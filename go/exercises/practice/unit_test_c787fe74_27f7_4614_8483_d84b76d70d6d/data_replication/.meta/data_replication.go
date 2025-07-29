package data_replication

import (
	"container/heap"
	"math"
)

// OptimalReplicationCost computes the total cost defined as the
// sum of replication time and data storage costs. It determines the maximum 
// bottleneck bandwidth for each replica data center (non primary) and uses 
// the slowest replication time among these as the overall replication time.
func OptimalReplicationCost(N int, dataCenterCosts []int, bandwidthMatrix [][]int, dataSize int, primaryDataCenter int) float64 {
	// best[i] will hold the maximum possible minimum bandwidth from primary to node i.
	best := make([]int, N)
	for i := 0; i < N; i++ {
		best[i] = -1
	}
	// Set primary bandwidth to a large value.
	best[primaryDataCenter] = math.MaxInt64

	// Priority queue to perform a modified Dijkstra's algorithm to maximize the bottleneck bandwidth.
	pq := &PriorityQueue{}
	heap.Init(pq)
	heap.Push(pq, &Item{
		index:     primaryDataCenter,
		bandwidth: best[primaryDataCenter],
	})

	for pq.Len() > 0 {
		current := heap.Pop(pq).(*Item)
		// If the current item's bandwidth is not up-to-date, skip it.
		if current.bandwidth != best[current.index] {
			continue
		}
		// Relax edges from current node.
		for neighbor := 0; neighbor < N; neighbor++ {
			edgeBandwidth := bandwidthMatrix[current.index][neighbor]
			if edgeBandwidth > 0 {
				// The bottleneck of the new path is the minimum of the current bandwidth and the edge's bandwidth.
				candidate := min(current.bandwidth, edgeBandwidth)
				// If the new path offers a better bottleneck bandwidth, update and push to queue.
				if candidate > best[neighbor] {
					best[neighbor] = candidate
					heap.Push(pq, &Item{
						index:     neighbor,
						bandwidth: candidate,
					})
				}
			}
		}
	}

	// Calculate the replication time as the maximum time taken for any replica.
	replicationTime := 0.0
	for i := 0; i < N; i++ {
		if i == primaryDataCenter {
			continue
		}
		// If a replica is unreachable, return infinity.
		if best[i] <= 0 {
			return math.Inf(1)
		}
		// Time to replicate to node i.
		timeForNode := float64(dataSize) / float64(best[i])
		if timeForNode > replicationTime {
			replicationTime = timeForNode
		}
	}

	// Compute storage costs for all replica data centers.
	storageCost := 0
	for i := 0; i < N; i++ {
		if i == primaryDataCenter {
			continue
		}
		storageCost += dataSize * dataCenterCosts[i]
	}

	totalCost := replicationTime + float64(storageCost)
	return totalCost
}

func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}

// Item represents a data center node with its effective bandwidth from the primary.
type Item struct {
	index     int
	bandwidth int
}

// PriorityQueue implements a max-heap for *Item based on the bandwidth value.
type PriorityQueue []*Item

func (pq PriorityQueue) Len() int { 
	return len(pq) 
}

func (pq PriorityQueue) Less(i, j int) bool {
	// We want a max-heap, so we invert the logic.
	return pq[i].bandwidth > pq[j].bandwidth
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