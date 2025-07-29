package circuit

import (
	"errors"
	"math"
	"math/cmplx"
)

// FindOptimalCircuit finds the shortest sequence of gates that transforms the initial state to the target state
func FindOptimalCircuit(numQubits int, initialState string, targetState string, gates []Gate) []Gate {
	// Validate inputs
	if err := validateInputs(numQubits, initialState, targetState, gates); err != nil {
		return []Gate{}
	}

	// Convert binary strings to state vectors
	initVector := stateToVector(initialState)
	targetVector := stateToVector(targetState)

	// Use BFS to find the shortest sequence of gates
	return findShortestSequence(numQubits, initVector, targetVector, gates)
}

// validateInputs checks if all inputs meet the specified constraints
func validateInputs(numQubits int, initialState string, targetState string, gates []Gate) error {
	if numQubits < 1 || numQubits > 5 {
		return errors.New("invalid number of qubits")
	}

	if len(initialState) != numQubits || len(targetState) != numQubits {
		return errors.New("state length doesn't match number of qubits")
	}

	for _, c := range initialState + targetState {
		if c != '0' && c != '1' {
			return errors.New("invalid character in state")
		}
	}

	for _, gate := range gates {
		for _, qubit := range gate.qubits {
			if qubit < 0 || qubit >= numQubits {
				return errors.New("invalid qubit index in gate")
			}
		}
	}

	return nil
}

// stateToVector converts a binary string representation to a quantum state vector
func stateToVector(state string) []complex128 {
	n := len(state)
	size := 1 << n
	vector := make([]complex128, size)
	
	// Convert binary string to decimal
	idx := 0
	for i := 0; i < n; i++ {
		if state[i] == '1' {
			idx |= 1 << (n - 1 - i)
		}
	}
	
	// Set the corresponding amplitude to 1
	vector[idx] = complex(1, 0)
	return vector
}

// findShortestSequence uses BFS to find the shortest sequence of gates
func findShortestSequence(numQubits int, initialVector, targetVector []complex128, gates []Gate) []Gate {
	type state struct {
		vector    []complex128
		sequence  []Gate
	}

	// Initialize queue with initial state
	queue := []state{{initialVector, []Gate{}}}
	visited := make(map[string]bool)
	visited[vectorToString(initialVector)] = true

	for len(queue) > 0 {
		current := queue[0]
		queue = queue[1:]

		// Check if current state matches target
		if vectorsEqual(current.vector, targetVector) {
			return current.sequence
		}

		// Stop if sequence length would exceed 10
		if len(current.sequence) >= 10 {
			continue
		}

		// Try applying each gate
		for _, gate := range gates {
			newVector := applyGate(current.vector, gate, numQubits)
			vectorStr := vectorToString(newVector)
			
			if !visited[vectorStr] {
				visited[vectorStr] = true
				newSequence := append(append([]Gate{}, current.sequence...), gate)
				queue = append(queue, state{newVector, newSequence})
			}
		}
	}

	return []Gate{} // No solution found
}

// applyGate applies a quantum gate to a state vector
func applyGate(vector []complex128, gate Gate, numQubits int) []complex128 {
	result := make([]complex128, len(vector))
	copy(result, vector)

	// Calculate affected qubits mask
	mask := 0
	for _, qubit := range gate.qubits {
		mask |= 1 << qubit
	}

	// Apply gate matrix to relevant amplitudes
	for i := 0; i < len(vector); i++ {
		if (i & mask) == 0 { // Only process once per affected subspace
			indices := make([]int, 1<<len(gate.qubits))
			indices[0] = i
			
			// Generate all affected indices
			for j := 1; j < len(indices); j++ {
				indices[j] = indices[j-1] ^ (1 << gate.qubits[countBits(j-1)])
			}

			// Apply matrix
			temp := make([]complex128, len(indices))
			for j := 0; j < len(indices); j++ {
				for k := 0; k < len(indices); k++ {
					temp[j] += gate.matrix[j][k] * vector[indices[k]]
				}
			}

			// Store results
			for j := 0; j < len(indices); j++ {
				result[indices[j]] = temp[j]
			}
		}
	}

	return result
}

// vectorsEqual checks if two quantum state vectors are equivalent up to global phase
func vectorsEqual(v1, v2 []complex128) bool {
	// Find first non-zero elements
	var phase complex128
	for i := 0; i < len(v1); i++ {
		if cmplx.Abs(v1[i]) > 1e-10 && cmplx.Abs(v2[i]) > 1e-10 {
			phase = v2[i] / v1[i]
			break
		}
	}

	// Compare all elements
	for i := 0; i < len(v1); i++ {
		if cmplx.Abs(v1[i]*phase-v2[i]) > 1e-10 {
			return false
		}
	}
	return true
}

// vectorToString converts a state vector to a string for use as map key
func vectorToString(v []complex128) string {
	result := make([]byte, len(v)*16)
	for i, c := range v {
		re := math.Round(real(c)*1e10) / 1e10
		im := math.Round(imag(c)*1e10) / 1e10
		result[i*16] = byte(re)
		result[i*16+8] = byte(im)
	}
	return string(result)
}

// countBits counts the number of 1 bits in an integer
func countBits(n int) int {
	count := 0
	for n > 0 {
		count += n & 1
		n >>= 1
	}
	return count
}