package distributed_commit

import (
	"fmt"
	"math/rand"
	"strings"
	"sync"
	"time"
)

// SimulateTransaction simulates a distributed transaction commit protocol
// using a simplified two-phase commit protocol. Nodes are simulated with
// given failure probabilities, and the coordinator (node 0) initiates the transaction.
func SimulateTransaction(n int, failureProbabilities []float64, timeoutDuration int) string {
	if len(failureProbabilities) != n {
		panic(fmt.Sprintf("Length of failureProbabilities (%d) does not match n (%d)", len(failureProbabilities), n))
	}

	// Seed random generator
	rand.Seed(time.Now().UnixNano())

	// Prepare a slice to store the final state of each node.
	// States can be "Committed", "Aborted", or "Undecided"
	states := make([]string, n)
	// Coordinator (node 0) will always complete its commit/abort phase.
	// Other nodes will update their state in their own goroutines.
	for i := 1; i < n; i++ {
		states[i] = "Undecided"
	}
	// Coordinator's state will be updated after decision phase.
	states[0] = "Undecided"

	// Channel for votes from nodes.
	type voteResult struct {
		node int
		vote string // always "commit" if sent
	}
	voteChan := make(chan voteResult, n-1)

	var wg sync.WaitGroup

	// Voting Phase: Coordinator sends prepare message to nodes 1..n-1 concurrently.
	for i := 1; i < n; i++ {
		wg.Add(1)
		go func(node int) {
			defer wg.Done()
			// Simulate a small random delay in processing.
			time.Sleep(time.Duration(rand.Intn(10)) * time.Millisecond)
			// Simulate failure in voting phase:
			// if random value is less than failure probability, node fails to send vote.
			if rand.Float64() < failureProbabilities[node] {
				// Node fails during voting phase, no vote sent.
				return
			}
			// Otherwise, node votes "commit".
			voteChan <- voteResult{node: node, vote: "commit"}
		}(i)
	}

	// Coordinator waits for votes.
	receivedVotes := make(map[int]string)
	timeout := time.After(time.Duration(timeoutDuration) * time.Millisecond)
	expectedVotes := n - 1

	collectLoop:
	for len(receivedVotes) < expectedVotes {
		select {
		case vote := <-voteChan:
			receivedVotes[vote.node] = vote.vote
		case <-timeout:
			// Timeout reached, break out.
			break collectLoop
		}
	}
	// Ensure all vote goroutines have finished.
	wg.Wait()
	close(voteChan)

	// Decision Phase:
	decision := "commit"
	// If not all votes received, then abort.
	if len(receivedVotes) < expectedVotes {
		decision = "abort"
	}
	// If any node explicitly voted abort, then decision becomes abort.
	for _, v := range receivedVotes {
		if v != "commit" {
			decision = "abort"
			break
		}
	}

	// Set coordinator's state based on decision.
	if decision == "commit" {
		states[0] = "Committed"
	} else {
		states[0] = "Aborted"
	}

	// Commit/Rollback Phase: Coordinator sends decision to nodes concurrently.
	var phaseWg sync.WaitGroup
	for i := 1; i < n; i++ {
		// Only send message to nodes that participated in voting.
		// If a node did not vote, simulate that it never receives the commit/rollback message.
		if _, ok := receivedVotes[i]; !ok {
			// Node did not vote, remains "Undecided".
			continue
		}
		phaseWg.Add(1)
		go func(node int) {
			defer phaseWg.Done()
			// Simulate a small random delay in receiving message.
			time.Sleep(time.Duration(rand.Intn(10)) * time.Millisecond)
			// Simulate potential failure during commit/rollback phase.
			// If failure occurs, the node remains in "Undecided" state.
			if rand.Float64() < failureProbabilities[node] {
				// Failure in commit/rollback phase.
				return
			}
			// Node successfully processes the decision.
			if decision == "commit" {
				states[node] = "Committed"
			} else {
				states[node] = "Aborted"
			}
		}(i)
	}
	phaseWg.Wait()

	// Format the final state string.
	var sb strings.Builder
	for i := 0; i < n; i++ {
		sb.WriteString(fmt.Sprintf("Node %d: %s", i, states[i]))
		if i != n-1 {
			sb.WriteString(", ")
		}
	}
	return sb.String()
}