package network_orchestrator

import (
	"reflect"
	"testing"
)

func TestOrchestrate(t *testing.T) {
	tests := []struct {
		name     string
		topology string
		requests []Request
		want     []Response
	}{
		{
			name: "empty topology",
			topology: ``,
			requests: []Request{
				{ID: 1, Source: 0, Destination: 1, Payload: "test"},
			},
			want: []Response{
				{RequestID: 1, Success: false, Path: nil},
			},
		},
		{
			name: "simple successful routing",
			topology: `0:1
1:0,2
2:1`,
			requests: []Request{
				{ID: 1, Source: 0, Destination: 2, Payload: "test"},
			},
			want: []Response{
				{RequestID: 1, Success: true, Path: []int{0, 1, 2}},
			},
		},
		{
			name: "multiple requests with congestion",
			topology: `0:1
1:0,2
2:1,3
3:2`,
			requests: []Request{
				{ID: 1, Source: 0, Destination: 3, Payload: "test1"},
				{ID: 2, Source: 0, Destination: 3, Payload: "test2"},
			},
			want: []Response{
				{RequestID: 1, Success: true, Path: []int{0, 1, 2, 3}},
				{RequestID: 2, Success: false, Path: nil},
			},
		},
		{
			name: "disconnected nodes",
			topology: `0:1
1:0
2:3
3:2`,
			requests: []Request{
				{ID: 1, Source: 0, Destination: 3, Payload: "test"},
			},
			want: []Response{
				{RequestID: 1, Success: false, Path: nil},
			},
		},
		{
			name: "multiple shortest paths",
			topology: `0:1,2
1:0,3
2:0,3
3:1,2`,
			requests: []Request{
				{ID: 1, Source: 0, Destination: 3, Payload: "test"},
			},
			want: []Response{
				{RequestID: 1, Success: true, Path: []int{0, 1, 3}},
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := Orchestrate(tt.topology, tt.requests)
			if !reflect.DeepEqual(got, tt.want) {
				t.Errorf("Orchestrate() = %v, want %v", got, tt.want)
			}
		})
	}
}

func BenchmarkOrchestrate(b *testing.B) {
	topology := `0:1,2
1:0,3
2:0,3,4
3:1,2,5
4:2,5
5:3,4`

	requests := make([]Request, 100)
	for i := 0; i < 100; i++ {
		requests[i] = Request{
			ID:         i,
			Source:     i % 6,
			Destination: (i + 2) % 6,
			Payload:    "benchmark",
		}
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		Orchestrate(topology, requests)
	}
}