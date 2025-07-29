package intercity_express

import (
	"testing"
)

func TestFindFastestRoute(t *testing.T) {
	tests := []struct {
		name          string
		cities        []string
		railLines     []RailLine
		queries       []Query
		expected      []Result
		expectError   bool
	}{
		{
			name: "basic two cities connected",
			cities: []string{"A", "B"},
			railLines: []RailLine{
				{StartCity: "A", EndCity: "B", Length: 100, MaxSpeed: 100, MaintenanceCostPerKm: 1},
			},
			queries: []Query{
				{StartCity: "A", DestinationCity: "B"},
			},
			expected: []Result{
				{FastestTime: 1.00, MinimumMaintenanceCost: 100},
			},
			expectError: false,
		},
		{
			name: "three cities with multiple paths",
			cities: []string{"A", "B", "C"},
			railLines: []RailLine{
				{StartCity: "A", EndCity: "B", Length: 100, MaxSpeed: 100, MaintenanceCostPerKm: 1},
				{StartCity: "A", EndCity: "C", Length: 200, MaxSpeed: 50, MaintenanceCostPerKm: 2},
				{StartCity: "B", EndCity: "C", Length: 50, MaxSpeed: 100, MaintenanceCostPerKm: 3},
			},
			queries: []Query{
				{StartCity: "A", DestinationCity: "C"},
			},
			expected: []Result{
				{FastestTime: 1.50, MinimumMaintenanceCost: 250},
			},
			expectError: false,
		},
		{
			name: "disconnected cities",
			cities: []string{"A", "B", "C", "D"},
			railLines: []RailLine{
				{StartCity: "A", EndCity: "B", Length: 100, MaxSpeed: 100, MaintenanceCostPerKm: 1},
				{StartCity: "C", EndCity: "D", Length: 150, MaxSpeed: 75, MaintenanceCostPerKm: 2},
			},
			queries: []Query{
				{StartCity: "A", DestinationCity: "D"},
			},
			expected: []Result{
				{FastestTime: -1.00, MinimumMaintenanceCost: -1},
			},
			expectError: false,
		},
		{
			name: "multiple queries",
			cities: []string{"A", "B", "C"},
			railLines: []RailLine{
				{StartCity: "A", EndCity: "B", Length: 100, MaxSpeed: 100, MaintenanceCostPerKm: 1},
				{StartCity: "B", EndCity: "C", Length: 50, MaxSpeed: 100, MaintenanceCostPerKm: 3},
				{StartCity: "A", EndCity: "C", Length: 200, MaxSpeed: 50, MaintenanceCostPerKm: 2},
			},
			queries: []Query{
				{StartCity: "A", DestinationCity: "B"},
				{StartCity: "A", DestinationCity: "C"},
				{StartCity: "B", DestinationCity: "C"},
			},
			expected: []Result{
				{FastestTime: 1.00, MinimumMaintenanceCost: 100},
				{FastestTime: 1.50, MinimumMaintenanceCost: 250},
				{FastestTime: 0.50, MinimumMaintenanceCost: 150},
			},
			expectError: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			results, err := FindFastestRoutes(tt.cities, tt.railLines, tt.queries)
			if (err != nil) != tt.expectError {
				t.Errorf("FindFastestRoutes() error = %v, expectError %v", err, tt.expectError)
				return
			}

			if len(results) != len(tt.expected) {
				t.Errorf("expected %d results, got %d", len(tt.expected), len(results))
				return
			}

			for i := range results {
				if results[i].FastestTime != tt.expected[i].FastestTime {
					t.Errorf("result %d: expected fastest time %.2f, got %.2f",
						i, tt.expected[i].FastestTime, results[i].FastestTime)
				}
				if results[i].MinimumMaintenanceCost != tt.expected[i].MinimumMaintenanceCost {
					t.Errorf("result %d: expected maintenance cost %d, got %d",
						i, tt.expected[i].MinimumMaintenanceCost, results[i].MinimumMaintenanceCost)
				}
			}
		})
	}
}

func BenchmarkFindFastestRoutes(b *testing.B) {
	cities := []string{"A", "B", "C", "D", "E", "F", "G"}
	railLines := []RailLine{
		{StartCity: "A", EndCity: "B", Length: 100, MaxSpeed: 100, MaintenanceCostPerKm: 1},
		{StartCity: "A", EndCity: "C", Length: 200, MaxSpeed: 50, MaintenanceCostPerKm: 2},
		{StartCity: "B", EndCity: "C", Length: 50, MaxSpeed: 100, MaintenanceCostPerKm: 3},
		{StartCity: "B", EndCity: "D", Length: 150, MaxSpeed: 120, MaintenanceCostPerKm: 2},
		{StartCity: "C", EndCity: "E", Length: 300, MaxSpeed: 80, MaintenanceCostPerKm: 1},
		{StartCity: "D", EndCity: "F", Length: 100, MaxSpeed: 150, MaintenanceCostPerKm: 4},
		{StartCity: "E", EndCity: "G", Length: 200, MaxSpeed: 90, MaintenanceCostPerKm: 3},
		{StartCity: "F", EndCity: "G", Length: 50, MaxSpeed: 200, MaintenanceCostPerKm: 5},
	}
	queries := []Query{
		{StartCity: "A", DestinationCity: "G"},
		{StartCity: "B", DestinationCity: "E"},
		{StartCity: "C", DestinationCity: "F"},
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		FindFastestRoutes(cities, railLines, queries)
	}
}