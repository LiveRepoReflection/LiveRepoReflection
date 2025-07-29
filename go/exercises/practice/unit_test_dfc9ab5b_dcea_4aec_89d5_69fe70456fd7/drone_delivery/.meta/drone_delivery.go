package drone_delivery

// CalculateTotalIdleTime computes the total idle time (waiting time) required
// for a fleet of drones to deliver packages from their respective origins to destinations.
// Each drone route is based on a direct edge from origin to destination. The drone's actual
// delivery time is the maximum of the edge's travel time and the earliest allowable delivery time.
// Idle time for a route is defined as (earliest allowable delivery time - travel time) if the travel
// time is less than the earliest allowable time, and 0 otherwise.
// If any route is invalid (e.g., no direct edge exists or the travel time exceeds the latest allowable time),
// the function returns -1.
func CalculateTotalIdleTime(N, M int, adjMatrix [][]int, origins, destinations []int, timeWindows [][]int) int {
	totalIdle := 0
	for i := 0; i < M; i++ {
		// Validate indices for origin and destination
		origin := origins[i]
		dest := destinations[i]
		if origin < 0 || origin >= N || dest < 0 || dest >= N {
			return -1
		}
		travelTime := adjMatrix[origin][dest]
		if travelTime == -1 {
			return -1
		}
		windowStart := timeWindows[i][0]
		windowEnd := timeWindows[i][1]
		// If travel time is greater than the latest allowed time, the route is invalid.
		if travelTime > windowEnd {
			return -1
		}
		// If travel time is less than the earliest allowed time, waiting (idle time) is required.
		if travelTime < windowStart {
			totalIdle += windowStart - travelTime
		}
	}
	return totalIdle
}