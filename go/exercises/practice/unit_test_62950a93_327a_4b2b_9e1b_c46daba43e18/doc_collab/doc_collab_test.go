package doc_collab

import (
	"errors"
	"testing"
)

func TestProcessOperations(t *testing.T) {
	testCases := []struct {
		name          string
		operations    []Operation
		expectedDoc   string
		expectingError bool
	}{
		{
			name:          "Empty Operation List",
			operations:    []Operation{},
			expectedDoc:   "",
			expectingError: false,
		},
		{
			name: "Simple Insert",
			operations: []Operation{
				{UserID: 1, OperationType: INSERT, Position: 0, Text: "hello"},
			},
			expectedDoc:   "hello",
			expectingError: false,
		},
		{
			name: "Concurrent Insert at Same Position",
			operations: []Operation{
				{UserID: 2, OperationType: INSERT, Position: 0, Text: "world "},
				{UserID: 1, OperationType: INSERT, Position: 0, Text: "hello "},
			},
			// The final ordering should respect causality from same user and tiebreaker using user IDs.
			// In this test, since the operations are concurrent and their order is determined by user ID (lower user id first if timestamp not provided)
			// Expected result: "hello world "
			expectedDoc:   "hello world ",
			expectingError: false,
		},
		{
			name: "Insert and Delete with Conflict Resolution",
			operations: []Operation{
				{UserID: 1, OperationType: INSERT, Position: 0, Text: "hello"},
				{UserID: 2, OperationType: INSERT, Position: 0, Text: "world "},
				{UserID: 1, OperationType: INSERT, Position: 5, Text: ", "},
				{UserID: 2, OperationType: DELETE, Position: 0, Text: "world "},
				{UserID: 1, OperationType: INSERT, Position: 6, Text: "!"},
			},
			// Expected final document should be "hello, world!" after conflict resolution.
			expectedDoc:   "hello, world!",
			expectingError: false,
		},
		{
			name: "Overlapping Delete and Insert",
			operations: []Operation{
				{UserID: 1, OperationType: INSERT, Position: 0, Text: "abcdef"},
				{UserID: 2, OperationType: DELETE, Position: 2, Text: "cd"},
				{UserID: 3, OperationType: INSERT, Position: 2, Text: "XY"},
			},
			// "abcdef" -> deletion at pos(2, "cd") becomes "abef", then insert "XY" at position 2 gives "abXYef"
			expectedDoc:   "abXYef",
			expectingError: false,
		},
		{
			name: "Invalid Negative Position",
			operations: []Operation{
				{UserID: 1, OperationType: INSERT, Position: -1, Text: "oops"},
			},
			expectedDoc:   "",
			expectingError: true,
		},
		{
			name: "Delete with Mismatched Text",
			operations: []Operation{
				{UserID: 1, OperationType: INSERT, Position: 0, Text: "test"},
				// Trying to delete text that does not match current content at given position should error.
				{UserID: 1, OperationType: DELETE, Position: 0, Text: "fail"},
			},
			expectedDoc:   "",
			expectingError: true,
		},
		{
			name: "Multiple Sequential Operations Preserving Causality",
			operations: []Operation{
				// User 1 operations should be applied in order
				{UserID: 1, OperationType: INSERT, Position: 0, Text: "A"},
				{UserID: 1, OperationType: INSERT, Position: 1, Text: "B"},
				// Concurrent operations from other users
				{UserID: 2, OperationType: INSERT, Position: 1, Text: "X"},
				{UserID: 3, OperationType: INSERT, Position: 1, Text: "Y"},
			},
			// Expected: User1's operations are in order and concurrent inserts at same index are resolved deterministically,
			// e.g., lower user id comes first. So final document can be "AXYB" if order is: A, (User2's X then User3's Y) then B.
			expectedDoc:   "AXYB",
			expectingError: false,
		},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			result, err := processOperations(tc.operations)
			if tc.expectingError {
				if err == nil {
					t.Errorf("Test '%s' expected an error but got none", tc.name)
				}
			} else {
				if err != nil {
					t.Errorf("Test '%s' did not expect error but got: %v", tc.name, err)
				}
				if result != tc.expectedDoc {
					t.Errorf("Test '%s' expected document: '%s' but got: '%s'", tc.name, tc.expectedDoc, result)
				}
			}
		})
	}
}

