package rideshare_network

import (
	"container/heap"
)

// Distance is a mock function that calculates distance between nodes
// In a real implementation, this would use actual distance calculations
func Distance(startNode, endNode int) int {
	return abs(startNode - endNode)
}

func abs(x int) int {
	if x < 0 {
		return -x
	}
	return x
}

// NodeDiscovery returns all nodes within maxDistance from startNode
func NodeDiscovery(adjacencyList map[int][]int, startNode int, maxDistance int) []int {
	if maxDistance < 0 {
		return []int{}
	}

	visited := make(map[int]bool)
	queue := [][]int{{startNode, 0}}
	visited[startNode] = true
	result := []int{}

	for len(queue) > 0 {
		current := queue[0]
		queue = queue[1:]
		node, dist := current[0], current[1]

		if dist <= maxDistance {
			result = append(result, node)
		}

		if dist == maxDistance {
			continue
		}

		for _, neighbor := range adjacencyList[node] {
			if !visited[neighbor] {
				visited[neighbor] = true
				queue = append(queue, []int{neighbor, dist + 1})
			}
		}
	}

	return result
}

// RideMatching finds the optimal driver for a rider
func RideMatching(adjacencyList map[int][]int, riderNode int, driverNodes []int, riderDestination int) int {
	if len(driverNodes) == 0 {
		return -1
	}

	minTotal := -1
	bestDriver := -1

	for _, driver := range driverNodes {
		driverToRider := Distance(driver, riderNode)
		riderToDest := Distance(riderNode, riderDestination)
		total := driverToRider + riderToDest

		if minTotal == -1 || total < minTotal {
			minTotal = total
			bestDriver = driver
		}
	}

	return bestDriver
}

// NetworkPartitioning counts the number of connected components
func NetworkPartitioning(adjacencyList map[int][]int) int {
	visited := make(map[int]bool)
	count := 0

	for node := range adjacencyList {
		if !visited[node] {
			count++
			queue := []int{node}
			visited[node] = true

			for len(queue) > 0 {
				current := queue[0]
				queue = queue[1:]

				for _, neighbor := range adjacencyList[current] {
					if !visited[neighbor] {
						visited[neighbor] = true
						queue = append(queue, neighbor)
					}
				}
			}
		}
	}

	return count
}

// Below is an alternative optimized implementation of RideMatching using Dijkstra's algorithm

type Item struct {
	node     int
	distance int
	index    int
}

type PriorityQueue []*Item

func (pq PriorityQueue) Len() int { return len(pq) }

func (pq PriorityQueue) Less(i, j int) bool {
	return pq[i].distance < pq[j].distance
}

func (pq PriorityQueue) Swap(i, j int) {
	pq[i], pq[j] = pq[j], pq[i]
	pq[i].index = i
	pq[j].index = j
}

func (pq *PriorityQueue) Push(x interface{}) {
	n := len(*pq)
	item := x.(*Item)
	item.index = n
	*pq = append(*pq, item)
}

func (pq *PriorityQueue) Pop() interface{} {
	old := *pq
	n := len(old)
	item := old[n-1]
	old[n-1] = nil
	item.index = -1
	*pq = old[0 : n-1]
	return item
}

// OptimizedRideMatching uses Dijkstra's algorithm for more accurate pathfinding
func OptimizedRideMatching(adjacencyList map[int][]int, riderNode int, driverNodes []int, riderDestination int) int {
	if len(driverNodes) == 0 {
		return -1
	}

	// Precompute distances from rider to all nodes
	riderDistances := dijkstra(adjacencyList, riderNode)
	destDistances := dijkstra(adjacencyList, riderDestination)

	minTotal := -1
	bestDriver := -1

	for _, driver := range driverNodes {
		driverToRider := riderDistances[driver]
		riderToDest := destDistances[driver]
		total := driverToRider + riderToDest

		if minTotal == -1 || total < minTotal {
			minTotal = total
			bestDriver = driver
		}
	}

	return bestDriver
}

func dijkstra(adjacencyList map[int][]int, start int) map[int]int {
	distances := make(map[int]int)
	for node := range adjacencyList {
		distances[node] = 1 << 30 // Infinity equivalent
	}
	distances[start] = 0

	pq := make(PriorityQueue, 0)
	heap.Init(&pq)
	heap.Push(&pq, &Item{node: start, distance: 0})

	for pq.Len() > 0 {
		item := heap.Pop(&pq).(*Item)
		u := item.node

		for _, v := range adjacencyList[u] {
			newDist := distances[u] + Distance(u, v)
			if newDist < distances[v] {
				distances[v] = newDist
				heap.Push(&pq, &Item{node: v, distance: newDist})
			}
		}
	}

	return distances
}