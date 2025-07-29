package social_mapper

import (
	"errors"
	"testing"
)

type nodeData struct {
	friends []string
	gossip  map[string][]string
}

func makeGetNodeInfo(network map[string]nodeData, unreachableSet map[string]bool) func(string) (friends []string, gossip map[string][]string, err error) {
	return func(node string) ([]string, map[string][]string, error) {
		if unreachableSet != nil {
			if unreachableSet[node] {
				return nil, nil, errors.New("node unreachable")
			}
		}
		data, ok := network[node]
		if !ok {
			return nil, nil, errors.New("node not found")
		}
		return data.friends, data.gossip, nil
	}
}

func TestEstimateComponentSize(t *testing.T) {
	// Test case 1: Simple network with nodes A-F.
	// A: friends [B, C] ; B: [A, D] ; C: [A, E] ; D: [B] ; E: [C, F] ; F: [E]
	network1 := map[string]nodeData{
		"A": {friends: []string{"B", "C"}, gossip: map[string][]string{"B": {"A", "D"}, "C": {"A", "E"}}},
		"B": {friends: []string{"A", "D"}, gossip: map[string][]string{"A": {"B", "C"}, "D": {"B"}}},
		"C": {friends: []string{"A", "E"}, gossip: map[string][]string{"A": {"B", "C"}, "E": {"C", "F"}}},
		"D": {friends: []string{"B"}, gossip: map[string][]string{"B": {"A", "D"}}},
		"E": {friends: []string{"C", "F"}, gossip: map[string][]string{"C": {"A", "E"}, "F": {"E"}}},
		"F": {friends: []string{"E"}, gossip: map[string][]string{"E": {"C", "F"}}},
	}
	getInfo1 := makeGetNodeInfo(network1, nil)
	size1 := EstimateComponentSize("A", getInfo1)
	if size1 != 6 {
		t.Errorf("Test case 1 failed: expected 6, got %d", size1)
	}

	// Test case 2: Two disconnected components.
	// Component 1: A, B, C; Component 2: D, E.
	network2 := map[string]nodeData{
		"A": {friends: []string{"B"}, gossip: map[string][]string{"B": {"A", "C"}}},
		"B": {friends: []string{"A", "C"}, gossip: map[string][]string{"A": {"B"}, "C": {"B"}}},
		"C": {friends: []string{"B"}, gossip: map[string][]string{"B": {"A", "C"}}},
		"D": {friends: []string{"E"}, gossip: map[string][]string{"E": {"D"}}},
		"E": {friends: []string{"D"}, gossip: map[string][]string{"D": {"E"}}},
	}
	getInfo2 := makeGetNodeInfo(network2, nil)
	size2 := EstimateComponentSize("A", getInfo2)
	if size2 != 3 {
		t.Errorf("Test case 2 failed starting from A: expected 3, got %d", size2)
	}
	size2b := EstimateComponentSize("D", getInfo2)
	if size2b != 2 {
		t.Errorf("Test case 2 failed starting from D: expected 2, got %d", size2b)
	}

	// Test case 3: Starting node is unreachable; should return 0.
	network3 := map[string]nodeData{
		"A": {friends: []string{"B"}, gossip: map[string][]string{"B": {"A"}}},
		"B": {friends: []string{"A"}, gossip: map[string][]string{"A": {"B"}}},
	}
	unreachable := map[string]bool{"A": true}
	getInfo3 := makeGetNodeInfo(network3, unreachable)
	size3 := EstimateComponentSize("A", getInfo3)
	if size3 != 0 {
		t.Errorf("Test case 3 failed: expected 0 for unreachable start node, got %d", size3)
	}

	// Test case 4: Network with cycles and inaccurate gossip data.
	// X - Y - Z forming a cycle with extra gossip that is unreliable.
	network4 := map[string]nodeData{
		"X": {friends: []string{"Y"}, gossip: map[string][]string{"Y": {"Z"}}},
		"Y": {friends: []string{"X", "Z"}, gossip: map[string][]string{"X": {"Y"}, "Z": {"Y", "X"}}},
		"Z": {friends: []string{"Y"}, gossip: map[string][]string{"Y": {"X"}}},
	}
	getInfo4 := makeGetNodeInfo(network4, nil)
	size4 := EstimateComponentSize("X", getInfo4)
	if size4 != 3 {
		t.Errorf("Test case 4 failed: expected 3, got %d", size4)
	}

	// Test case 5: Complex network with inaccurate gossip and multiple branches.
	network5 := map[string]nodeData{
		"node1": {friends: []string{"node2", "node3"}, gossip: map[string][]string{"node2": {"node1", "node4"}, "node3": {"node1"}}},
		"node2": {friends: []string{"node1", "node4"}, gossip: map[string][]string{"node1": {"node2"}, "node4": {"node2", "node5"}}},
		"node3": {friends: []string{"node1"}, gossip: map[string][]string{"node1": {"node3"}, "node5": {"node3"}}},
		"node4": {friends: []string{"node2"}, gossip: map[string][]string{"node2": {"node1", "node4"}}},
		"node5": {friends: []string{"node6"}, gossip: map[string][]string{"node6": {"node5"}}},
		"node6": {friends: []string{"node5"}, gossip: map[string][]string{"node5": {"node6", "node1"}}},
	}
	// There are two components: {node1, node2, node3, node4} and {node5, node6}.
	getInfo5 := makeGetNodeInfo(network5, nil)
	size5 := EstimateComponentSize("node1", getInfo5)
	if size5 != 4 {
		t.Errorf("Test case 5 failed starting from node1: expected 4, got %d", size5)
	}
	size5b := EstimateComponentSize("node5", getInfo5)
	if size5b != 2 {
		t.Errorf("Test case 5 failed starting from node5: expected 2, got %d", size5b)
	}
}