func TestConcurrentOperationOrdering(t *testing.T) {
	// This test simulates operations that could be coming concurrently.
	// In a real-world scenario, these operations may arrive in an arbitrary order.
	// Our processing function should ensure causality and determinism.
	operations := []Operation{
		{UserID: 1, OperationType: INSERT, Position: 0, Text: "start"},
		{UserID: 2, OperationType: INSERT, Position: 0, Text: "alpha "},
		{UserID: 1, OperationType: INSERT, Position: 5, Text: " middle"},
		{UserID: 3, OperationType: INSERT, Position: 0, Text: "beta "},
		{UserID: 2, OperationType: DELETE, Position: 0, Text: "alpha "},
		{UserID: 3, OperationType: INSERT, Position: 11, Text: " end"},
	}
	// Expected transformation:
	// Start with "start"
	// User 2 inserts "alpha " at pos 0 => "alpha start"
	// User 1 inserts " middle" at pos 5 => "alph middlea start" in adjusted positions,
	// then User 3 inserts "beta " at pos 0 => "beta alph middlea start"
	// then User 2 deletes "alpha " from pos 0 (assuming deletion targets exact matching substring) 
	// and finally User 3 inserts " end" at adjusted position.
	// The final expected document may depend on the conflict resolution rules.
	// For this test, we assume the deletion removes the "alpha " inserted by User 2.
	// Therefore, expected becomes "beta  middlea start end" with the appropriate position adjustments.
	// To simplify, we assume processOperations has deterministic ordering with tiebreaker favoring lower user IDs.
	// Thus, we provide an expected output based on that deterministic resolution.
	expected := "beta start middle end"
	result, err := processOperations(operations)
	if err != nil {
		t.Errorf("Unexpected error during concurrent ordering test: %v", err)
	}
	if result != expected {
		t.Errorf("Expected final document '%s', but got '%s'", expected, result)
	}
}

func TestBenchmarkProcessOperations(t *testing.T) {
	// This benchmark tests the efficiency of processOperations
	// with a relatively large number of operations.
	ops := make([]Operation, 0, 1000)
	// Build an initial string of 100 characters.
	initialText := "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()_+"
	ops = append(ops, Operation{UserID: 1, OperationType: INSERT, Position: 0, Text: initialText})
	// Append 990 simple insert operations.
	for i := 0; i < 990; i++ {
		ops = append(ops, Operation{UserID: (i % 5) + 1, OperationType: INSERT, Position: i % (len(initialText) + i), Text: "x"})
	}
	// Run the benchmark loop.
	for i := 0; i < 1000; i++ {
		_, err := processOperations(ops)
		if err != nil {
			t.Fatalf("Benchmark iteration %d resulted in error: %v", i, err)
		}
	}
}

func TestErrorOnInvalidOperations(t *testing.T) {
	// Test specific invalid operations separately
	invalidOps := []Operation{
		{UserID: 1, OperationType: INSERT, Position: -5, Text: "invalid"},
	}
	_, err := processOperations(invalidOps)
	if err == nil || !errors.Is(err, ErrInvalidOperation) {
		t.Errorf("Expected ErrInvalidOperation for negative position, got: %v", err)
	}

	mismatchOps := []Operation{
		{UserID: 1, OperationType: INSERT, Position: 0, Text: "sample"},
		{UserID: 1, OperationType: DELETE, Position: 0, Text: "nomatch"},
	}
	_, err = processOperations(mismatchOps)
	if err == nil || !errors.Is(err, ErrInvalidOperation) {
		t.Errorf("Expected ErrInvalidOperation for mismatched delete text, got: %v", err)
	}
}