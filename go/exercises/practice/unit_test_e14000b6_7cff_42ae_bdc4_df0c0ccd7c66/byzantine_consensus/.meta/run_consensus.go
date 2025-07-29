package byzantine_consensus

import (
	"time"
)

// RunConsensus executes a simplified Byzantine consensus algorithm.
// It runs for f+1 rounds. In each round, the node broadcasts its current value
// to all other nodes and collects incoming messages for a fixed period.
// If any candidate value is received from at least (n - f) nodes (including itself),
// the node updates its current value to that candidate.
// The algorithm returns the final agreed-upon value.
func RunConsensus(nodeID, n, f int, initialValue string, sendFn func(dest int, msg []byte), receiveFn func() [][]byte) string {
	v := initialValue
	rounds := f + 1
	threshold := n - f

	for round := 0; round < rounds; round++ {
		// Broadcast the current value to all other nodes.
		for dest := 0; dest < n; dest++ {
			if dest == nodeID {
				continue
			}
			sendFn(dest, []byte(v))
		}

		// Prepare to count messages.
		countMap := make(map[string]int)
		// Count own value.
		countMap[v] = 1

		// Set a deadline to simulate waiting for messages.
		deadline := time.Now().Add(50 * time.Millisecond)
		for time.Now().Before(deadline) {
			msgs := receiveFn()
			for _, m := range msgs {
				strVal := string(m)
				countMap[strVal]++
			}
			time.Sleep(5 * time.Millisecond)
		}

		// Update current value if a candidate reached the threshold.
		for candidate, cnt := range countMap {
			if cnt >= threshold {
				v = candidate
				break
			}
		}
	}

	return v
}