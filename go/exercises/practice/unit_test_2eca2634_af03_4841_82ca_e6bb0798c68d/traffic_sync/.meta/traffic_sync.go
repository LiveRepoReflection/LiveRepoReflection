package traffic_sync

// SynchronizeTrafficLights computes the optimal offsets for a series of traffic lights
// in order to minimize the travel time of a vehicle along an avenue.
// The vehicle starts at time 0 from the first traffic light. For each subsequent traffic light,
// the offset is chosen based on the arrival time (assuming no waiting at previous lights)
// such that the vehicle arrives during the green phase. Since offsets must be integers,
// we use the integer part of the arrival time modulo the light's cycle length.
//
// Parameters:
//   N: number of traffic lights.
//   distances: an array of N-1 integers, distance (in meters) between consecutive traffic lights.
//   cycleLengths: an array of N integers representing the full cycle length (green + red) for each traffic light.
//   greenDurations: an array of N integers representing the green phase duration for each traffic light.
//   speedLimit: constant speed (in m/s) at which the vehicle travels.
//
// Returns:
//   An array of N integer offsets where the i-th offset (0-indexed) is in the range [0, cycleLengths[i]-1].
//
// Note:
//   For the first traffic light (index 0), the offset is set to 0 because the simulation starts there.
func SynchronizeTrafficLights(N int, distances, cycleLengths, greenDurations []int, speedLimit int) []int {
	offsets := make([]int, N)

	// For the first traffic light, the offset is inconsequential, set to 0.
	if N == 0 {
		return offsets
	}

	offsets[0] = 0
	currentTime := 0.0

	// For each subsequent traffic light, compute the arrival time when driving constantly.
	// Choose the offset such that the relative arrival time is the fractional part of the travel time.
	// Since the fractional part is always in [0, 1) and greenDurations are at least 1, the light is green.
	for i := 1; i < N; i++ {
		travelTime := float64(distances[i-1]) / float64(speedLimit)
		currentTime += travelTime

		// We choose the offset as the integer part of currentTime modulo the cycle length.
		// This guarantees (currentTime - offset) == fractional part which is less than 1.
		// Since greenDurations[i] is at least 1, the vehicle will hit the green phase.
		offset := int(currentTime) % cycleLengths[i]
		offsets[i] = offset
	}

	return offsets
}