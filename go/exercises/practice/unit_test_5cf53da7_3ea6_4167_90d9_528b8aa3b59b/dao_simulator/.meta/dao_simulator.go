package dao

// Proposal represents a proposal in the DAO
type Proposal struct {
	ID         int
	ProposerID int
	Amount     int
	StartBlock int
	EndBlock   int
}

// ProcessBlock processes all active proposals in the current block and returns the updated treasury balance
func ProcessBlock(blockNumber int, treasury int, members map[int]int, activeProposals map[int]Proposal, votes map[int]map[int]bool) int {
	// Create a slice to store active proposal IDs so we can sort them
	var activeProposalIDs []int
	
	// Filter active proposals
	for id, proposal := range activeProposals {
		// Check if proposal is active in the current block
		if proposal.StartBlock <= blockNumber && blockNumber <= proposal.EndBlock {
			// Check if proposal amount is valid (positive)
			if proposal.Amount > 0 {
				activeProposalIDs = append(activeProposalIDs, id)
			}
		}
	}
	
	// Sort active proposal IDs to process them in order
	sortProposalIDs(activeProposalIDs)
	
	// Process each active proposal
	for _, proposalID := range activeProposalIDs {
		proposal := activeProposals[proposalID]
		
		// Skip if proposal's amount is greater than current treasury
		if proposal.Amount > treasury {
			continue
		}
		
		// Tally votes
		yesVotingPower := 0
		noVotingPower := 0
		
		// Get votes for this proposal
		proposalVotes, exists := votes[proposalID]
		if exists {
			for memberID, voteYes := range proposalVotes {
				// Get member's voting power
				votingPower, memberExists := members[memberID]
				if !memberExists || votingPower <= 0 {
					// Skip if member doesn't exist or has zero voting power
					continue
				}
				
				// Add voting power to appropriate tally
				if voteYes {
					yesVotingPower += votingPower
				} else {
					noVotingPower += votingPower
				}
			}
		}
		
		// Check if proposal passes
		if yesVotingPower > noVotingPower {
			// Proposal passes, deduct amount from treasury
			treasury -= proposal.Amount
		}
	}
	
	return treasury
}

// sortProposalIDs sorts proposal IDs in ascending order
func sortProposalIDs(ids []int) {
	// Simple insertion sort for the IDs
	for i := 1; i < len(ids); i++ {
		key := ids[i]
		j := i - 1
		
		for j >= 0 && ids[j] > key {
			ids[j+1] = ids[j]
			j--
		}
		
		ids[j+1] = key
	}
}