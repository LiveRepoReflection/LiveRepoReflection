package network_congestion

import (
	"testing"
)

func TestSimulateNetwork(t *testing.T) {
	tests := []struct {
		name               string
		routers           []Router
		packets           []Packet
		routingTable      map[int][]int
		simulationDuration int
		want              int
	}{
		{
			name: "simple network with sufficient capacity",
			routers: []Router{
				{ID: 1, Capacity: 2, NextHop: []int{2}},
				{ID: 2, Capacity: 2, NextHop: []int{3}},
				{ID: 3, Capacity: 2, NextHop: []int{}},
			},
			packets: []Packet{
				{Source: 1, Destination: 3, CreationTime: 0},
				{Source: 1, Destination: 3, CreationTime: 0},
			},
			routingTable: map[int][]int{
				1: {1, 2, 3},
				2: {2, 3},
				3: {3},
			},
			simulationDuration: 3,
			want:              2,
		},
		{
			name: "network with congestion and drops",
			routers: []Router{
				{ID: 1, Capacity: 2, NextHop: []int{2}},
				{ID: 2, Capacity: 1, NextHop: []int{3}},
				{ID: 3, Capacity: 1, NextHop: []int{}},
			},
			packets: []Packet{
				{Source: 1, Destination: 3, CreationTime: 0},
				{Source: 1, Destination: 3, CreationTime: 0},
				{Source: 1, Destination: 3, CreationTime: 1},
			},
			routingTable: map[int][]int{
				1: {1, 2, 3},
				2: {2, 3},
				3: {3},
			},
			simulationDuration: 5,
			want:              2,
		},
		{
			name: "multiple sources to single destination",
			routers: []Router{
				{ID: 1, Capacity: 1, NextHop: []int{3}},
				{ID: 2, Capacity: 1, NextHop: []int{3}},
				{ID: 3, Capacity: 2, NextHop: []int{4}},
				{ID: 4, Capacity: 2, NextHop: []int{}},
			},
			packets: []Packet{
				{Source: 1, Destination: 4, CreationTime: 0},
				{Source: 2, Destination: 4, CreationTime: 0},
				{Source: 1, Destination: 4, CreationTime: 1},
				{Source: 2, Destination: 4, CreationTime: 1},
			},
			routingTable: map[int][]int{
				1: {1, 3, 4},
				2: {2, 3, 4},
				3: {3, 4},
				4: {4},
			},
			simulationDuration: 4,
			want:              4,
		},
		{
			name: "packets with invalid source or destination",
			routers: []Router{
				{ID: 1, Capacity: 1, NextHop: []int{2}},
				{ID: 2, Capacity: 1, NextHop: []int{}},
			},
			packets: []Packet{
				{Source: 1, Destination: 2, CreationTime: 0},
				{Source: 3, Destination: 2, CreationTime: 0},
				{Source: 1, Destination: 3, CreationTime: 0},
			},
			routingTable: map[int][]int{
				1: {1, 2},
				2: {2},
			},
			simulationDuration: 2,
			want:              1,
		},
		{
			name: "longer simulation with staggered packets",
			routers: []Router{
				{ID: 1, Capacity: 1, NextHop: []int{2}},
				{ID: 2, Capacity: 1, NextHop: []int{3}},
				{ID: 3, Capacity: 1, NextHop: []int{}},
			},
			packets: []Packet{
				{Source: 1, Destination: 3, CreationTime: 0},
				{Source: 1, Destination: 3, CreationTime: 1},
				{Source: 1, Destination: 3, CreationTime: 2},
				{Source: 1, Destination: 3, CreationTime: 3},
			},
			routingTable: map[int][]int{
				1: {1, 2, 3},
				2: {2, 3},
				3: {3},
			},
			simulationDuration: 10,
			want:              4,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := SimulateNetwork(tt.routers, tt.packets, tt.routingTable, tt.simulationDuration)
			if got != tt.want {
				t.Errorf("SimulateNetwork() = %v, want %v", got, tt.want)
			}
		})
	}
}

func BenchmarkSimulateNetwork(b *testing.B) {
	routers := []Router{
		{ID: 1, Capacity: 10, NextHop: []int{2}},
		{ID: 2, Capacity: 10, NextHop: []int{3}},
		{ID: 3, Capacity: 10, NextHop: []int{}},
	}
	packets := make([]Packet, 1000)
	for i := 0; i < 1000; i++ {
		packets[i] = Packet{Source: 1, Destination: 3, CreationTime: i % 10}
	}
	routingTable := map[int][]int{
		1: {1, 2, 3},
		2: {2, 3},
		3: {3},
	}
	simulationDuration := 100

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		SimulateNetwork(routers, packets, routingTable, simulationDuration)
	}
}