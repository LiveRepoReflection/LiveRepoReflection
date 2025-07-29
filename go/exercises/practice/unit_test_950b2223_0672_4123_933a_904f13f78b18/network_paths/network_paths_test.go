package networkpaths

import (
	"reflect"
	"testing"
)

func TestNetworkPathOptimizer(t *testing.T) {
	for _, tc := range testCases {
		t.Run(tc.description, func(t *testing.T) {
			npo := NewNetworkPathOptimizer(tc.edges)
			
			for _, op := range tc.operations {
				switch op.name {
				case "FindLowestLatencyPath":
					start := op.args[0].(int)
					end := op.args[1].(int)
					latency, path := npo.FindLowestLatencyPath(start, end)
					
					expectedLatency := op.expect.([]interface{})[0].(int)
					expectedPath := op.expect.([]interface{})[1].([]int)
					
					if latency != expectedLatency {
						t.Errorf("FindLowestLatencyPath(%d, %d) latency = %d, want %d", start, end, latency, expectedLatency)
					}
					
					if !reflect.DeepEqual(path, expectedPath) {
						t.Errorf("FindLowestLatencyPath(%d, %d) path = %v, want %v", start, end, path, expectedPath)
					}
					
				case "AddEdge":
					router1 := op.args[0].(int)
					router2 := op.args[1].(int)
					latency := op.args[2].(int)
					npo.AddEdge(router1, router2, latency)
					
				case "RemoveEdge":
					router1 := op.args[0].(int)
					router2 := op.args[1].(int)
					npo.RemoveEdge(router1, router2)
					
				case "DisableRouter":
					router := op.args[0].(int)
					npo.DisableRouter(router)
					
				case "EnableRouter":
					router := op.args[0].(int)
					npo.EnableRouter(router)
				}
			}
		})
	}
}

func BenchmarkNetworkPathOptimizer(b *testing.B) {
	for i := 0; i < b.N; i++ {
		for _, tc := range testCases {
			npo := NewNetworkPathOptimizer(tc.edges)
			for _, op := range tc.operations {
				switch op.name {
				case "FindLowestLatencyPath":
					start := op.args[0].(int)
					end := op.args[1].(int)
					npo.FindLowestLatencyPath(start, end)
				case "AddEdge":
					router1 := op.args[0].(int)
					router2 := op.args[1].(int)
					latency := op.args[2].(int)
					npo.AddEdge(router1, router2, latency)
				case "RemoveEdge":
					router1 := op.args[0].(int)
					router2 := op.args[1].(int)
					npo.RemoveEdge(router1, router2)
				case "DisableRouter":
					router := op.args[0].(int)
					npo.DisableRouter(router)
				case "EnableRouter":
					router := op.args[0].(int)
					npo.EnableRouter(router)
				}
			}
		}
	}
}