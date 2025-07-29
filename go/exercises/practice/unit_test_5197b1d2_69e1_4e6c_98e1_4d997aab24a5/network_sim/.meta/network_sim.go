package network_sim

import (
	"math/rand"
	"sort"
)

type Message struct {
	Source       int
	Destination  int
	Size         int
	CreationTime int
}

type Node struct {
	ID              int
	Capacity        int
	FailureProb     float64
	Downtime        int
	FailureTime     int
	Queue           []Message
	ProcessingQueue []Message
}

type Network struct {
	Bandwidth     int
	Latency       int
	CurrentLoad   int
	TransitQueue  []Message
	DeliveryQueue map[int][]Message
}

func SimulateNetwork(
	n int,
	nodeCapacities []int,
	failureProbabilities []float64,
	downtime int,
	networkBandwidth int,
	networkLatency int,
	messages []Message,
	simulationDuration int,
) []float64 {
	// Initialize nodes
	nodes := make([]Node, n)
	for i := 0; i < n; i++ {
		nodes[i] = Node{
			ID:          i,
			Capacity:    nodeCapacities[i],
			FailureProb: failureProbabilities[i],
			Downtime:    downtime,
			Queue:       make([]Message, 0),
		}
	}

	// Initialize network
	network := Network{
		Bandwidth:     networkBandwidth,
		Latency:       networkLatency,
		DeliveryQueue: make(map[int][]Message),
	}

	// Sort messages by creation time
	sort.Slice(messages, func(i, j int) bool {
		return messages[i].CreationTime < messages[j].CreationTime
	})

	latencies := make([]float64, 0, len(messages))

	// Simulation loop
	for currentTime := 0; currentTime <= simulationDuration; currentTime++ {
		// Inject messages at their creation time
		for len(messages) > 0 && messages[0].CreationTime == currentTime {
			msg := messages[0]
			messages = messages[1:]
			nodes[msg.Source].Queue = append(nodes[msg.Source].Queue, msg)
		}

		// Process each node
		for i := range nodes {
			// Check for node failure/recovery
			if nodes[i].FailureTime > 0 {
				nodes[i].FailureTime--
				continue
			} else if rand.Float64() < nodes[i].FailureProb {
				nodes[i].FailureTime = nodes[i].Downtime
				continue
			}

			// Process messages in queue
			remainingCapacity := nodes[i].Capacity
			for len(nodes[i].Queue) > 0 && remainingCapacity > 0 {
				msg := nodes[i].Queue[0]
				nodes[i].Queue = nodes[i].Queue[1:]

				if msg.Size <= remainingCapacity {
					remainingCapacity -= msg.Size
					if msg.Destination == nodes[i].ID {
						latency := float64(currentTime - msg.CreationTime)
						latencies = append(latencies, latency)
					} else {
						network.TransitQueue = append(network.TransitQueue, msg)
					}
				} else {
					nodes[i].Queue = append([]Message{msg}, nodes[i].Queue...)
					break
				}
			}
		}

		// Process network transmission
		network.CurrentLoad = 0
		newTransitQueue := make([]Message, 0)
		for _, msg := range network.TransitQueue {
			if network.CurrentLoad+msg.Size <= network.Bandwidth {
				network.CurrentLoad += msg.Size
				deliveryTime := currentTime + network.Latency
				network.DeliveryQueue[deliveryTime] = append(network.DeliveryQueue[deliveryTime], msg)
			}
		}
		network.TransitQueue = newTransitQueue

		// Deliver messages that have completed transit
		if deliveryMsgs, exists := network.DeliveryQueue[currentTime]; exists {
			for _, msg := range deliveryMsgs {
				nodes[msg.Destination].Queue = append(nodes[msg.Destination].Queue, msg)
			}
			delete(network.DeliveryQueue, currentTime)
		}
	}

	return latencies
}