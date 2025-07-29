package network_congestion

import (
	"container/list"
	"sort"
)

type Router struct {
	ID       int
	Capacity int
	NextHop  []int
}

type Packet struct {
	Source       int
	Destination  int
	CreationTime int
	currentHop   int
	pathIndex    int
}

type RouterState struct {
	queue    *list.List
	capacity int
}

func SimulateNetwork(routers []Router, packets []Packet, routingTable map[int][]int, simulationDuration int) int {
	// Initialize router states
	routerStates := make(map[int]*RouterState)
	for _, router := range routers {
		routerStates[router.ID] = &RouterState{
			queue:    list.New(),
			capacity: router.Capacity,
		}
	}

	// Sort packets by creation time
	sort.Slice(packets, func(i, j int) bool {
		return packets[i].CreationTime < packets[j].CreationTime
	})

	// Initialize packet paths
	validPackets := make([]Packet, 0, len(packets))
	for _, pkt := range packets {
		path, exists := routingTable[pkt.Source]
		if !exists {
			continue
		}
		valid := false
		for _, hop := range path {
			if hop == pkt.Destination {
				valid = true
				break
			}
		}
		if valid {
			newPkt := pkt
			newPkt.currentHop = pkt.Source
			newPkt.pathIndex = 0
			validPackets = make([]Packet, 0, len(packets))
			for _, pkt := range packets {
				path, exists := routingTable[pkt.Source]
				if !exists {
					continue
				}
				valid := false
				for _, hop := range path {
					if hop == pkt.Destination {
						valid = true
						break
					}
				}
				if valid {
					newPkt := pkt
					newPkt.currentHop = pkt.Source
					newPkt.pathIndex = 0
					validPackets = append(validPackets, newPkt)
				}
			}
		}
	}

	delivered := 0

	for currentTime := 0; currentTime <= simulationDuration; currentTime++ {
		// Process packets arriving at this time
		for i := 0; i < len(validPackets); i++ {
			if validPackets[i].CreationTime == currentTime {
				rs := routerStates[validPackets[i].currentHop]
				if rs.queue.Len() < rs.capacity {
					rs.queue.PushBack(&validPackets[i])
				}
			}
		}

		// Process each router's queue
		for _, router := range routers {
			rs := routerStates[router.ID]
			packetsToProcess := rs.capacity
			if rs.queue.Len() < packetsToProcess {
				packetsToProcess = rs.queue.Len()
			}

			for i := 0; i < packetsToProcess; i++ {
				front := rs.queue.Front()
				pkt := front.Value.(*Packet)

				// Check if packet is at destination
				if len(router.NextHop) == 0 {
					delivered++
					rs.queue.Remove(front)
					continue
				}

				// Get next hop
				path := routingTable[pkt.Source]
				if pkt.pathIndex+1 >= len(path) {
					rs.queue.Remove(front)
					continue
				}
				nextHop := path[pkt.pathIndex+1]

				// Forward packet to next router
				nextRs := routerStates[nextHop]
				if nextRs.queue.Len() < nextRs.capacity {
					newPkt := *pkt
					newPkt.currentHop = nextHop
					newPkt.pathIndex++
					nextRs.queue.PushBack(&newPkt)
				}
				rs.queue.Remove(front)
			}
		}
	}

	return delivered
}