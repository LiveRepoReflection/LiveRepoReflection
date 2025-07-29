package datastream

// This test cases data for the data stream analytics system
// These cases test the core functionality with different scenarios

type DataPoint struct {
	SensorID  int
	Timestamp int64
	Value     float64
}

type StatQuery struct {
	StartTime int64
	EndTime   int64
	StatType  string
	Param     float64 // Used for percentile queries
}

type TestCase struct {
	Description string
	DataPoints  []DataPoint
	Queries     []QueryTestCase
	Config      SystemConfig
}

type QueryTestCase struct {
	Query        StatQuery
	ExpectedVal  float64
	ErrorMargin  float64 // Allowable error margin for approximate algorithms
	Description  string
}

type SystemConfig struct {
	NumSensors      int
	MaxRetentionSec int64
}

var testCases = []TestCase{
	{
		Description: "Basic test with small dataset",
		DataPoints: []DataPoint{
			{0, 1000, 10.0},
			{1, 1000, 20.0},
			{2, 1000, 30.0},
			{0, 2000, 15.0},
			{1, 2000, 25.0},
			{2, 2000, 35.0},
		},
		Queries: []QueryTestCase{
			{
				Query:       StatQuery{1000, 2000, "mean", 0},
				ExpectedVal: 20.0,
				ErrorMargin: 0.001,
				Description: "Mean calculation over all data points",
			},
			{
				Query:       StatQuery{1000, 1000, "median", 0},
				ExpectedVal: 20.0,
				ErrorMargin: 0.5,
				Description: "Median calculation for timestamp 1000",
			},
			{
				Query:       StatQuery{1000, 2000, "percentile", 50},
				ExpectedVal: 22.5,
				ErrorMargin: 1.0,
				Description: "50th percentile across all data",
			},
			{
				Query:       StatQuery{1000, 2000, "variance", 0},
				ExpectedVal: 83.33333, // Variance of [10,15,20,25,30,35]
				ErrorMargin: 1.0,
				Description: "Variance calculation over all data points",
			},
		},
		Config: SystemConfig{
			NumSensors:      3,
			MaxRetentionSec: 3600,
		},
	},
	{
		Description: "Test with larger dataset and time window filtering",
		DataPoints: []DataPoint{
			{0, 1000, 10.0},
			{1, 1000, 20.0},
			{2, 1000, 30.0},
			{0, 2000, 15.0},
			{1, 2000, 25.0},
			{2, 2000, 35.0},
			{0, 3000, 5.0},
			{1, 3000, 15.0}, 
			{2, 3000, 25.0},
			{0, 4000, 0.0},
			{1, 4000, 10.0},
			{2, 4000, 20.0},
		},
		Queries: []QueryTestCase{
			{
				Query:       StatQuery{2000, 3000, "mean", 0},
				ExpectedVal: 20.0,
				ErrorMargin: 0.001,
				Description: "Mean calculation for window [2000,3000]",
			},
			{
				Query:       StatQuery{1000, 4000, "median", 0},
				ExpectedVal: 17.5,
				ErrorMargin: 1.0,
				Description: "Median calculation across all timestamps",
			},
			{
				Query:       StatQuery{3000, 4000, "percentile", 75},
				ExpectedVal: 17.5,
				ErrorMargin: 2.5,
				Description: "75th percentile for window [3000,4000]",
			},
			{
				Query:       StatQuery{1000, 2000, "variance", 0},
				ExpectedVal: 83.33333,
				ErrorMargin: 1.0,
				Description: "Variance for window [1000,2000]",
			},
		},
		Config: SystemConfig{
			NumSensors:      3,
			MaxRetentionSec: 3600,
		},
	},
	{
		Description: "Test with data outside retention window",
		DataPoints: []DataPoint{
			{0, 1000, 10.0},
			{1, 1000, 20.0},
			{0, 6000, 30.0}, // Should be retained
			{1, 6000, 40.0}, // Should be retained
		},
		Queries: []QueryTestCase{
			{
				Query:       StatQuery{5000, 7000, "mean", 0},
				ExpectedVal: 35.0,
				ErrorMargin: 0.001,
				Description: "Mean calculation for data within retention window",
			},
		},
		Config: SystemConfig{
			NumSensors:      2,
			MaxRetentionSec: 3600,
		},
	},
	{
		Description: "Test with high data volume and distribution",
		DataPoints: generateHighVolumeData(),
		Queries: []QueryTestCase{
			{
				Query:       StatQuery{10000, 20000, "mean", 0},
				ExpectedVal: 499.5, // Mean of numbers 0-999
				ErrorMargin: 10.0,
				Description: "Mean calculation for high volume data",
			},
			{
				Query:       StatQuery{10000, 20000, "median", 0},
				ExpectedVal: 499.5,
				ErrorMargin: 25.0,
				Description: "Approximate median for high volume data",
			},
			{
				Query:       StatQuery{10000, 20000, "percentile", 90},
				ExpectedVal: 899.1, // 90th percentile of 0-999
				ErrorMargin: 45.0,
				Description: "90th percentile for high volume data",
			},
			{
				Query:       StatQuery{10000, 20000, "variance", 0},
				ExpectedVal: 83333.25, // Variance of 0-999
				ErrorMargin: 5000.0,
				Description: "Variance for high volume data",
			},
		},
		Config: SystemConfig{
			NumSensors:      10,
			MaxRetentionSec: 3600,
		},
	},
}

// Helper function to generate a dataset with 10000 data points
func generateHighVolumeData() []DataPoint {
	data := make([]DataPoint, 0, 10000)
	
	// Generate 1000 values for each of 10 sensors with timestamps between 10000-20000
	for sensorID := 0; sensorID < 10; sensorID++ {
		for i := 0; i < 1000; i++ {
			timestamp := int64(10000 + i%10000)
			data = append(data, DataPoint{
				SensorID:  sensorID,
				Timestamp: timestamp,
				Value:     float64(i),
			})
		}
	}
	
	return data
}