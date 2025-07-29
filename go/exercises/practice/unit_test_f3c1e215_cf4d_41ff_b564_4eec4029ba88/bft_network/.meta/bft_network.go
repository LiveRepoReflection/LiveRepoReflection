package bft_network

import (
	"crypto/sha256"
	"encoding/hex"
	"errors"
	"time"
)

// Message represents a protocol message in PBFT phases.
type Message struct {
	phase     string // "PREPREPARE", "PREPARE", "COMMIT"
	seqNo     int
	viewNo    int
	digest    string
	operation string
	sender    int
}

// StartBFTConsensus simulates the PBFT consensus protocol.
// It accepts a list of proposals (one per round), a list of faulty node indices,
// and a timeout duration. It returns the committed operations in order, or an error
// if consensus is not reached (for instance if too many nodes are faulty).
//
// Protocol assumptions:
// - The maximum tolerated number of faulty nodes (f) is 1.
// - Total nodes n = 3*f + 1 = 4.
// - Node 0 is always the static leader.
// - Honest nodes follow the protocol strictly.
// - Faulty nodes (nodes in faultyIndices) behave in a Byzantine manner by not sending any messages.
func StartBFTConsensus(proposals []string, faultyIndices []int, timeout time.Duration) ([]string, error) {
	// For simplicity, fix f = 1.
	var f int = 1
	// Check if faulty actors exceed tolerated f.
	if len(faultyIndices) > f {
		return nil, errors.New("too many faulty nodes")
	}

	// Total number of nodes.
	n := 3*f + 1

	// Create a map for quick lookup to mark faulty nodes.
	faultyMap := make(map[int]bool)
	for _, idx := range faultyIndices {
		if idx < 0 || idx >= n {
			return nil, errors.New("faulty node index out of range")
		}
		faultyMap[idx] = true
	}

	// Determine honest nodes.
	var honestNodes []int
	for i := 0; i < n; i++ {
		if !faultyMap[i] {
			honestNodes = append(honestNodes, i)
		}
	}

	// In PBFT, for consensus to be reached, each honest node must collect:
	// - In prepare phase: at least 2f prepare messages (including its own).
	// - In commit phase: at least 2f+1 commit messages (including its own).
	prepareThreshold := 2 * f
	commitThreshold := 2*f + 1

	// Simulate each round sequentially.
	committedOps := make([]string, 0, len(proposals))
	// Use a timeout channel for overall consensus duration.
	timeoutC := time.After(timeout)

	for round, op := range proposals {
		// For each round, use a local channel to simulate completion.
		done := make(chan bool, 1)

		// Run simulation in a goroutine to allow for timeout.
		var roundError error
		go func(seq int, operation string, view int) {
			// Prepare phase: Leader (node 0) sends PRE-PREPARE message.
			// Leader must be honest.
			if faultyMap[0] {
				roundError = errors.New("leader is faulty; cannot propose")
				done <- true
				return
			}

			// Compute digest.
			digest := computeDigest(operation)

			prePrepareMsg := Message{
				phase:     "PREPREPARE",
				seqNo:     seq,
				viewNo:    view,
				digest:    digest,
				operation: operation,
				sender:    0,
			}

			// Each honest node processes the pre-prepare message.
			// They validate the message (check digest consistency).
			// For simulation, if digest is valid, they accept and broadcast a PREPARE message.
			prepareMsgs := make([]Message, 0, len(honestNodes))
			for _, nodeID := range honestNodes {
				// Validate pre-prepare message.
				if validateDigest(operation, prePrepareMsg.digest) {
					// Honest node sends PREPARE.
					prepareMsg := Message{
						phase:     "PREPARE",
						seqNo:     seq,
						viewNo:    view,
						digest:    digest,
						operation: operation,
						sender:    nodeID,
					}
					prepareMsgs = append(prepareMsgs, prepareMsg)
				}
			}

			// Simulate each honest node receiving prepare messages.
			// In a synchronous network, every honest node receives messages from all honest nodes.
			// Count of prepare messages must be at least prepareThreshold.
			prepareCount := len(prepareMsgs)
			if prepareCount < prepareThreshold {
				roundError = errors.New("insufficient prepare messages received")
				done <- true
				return
			}

			// Prepare commit phase: Each honest node that reached prepare threshold broadcasts COMMIT.
			commitMsgs := make([]Message, 0, len(honestNodes))
			for _, nodeID := range honestNodes {
				commitMsg := Message{
					phase:     "COMMIT",
					seqNo:     seq,
					viewNo:    view,
					digest:    digest,
					operation: operation,
					sender:    nodeID,
				}
				commitMsgs = append(commitMsgs, commitMsg)
			}

			// Simulate commit phase: Each honest node collects commit messages.
			commitCount := len(commitMsgs)
			if commitCount < commitThreshold {
				roundError = errors.New("insufficient commit messages received")
				done <- true
				return
			}

			// Consensus reached for this round.
			done <- true
		}(round+1, op, round)

		select {
		case <-done:
			if roundError != nil {
				return nil, roundError
			}
			committedOps = append(committedOps, op)
		case <-timeoutC:
			return nil, errors.New("consensus timed out")
		}
	}

	return committedOps, nil
}

// computeDigest computes the SHA256 digest of the given operation string and returns its hex encoding.
func computeDigest(operation string) string {
	hash := sha256.Sum256([]byte(operation))
	return hex.EncodeToString(hash[:])
}

// validateDigest checks if the provided digest matches the computed digest of the operation.
func validateDigest(operation, digest string) bool {
	return computeDigest(operation) == digest
}