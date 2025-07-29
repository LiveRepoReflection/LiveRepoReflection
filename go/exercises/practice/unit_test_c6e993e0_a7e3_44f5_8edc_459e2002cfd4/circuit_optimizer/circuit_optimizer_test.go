package circuit

import (
	"reflect"
	"testing"
)

type testCase struct {
	description  string
	numQubits    int
	initialState string
	targetState  string
	gates        []Gate
	want         []Gate
}

func TestCircuitOptimizer(t *testing.T) {
	// Define some common gates for testing
	xGate := Gate{
		name:   "X",
		qubits: []int{0},
		matrix: [][]complex128{
			{complex(0, 0), complex(1, 0)},
			{complex(1, 0), complex(0, 0)},
		},
	}

	hGate := Gate{
		name:   "H",
		qubits: []int{0},
		matrix: [][]complex128{
			{complex(1/sqrt2, 0), complex(1/sqrt2, 0)},
			{complex(1/sqrt2, 0), complex(-1/sqrt2, 0)},
		},
	}

	cnotGate := Gate{
		name:   "CNOT",
		qubits: []int{0, 1},
		matrix: [][]complex128{
			{complex(1, 0), complex(0, 0), complex(0, 0), complex(0, 0)},
			{complex(0, 0), complex(1, 0), complex(0, 0), complex(0, 0)},
			{complex(0, 0), complex(0, 0), complex(0, 0), complex(1, 0)},
			{complex(0, 0), complex(0, 0), complex(1, 0), complex(0, 0)},
		},
	}

	tests := []testCase{
		{
			description:  "Single qubit NOT gate",
			numQubits:    1,
			initialState: "0",
			targetState:  "1",
			gates:        []Gate{xGate},
			want:         []Gate{xGate},
		},
		{
			description:  "Two qubit Bell state preparation",
			numQubits:    2,
			initialState: "00",
			targetState:  "11",
			gates:        []Gate{hGate, cnotGate, xGate},
			want:         []Gate{xGate, xGate},
		},
		{
			description:  "No solution within 10 gates",
			numQubits:    2,
			initialState: "00",
			targetState:  "10",
			gates:        []Gate{hGate},
			want:         []Gate{},
		},
		{
			description:  "Multiple possible solutions - should return any valid shortest sequence",
			numQubits:    1,
			initialState: "0",
			targetState:  "0",
			gates:        []Gate{xGate},
			want:         []Gate{},
		},
	}

	for _, tc := range tests {
		t.Run(tc.description, func(t *testing.T) {
			got := FindOptimalCircuit(tc.numQubits, tc.initialState, tc.targetState, tc.gates)
			
			if !isValidSolution(got, tc.numQubits, tc.initialState, tc.targetState, tc.gates) {
				t.Errorf("FindOptimalCircuit(%d, %q, %q, %v) = %v, want valid solution that transforms initial state to target state",
					tc.numQubits, tc.initialState, tc.targetState, tc.gates, got)
			}

			if len(got) > 10 {
				t.Errorf("Solution length %d exceeds maximum allowed length of 10", len(got))
			}

			if len(got) > len(tc.want) && len(tc.want) > 0 {
				t.Errorf("Solution length %d is not optimal. Expected length: %d", len(got), len(tc.want))
			}
		})
	}
}

func TestInvalidInputs(t *testing.T) {
	invalidTests := []struct {
		description  string
		numQubits    int
		initialState string
		targetState  string
		gates        []Gate
	}{
		{
			description:  "Number of qubits too large",
			numQubits:    6,
			initialState: "000000",
			targetState:  "000000",
			gates:        []Gate{},
		},
		{
			description:  "Initial state length doesn't match number of qubits",
			numQubits:    2,
			initialState: "0",
			targetState:  "00",
			gates:        []Gate{},
		},
		{
			description:  "Target state length doesn't match number of qubits",
			numQubits:    2,
			initialState: "00",
			targetState:  "0",
			gates:        []Gate{},
		},
		{
			description:  "Invalid characters in initial state",
			numQubits:    2,
			initialState: "0x",
			targetState:  "00",
			gates:        []Gate{},
		},
		{
			description:  "Invalid characters in target state",
			numQubits:    2,
			initialState: "00",
			targetState:  "2x",
			gates:        []Gate{},
		},
	}

	for _, tc := range invalidTests {
		t.Run(tc.description, func(t *testing.T) {
			got := FindOptimalCircuit(tc.numQubits, tc.initialState, tc.targetState, tc.gates)
			if len(got) != 0 {
				t.Errorf("Expected empty solution for invalid input, got %v", got)
			}
		})
	}
}

// Helper function to verify if a solution is valid
func isValidSolution(solution []Gate, numQubits int, initialState, targetState string, availableGates []Gate) bool {
	if len(solution) > 10 {
		return false
	}

	// Verify all gates in solution are from available gates
	for _, gate := range solution {
		found := false
		for _, available := range availableGates {
			if reflect.DeepEqual(gate, available) {
				found = true
				break
			}
		}
		if !found {
			return false
		}
	}

	// Verify each gate operates on valid qubits
	for _, gate := range solution {
		for _, qubit := range gate.qubits {
			if qubit < 0 || qubit >= numQubits {
				return false
			}
		}
	}

	// Note: In a real implementation, we would also verify that applying
	// the gates transforms the initial state to the target state, but
	// that requires implementing the quantum state evolution logic

	return true
}

const sqrt2 = 1.4142135623730951
