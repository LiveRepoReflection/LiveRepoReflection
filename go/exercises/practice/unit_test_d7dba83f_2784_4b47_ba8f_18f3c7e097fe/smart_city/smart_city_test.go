package smart_city

import (
	"testing"
)

func TestSmartCity(t *testing.T) {
	tests := []struct {
		name            string
		N               int
		M               int
		channels        [][4]int
		dataSources     [][5]interface{}
		simulationTime  int
		expectedScore   int
	}{
		{
			name: "single data source with sufficient bandwidth",
			N:    3,
			M:    2,
			channels: [][4]int{
				{1, 0, 20, 5},
				{2, 1, 15, 3},
			},
			dataSources: [][5]interface{}{
				{2, "SensorData", 8, 10, 5},
			},
			simulationTime: 1,
			expectedScore:  8,
		},
		{
			name: "multiple data sources with bandwidth contention",
			N:    4,
			M:    3,
			channels: [][4]int{
				{1, 0, 10, 2},
				{2, 1, 15, 3},
				{3, 2, 20, 1},
			},
			dataSources: [][5]interface{}{
				{2, "TrafficData", 5, 8, 10},
				{3, "EmergencyData", 9, 6, 8},
			},
			simulationTime: 1,
			expectedScore:  9,
		},
		{
			name: "data exceeds max latency",
			N:    3,
			M:    2,
			channels: [][4]int{
				{1, 0, 30, 8},
				{2, 1, 25, 7},
			},
			dataSources: [][5]interface{}{
				{2, "WeatherData", 7, 10, 10},
			},
			simulationTime: 1,
			expectedScore:  0,
		},
		{
			name: "channel failure scenario",
			N:    4,
			M:    4,
			channels: [][4]int{
				{1, 0, 0, 5},  // failed channel
				{2, 0, 15, 3},
				{3, 1, 10, 2},
				{3, 2, 20, 4},
			},
			dataSources: [][5]interface{}{
				{3, "PowerGridData", 8, 10, 5},
			},
			simulationTime: 1,
			expectedScore:  8,
		},
		{
			name: "multiple time steps",
			N:    3,
			M:    2,
			channels: [][4]int{
				{1, 0, 10, 2},
				{2, 1, 15, 3},
			},
			dataSources: [][5]interface{}{
				{2, "AirQualityData", 6, 8, 5},
			},
			simulationTime: 3,
			expectedScore:  18,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			actualScore := CalculateMaxCriticalityScore(
				tt.N,
				tt.M,
				tt.channels,
				tt.dataSources,
				tt.simulationTime,
			)
			if actualScore != tt.expectedScore {
				t.Errorf("CalculateMaxCriticalityScore() = %v, want %v", actualScore, tt.expectedScore)
			}
		})
	}
}

func BenchmarkSmartCity(b *testing.B) {
	N := 10
	M := 15
	channels := [][4]int{
		{1, 0, 20, 5},
		{2, 1, 15, 3},
		{3, 0, 25, 4},
		{4, 2, 10, 2},
		{5, 3, 30, 6},
		{6, 4, 15, 3},
		{7, 5, 20, 4},
		{8, 6, 10, 1},
		{9, 7, 25, 5},
		{1, 2, 15, 2},
		{3, 4, 20, 3},
		{5, 6, 10, 2},
		{7, 8, 15, 4},
		{2, 3, 10, 1},
		{4, 5, 20, 3},
	}
	dataSources := [][5]interface{}{
		{2, "SensorData", 8, 10, 5},
		{5, "TrafficData", 6, 8, 7},
		{8, "EmergencyData", 9, 6, 4},
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		CalculateMaxCriticalityScore(N, M, channels, dataSources, 5)
	}
}