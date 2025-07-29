package light_sync

import (
	"math"
	"testing"
)

// simulateTravelTime simulates the travel time for a vehicle from intersection 0 to N-1 using the provided traffic light offsets.
// The simulation follows the described process: vehicles travel at a constant speed, must stop at red lights, and wait for green.
func simulateTravelTime(distance []int, offsets []int, cycleTime []int, redDuration []int, speed int) float64 {
	t := 0.0
	N := len(cycleTime)
	// For each intersection, except the first which is the start.
	for i := 0; i < N; i++ {
		// If not the first light, add travel time from previous intersection.
		if i > 0 {
			t += float64(distance[i-1]) / float64(speed)
		}
		// Determine current light's cycle information.
		cycle := float64(cycleTime[i])
		red := float64(redDuration[i])
		off := float64(offsets[i])
		// Calculate elapsed time in the current cycle relative to offset.
		// To handle negative remainder correctly, use math.Mod and adjust.
		phase := math.Mod(t - off + cycle, cycle)
		greenPeriod := cycle - red
		// If vehicle arrives during red, wait until green.
		if phase >= greenPeriod {
			wait := cycle - phase
			t += wait
		}
	}
	return t
}

func TestOptimizeTrafficLights(t *testing.T) {
	tests := []struct {
		name        string
		N           int
		distance    []int
		cycleTime   []int
		redDuration []int
		speed       int
	}{
		{
			name:        "Single intersection",
			N:           1,
			distance:    []int{},
			cycleTime:   []int{60},
			redDuration: []int{30},
			speed:       10,
		},
		{
			name:        "Two intersections simple",
			N:           2,
			distance:    []int{500},
			cycleTime:   []int{50, 40},
			redDuration: []int{20, 15},
			speed:       10,
		},
		{
			name:        "Three intersections sample",
			N:           3,
			distance:    []int{200, 300},
			cycleTime:   []int{60, 45, 50},
			redDuration: []int{30, 20, 25},
			speed:       10,
		},
		{
			name:        "Multiple intersections varied",
			N:           5,
			distance:    []int{150, 250, 100, 300},
			cycleTime:   []int{55, 65, 70, 50, 80},
			redDuration: []int{25, 30, 35, 20, 40},
			speed:       15,
		},
		{
			name:        "Edge case: Minimum distances",
			N:           4,
			distance:    []int{1, 1, 1},
			cycleTime:   []int{10, 20, 30, 40},
			redDuration: []int{3, 5, 10, 15},
			speed:       1,
		},
	}

	for _, tc := range tests {
		tc := tc
		t.Run(tc.name, func(t *testing.T) {
			// Call the optimizeTrafficLights function to obtain offsets.
			offsets := optimizeTrafficLights(tc.N, tc.distance, tc.cycleTime, tc.redDuration, tc.speed)

			// Check that the returned offsets have the correct length.
			if len(offsets) != tc.N {
				t.Fatalf("expected offsets length %d, got %d", tc.N, len(offsets))
			}

			// Verify that each offset is in the valid range: 0 <= offset < cycleTime[i]
			for i, offset := range offsets {
				if offset < 0 || offset >= tc.cycleTime[i] {
					t.Errorf("offset[%d] = %d is out of range [0, %d)", i, offset, tc.cycleTime[i])
				}
			}

			// Compute travel time based on the optimized offsets.
			travelTimeOptimized := simulateTravelTime(tc.distance, offsets, tc.cycleTime, tc.redDuration, tc.speed)

			// For baseline comparison, simulate travel time using a naive offset (e.g., all zeros).
			naiveOffsets := make([]int, tc.N)
			travelTimeNaive := simulateTravelTime(tc.distance, naiveOffsets, tc.cycleTime, tc.redDuration, tc.speed)

			// Log the travel times for reference.
			t.Logf("Test %q: Optimized travel time = %f, Naive travel time = %f", tc.name, travelTimeOptimized, travelTimeNaive)

			// Since the function is supposed to optimize travel time, we expect the optimized travel time
			// to be less than or equal to the naive travel time. However, due to multiple valid approaches,
			// allow a tolerance of a small epsilon value.
			epsilon := 1e-6
			if travelTimeOptimized > travelTimeNaive+epsilon {
				t.Errorf("optimized travel time %f is worse than naive travel time %f", travelTimeOptimized, travelTimeNaive)
			}
		})
	}
}

func BenchmarkOptimizeTrafficLights(b *testing.B) {
	// Set up a moderate test case.
	N := 5
	distance := []int{150, 250, 100, 300}
	cycleTime := []int{55, 65, 70, 50, 80}
	redDuration := []int{25, 30, 35, 20, 40}
	speed := 15

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_ = optimizeTrafficLights(N, distance, cycleTime, redDuration, speed)
	}
}