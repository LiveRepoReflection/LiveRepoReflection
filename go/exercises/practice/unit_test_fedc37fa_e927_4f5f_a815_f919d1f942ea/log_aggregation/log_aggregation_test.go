package logaggregation

import (
	"reflect"
	"testing"
	"time"
)

func TestLogAggregation(t *testing.T) {
	tests := []struct {
		name      string
		logs      []LogEntry
		startTime int64
		endTime   int64
		severity  string
		want      map[string][]LogEntry
	}{
		{
			name: "Basic test with single data center",
			logs: []LogEntry{
				{
					Timestamp:  1000,
					DataCenter: "us-east-1",
					Severity:   "ERROR",
					Message:    "Error in service A",
				},
				{
					Timestamp:  2000,
					DataCenter: "us-east-1",
					Severity:   "ERROR",
					Message:    "Error in service B",
				},
			},
			startTime: 0,
			endTime:   3000,
			severity:  "ERROR",
			want: map[string][]LogEntry{
				"us-east-1": {
					{
						Timestamp:  1000,
						DataCenter: "us-east-1",
						Severity:   "ERROR",
						Message:    "Error in service A",
					},
					{
						Timestamp:  2000,
						DataCenter: "us-east-1",
						Severity:   "ERROR",
						Message:    "Error in service B",
					},
				},
			},
		},
		{
			name: "Multiple data centers",
			logs: []LogEntry{
				{
					Timestamp:  1000,
					DataCenter: "us-east-1",
					Severity:   "ERROR",
					Message:    "Error in US",
				},
				{
					Timestamp:  2000,
					DataCenter: "eu-west-1",
					Severity:   "ERROR",
					Message:    "Error in EU",
				},
			},
			startTime: 0,
			endTime:   3000,
			severity:  "ERROR",
			want: map[string][]LogEntry{
				"us-east-1": {
					{
						Timestamp:  1000,
						DataCenter: "us-east-1",
						Severity:   "ERROR",
						Message:    "Error in US",
					},
				},
				"eu-west-1": {
					{
						Timestamp:  2000,
						DataCenter: "eu-west-1",
						Severity:   "ERROR",
						Message:    "Error in EU",
					},
				},
			},
		},
		{
			name: "Time range filtering",
			logs: []LogEntry{
				{
					Timestamp:  1000,
					DataCenter: "us-east-1",
					Severity:   "ERROR",
					Message:    "Old error",
				},
				{
					Timestamp:  5000,
					DataCenter: "us-east-1",
					Severity:   "ERROR",
					Message:    "New error",
				},
			},
			startTime: 2000,
			endTime:   6000,
			severity:  "ERROR",
			want: map[string][]LogEntry{
				"us-east-1": {
					{
						Timestamp:  5000,
						DataCenter: "us-east-1",
						Severity:   "ERROR",
						Message:    "New error",
					},
				},
			},
		},
		{
			name: "Severity filtering",
			logs: []LogEntry{
				{
					Timestamp:  1000,
					DataCenter: "us-east-1",
					Severity:   "ERROR",
					Message:    "Error message",
				},
				{
					Timestamp:  2000,
					DataCenter: "us-east-1",
					Severity:   "INFO",
					Message:    "Info message",
				},
			},
			startTime: 0,
			endTime:   3000,
			severity:  "ERROR",
			want: map[string][]LogEntry{
				"us-east-1": {
					{
						Timestamp:  1000,
						DataCenter: "us-east-1",
						Severity:   "ERROR",
						Message:    "Error message",
					},
				},
			},
		},
		{
			name:      "Empty result",
			logs:      []LogEntry{},
			startTime: 0,
			endTime:   1000,
			severity:  "ERROR",
			want:      map[string][]LogEntry{},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			system := NewLogAggregator()
			
			// Test concurrent ingestion
			done := make(chan bool)
			for _, log := range tt.logs {
				go func(l LogEntry) {
					system.IngestLog(l)
					done <- true
				}(log)
			}
			
			// Wait for all ingestions to complete
			for range tt.logs {
				<-done
			}

			// Allow some time for indexing
			time.Sleep(100 * time.Millisecond)

			got := system.QueryLogs(tt.startTime, tt.endTime, tt.severity)
			
			if !reflect.DeepEqual(got, tt.want) {
				t.Errorf("QueryLogs() = %v, want %v", got, tt.want)
			}
		})
	}
}

func TestConcurrentQueries(t *testing.T) {
	system := NewLogAggregator()
	
	// Ingest some test data
	testLogs := []LogEntry{
		{
			Timestamp:  1000,
			DataCenter: "us-east-1",
			Severity:   "ERROR",
			Message:    "Error 1",
		},
		{
			Timestamp:  2000,
			DataCenter: "us-east-1",
			Severity:   "ERROR",
			Message:    "Error 2",
		},
	}

	for _, log := range testLogs {
		system.IngestLog(log)
	}

	// Test concurrent queries
	numQueries := 10
	done := make(chan bool)

	for i := 0; i < numQueries; i++ {
		go func() {
			result := system.QueryLogs(0, 3000, "ERROR")
			if len(result["us-east-1"]) != 2 {
				t.Errorf("Concurrent query returned incorrect number of results: got %d, want 2", len(result["us-east-1"]))
			}
			done <- true
		}()
	}

	// Wait for all queries to complete
	for i := 0; i < numQueries; i++ {
		<-done
	}
}