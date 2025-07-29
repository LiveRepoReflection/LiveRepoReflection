package dao

import (
	"reflect"
	"testing"
)

func TestProcessBlock(t *testing.T) {
	tests := []struct {
		name           string
		blockNumber    int
		treasury       int
		members        map[int]int
		activeProposals map[int]Proposal
		votes          map[int]map[int]bool
		want           int
	}{
		{
			name:        "Simple passing proposal",
			blockNumber: 5,
			treasury:    1000,
			members: map[int]int{
				1: 10,
				2: 5,
				3: 3,
			},
			activeProposals: map[int]Proposal{
				1: {ID: 1, ProposerID: 1, Amount: 500, StartBlock: 1, EndBlock: 10},
			},
			votes: map[int]map[int]bool{
				1: {
					1: true,  // 10 voting power for yes
					2: false, // 5 voting power for no
					3: true,  // 3 voting power for yes
				},
			},
			want: 500, // Treasury after deducting 500
		},
		{
			name:        "Simple failing proposal - insufficient votes",
			blockNumber: 5,
			treasury:    1000,
			members: map[int]int{
				1: 10,
				2: 15,
			},
			activeProposals: map[int]Proposal{
				1: {ID: 1, ProposerID: 1, Amount: 500, StartBlock: 1, EndBlock: 10},
			},
			votes: map[int]map[int]bool{
				1: {
					1: true,  // 10 voting power for yes
					2: false, // 15 voting power for no
				},
			},
			want: 1000, // Treasury unchanged
		},
		{
			name:        "Simple failing proposal - insufficient funds",
			blockNumber: 5,
			treasury:    400,
			members: map[int]int{
				1: 10,
				2: 5,
			},
			activeProposals: map[int]Proposal{
				1: {ID: 1, ProposerID: 1, Amount: 500, StartBlock: 1, EndBlock: 10},
			},
			votes: map[int]map[int]bool{
				1: {
					1: true, // 10 voting power for yes
					2: true, // 5 voting power for yes
				},
			},
			want: 400, // Treasury unchanged due to insufficient funds
		},
		{
			name:        "Multiple proposals",
			blockNumber: 5,
			treasury:    1000,
			members: map[int]int{
				1: 10,
				2: 5,
				3: 3,
			},
			activeProposals: map[int]Proposal{
				1: {ID: 1, ProposerID: 1, Amount: 300, StartBlock: 1, EndBlock: 10},
				2: {ID: 2, ProposerID: 2, Amount: 200, StartBlock: 5, EndBlock: 15},
				3: {ID: 3, ProposerID: 3, Amount: 100, StartBlock: 3, EndBlock: 6},
			},
			votes: map[int]map[int]bool{
				1: {
					1: true,  // 10 voting power for yes
					2: false, // 5 voting power for no
					3: true,  // 3 voting power for yes
				},
				2: {
					1: true, // 10 voting power for yes
					2: true, // 5 voting power for yes
				},
				3: {
					1: false, // 10 voting power for no
					3: true,  // 3 voting power for yes
				},
			},
			want: 500, // 1000 - 300 - 200 = 500 (proposal 3 fails)
		},
		{
			name:        "Inactive proposals",
			blockNumber: 5,
			treasury:    1000,
			members: map[int]int{
				1: 10,
				2: 5,
			},
			activeProposals: map[int]Proposal{
				1: {ID: 1, ProposerID: 1, Amount: 300, StartBlock: 6, EndBlock: 10},  // Not active yet
				2: {ID: 2, ProposerID: 2, Amount: 200, StartBlock: 1, EndBlock: 4},   // Already ended
			},
			votes: map[int]map[int]bool{
				1: {
					1: true, // 10 voting power for yes
					2: true, // 5 voting power for yes
				},
				2: {
					1: true, // 10 voting power for yes
					2: true, // 5 voting power for yes
				},
			},
			want: 1000, // No active proposals
		},
		{
			name:        "Invalid proposal amount",
			blockNumber: 5,
			treasury:    1000,
			members: map[int]int{
				1: 10,
				2: 5,
			},
			activeProposals: map[int]Proposal{
				1: {ID: 1, ProposerID: 1, Amount: 0, StartBlock: 1, EndBlock: 10},    // Invalid amount
				2: {ID: 2, ProposerID: 2, Amount: -100, StartBlock: 1, EndBlock: 10},  // Invalid amount
				3: {ID: 3, ProposerID: 1, Amount: 300, StartBlock: 1, EndBlock: 10},   // Valid
			},
			votes: map[int]map[int]bool{
				1: {
					1: true, // 10 voting power for yes
					2: true, // 5 voting power for yes
				},
				2: {
					1: true, // 10 voting power for yes
					2: true, // 5 voting power for yes
				},
				3: {
					1: true, // 10 voting power for yes
					2: true, // 5 voting power for yes
				},
			},
			want: 700, // Only proposal 3 is valid and executed
		},
		{
			name:        "Zero voting power",
			blockNumber: 5,
			treasury:    1000,
			members: map[int]int{
				1: 10,
				2: 0,  // Zero voting power
				3: 5,
			},
			activeProposals: map[int]Proposal{
				1: {ID: 1, ProposerID: 1, Amount: 300, StartBlock: 1, EndBlock: 10},
			},
			votes: map[int]map[int]bool{
				1: {
					1: true,  // 10 voting power for yes
					2: true,  // 0 voting power - should be ignored
					3: false, // 5 voting power for no
				},
			},
			want: 700, // Proposal passes with 10 vs 5
		},
		{
			name:        "Duplicate votes",
			blockNumber: 5,
			treasury:    1000,
			members: map[int]int{
				1: 10,
				2: 5,
			},
			activeProposals: map[int]Proposal{
				1: {ID: 1, ProposerID: 1, Amount: 300, StartBlock: 1, EndBlock: 10},
			},
			votes: map[int]map[int]bool{
				1: {
					1: false, // This is the final vote (false)
					2: true,  // 5 voting power for yes
				},
			},
			want: 1000, // Proposal fails with 5 vs 10
		},
		{
			name:        "Treasury depletion order",
			blockNumber: 5,
			treasury:    500,
			members: map[int]int{
				1: 10,
				2: 5,
			},
			activeProposals: map[int]Proposal{
				1: {ID: 1, ProposerID: 1, Amount: 300, StartBlock: 1, EndBlock: 10},
				2: {ID: 2, ProposerID: 2, Amount: 300, StartBlock: 1, EndBlock: 10},
			},
			votes: map[int]map[int]bool{
				1: {
					1: true, // 10 voting power for yes
					2: true, // 5 voting power for yes
				},
				2: {
					1: true, // 10 voting power for yes
					2: true, // 5 voting power for yes
				},
			},
			want: 200, // First proposal passes (500-300=200), second fails (insufficient funds)
		},
		{
			name:        "Large scale test",
			blockNumber: 5,
			treasury:    10000,
			members: map[int]int{
				1: 1000,
				2: 800,
				3: 600,
				4: 500,
				5: 400,
			},
			activeProposals: map[int]Proposal{
				1: {ID: 1, ProposerID: 1, Amount: 3000, StartBlock: 1, EndBlock: 10},
				2: {ID: 2, ProposerID: 2, Amount: 2000, StartBlock: 1, EndBlock: 10},
				3: {ID: 3, ProposerID: 3, Amount: 1500, StartBlock: 1, EndBlock: 10},
			},
			votes: map[int]map[int]bool{
				1: {
					1: true,  // 1000 for yes
					2: true,  // 800 for yes
					3: false, // 600 for no
					4: false, // 500 for no
					5: false, // 400 for no
				},
				2: {
					1: false, // 1000 for no
					2: true,  // 800 for yes
					3: true,  // 600 for yes
					4: true,  // 500 for yes
					5: false, // 400 for no
				},
				3: {
					1: true,  // 1000 for yes
					2: false, // 800 for no
					3: true,  // 600 for yes
					4: true,  // 500 for yes
					5: true,  // 400 for yes
				},
			},
			want: 3500, // 10000 - 3000 - 2000 - 1500 = 3500
		},
		{
			name:        "No members or proposals",
			blockNumber: 5,
			treasury:    1000,
			members:     map[int]int{},
			activeProposals: map[int]Proposal{},
			votes:      map[int]map[int]bool{},
			want:       1000, // Treasury unchanged
		},
		{
			name:        "No votes on proposal",
			blockNumber: 5,
			treasury:    1000,
			members: map[int]int{
				1: 10,
				2: 5,
			},
			activeProposals: map[int]Proposal{
				1: {ID: 1, ProposerID: 1, Amount: 300, StartBlock: 1, EndBlock: 10},
			},
			votes: map[int]map[int]bool{
				// No votes for proposal 1
			},
			want: 1000, // No votes, proposal fails
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Create deep copies to ensure originals aren't modified
			membersCopy := make(map[int]int)
			for k, v := range tt.members {
				membersCopy[k] = v
			}
			
			proposalsCopy := make(map[int]Proposal)
			for k, v := range tt.activeProposals {
				proposalsCopy[k] = v
			}
			
			votesCopy := make(map[int]map[int]bool)
			for k, v := range tt.votes {
				votesCopy[k] = make(map[int]bool)
				for mk, mv := range v {
					votesCopy[k][mk] = mv
				}
			}
			
			got := ProcessBlock(tt.blockNumber, tt.treasury, membersCopy, proposalsCopy, votesCopy)
			if got != tt.want {
				t.Errorf("ProcessBlock() = %v, want %v", got, tt.want)
			}
			
			// Verify that inputs weren't modified
			if !reflect.DeepEqual(membersCopy, tt.members) {
				t.Errorf("ProcessBlock() modified members map")
			}
			if !reflect.DeepEqual(proposalsCopy, tt.activeProposals) {
				t.Errorf("ProcessBlock() modified proposals map")
			}
			
			// Check if the votes map structure is still the same
			for proposalID, memberVotes := range tt.votes {
				if _, exists := votesCopy[proposalID]; !exists {
					t.Errorf("ProcessBlock() removed proposal %d from votes map", proposalID)
					continue
				}
				for memberID, vote := range memberVotes {
					if votesCopy[proposalID][memberID] != vote {
						t.Errorf("ProcessBlock() modified vote for member %d on proposal %d", memberID, proposalID)
					}
				}
			}
		})
	}
}

func BenchmarkProcessBlock(b *testing.B) {
	// Setup a reasonable-sized test case
	treasury := 1000000
	blockNumber := 100
	
	// Create members (10,000 members)
	members := make(map[int]int)
	for i := 1; i <= 10000; i++ {
		members[i] = i % 100 + 1 // Voting power between 1 and 100
	}
	
	// Create proposals (1,000 proposals)
	proposals := make(map[int]Proposal)
	for i := 1; i <= 1000; i++ {
		proposals[i] = Proposal{
			ID:         i,
			ProposerID: i % 10000 + 1,
			Amount:     i * 100,
			StartBlock: 50,
			EndBlock:   150,
		}
	}
	
	// Create votes (100,000 votes)
	votes := make(map[int]map[int]bool)
	for i := 1; i <= 1000; i++ {
		votes[i] = make(map[int]bool)
		for j := 1; j <= 100; j++ {
			memberID := (i * j) % 10000 + 1
			votes[i][memberID] = j%2 == 0 // Alternate between true and false
		}
	}
	
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		ProcessBlock(blockNumber, treasury, members, proposals, votes)
	}
}