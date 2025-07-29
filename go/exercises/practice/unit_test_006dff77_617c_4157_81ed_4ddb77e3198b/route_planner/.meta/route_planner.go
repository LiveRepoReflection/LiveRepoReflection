package route_planner

import (
	"container/heap"
	"errors"
	"strconv"
	"strings"
)

type Edge struct {
	to     int
	weight int
}

var graph [][]Edge
var numNodes int

// Initialize parses the provided graphData string and builds an internal graph representation.
func Initialize(graphData string) {
	fields := strings.Fields(graphData)
	if len(fields) < 2 {
		return
	}
	n, _ := strconv.Atoi(fields[0])
	e, _ := strconv.Atoi(fields[1])
	numNodes = n
	graph = make([][]Edge, numNodes)
	// There should be exactly 3*e values following.
	for i := 0; i < e; i++ {
		base := 2 + i*3
		if base+2 >= len(fields) {
			break
		}
		from, _ := strconv.Atoi(fields[base])
		to, _ := strconv.Atoi(fields[base+1])
		weight, _ := strconv.Atoi(fields[base+2])
		graph[from] = append(graph[from], Edge{to: to, weight: weight})
	}
}

// FindOptimalRoute finds the optimal route from startNodeId to endNodeId such that
// the total time is minimized and the route arrives before the deadline.
// If a valid route exists, it returns the route slice, total travel time, penalty fee, and nil error.
// If no such route exists, it returns an error.
func FindOptimalRoute(startNodeId, endNodeId int, deadline int, penalty float64) ([]int, int, float64, error) {
	if startNodeId < 0 || startNodeId >= numNodes || endNodeId < 0 || endNodeId >= numNodes {
		return nil, 0, 0, errors.New("invalid start or end node id")
	}
	// If start equals destination, return immediately.
	if startNodeId == endNodeId {
		return []int{startNodeId}, 0, 0, nil
	}

	// dijkstra algorithm
	const INF = 1 << 30
	dist := make([]int, numNodes)
	prev := make([]int, numNodes)
	for i := range dist {
		dist[i] = INF
		prev[i] = -1
	}
	dist[startNodeId] = 0

	pq := &PriorityQueue{}
	heap.Init(pq)
	heap.Push(pq, &Item{node: startNodeId, distance: 0})

	for pq.Len() > 0 {
		current := heap.Pop(pq).(*Item)
		u := current.node
		if current.distance > dist[u] {
			continue
		}
		// Early exit if we reached destination
		if u == endNodeId {
			break
		}
		for _, edge := range graph[u] {
			v := edge.to
			newDist := dist[u] + edge.weight
			if newDist < dist[v] {
				dist[v] = newDist
				prev[v] = u
				heap.Push(pq, &Item{node: v, distance: newDist})
			}
		}
	}

	if dist[endNodeId] == INF || dist[endNodeId] > deadline {
		return nil, 0, 0, errors.New("no valid route found within the deadline")
	}

	// reconstruct path
	path := []int{}
	for u := endNodeId; u != -1; u = prev[u] {
		path = append([]int{u}, path...)
	}

	// As the route is within deadline, penalty fee is 0.
	return path, dist[endNodeId], 0, nil
}

// UpdateEdgeWeight updates the weight of the edge from fromNodeId to toNodeId.
func UpdateEdgeWeight(fromNodeId, toNodeId int, newWeight int) {
	if fromNodeId < 0 || fromNodeId >= numNodes {
		return
	}
	edges := graph[fromNodeId]
	for i := range edges {
		if edges[i].to == toNodeId {
			graph[fromNodeId][i].weight = newWeight
			break
		}
	}
}

// PriorityQueue and Item implementation for Dijkstra's algorithm.

type Item struct {
	node     int
	distance int
	index    int
}

type PriorityQueue []*Item

func (pq PriorityQueue) Len() int { 
	return len(pq) 
}

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
	item.index = -1 // for safety
	*pq = old[0 : n-1]
	return item
}