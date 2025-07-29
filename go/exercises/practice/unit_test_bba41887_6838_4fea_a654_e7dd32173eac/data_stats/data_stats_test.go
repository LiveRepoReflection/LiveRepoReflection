package data_stats

import (
	"math"
	"sync"
	"testing"
)

func approxEqual(a, b, tol float64) bool {
	return math.Abs(a-b) < tol
}

func TestEmptySensor(t *testing.T) {
	dsp := NewDataStreamProcessor(10000)
	_, _, found := dsp.GetStatistics("nonexistent")
	if found {
		t.Fatalf("Expected sensor 'nonexistent' to not be found")
	}
}

func TestSingleDataPoint(t *testing.T) {
	dsp := NewDataStreamProcessor(10000)
	timestamp := int64(1000)
	dsp.Ingest(timestamp, "sensor1", 10)
	avg, stdDev, found := dsp.GetStatistics("sensor1")
	if !found {
		t.Fatalf("Expected sensor 'sensor1' to be found")
	}
	if !approxEqual(avg, 10.0, 1e-6) {
		t.Fatalf("Expected average 10.0 but got %v", avg)
	}
	if !approxEqual(stdDev, 0.0, 1e-6) {
		t.Fatalf("Expected stdDev 0.0 for single data point but got %v", stdDev)
	}
}

func TestMultipleDataPoints(t *testing.T) {
	dsp := NewDataStreamProcessor(10000)
	// Ingest data points in order
	dsp.Ingest(1000, "sensor1", 2)
	dsp.Ingest(2000, "sensor1", 4)
	dsp.Ingest(3000, "sensor1", 6)
	avg, stdDev, found := dsp.GetStatistics("sensor1")
	if !found {
		t.Fatalf("Expected sensor 'sensor1' to be found")
	}
	// average = (2+4+6)/3 = 4.0
	if !approxEqual(avg, 4.0, 1e-6) {
		t.Fatalf("Expected average 4.0 but got %v", avg)
	}
	// Using sample standard deviation:
	// variance = ((2-4)^2+(4-4)^2+(6-4)^2)/(3-1) = (4+0+4)/2 = 4.0, stdDev = 2.0
	if !approxEqual(stdDev, 2.0, 1e-6) {
		t.Fatalf("Expected stdDev 2.0 but got %v", stdDev)
	}
}

func TestSlidingWindow(t *testing.T) {
	// Create a processor with a 5000ms window
	dsp := NewDataStreamProcessor(5000)
	// Ingest data that all fall in the initial window:
	dsp.Ingest(1000, "sensor1", 10)
	dsp.Ingest(2000, "sensor1", 20)
	dsp.Ingest(3000, "sensor1", 30)
	avg, stdDev, found := dsp.GetStatistics("sensor1")
	if !found {
		t.Fatalf("Expected sensor 'sensor1' to be found")
	}
	// With latest timestamp 3000, window = [-2000,3000], so all data included
	if !approxEqual(avg, 20.0, 1e-6) {
		t.Fatalf("Expected average 20.0 but got %v", avg)
	}
	// Sample stdDev = sqrt(((10-20)^2+(20-20)^2+(30-20)^2)/2) = sqrt((100+0+100)/2) = sqrt(100) = 10
	if !approxEqual(stdDev, 10.0, 1e-6) {
		t.Fatalf("Expected stdDev 10.0 but got %v", stdDev)
	}
	// Now ingest a new packet with a much later timestamp which pushes out the older data.
	dsp.Ingest(10000, "sensor1", 40)
	avg, stdDev, found = dsp.GetStatistics("sensor1")
	if !found {
		t.Fatalf("Expected sensor 'sensor1' to be found after window slide")
	}
	// Now window = [5000, 10000]. Only the data point at 10000 is valid.
	if !approxEqual(avg, 40.0, 1e-6) {
		t.Fatalf("Expected average 40.0 but got %v", avg)
	}
	if !approxEqual(stdDev, 0.0, 1e-6) {
		t.Fatalf("Expected stdDev 0.0 for a single data point in window but got %v", stdDev)
	}
}

func TestOutOfOrderIngestion(t *testing.T) {
	dsp := NewDataStreamProcessor(10000)
	// Ingest out-of-order data packets for sensor2.
	dsp.Ingest(5000, "sensor2", 100)
	dsp.Ingest(2000, "sensor2", 50)
	dsp.Ingest(7000, "sensor2", 150)
	// Latest timestamp is 7000, window = [-3000,7000], so all datapoints are valid.
	avg, stdDev, found := dsp.GetStatistics("sensor2")
	if !found {
		t.Fatalf("Expected sensor 'sensor2' to be found")
	}
	// average = (50+100+150)/3 = 100
	if !approxEqual(avg, 100.0, 1e-6) {
		t.Fatalf("Expected average 100.0 but got %v", avg)
	}
	// Sample standard deviation = sqrt(((50-100)^2+(100-100)^2+(150-100)^2)/2)
	// = sqrt((2500+0+2500)/2) = sqrt(2500) = 50
	if !approxEqual(stdDev, 50.0, 1e-6) {
		t.Fatalf("Expected stdDev 50.0 but got %v", stdDev)
	}
}

func TestConcurrentIngestionAndRetrieval(t *testing.T) {
	dsp := NewDataStreamProcessor(10000)
	var wg sync.WaitGroup
	sensorIDs := []string{"sensor1", "sensor2", "sensor3"}

	// Launch concurrent ingestion routines.
	for i := 0; i < 1000; i++ {
		for _, id := range sensorIDs {
			wg.Add(1)
			go func(ts int64, sensor string, value int) {
				defer wg.Done()
				dsp.Ingest(ts, sensor, value)
			}(int64(i), id, i)
		}
	}
	wg.Wait()

	// Launch concurrent retrieval routines.
	var retWg sync.WaitGroup
	for _, id := range sensorIDs {
		retWg.Add(1)
		go func(sensor string) {
			defer retWg.Done()
			avg, stdDev, found := dsp.GetStatistics(sensor)
			if !found {
				t.Errorf("Expected sensor '%s' to be found", sensor)
			}
			if avg < 0 || stdDev < 0 {
				t.Errorf("Expected non-negative statistics for sensor '%s', got avg=%v, stdDev=%v", sensor, avg, stdDev)
			}
		}(id)
	}
	retWg.Wait()
}