package circuit

// Gate represents a quantum gate
type Gate struct {
	name   string
	qubits []int
	matrix [][]complex128
}
