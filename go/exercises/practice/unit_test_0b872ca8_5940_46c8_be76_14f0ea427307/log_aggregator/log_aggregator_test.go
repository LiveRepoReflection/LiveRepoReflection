package log_aggregator

import (
	"testing"
	"time"
)

func TestIngestLog(t *testing.T) {
	agg := NewLogAggregator()
	defer agg.Shutdown()

	testCases := []struct {
		name      string
		timestamp int64
		level     string
		message   string
		appID     string
		wantErr   bool
	}{
		{"valid log", time.Now().UnixNano(), "INFO", "test message", "app1", false},
		{"empty message", time.Now().UnixNano(), "WARN", "", "app2", false},
		{"invalid level", time.Now().UnixNano(), "INVALID", "msg", "app3", true},
		{"empty appID", time.Now().UnixNano(), "ERROR", "msg", "", true},
		{"future timestamp", time.Now().Add(1 * time.Hour).UnixNano(), "DEBUG", "msg", "app4", true},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			err := agg.IngestLog(tc.timestamp, tc.level, tc.message, tc.appID)
			if (err != nil) != tc.wantErr {
				t.Errorf("IngestLog() error = %v, wantErr %v", err, tc.wantErr)
			}
		})
	}
}

func TestQueryLogs(t *testing.T) {
	agg := NewLogAggregator()
	defer agg.Shutdown()

	now := time.Now()
	logs := []struct {
		timestamp int64
		level     string
		message   string
		appID     string
	}{
		{now.Add(-5 * time.Minute).UnixNano(), "INFO", "msg1", "app1"},
		{now.Add(-4 * time.Minute).UnixNano(), "WARN", "msg2", "app1"},
		{now.Add(-3 * time.Minute).UnixNano(), "ERROR", "msg3", "app2"},
		{now.Add(-2 * time.Minute).UnixNano(), "DEBUG", "msg4", "app2"},
		{now.Add(-1 * time.Minute).UnixNano(), "INFO", "msg5", "app3"},
	}

	for _, log := range logs {
		if err := agg.IngestLog(log.timestamp, log.level, log.message, log.appID); err != nil {
			t.Fatalf("Failed to ingest test log: %v", err)
		}
	}

	tests := []struct {
		name     string
		appID    string
		start    int64
		end      int64
		levels   []string
		wantLen  int
		wantErr  bool
	}{
		{"all logs", "", now.Add(-10 * time.Minute).UnixNano(), now.UnixNano(), nil, 5, false},
		{"specific app", "app1", now.Add(-10 * time.Minute).UnixNano(), now.UnixNano(), nil, 2, false},
		{"time range", "", now.Add(-4 * time.Minute).UnixNano(), now.Add(-2 * time.Minute).UnixNano(), nil, 3, false},
		{"level filter", "", now.Add(-10 * time.Minute).UnixNano(), now.UnixNano(), []string{"INFO", "WARN"}, 3, false},
		{"invalid time range", "", now.UnixNano(), now.Add(-10 * time.Minute).UnixNano(), nil, 0, true},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := agg.QueryLogs(tt.appID, tt.start, tt.end, tt.levels)
			if (err != nil) != tt.wantErr {
				t.Errorf("QueryLogs() error = %v, wantErr %v", err, tt.wantErr)
				return
			}
			if len(got) != tt.wantLen {
				t.Errorf("QueryLogs() got %d logs, want %d", len(got), tt.wantLen)
			}
		})
	}
}

func TestGetLevelCounts(t *testing.T) {
	agg := NewLogAggregator()
	defer agg.Shutdown()

	now := time.Now()
	logs := []struct {
		timestamp int64
		level     string
		message   string
		appID     string
	}{
		{now.Add(-5 * time.Minute).UnixNano(), "INFO", "msg1", "app1"},
		{now.Add(-4 * time.Minute).UnixNano(), "INFO", "msg2", "app1"},
		{now.Add(-3 * time.Minute).UnixNano(), "ERROR", "msg3", "app2"},
		{now.Add(-2 * time.Minute).UnixNano(), "DEBUG", "msg4", "app2"},
		{now.Add(-1 * time.Minute).UnixNano(), "INFO", "msg5", "app3"},
	}

	for _, log := range logs {
		if err := agg.IngestLog(log.timestamp, log.level, log.message, log.appID); err != nil {
			t.Fatalf("Failed to ingest test log: %v", err)
		}
	}

	tests := []struct {
		name    string
		start   int64
		end     int64
		want    map[string]int
		wantErr bool
	}{
		{
			"full range",
			now.Add(-10 * time.Minute).UnixNano(),
			now.UnixNano(),
			map[string]int{"INFO": 3, "ERROR": 1, "DEBUG": 1},
			false,
		},
		{
			"partial range",
			now.Add(-4 * time.Minute).UnixNano(),
			now.Add(-2 * time.Minute).UnixNano(),
			map[string]int{"INFO": 1, "ERROR": 1, "DEBUG": 1},
			false,
		},
		{
			"invalid range",
			now.UnixNano(),
			now.Add(-10 * time.Minute).UnixNano(),
			nil,
			true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := agg.GetLevelCounts(tt.start, tt.end)
			if (err != nil) != tt.wantErr {
				t.Errorf("GetLevelCounts() error = %v, wantErr %v", err, tt.wantErr)
				return
			}
			if !tt.wantErr {
				for level, count := range tt.want {
					if got[level] != count {
						t.Errorf("GetLevelCounts() level %s count = %d, want %d", level, got[level], count)
					}
				}
			}
		})
	}
}

func TestConcurrentAccess(t *testing.T) {
	agg := NewLogAggregator()
	defer agg.Shutdown()

	numRoutines := 100
	done := make(chan bool)

	for i := 0; i < numRoutines; i++ {
		go func(id int) {
			appID := "app" + string(rune(id%3))
			level := "INFO"
			if id%5 == 0 {
				level = "ERROR"
			} else if id%3 == 0 {
				level = "WARN"
			}

			err := agg.IngestLog(time.Now().UnixNano(), level, "message", appID)
			if err != nil {
				t.Errorf("IngestLog failed in goroutine: %v", err)
			}

			_, err = agg.QueryLogs(appID, time.Now().Add(-1*time.Minute).UnixNano(), time.Now().UnixNano(), []string{level})
			if err != nil {
				t.Errorf("QueryLogs failed in goroutine: %v", err)
			}

			done <- true
		}(i)
	}

	for i := 0; i < numRoutines; i++ {
		<-done
	}

	counts, err := agg.GetLevelCounts(time.Now().Add(-1*time.Minute).UnixNano(), time.Now().UnixNano())
	if err != nil {
		t.Fatalf("GetLevelCounts failed: %v", err)
	}

	total := 0
	for _, count := range counts {
		total += count
	}
	if total != numRoutines {
		t.Errorf("Expected %d logs, got %d", numRoutines, total)
	}
}