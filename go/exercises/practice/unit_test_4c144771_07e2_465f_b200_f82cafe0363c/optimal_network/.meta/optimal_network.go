package optimal_network

import (
	"math"
	"sort"
)

const INF = math.MaxInt32

type LocationData struct {
	DataDemand int
	Population int
}

type Station struct {
	index    int
	capacity int
}

// OptimalNetworkDeployment returns the maximum total satisfied data demand
// achieved by deploying up to numBaseStationsToDeploy base stations and establishing
// communication links within the provided budget.
func OptimalNetworkDeployment(numLocations int, edges [][]int, locationData []LocationData, baseStationCapacity int, numBaseStationsToDeploy int, budget int) int {
	satisfied := 0
	remainingBudget := budget

	// Create candidate list: indices sorted descending by DataDemand.
	candidates := make([]int, numLocations)
	for i := 0; i < numLocations; i++ {
		candidates[i] = i
	}
	sort.Slice(candidates, func(i, j int) bool {
		return locationData[candidates[i]].DataDemand > locationData[candidates[j]].DataDemand
	})

	// Greedily deploy base stations based on candidate order.
	// Also mark deployed nodes.
	deployed := make([]bool, numLocations)
	deployedStations := []Station{}

	for _, i := range candidates {
		if len(deployedStations) >= numBaseStationsToDeploy {
			break
		}
		// Cost to deploy base station at location i.
		costStation := locationData[i].Population * 10
		// Only deploy if the station can cover its own demand.
		if locationData[i].DataDemand > baseStationCapacity {
			continue
		}
		if remainingBudget >= costStation {
			remainingBudget -= costStation
			deployedStations = append(deployedStations, Station{
				index:    i,
				capacity: baseStationCapacity - locationData[i].DataDemand,
			})
			deployed[i] = true
			satisfied += locationData[i].DataDemand
		}
	}

	// Build graph distance matrix using Floyd Warshall algorithm.
	dist := make([][]int, numLocations)
	for i := 0; i < numLocations; i++ {
		dist[i] = make([]int, numLocations)
		for j := 0; j < numLocations; j++ {
			if i == j {
				dist[i][j] = 0
			} else {
				dist[i][j] = INF
			}
		}
	}
	for _, edge := range edges {
		u, v, cost := edge[0], edge[1], edge[2]
		if cost < dist[u][v] {
			dist[u][v] = cost
			dist[v][u] = cost
		}
	}
	for k := 0; k < numLocations; k++ {
		for i := 0; i < numLocations; i++ {
			for j := 0; j < numLocations; j++ {
				if dist[i][k] < INF && dist[k][j] < INF && dist[i][k]+dist[k][j] < dist[i][j] {
					dist[i][j] = dist[i][k] + dist[k][j]
				}
			}
		}
	}

	// Prepare possible connections for unassigned nodes.
	type connection struct {
		node         int
		stationIndex int // index in deployedStations slice
		cost         int
	}
	connections := []connection{}
	for i := 0; i < numLocations; i++ {
		if deployed[i] {
			continue
		}
		bestCost := INF
		bestStation := -1
		for sIdx, s := range deployedStations {
			if s.capacity >= locationData[i].DataDemand && dist[s.index][i] < bestCost {
				bestCost = dist[s.index][i]
				bestStation = sIdx
			}
		}
		if bestCost < INF && bestStation != -1 {
			connections = append(connections, connection{
				node:         i,
				stationIndex: bestStation,
				cost:         bestCost,
			})
		}
	}

	// Sort all potential connections by ascending cost.
	sort.Slice(connections, func(i, j int) bool {
		return connections[i].cost < connections[j].cost
	})
	for _, conn := range connections {
		if remainingBudget >= conn.cost {
			if deployedStations[conn.stationIndex].capacity >= locationData[conn.node].DataDemand {
				remainingBudget -= conn.cost
				deployedStations[conn.stationIndex].capacity -= locationData[conn.node].DataDemand
				satisfied += locationData[conn.node].DataDemand
			}
		}
	}
	return satisfied
}