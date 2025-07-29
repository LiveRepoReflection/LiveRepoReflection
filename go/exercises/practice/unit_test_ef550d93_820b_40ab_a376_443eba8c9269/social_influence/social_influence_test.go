package social_influence

import (
	"bytes"
	"strings"
	"testing"
)

// TestSocialInfluence runs comprehensive tests on the Process function.
// It feeds the input stream that contains the network description and analytical queries,
// and compares the output with the expected result.
func TestSocialInfluence(t *testing.T) {
	tests := []struct {
		name     string
		input    string
		expected string
	}{
		{
			name: "simple_propagation",
			input: "Alice Bob add\n" +
				"Alice Charlie add\n" +
				"Bob Dave add\n" +
				"END END END\n" +
				"Alice 10.0 2 0.5\n" +
				"Charlie -5.0 1 0.2\n" +
				"END 0.0 0 0.0\n",
			expected: "Alice:10.000000\n" +
				"Bob:5.000000\n" +
				"Charlie:5.000000\n" +
				"Dave:2.500000\n" +
				"Alice:-1.000000\n" +
				"Charlie:-5.000000\n",
		},
		{
			name: "edge_removal",
			input: "Alice Bob add\n" +
				"Alice Charlie add\n" +
				"Bob Dave add\n" +
				"Alice Bob remove\n" +
				"END END END\n" +
				"Alice 10.0 2 0.5\n" +
				"END 0.0 0 0.0\n",
			expected: "Alice:10.000000\n" +
				"Charlie:5.000000\n",
		},
		{
			name: "cycle_handling",
			input: "A B add\n" +
				"B C add\n" +
				"C A add\n" +
				"END END END\n" +
				"A 6.0 3 0.5\n" +
				"END 0.0 0 0.0\n",
			expected: "A:6.000000\n" +
				"B:3.000000\n" +
				"C:3.000000\n",
		},
	}

	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			inputReader := strings.NewReader(tc.input)
			var outputBuffer bytes.Buffer

			err := Process(inputReader, &outputBuffer)
			if err != nil {
				t.Fatalf("Process returned an error: %v", err)
			}

			actualOutput := outputBuffer.String()
			if actualOutput != tc.expected {
				t.Errorf("unexpected output:\nGot:\n%s\nExpected:\n%s", actualOutput, tc.expected)
			}
		})
	}
}