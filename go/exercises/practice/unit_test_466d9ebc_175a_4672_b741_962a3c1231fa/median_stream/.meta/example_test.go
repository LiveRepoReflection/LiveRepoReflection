package medianstream_test

import (
	"fmt"
	"median_stream"
)

func ExampleDistributedMedianStream() {
	// Create a new distributed median stream
	ms := medianstream.New()
	
	// Add some values from different sources
	ms.AddValue("temp-sensor-1", 22)
	ms.AddValue("temp-sensor-2", 25)
	ms.AddValue("temp-sensor-1", 21)
	ms.AddValue("temp-sensor-3", 24)
	ms.AddValue("temp-sensor-2", 23)
	
	// Get the current median temperature
	median := ms.GetMedian()
	fmt.Printf("Current median temperature: %.1f°C\n", median)
	
	// Add more values
	ms.AddValue("temp-sensor-3", 26)
	ms.AddValue("temp-sensor-1", 20)
	
	// Get the updated median
	median = ms.GetMedian()
	fmt.Printf("Updated median temperature: %.1f°C\n", median)
	
	// Output:
	// Current median temperature: 23.0°C
	// Updated median temperature: 23.0°C
}