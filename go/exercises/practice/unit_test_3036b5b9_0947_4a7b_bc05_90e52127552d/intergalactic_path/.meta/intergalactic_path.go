package intergalactic

import (
	"container/heap"
)

// Network represents the intergalactic network of planets and stargates
type Network struct {
	planets   map[int]bool
	stargates map[int]map[int]map[int]int // from -> to -> cost -> count
}

// NewNetwork creates a new empty network
func NewNetwork() *Network {
	return &Network{
		planets:   make(map[int]bool),
		stargates: make(map[int]map[int]map[int]int),
	}
}

// AddPlanet adds a new planet to the network
func (n *Network) AddPlanet(planetID int) {
	if !n.planets[planetID] {
		n.planets[planetID] = true
		n.stargates[planetID] = make(map[int]map[int]int)
	}
}

// RemovePlanet removes a planet and all its connected stargates
func (n *Network) RemovePlanet(planetID int) {
	if !n.planets[planetID] {
		return
	}
	
	// Remove all stargates connected to this planet
	for otherPlanet := range n.stargates[planetID] {
		delete(n.stargates[otherPlanet], planetID)
	}
	delete(n.stargates, planetID)
	delete(n.planets, planetID)
}

// AddStargate adds a new stargate between two planets
func (n *Network) AddStargate(planet1, planet2, cost int) {
	if !n.planets[planet1] || !n.planets[planet2] {
		return
	}

	// Initialize maps if they don't exist
	if n.stargates[planet1][planet2] == nil {
		n.stargates[planet1][planet2] = make(map[int]int)
	}
	if n.stargates[planet2][planet1] == nil {
		n.stargates[planet2][planet1] = make(map[int]int)
	}

	// Add or increment count for this cost
	n.stargates[planet1][planet2][cost]++
	n.stargates[planet2][planet1][cost]++
}

// RemoveStargate removes a stargate between two planets with specific cost
func (n *Network) RemoveStargate(planet1, planet2, cost int) {
	if !n.planets[planet1] || !n.planets[planet2] {
		return
	}

	if n.stargates[planet1][planet2] != nil && n.stargates[planet1][planet2][cost] > 0 {
		n.stargates[planet1][planet2][cost]--
		n.stargates[planet2][planet1][cost]--

		if n.stargates[planet1][planet2][cost] == 0 {
			delete(n.stargates[planet1][planet2], cost)
			delete(n.stargates[planet2][planet1], cost)
		}
	}
}

// UpdateStargateCost updates the cost of an existing stargate
func (n *Network) UpdateStargateCost(planet1, planet2, oldCost, newCost int) {
	if !n.planets[planet1] || !n.planets[planet2] {
		return
	}

	if n.stargates[planet1][planet2] != nil && n.stargates[planet1][planet2][oldCost] > 0 {
		n.RemoveStargate(planet1, planet2, oldCost)
		n.AddStargate(planet1, planet2, newCost)
	}
}

// PriorityQueueItem represents an item in the priority queue
type PriorityQueueItem struct {
	planetID int
	cost     int
	index    int
}

// PriorityQueue implements heap.Interface
type PriorityQueue []*PriorityQueueItem

func (pq PriorityQueue) Len() int           { return len(pq) }
func (pq PriorityQueue) Less(i, j int) bool { return pq[i].cost < pq[j].cost }
func (pq PriorityQueue) Swap(i, j int) {
	pq[i], pq[j] = pq[j], pq[i]
	pq[i].index = i
	pq[j].index = j
}

func (pq *PriorityQueue) Push(x interface{}) {
	n := len(*pq)
	item := x.(*PriorityQueueItem)
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

// QueryShortestPath finds the shortest path between two planets
func (n *Network) QueryShortestPath(planet1, planet2 int) int {
	if !n.planets[planet1] || !n.planets[planet2] {
		return -1
	}

	if planet1 == planet2 {
		return 0
	}

	// Initialize distances map and priority queue
	distances := make(map[int]int)
	pq := make(PriorityQueue, 0)
	heap.Init(&pq)

	// Set initial distance for starting planet
	distances[planet1] = 0
	heap.Push(&pq, &PriorityQueueItem{planetID: planet1, cost: 0})

	// Dijkstra's algorithm
	for pq.Len() > 0 {
		current := heap.Pop(&pq).(*PriorityQueueItem)
		currentPlanet := current.planetID
		currentCost := current.cost

		// If we've found a shorter path already, skip
		if currentCost > distances[currentPlanet] {
			continue
		}

		// If we've reached the destination, return the cost
		if currentPlanet == planet2 {
			return currentCost
		}

		// Check all neighboring planets
		for neighborPlanet, costs := range n.stargates[currentPlanet] {
			for edgeCost, count := range costs {
				if count > 0 {
					newCost := currentCost + edgeCost
					if dist, exists := distances[neighborPlanet]; !exists || newCost < dist {
						distances[neighborPlanet] = newCost
						heap.Push(&pq, &PriorityQueueItem{
							planetID: neighborPlanet,
							cost:     newCost,
						})
					}
				}
			}
		}
	}

	return -1 // No path found
}