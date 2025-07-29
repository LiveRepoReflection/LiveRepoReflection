package intercity_express

import (
	"container/heap"
	"errors"
	"math"
)

type RailLine struct {
	StartCity           string
	EndCity             string
	Length              int
	MaxSpeed            int
	MaintenanceCostPerKm int
}

type Query struct {
	StartCity       string
	DestinationCity string
}

type Result struct {
	FastestTime            float64
	MinimumMaintenanceCost int
}

type cityGraph struct {
	cities    map[string]bool
	adjacency map[string][]railEdge
}

type railEdge struct {
	toCity     string
	time       float64
	cost       int
}

type timeCost struct {
	time float64
	cost int
}

type priorityItem struct {
	city      string
	time      float64
	cost      int
	index     int
}

type priorityQueue []*priorityItem

func (pq priorityQueue) Len() int { return len(pq) }

func (pq priorityQueue) Less(i, j int) bool {
	if pq[i].time == pq[j].time {
		return pq[i].cost < pq[j].cost
	}
	return pq[i].time < pq[j].time
}

func (pq priorityQueue) Swap(i, j int) {
	pq[i], pq[j] = pq[j], pq[i]
	pq[i].index = i
	pq[j].index = j
}

func (pq *priorityQueue) Push(x interface{}) {
	n := len(*pq)
	item := x.(*priorityItem)
	item.index = n
	*pq = append(*pq, item)
}

func (pq *priorityQueue) Pop() interface{} {
	old := *pq
	n := len(old)
	item := old[n-1]
	old[n-1] = nil
	item.index = -1
	*pq = old[0 : n-1]
	return item
}

func buildCityGraph(cities []string, railLines []RailLine) (*cityGraph, error) {
	graph := &cityGraph{
		cities:    make(map[string]bool),
		adjacency: make(map[string][]railEdge),
	}

	for _, city := range cities {
		graph.cities[city] = true
		graph.adjacency[city] = []railEdge{}
	}

	for _, line := range railLines {
		if !graph.cities[line.StartCity] || !graph.cities[line.EndCity] {
			return nil, errors.New("rail line references non-existent city")
		}

		time := float64(line.Length) / float64(line.MaxSpeed)
		cost := line.Length * line.MaintenanceCostPerKm
		graph.adjacency[line.StartCity] = append(graph.adjacency[line.StartCity], railEdge{
			toCity: line.EndCity,
			time:   time,
			cost:   cost,
		})
	}

	return graph, nil
}

func FindFastestRoutes(cities []string, railLines []RailLine, queries []Query) ([]Result, error) {
	graph, err := buildCityGraph(cities, railLines)
	if err != nil {
		return nil, err
	}

	results := make([]Result, len(queries))
	for i, query := range queries {
		if !graph.cities[query.StartCity] || !graph.cities[query.DestinationCity] {
			results[i] = Result{FastestTime: -1.00, MinimumMaintenanceCost: -1}
			continue
		}

		timeCostMap := make(map[string]timeCost)
		pq := make(priorityQueue, 0)
		heap.Init(&pq)

		for city := range graph.cities {
			timeCostMap[city] = timeCost{
				time: math.Inf(1),
				cost: math.MaxInt32,
			}
		}

		timeCostMap[query.StartCity] = timeCost{time: 0, cost: 0}
		heap.Push(&pq, &priorityItem{
			city:  query.StartCity,
			time:  0,
			cost:  0,
		})

		for pq.Len() > 0 {
			current := heap.Pop(&pq).(*priorityItem)
			if current.city == query.DestinationCity {
				break
			}

			if current.time > timeCostMap[current.city].time {
				continue
			}

			for _, edge := range graph.adjacency[current.city] {
				newTime := current.time + edge.time
				newCost := current.cost + edge.cost

				if newTime < timeCostMap[edge.toCity].time ||
					(newTime == timeCostMap[edge.toCity].time && newCost < timeCostMap[edge.toCity].cost) {
					timeCostMap[edge.toCity] = timeCost{time: newTime, cost: newCost}
					heap.Push(&pq, &priorityItem{
						city:  edge.toCity,
						time:  newTime,
						cost:  newCost,
					})
				}
			}
		}

		if timeCostMap[query.DestinationCity].time == math.Inf(1) {
			results[i] = Result{FastestTime: -1.00, MinimumMaintenanceCost: -1}
		} else {
			results[i] = Result{
				FastestTime:            roundToTwoDecimal(timeCostMap[query.DestinationCity].time),
				MinimumMaintenanceCost: timeCostMap[query.DestinationCity].cost,
			}
		}
	}

	return results, nil
}

func roundToTwoDecimal(num float64) float64 {
	return math.Round(num*100) / 100
}