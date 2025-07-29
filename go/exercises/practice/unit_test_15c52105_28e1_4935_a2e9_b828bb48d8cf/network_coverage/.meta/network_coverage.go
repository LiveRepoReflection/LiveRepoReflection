package network_coverage

import (
	"math"
)

// Contribution represents the coverage contribution of a base station at a candidate cell to a target cell.
type Contribution struct {
	x      int
	y      int
	signal float64
}

// DeployBaseStations selects K base station locations on an N x M grid to maximize the total population coverage.
// Each base station at position (i, j) provides coverage to cells within a Manhattan distance R with a signal strength:
//    signal = baseSignal / (ManhattanDistance + 1)
// A cell is considered covered if the maximum signal strength from any base station is greater than or equal to minSignal.
// This function uses a greedy iterative algorithm to choose base station positions.
func DeployBaseStations(N, M int, population [][]int, K, R int, baseSignal, minSignal float64) [][2]int {
	// Precompute candidate contributions for each candidate position (i, j)
	// candidateContrib[i][j] is a slice of contributions for a candidate at (i, j)
	candidateContrib := make([][]Contribution, N)
	for i := 0; i < N; i++ {
		candidateContrib[i] = make([]Contribution, 0) // Not used as a 2D array directly; will compute for each candidate separately.
	}
	// Instead, we build a 2D slice of slices for each candidate position.
	// contributions[i][j] will be the list of contributions for candidate at (i, j).
	contributions := make([][][]Contribution, N)
	for i := 0; i < N; i++ {
		contributions[i] = make([][]Contribution, M)
		for j := 0; j < M; j++ {
			var candContrib []Contribution
			// Iterate over possible offsets within Manhattan distance R.
			// For dx in [-R,R] and for dy such that |dx|+|dy| <= R.
			for dx := -R; dx <= R; dx++ {
				maxDy := R - int(math.Abs(float64(dx)))
				for dy := -maxDy; dy <= maxDy; dy++ {
					x := i + dx
					y := j + dy
					// Check bounds
					if x >= 0 && x < N && y >= 0 && y < M {
						dist := math.Abs(float64(dx)) + math.Abs(float64(dy))
						signal := baseSignal / (dist + 1)
						// Include only if within R (manhattan distance check is implicit by loop limits)
						candContrib = append(candContrib, Contribution{
							x:      x,
							y:      y,
							signal: signal,
						})
					}
				}
			}
			contributions[i][j] = candContrib
		}
	}

	// currentSignal holds the best signal strength achieved at each cell from the chosen base stations so far.
	currentSignal := make([][]float64, N)
	for i := range currentSignal {
		currentSignal[i] = make([]float64, M)
		for j := range currentSignal[i] {
			currentSignal[i][j] = 0.0
		}
	}

	// The list of chosen base station positions.
	var stations [][2]int

	// Greedily select K base stations.
	for count := 0; count < K; count++ {
		var bestCandidate [2]int
		bestGain := 0
		// Loop over every cell as candidate base station.
		for i := 0; i < N; i++ {
			for j := 0; j < M; j++ {
				gain := 0
				// Evaluate marginal gain from placing a base station at (i,j)
				for _, contrib := range contributions[i][j] {
					// If this candidate provides signal above or equal minSignal and current signal is below threshold.
					if contrib.signal >= minSignal && currentSignal[contrib.x][contrib.y] < minSignal {
						gain += population[contrib.x][contrib.y]
					}
				}
				if gain > bestGain {
					bestGain = gain
					bestCandidate = [2]int{i, j}
				}
			}
		}
		// If bestGain remains 0, it means no candidate can increase the coverage.
		// In that case, choose an arbitrary candidate, for instance (0,0).
		if bestGain == 0 {
			bestCandidate = [2]int{0, 0}
		}
		// Update the coverage based on the selected best candidate.
		for _, contrib := range contributions[bestCandidate[0]][bestCandidate[1]] {
			// Update the cell with maximum signal from any base station.
			if contrib.signal > currentSignal[contrib.x][contrib.y] {
				currentSignal[contrib.x][contrib.y] = contrib.signal
			}
		}
		// Append the chosen candidate to the list of stations.
		stations = append(stations, bestCandidate)
	}

	return stations
}