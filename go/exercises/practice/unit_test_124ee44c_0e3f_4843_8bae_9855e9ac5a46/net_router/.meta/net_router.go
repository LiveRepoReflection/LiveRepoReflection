package net_router

import (
	"container/heap"
	"math"
	"sync"
)

type RouteInfo struct {
	NextHop   string
	Cost      int
	Reachable bool
}

type NetworkRouter struct {
	mu           sync.RWMutex
	devices      map[string]struct{}
	graph        map[string]map[string]int
	routingTable map[string]map[string]RouteInfo
}

func NewNetworkRouter() *NetworkRouter {
	return &NetworkRouter{
		devices:      make(map[string]struct{}),
		graph:        make(map[string]map[string]int),
		routingTable: make(map[string]map[string]RouteInfo),
	}
}

func (nr *NetworkRouter) AddDevice(deviceID string) {
	nr.mu.Lock()
	defer nr.mu.Unlock()
	if _, exists := nr.devices[deviceID]; exists {
		return
	}
	nr.devices[deviceID] = struct{}{}
	if _, exists := nr.graph[deviceID]; !exists {
		nr.graph[deviceID] = make(map[string]int)
	}
}

func (nr *NetworkRouter) RemoveDevice(deviceID string) {
	nr.mu.Lock()
	defer nr.mu.Unlock()
	if _, exists := nr.devices[deviceID]; !exists {
		return
	}
	delete(nr.devices, deviceID)
	delete(nr.graph, deviceID)
	for src := range nr.graph {
		delete(nr.graph[src], deviceID)
	}
}

func (nr *NetworkRouter) AddConnection(sourceID string, destinationID string, cost int) {
	if cost <= 0 {
		return
	}
	nr.mu.Lock()
	defer nr.mu.Unlock()
	if _, exists := nr.devices[sourceID]; !exists {
		return
	}
	if _, exists := nr.devices[destinationID]; !exists {
		return
	}
	if _, exists := nr.graph[sourceID]; !exists {
		nr.graph[sourceID] = make(map[string]int)
	}
	nr.graph[sourceID][destinationID] = cost
}

func (nr *NetworkRouter) RemoveConnection(sourceID string, destinationID string) {
	nr.mu.Lock()
	defer nr.mu.Unlock()
	if _, exists := nr.graph[sourceID]; exists {
		delete(nr.graph[sourceID], destinationID)
	}
}

type pqItem struct {
	node    string
	cost    int
	nextHop string
	index   int
}

type PriorityQueue []*pqItem

func (pq PriorityQueue) Len() int { return len(pq) }

func (pq PriorityQueue) Less(i, j int) bool { return pq[i].cost < pq[j].cost }

func (pq PriorityQueue) Swap(i, j int) {
	pq[i], pq[j] = pq[j], pq[i]
	pq[i].index = i
	pq[j].index = j
}

func (pq *PriorityQueue) Push(x interface{}) {
	n := len(*pq)
	item := x.(*pqItem)
	item.index = n
	*pq = append(*pq, item)
}

func (pq *PriorityQueue) Pop() interface{} {
	old := *pq
	n := len(old)
	item := old[n-1]
	item.index = -1
	*pq = old[0 : n-1]
	return item
}

func (nr *NetworkRouter) UpdateRoutingTable() {
	nr.mu.Lock()
	defer nr.mu.Unlock()

	newRoutingTable := make(map[string]map[string]RouteInfo)
	for src := range nr.devices {
		routes := nr.dijkstra(src)
		newRoutingTable[src] = routes
	}
	nr.routingTable = newRoutingTable
}

func (nr *NetworkRouter) dijkstra(source string) map[string]RouteInfo {
	dist := make(map[string]int)
	nextHop := make(map[string]string)
	for device := range nr.devices {
		dist[device] = math.MaxInt64
		nextHop[device] = ""
	}
	dist[source] = 0
	nextHop[source] = source

	pq := make(PriorityQueue, 0)
	heap.Init(&pq)
	heap.Push(&pq, &pqItem{node: source, cost: 0, nextHop: source})

	for pq.Len() > 0 {
		currentItem := heap.Pop(&pq).(*pqItem)
		currentNode := currentItem.node
		currentCost := currentItem.cost

		if currentCost > dist[currentNode] {
			continue
		}

		for neighbor, edgeCost := range nr.graph[currentNode] {
			newCost := currentCost + edgeCost
			if newCost < dist[neighbor] {
				dist[neighbor] = newCost
				if currentNode == source {
					nextHop[neighbor] = neighbor
				} else {
					nextHop[neighbor] = nextHop[currentNode]
				}
				heap.Push(&pq, &pqItem{node: neighbor, cost: newCost, nextHop: nextHop[neighbor]})
			}
		}
	}

	routes := make(map[string]RouteInfo)
	for device, d := range dist {
		if d == math.MaxInt64 {
			routes[device] = RouteInfo{NextHop: "", Cost: d, Reachable: false}
		} else {
			routes[device] = RouteInfo{NextHop: nextHop[device], Cost: d, Reachable: true}
		}
	}
	return routes
}

func (nr *NetworkRouter) GetNextHop(sourceID string, destinationIP string) (string, int, bool) {
	nr.mu.RLock()
	defer nr.mu.RUnlock()
	if _, exists := nr.devices[sourceID]; !exists {
		return "", 0, false
	}
	if sourceID == destinationIP {
		return sourceID, 0, true
	}
	routes, exists := nr.routingTable[sourceID]
	if !exists {
		return "", 0, false
	}
	routeInfo, exists := routes[destinationIP]
	if !exists || !routeInfo.Reachable {
		return "", 0, false
	}
	return routeInfo.NextHop, routeInfo.Cost, true
}