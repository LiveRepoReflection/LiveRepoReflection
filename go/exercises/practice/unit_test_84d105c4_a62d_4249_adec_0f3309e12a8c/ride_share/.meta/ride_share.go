package ride_share

import (
	"container/heap"
	"math"
)

type path struct {
	node int
	time int
}

type vehicleState struct {
	vehicleIndex int
	location     int
	availableAt  int64
}

func OptimalRideSharing(cityGraph map[int][]Edge, rideRequests []RideRequest, vehicles []Vehicle, maxPassengerCapacity int) ([]RideAssignment, int) {
	assignments := make([]RideAssignment, 0)
	fulfilled := 0

	// Precompute all shortest paths using Dijkstra's algorithm
	allShortestPaths := make(map[int]map[int]int)
	for node := range cityGraph {
		allShortestPaths[node] = shortestPaths(cityGraph, node)
	}

	// Initialize vehicle states
	vehicleStates := make([]vehicleState, len(vehicles))
	for i, v := range vehicles {
		vehicleStates[i] = vehicleState{
			vehicleIndex: i,
			location:     v.Location,
			availableAt:  0,
		}
	}

	// Process ride requests in order of earliest drop-off limit
	processedRides := make([]bool, len(rideRequests))
	for {
		bestAssignment := -1
		bestVehicle := -1
		minCompletionTime := int64(math.MaxInt64)

		for i, ride := range rideRequests {
			if processedRides[i] || ride.Passengers > maxPassengerCapacity {
				continue
			}

			for vIdx, vState := range vehicleStates {
				vehicle := vehicles[vIdx]
				if ride.Passengers > vehicle.Capacity {
					continue
				}

				// Check if vehicle can reach pickup location and complete ride in time
				pickupTime, ok1 := allShortestPaths[vState.location][ride.Start]
				rideTime, ok2 := allShortestPaths[ride.Start][ride.Destination]
				if !ok1 || !ok2 {
					continue
				}

				arrivalAtPickup := vState.availableAt + int64(pickupTime)
				if arrivalAtPickup < ride.PickupTime {
					arrivalAtPickup = ride.PickupTime
				}

				completionTime := arrivalAtPickup + int64(rideTime)
				if completionTime > ride.DropoffLimit {
					continue
				}

				if completionTime < minCompletionTime {
					minCompletionTime = completionTime
					bestAssignment = i
					bestVehicle = vIdx
				}
			}
		}

		if bestAssignment == -1 {
			break
		}

		// Assign the best ride to the best vehicle
		ride := rideRequests[bestAssignment]
		vState := &vehicleStates[bestVehicle]

		pickupTime := allShortestPaths[vState.location][ride.Start]
		rideTime := allShortestPaths[ride.Start][ride.Destination]

		arrivalAtPickup := vState.availableAt + int64(pickupTime)
		if arrivalAtPickup < ride.PickupTime {
			arrivalAtPickup = ride.PickupTime
		}

		vState.location = ride.Destination
		vState.availableAt = arrivalAtPickup + int64(rideTime)

		assignments = append(assignments, RideAssignment{
			RideIndex:   bestAssignment,
			VehicleIndex: bestVehicle,
		})
		processedRides[bestAssignment] = true
		fulfilled++
	}

	return assignments, fulfilled
}

func shortestPaths(graph map[int][]Edge, start int) map[int]int {
	dist := make(map[int]int)
	for node := range graph {
		dist[node] = math.MaxInt32
	}
	dist[start] = 0

	pq := make(PriorityQueue, 0)
	heap.Init(&pq)
	heap.Push(&pq, &path{node: start, time: 0})

	for pq.Len() > 0 {
		current := heap.Pop(&pq).(*path)
		if current.time > dist[current.node] {
			continue
		}

		for _, edge := range graph[current.node] {
			newTime := current.time + edge.Time
			if newTime < dist[edge.Destination] {
				dist[edge.Destination] = newTime
				heap.Push(&pq, &path{node: edge.Destination, time: newTime})
			}
		}
	}

	// Remove unreachable nodes
	for node, d := range dist {
		if d == math.MaxInt32 {
			delete(dist, node)
		}
	}

	return dist
}

type PriorityQueue []*path

func (pq PriorityQueue) Len() int           { return len(pq) }
func (pq PriorityQueue) Less(i, j int) bool { return pq[i].time < pq[j].time }
func (pq PriorityQueue) Swap(i, j int)      { pq[i], pq[j] = pq[j], pq[i] }

func (pq *PriorityQueue) Push(x interface{}) {
	*pq = append(*pq, x.(*path))
}

func (pq *PriorityQueue) Pop() interface{} {
	old := *pq
	n := len(old)
	item := old[n-1]
	*pq = old[0 : n-1]
	return item
}