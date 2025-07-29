package dao

// Proposal represents a proposal in the DAO
type Proposal struct {
	ID         int
	ProposerID int
	Amount     int
	StartBlock int
	EndBlock   int
}