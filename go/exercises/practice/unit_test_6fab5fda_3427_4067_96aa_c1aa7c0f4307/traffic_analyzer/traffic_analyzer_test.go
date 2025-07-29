package traffic_analyzer

import (
	"reflect"
	"sort"
	"testing"
)

// floatEquals checks if two floating-point numbers are almost equal.
func floatEquals(a, b float64) bool {
	const epsilon = 1e-6
	if (a-b < epsilon && b-a < epsilon) {
		return true
	}
	return false
}

func TestEmptyAnalyzer(t *testing.T) {
	analyzer := NewTrafficAnalyzer()

	// Test TopKDestinationIPs on empty analyzer.
	topK := analyzer.TopKDestinationIPs(0, 100, 5)
	if len(topK) != 0 {
		t.Errorf("Expected empty result for TopKDestinationIPs on empty analyzer, got %v", topK)
	}

	// Test AverageBytesTransferred on empty analyzer.
	avg := analyzer.AverageBytesTransferred("192.168.1.1", 0, 100)
	if !floatEquals(avg, 0.0) {
		t.Errorf("Expected average 0.0 for no data, got %f", avg)
	}
}

func TestIngestAndTopK(t *testing.T) {
	analyzer := NewTrafficAnalyzer()
	// Ingest a series of log entries.
	logs := []struct {
		timestamp      int64
		sourceIP       string
		destinationIP  string
		bytesTransferred int64
	}{
		{timestamp: 10, sourceIP: "10.0.0.1", destinationIP: "192.168.1.1", bytesTransferred: 500},
		{timestamp: 20, sourceIP: "10.0.0.2", destinationIP: "192.168.1.2", bytesTransferred: 300},
		{timestamp: 30, sourceIP: "10.0.0.3", destinationIP: "192.168.1.1", bytesTransferred: 700},
		{timestamp: 40, sourceIP: "10.0.0.4", destinationIP: "192.168.1.3", bytesTransferred: 200},
		{timestamp: 50, sourceIP: "10.0.0.5", destinationIP: "192.168.1.2", bytesTransferred: 100},
		// Additional entries to test tie-breaks:
		{timestamp: 35, sourceIP: "10.0.0.6", destinationIP: "192.168.1.3", bytesTransferred: 500},
		{timestamp: 45, sourceIP: "10.0.0.7", destinationIP: "192.168.1.4", bytesTransferred: 600},
		{timestamp: 12, sourceIP: "10.0.0.8", destinationIP: "192.168.1.4", bytesTransferred: 800},
		{timestamp: 42, sourceIP: "10.0.0.9", destinationIP: "192.168.1.4", bytesTransferred: 400},
	}

	for _, entry := range logs {
		analyzer.IngestLogEntry(entry.timestamp, entry.sourceIP, entry.destinationIP, entry.bytesTransferred)
	}

	// Query for time range [10, 50] and k=3.
	topK := analyzer.TopKDestinationIPs(10, 50, 3)
	// Expected frequencies:
	// "192.168.1.1": 2 entries
	// "192.168.1.2": 2 entries
	// "192.168.1.3": 2 entries
	// "192.168.1.4": 3 entries
	// Top 1 should be "192.168.1.4". Ties for frequency 2 should be sorted alphabetically.
	expectedTop3 := []string{"192.168.1.4", "192.168.1.1", "192.168.1.2"}

	if !reflect.DeepEqual(topK, expectedTop3) {
		t.Errorf("TopKDestinationIPs returned %v, expected %v", topK, expectedTop3)
	}
}

func TestAverageBytesTransferred(t *testing.T) {
	analyzer := NewTrafficAnalyzer()
	logs := []struct {
		timestamp         int64
		sourceIP          string
		destinationIP     string
		bytesTransferred  int64
	}{
		{timestamp: 100, sourceIP: "10.0.0.1", destinationIP: "192.168.2.1", bytesTransferred: 1000},
		{timestamp: 150, sourceIP: "10.0.0.1", destinationIP: "192.168.2.2", bytesTransferred: 2000},
		{timestamp: 200, sourceIP: "10.0.0.1", destinationIP: "192.168.2.3", bytesTransferred: 3000},
		{timestamp: 250, sourceIP: "10.0.0.2", destinationIP: "192.168.2.1", bytesTransferred: 4000},
	}
	for _, entry := range logs {
		analyzer.IngestLogEntry(entry.timestamp, entry.sourceIP, entry.destinationIP, entry.bytesTransferred)
	}

	// Calculate the average for source IP "10.0.0.1" in time range [100,200].
	avg := analyzer.AverageBytesTransferred("10.0.0.1", 100, 200)
	expectedAvg := float64(1000+2000+3000) / 3.0
	if !floatEquals(avg, expectedAvg) {
		t.Errorf("AverageBytesTransferred returned %f, expected %f", avg, expectedAvg)
	}

	// For an IP with no entries in the queried time range.
	avg2 := analyzer.AverageBytesTransferred("10.0.0.2", 300, 400)
	if !floatEquals(avg2, 0.0) {
		t.Errorf("AverageBytesTransferred for no entries returned %f, expected 0.0", avg2)
	}
}

func TestLargeK(t *testing.T) {
	analyzer := NewTrafficAnalyzer()
	logs := []struct {
		timestamp         int64
		sourceIP          string
		destinationIP     string
		bytesTransferred  int64
	}{
		{timestamp: 10, sourceIP: "10.0.0.1", destinationIP: "192.168.3.1", bytesTransferred: 500},
		{timestamp: 20, sourceIP: "10.0.0.2", destinationIP: "192.168.3.2", bytesTransferred: 700},
	}
	for _, entry := range logs {
		analyzer.IngestLogEntry(entry.timestamp, entry.sourceIP, entry.destinationIP, entry.bytesTransferred)
	}

	// Query with k greater than the number of distinct destination IPs.
	result := analyzer.TopKDestinationIPs(0, 30, 5)
	// Both destinations have frequency 1; sort alphabetically.
	expected := []string{"192.168.3.1", "192.168.3.2"}

	// Since frequency ties are resolved alphabetically, sort both slices before comparing.
	sort.Strings(result)
	sort.Strings(expected)
	if !reflect.DeepEqual(result, expected) {
		t.Errorf("TopKDestinationIPs with large k returned %v, expected %v", result, expected)
	}
}

func TestInvalidTimeRange(t *testing.T) {
	analyzer := NewTrafficAnalyzer()
	logs := []struct {
		timestamp         int64
		sourceIP          string
		destinationIP     string
		bytesTransferred  int64
	}{
		{timestamp: 100, sourceIP: "10.0.0.1", destinationIP: "192.168.4.1", bytesTransferred: 800},
	}
	for _, entry := range logs {
		analyzer.IngestLogEntry(entry.timestamp, entry.sourceIP, entry.destinationIP, entry.bytesTransferred)
	}

	// Query with an invalid time range: startTime > endTime.
	topK := analyzer.TopKDestinationIPs(200, 100, 3)
	if len(topK) != 0 {
		t.Errorf("Expected empty result for invalid time range in TopKDestinationIPs, got %v", topK)
	}

	avg := analyzer.AverageBytesTransferred("10.0.0.1", 200, 100)
	if !floatEquals(avg, 0.0) {
		t.Errorf("Expected 0.0 average for invalid time range, got %f", avg)
	}
}