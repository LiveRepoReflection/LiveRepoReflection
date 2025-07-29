package min_flight_cost

import (
	"container/heap"
	"math"
)

type Flight struct {
	src          int
	dst          int
	departure    int
	arrival      int
	cost         int
}

type Node struct {
	city       int
	time       int
	cost       int
	flights    int
	index      int
}

type PriorityQueue []*Node

func (pq PriorityQueue) Len() int { return len(pq) }

func (pq PriorityQueue) Less(i, j int) bool {
	return pq[i].cost < pq[j].cost
}

func (pq PriorityQueue) Swap(i, j int) {
	pq[i], pq[j] = pq[j], pq[i]
	pq[i].index = i
	pq[j].index = j
}

func (pq *PriorityQueue) Push(x interface{}) {
	n := len(*pq)
	node := x.(*Node)
	node.index = n
	*pq = append(*pq, node)
}

func (pq *PriorityQueue) Pop() interface{} {
	old := *pq
	n := len(old)
	node := old[n-1]
	old[n-1] = nil
	node.index = -1
	*pq = old[0 : n-1]
	return node
}

func MinFlightCost(n int, flights [][]int, src int, dst int, startTime int64, maxLayover int, maxFlights int) int {
	if src == dst {
		return 0
	}

	flightMap := make(map[int][]Flight)
	for _, f := range flights {
		flight := Flight{
			src:       f[0],
			dst:       f[1],
			departure: f[2],
			arrival:   f[3],
			cost:      f[4],
		}
		flightMap[flight.src] = append(flightMap[flight.src], flight)
	}

	pq := make(PriorityQueue, 0)
	heap.Init(&pq)
	heap.Push(&pq, &Node{
		city:    src,
		time:    int(startTime),
		cost:    0,
		flights: 0,
	})

	minCost := make([][]int, n)
	for i := range minCost {
		minCost[i] = make([]int, maxFlights+1)
		for j := range minCost[i] {
			minCost[i][j] = math.MaxInt32
		}
	}
	minCost[src][0] = 0

	for pq.Len() > 0 {
		current := heap.Pop(&pq).(*Node)
		if current.city == dst {
			return current.cost
		}
		if current.flights >= maxFlights {
			continue
		}

		for _, flight := range flightMap[current.city] {
			if flight.departure < current.time {
				continue
			}
			if current.city != src && flight.departure-current.time > maxLayover {
				continue
			}

			newCost := current.cost + flight.cost
			newFlights := current.flights + 1
			if newFlights > maxFlights {
				continue
			}

			if newCost < minCost[flight.dst][newFlights] {
				minCost[flight.dst][newFlights] = newCost
				heap.Push(&pq, &Node{
					city:    flight.dst,
					time:    flight.arrival,
					cost:    newCost,
					flights: newFlights,
				})
			}
		}
	}

	return -1
}