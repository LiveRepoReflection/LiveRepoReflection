import time
import math

class DelegationError(Exception):
    pass

class Proposal:
    def __init__(self, proposal_id, description, params, deadline, snapshot):
        self.id = proposal_id
        self.description = description
        self.params = params
        self.deadline = deadline
        self.vote_results = {"for": 0, "against": 0, "abstain": 0}
        self.status = "pending"
        self.snapshot = snapshot.copy()  # immutable snapshot of token balances at creation
        self.creation_time = time.time()
        # Record votes: mapping voter -> (vote_type, tokens contributed)
        self.vote_record = {}

class DAO:
    def __init__(self, members, portfolio, quorum, threshold, timelock):
        # members: dict of member_id to token balance (int)
        # portfolio: dict of asset_name to quantity (int)
        self.members = members.copy()
        self.portfolio = portfolio.copy()
        self.quorum = quorum  # fraction, e.g., 0.5 means 50%
        self.threshold = threshold  # fraction for "for" votes
        self.timelock = timelock  # in seconds
        # proposals stored with unique id as key
        self.proposals = {}
        self.proposal_counter = 1
        # delegation mapping: delegator -> delegatee
        self.delegations = {}
        # track which members have had their vote cast via delegation or individually per proposal
        # We'll keep the vote_record in Proposal to track voters who have voted (either directly or by delegation)

    def create_proposal(self, description, params, deadline):
        # Validate parameters: amount should be non-negative
        if "amount" in params and params["amount"] < 0:
            raise ValueError("Asset amount cannot be negative")
        # Create a snapshot of current members token balances for this proposal.
        snapshot = self.members.copy()
        proposal_id = self.proposal_counter
        self.proposal_counter += 1
        proposal = Proposal(proposal_id, description, params, deadline, snapshot)
        self.proposals[proposal_id] = proposal
        return proposal

    def vote(self, proposal_id, member, vote_type):
        if proposal_id not in self.proposals:
            raise ValueError("Proposal does not exist")
        proposal = self.proposals[proposal_id]
        # Check if proposal voting deadline has passed.
        if time.time() > proposal.deadline:
            raise ValueError("Voting deadline has passed")

        # If member already voted, do not allow voting twice.
        if member in proposal.vote_record:
            raise ValueError("Member has already voted on this proposal")
        
        total_tokens = proposal.snapshot.get(member, 0)
        # Check for delegations: add tokens from members that delegated to this voter and have not voted yet.
        delegated_members = [delegator for delegator, delegatee in self.delegations.items() if delegatee == member]
        for delegator in delegated_members:
            # Avoid double voting: if delegator already voted individually, skip.
            if delegator in proposal.vote_record:
                continue
            # Add delegator's snapshot tokens.
            total_tokens += proposal.snapshot.get(delegator, 0)
            # Mark delegator as having their vote cast via delegation.
            proposal.vote_record[delegator] = (vote_type, proposal.snapshot.get(delegator, 0))
        
        # Record the voter's own vote.
        proposal.vote_record[member] = (vote_type, proposal.snapshot.get(member, 0))
        # Update vote_results linearly.
        proposal.vote_results[vote_type] += total_tokens

    def delegate(self, delegator, delegatee):
        if delegator == delegatee:
            raise DelegationError("Delegator and delegatee must be different")
        # Ensure delegator hasn't already delegated or voted in any proposal is not checked at delegation time.
        self.delegations[delegator] = delegatee

    def snapshot_total(self, proposal):
        # Return list of snapshot tokens
        return list(proposal.snapshot.values())

    def is_quorum_met(self, proposal):
        total_snapshot = sum(proposal.snapshot.values())
        # Total tokens that participated in the vote are:
        participated = sum(proposal.vote_results.values())
        return participated >= self.quorum * total_snapshot

    def is_threshold_met(self, proposal):
        total_snapshot = sum(proposal.snapshot.values())
        # Check if "for" votes meet threshold of total eligible tokens
        return (proposal.vote_results["for"] / total_snapshot) >= self.threshold

    def can_execute(self, proposal):
        # Check if timelock has elapsed.
        return time.time() >= proposal.creation_time + self.timelock

    def is_malicious(self, proposal):
        # Simple malicious detection: check suspicious keywords in description.
        suspicious_keywords = ["MALICIOUS", "Drain", "!!!"]
        for keyword in suspicious_keywords:
            if keyword.lower() in proposal.description.lower():
                return True
        return False

    def get_effective_vote_weight(self, proposal, vote_type):
        # For quadratic voting, combine all tokens for the given vote_type and return the square root.
        # Find all votes of vote_type in the vote_record.
        total_tokens = 0
        # Instead of summing proposal.vote_results[vote_type] (which is the linear sum that might include delegation doubled),
        # we recalc from the vote_record to ensure we square only once per voter.
        # However, note that for delegated votes, we have stored each delegator separately.
        for voter, (v_type, tokens) in proposal.vote_record.items():
            if v_type == vote_type:
                total_tokens += tokens
        # Effective weight is square root of the sum.
        return math.sqrt(total_tokens)

    def execute_proposal(self, proposal_id):
        if proposal_id not in self.proposals:
            raise ValueError("Proposal does not exist")
        proposal = self.proposals[proposal_id]
        if not self.can_execute(proposal):
            raise ValueError("Timelock period has not elapsed")
        # Check if proposal is malicious
        if self.is_malicious(proposal):
            proposal.status = "rejected"
            return
        # Check quorum and threshold
        if not self.is_quorum_met(proposal) or not self.is_threshold_met(proposal):
            proposal.status = "rejected"
            return
        # Simulate execution: adjust portfolio based on proposal params.
        asset = proposal.params.get("asset")
        amount = proposal.params.get("amount")
        if asset not in self.portfolio:
            # If asset does not exist in portfolio, no transfer occurs.
            proposal.status = "rejected"
            return
        # Deduct asset amount from portfolio if sufficient funds exist.
        if self.portfolio[asset] >= amount:
            self.portfolio[asset] -= amount
            proposal.status = "executed"
        else:
            proposal.status = "rejected"