package dao_voting

import (
	"sync"
	"testing"
	"time"
)

// For the purpose of testing, we assume the following API is implemented in the dao_voting package:
// 
// func NewDAO() *DAO
// func (d *DAO) CreateProposal(proposalID int, deadline int64, description string) error
// func (d *DAO) Vote(proposalID int, memberID int, vote string, weight uint64) error
// func (d *DAO) GetResult(proposalID int) string
// func (d *DAO) SetQuorum(quorum int)
// func (d *DAO) SetThreshold(threshold int)
// func (d *DAO) SetCurrentTime(t int64)
//
// The test cases below cover various scenarios including edge cases, concurrent voting,
// quorum and threshold conditions, and invalid operations. The simulated time is controlled
// via the SetCurrentTime method.

func TestInvalidProposal(t *testing.T) {
	dao := NewDAO()
	// Test GET_RESULT on a proposal that doesn't exist.
	result := dao.GetResult(999)
	if result != "INVALID_PROPOSAL" {
		t.Errorf("Expected INVALID_PROPOSAL, got %s", result)
	}
}

func TestPendingProposal(t *testing.T) {
	dao := NewDAO()
	now := time.Now().Unix()
	// Proposal deadline in the future.
	err := dao.CreateProposal(1, now+1000, "Future proposal")
	if err != nil {
		t.Fatalf("Error creating proposal: %v", err)
	}
	// Set current time to now (before deadline).
	dao.SetCurrentTime(now)
	result := dao.GetResult(1)
	if result != "PENDING" {
		t.Errorf("Expected PENDING, got %s", result)
	}
}

func TestQuorumNotMet(t *testing.T) {
	dao := NewDAO()
	// Set quorum to 60% and threshold to 50% for this test.
	dao.SetQuorum(60)
	dao.SetThreshold(50)
	now := time.Now().Unix()
	// Create a proposal with deadline already passed.
	err := dao.CreateProposal(2, now-10, "Low participation")
	if err != nil {
		t.Fatalf("Error creating proposal: %v", err)
	}
	// Total potential voting weight in DAO assumed to be 100.
	// Cast a vote with a total weight lower than quorum (e.g., 40).
	err = dao.Vote(2, 1, "FOR", 40)
	if err != nil {
		t.Fatalf("Error casting vote: %v", err)
	}
	// Set current time to after deadline.
	dao.SetCurrentTime(now)
	result := dao.GetResult(2)
	if result != "QUORUM_NOT_MET" {
		t.Errorf("Expected QUORUM_NOT_MET, got %s", result)
	}
}

func TestPassingProposal(t *testing.T) {
	dao := NewDAO()
	// Set quorum to 50% and threshold to 60%
	dao.SetQuorum(50)
	dao.SetThreshold(60)
	now := time.Now().Unix()
	// Create a proposal with past deadline.
	err := dao.CreateProposal(3, now-10, "Increase budget")
	if err != nil {
		t.Fatalf("Error creating proposal: %v", err)
	}
	// Assume total possible voting weight is 200.
	// Cast FOR votes = 130, AGAINST votes = 40 (total = 170 which is > quorum of 50% of 200 = 100)
	err = dao.Vote(3, 1, "FOR", 80)
	if err != nil {
		t.Fatalf("Error casting vote: %v", err)
	}
	err = dao.Vote(3, 2, "FOR", 50)
	if err != nil {
		t.Fatalf("Error casting vote: %v", err)
	}
	err = dao.Vote(3, 3, "AGAINST", 40)
	if err != nil {
		t.Fatalf("Error casting vote: %v", err)
	}
	// Set current time to after deadline.
	dao.SetCurrentTime(now)
	result := dao.GetResult(3)
	if result != "PASS" {
		t.Errorf("Expected PASS, got %s", result)
	}
}

