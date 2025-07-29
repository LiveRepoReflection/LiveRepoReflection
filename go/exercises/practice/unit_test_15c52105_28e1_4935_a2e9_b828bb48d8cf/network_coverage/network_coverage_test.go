package network_coverage

import (
	"math"
	"testing"
)

// DeployBaseStations is assumed to be implemented in the network_coverage package.
// Its signature is assumed as follows:
// func DeployBaseStations(N, M int, population [][]int, K, R int, baseSignal, minSignal float64) [][2]int

// simulateCoverage calculates the total population covered by the given base station positions.
// A cell is covered if the maximum signal strength received from any base station is
// greater than or equal to minSignal.
// Signal strength from a base station at (i, j) for a cell (x, y) is calculated as:
//    strength = baseSignal / (ManhattanDistance((x, y), (i, j)) + 1)
func simulateCoverage(n, m int, population [][]int, stations [][2]int, R int, baseSignal, minSignal float64) int {
	total := 0
	for i := 0; i < n; i++ {
		for j := 0; j < m; j++ {
			maxStrength := 0.0
			for _, station := range stations {
				dist := math.Abs(float64(i-station[0])) + math.Abs(float64(j-station[1]))
				strength := baseSignal / (dist + 1)
				if strength > maxStrength {
					maxStrength = strength
				}
			}
			if maxStrength >= minSignal {
				total += population[i][j]
			}
		}
	}
	return total
}

// Helper to check if a coordinate is within grid bounds.
func isWithinBounds(coord [2]int, n, m int) bool {
	return coord[0] >= 0 && coord[0] < n && coord[1] >= 0 && coord[1] < m
}

func TestDeploySingleCell(t *testing.T) {
	N, M := 1, 1
	population := [][]int{
		{50},
	}
	K, R := 1, 1
	baseSignal, minSignal := 10.0, 5.0

	stations := DeployBaseStations(N, M, population, K, R, baseSignal, minSignal)
	if len(stations) != K {
		t.Fatalf("Expected %d base stations, got %d", K, len(stations))
	}
	// The only valid coordinate is (0,0)
	expected := [2]int{0, 0}
	if stations[0][0] != expected[0] || stations[0][1] != expected[1] {
		t.Errorf("Expected station at %v, got %v", expected, stations[0])
	}

	coveredPopulation := simulateCoverage(N, M, population, stations, R, baseSignal, minSignal)
	if coveredPopulation != 50 {
		t.Errorf("Expected covered population 50, got %d", coveredPopulation)
	}
}

func TestDeployCenterHighPopulation(t *testing.T) {
	N, M := 3, 3
	population := [][]int{
		{5, 5, 5},
		{5, 100, 5},
		{5, 5, 5},
	}
	K, R := 1, 1
	baseSignal, minSignal := 10.0, 5.0

	stations := DeployBaseStations(N, M, population, K, R, baseSignal, minSignal)
	if len(stations) != K {
		t.Fatalf("Expected %d base station, got %d", K, len(stations))
	}
	// Expect the optimal solution to pick the center cell (1,1)
	expected := [2]int{1, 1}
	if stations[0][0] != expected[0] || stations[0][1] != expected[1] {
		t.Errorf("Expected station at %v, got %v", expected, stations[0])
	}

	coveredPopulation := simulateCoverage(N, M, population, stations, R, baseSignal, minSignal)
	// With station at (1,1): center and its adjacent cells get covered.
	// Covered cells: (1,1):100, (0,1):5, (1,0):5, (1,2):5, (2,1):5. Total expected = 100+5+5+5+5 = 120.
	expectedCoverage := 120
	if coveredPopulation != expectedCoverage {
		t.Errorf("Expected covered population %d, got %d", expectedCoverage, coveredPopulation)
	}
}

func TestDeployMultipleStations(t *testing.T) {
	N, M := 4, 4
	population := [][]int{
		{5, 5, 1, 1},
		{5, 100, 1, 1},
		{5, 5, 5, 5},
		{1, 1, 1, 1},
	}
	K, R := 2, 1
	baseSignal, minSignal := 10.0, 5.0

	stations := DeployBaseStations(N, M, population, K, R, baseSignal, minSignal)
	if len(stations) != K {
		t.Fatalf("Expected %d base stations, got %d", K, len(stations))
	}
	// Check that each station is within grid bounds.
	for _, coord := range stations {
		if !isWithinBounds(coord, N, M) {
			t.Errorf("Station coordinate %v out of bounds for grid %d x %d", coord, N, M)
		}
	}
	coveredPopulation := simulateCoverage(N, M, population, stations, R, baseSignal, minSignal)
	// It is hard to know the optimal coverage, but we expect a decent solution should cover at least 100.
	lowerBound := 100
	if coveredPopulation < lowerBound {
		t.Errorf("Expected covered population at least %d, got %d", lowerBound, coveredPopulation)
	}
}

func TestDeployFullCoverage(t *testing.T) {
	// When K is high and minSignal is low, all cells should be covered.
	N, M := 2, 2
	population := [][]int{
		{1, 2},
		{3, 4},
	}
	K, R := 4, 1
	baseSignal, minSignal := 10.0, 1.0

	stations := DeployBaseStations(N, M, population, K, R, baseSignal, minSignal)
	if len(stations) != K {
		t.Fatalf("Expected %d base stations, got %d", K, len(stations))
	}
	for _, coord := range stations {
		if !isWithinBounds(coord, N, M) {
			t.Errorf("Station coordinate %v out of bounds for grid %d x %d", coord, N, M)
		}
	}
	coveredPopulation := simulateCoverage(N, M, population, stations, R, baseSignal, minSignal)
	// With minSignal so low, all cells should be covered; expected total population = 1+2+3+4 = 10.
	expectedCoverage := 10
	if coveredPopulation != expectedCoverage {
		t.Errorf("Expected covered population %d, got %d", expectedCoverage, coveredPopulation)
	}
}