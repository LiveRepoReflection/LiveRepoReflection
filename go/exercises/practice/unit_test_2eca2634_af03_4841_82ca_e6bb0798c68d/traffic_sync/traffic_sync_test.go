package traffic_sync

import (
	"math"
	"testing"
)

// simulateTravelTime simulates the travel time of a vehicle through the avenue
// given the input traffic light parameters and a set of offsets.
// The simulation starts at time 0 from the first traffic light (which is assumed to not incur waiting).
// For each subsequent traffic light, the vehicle travels at constant speed and may incur waiting time.
func simulateTravelTime(N int, distances, cycleLengths, greenDurations []int, speedLimit int, offsets []int) float64 {
	// currentTime holds the current simulation time.
	currentTime := 0.0

	// For the first traffic light, assume the vehicle is already there at t=0.
	// For each subsequent light, advance travel time and simulate waiting if arriving during red phase.
	for i := 1; i < N; i++ {
		// Compute travel time between light i and i+1.
		travelTime := float64(distances[i-1]) / float64(speedLimit)
		currentTime += travelTime

		// At traffic light i (index i), compute the phase timing.
		L := float64(cycleLengths[i])
		G := float64(greenDurations[i])
		O := float64(offsets[i])

		// Determine the elapsed time in the current cycle.
		// Adjust time relative to the offset.
		relativeTime := math.Mod(currentTime - O, L)
		if relativeTime < 0 {
			relativeTime += L
		}

		// Check if vehicle arrives during red.
		if relativeTime >= G {
			// Vehicle must wait until next green phase.
			waitTime := L - relativeTime
			currentTime += waitTime
		}
	}
	return currentTime
}

// defaultOffsets returns an array of offsets all set to zero.
func defaultOffsets(N int) []int {
	offsets := make([]int, N)
	for i := 0; i < N; i++ {
		offsets[i] = 0
	}
	return offsets
}

// Test case structure.
type testCase struct {
	name           string
	N              int
	distances      []int
	cycleLengths   []int
	greenDurations []int
	speedLimit     int
}

func TestSynchronizeTrafficLights(t *testing.T) {
	testCases := []testCase{
		{
			name:           "Single Light",
			N:              1,
			distances:      []int{},
			cycleLengths:   []int{50},
			greenDurations: []int{30},
			speedLimit:     10,
		},
		{
			name:           "Three Lights",
			N:              3,
			distances:      []int{100, 200},
			cycleLengths:   []int{60, 60, 60},
			greenDurations: []int{30, 30, 30},
			speedLimit:     10,
		},
		{
			name:           "Five Lights",
			N:              5,
			distances:      []int{100, 150, 200, 250},
			cycleLengths:   []int{70, 80, 90, 100, 110},
			greenDurations: []int{30, 40, 45, 50, 60},
			speedLimit:     5,
		},
		{
			name:           "Varying Cycles",
			N:              4,
			distances:      []int{120, 180, 240},
			cycleLengths:   []int{55, 65, 75, 85},
			greenDurations: []int{25, 35, 40, 45},
			speedLimit:     8,
		},
	}

	// Loop through each test case.
	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			// Invoke the function from the solution to get the offsets.
			offsets := SynchronizeTrafficLights(tc.N, tc.distances, tc.cycleLengths, tc.greenDurations, tc.speedLimit)

			// Check that the returned array has exactly N offsets.
			if len(offsets) != tc.N {
				t.Fatalf("Expected %d offsets, got %d", tc.N, len(offsets))
			}

			// Check that each offset is in the valid range [0, cycleLength - 1].
			for i, offset := range offsets {
				if offset < 0 || offset >= tc.cycleLengths[i] {
					t.Errorf("Offset at index %d is out of valid range: got %d, expected in [0, %d)", i, offset, tc.cycleLengths[i])
				}
			}

			// Compute simulation travel time using the returned offsets.
			solverTime := simulateTravelTime(tc.N, tc.distances, tc.cycleLengths, tc.greenDurations, tc.speedLimit, offsets)
			// Compute simulation travel time using default offsets (all zeros).
			baseTime := simulateTravelTime(tc.N, tc.distances, tc.cycleLengths, tc.greenDurations, tc.speedLimit, defaultOffsets(tc.N))

			// The solver time should be less than or equal to the base time.
			// For the single light scenario, travel time is 0 regardless.
			if tc.N > 1 && solverTime > baseTime {
				t.Errorf("Solver travel time %.2f is greater than default travel time %.2f", solverTime, baseTime)
			}
		})
	}
}