func TestFailingProposal(t *testing.T) {
	dao := NewDAO()
	// Set quorum to 50% and threshold to 70%
	dao.SetQuorum(50)
	dao.SetThreshold(70)
	now := time.Now().Unix()
	// Create a proposal with past deadline.
	err := dao.CreateProposal(4, now-10, "Reduce spending")
	if err != nil {
		t.Fatalf("Error creating proposal: %v", err)
	}
	// Assume total possible voting weight is 150.
	// Cast FOR votes = 60, AGAINST votes = 50 (FOR ratio = 60/110 ~ 54.5%)
	err = dao.Vote(4, 1, "FOR", 30)
	if err != nil {
		t.Fatalf("Error casting vote: %v", err)
	}
	err = dao.Vote(4, 2, "FOR", 30)
	if err != nil {
		t.Fatalf("Error casting vote: %v", err)
	}
	err = dao.Vote(4, 3, "AGAINST", 25)
	if err != nil {
		t.Fatalf("Error casting vote: %v", err)
	}
	err = dao.Vote(4, 4, "AGAINST", 25)
	if err != nil {
		t.Fatalf("Error casting vote: %v", err)
	}
	// Set current time to after deadline.
	dao.SetCurrentTime(now)
	result := dao.GetResult(4)
	if result != "REJECT" {
		t.Errorf("Expected REJECT, got %s", result)
	}
}

func TestDoubleVoting(t *testing.T) {
	dao := NewDAO()
	now := time.Now().Unix()
	err := dao.CreateProposal(5, now-10, "Double voting test")
	if err != nil {
		t.Fatalf("Error creating proposal: %v", err)
	}
	// First vote should succeed.
	err = dao.Vote(5, 1, "FOR", 100)
	if err != nil {
		t.Fatalf("Error casting first vote: %v", err)
	}
	// Second vote from the same member should return an error.
	err = dao.Vote(5, 1, "AGAINST", 100)
	if err == nil {
		t.Errorf("Expected error on second vote from the same member, but got no error")
	}
}

func TestAbstainImpact(t *testing.T) {
	dao := NewDAO()
	// Set quorum to 50% and threshold to 60%
	dao.SetQuorum(50)
	dao.SetThreshold(60)
	now := time.Now().Unix()
	err := dao.CreateProposal(6, now-10, "Abstain Test Proposal")
	if err != nil {
		t.Fatalf("Error creating proposal: %v", err)
	}
	// Cast votes: FOR:80, AGAINST:20, ABSTAIN: 50. Abstain should not affect threshold calculation.
	err = dao.Vote(6, 1, "FOR", 80)
	if err != nil {
		t.Fatalf("Error casting FOR vote: %v", err)
	}
	err = dao.Vote(6, 2, "AGAINST", 20)
	if err != nil {
		t.Fatalf("Error casting AGAINST vote: %v", err)
	}
	err = dao.Vote(6, 3, "ABSTAIN", 50)
	if err != nil {
		t.Fatalf("Error casting ABSTAIN vote: %v", err)
	}
	// Total FOR and AGAINST = 100, FOR percentage = 80%
	dao.SetCurrentTime(now)
	result := dao.GetResult(6)
	if result != "PASS" {
		t.Errorf("Expected PASS (abstain ignored), got %s", result)
	}
}

func TestConcurrentVoting(t *testing.T) {
	dao := NewDAO()
	// Set quorum to 30 and threshold to 50
	dao.SetQuorum(30)
	dao.SetThreshold(50)
	now := time.Now().Unix()
	err := dao.CreateProposal(7, now-10, "Concurrent Voting Proposal")
	if err != nil {
		t.Fatalf("Error creating proposal: %v", err)
	}

	var wg sync.WaitGroup
	// Simulate 100 concurrent votes from different members.
	memberCount := 100
	for i := 1; i <= memberCount; i++ {
		wg.Add(1)
		go func(memberID int) {
			defer wg.Done()
			// Alternate votes between FOR and AGAINST
			voteChoice := "FOR"
			if memberID%2 == 0 {
				voteChoice = "AGAINST"
			}
			// Each member votes with weight = 10.
			err := dao.Vote(7, memberID, voteChoice, 10)
			if err != nil {
				// In a concurrent scenario, double voting errors or race conditions may arise;
				// reporting error if any unexpected error arises.
				t.Errorf("Error casting vote for member %d: %v", memberID, err)
			}
		}(i)
	}
	wg.Wait()
	// Set current time to after deadline.
	dao.SetCurrentTime(now)
	result := dao.GetResult(7)
	// Calculate totals: There should be 50 FOR votes and 50 AGAINST votes.
	// FOR percentage = 50% which meets the threshold exactly.
	// Quorum met because total weight = 1000 which is > 30% of assumed total.
	if result != "PASS" && result != "REJECT" {
		t.Errorf("Expected PASS or REJECT (depending on threshold calculation), got %s", result)
	}
}