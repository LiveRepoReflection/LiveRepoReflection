package light_sync

import (
	"math"
)

// optimizeTrafficLights computes an offset for each traffic light so that a vehicle traveling at a constant speed
// can ideally pass each intersection during the green phase with minimal waiting.
// For intersection i, the ideal arrival time is the sum of travel times from intersection 0 up to i.
// This function sets the offset[i] to align the arrival phase with the start of the green window.
// Specifically, for each intersection i, we compute t (the accumulated travel time) then choose:
//    offset[i] = floor(t mod cycleTime[i])
// In doing so, a vehicle arriving at intersection i at time t will see the light in its green phase if:
//    t mod cycleTime[i] >= offset[i]  and  t mod cycleTime[i] < offset[i] + (cycleTime[i] - redDuration[i])
// Since cycleTime[i] - redDuration[i] is always at least 1, small fractional differences ensure the arrival
// falls within the green period.
func optimizeTrafficLights(N int, distance []int, cycleTime []int, redDuration []int, speed int) []int {
	offsets := make([]int, N)
	t := 0.0

	for i := 0; i < N; i++ {
		if i > 0 {
			travelTime := float64(distance[i-1]) / float64(speed)
			t += travelTime
		}

		cycle := float64(cycleTime[i])
		idealPhase := math.Mod(t, cycle)
		// Choosing the offset as the floor of idealPhase makes the arrival time always fall into
		// the green window because t mod cycle will be >= offset.
		offset := int(math.Floor(idealPhase))
		offsets[i] = offset
	}
	return offsets
}