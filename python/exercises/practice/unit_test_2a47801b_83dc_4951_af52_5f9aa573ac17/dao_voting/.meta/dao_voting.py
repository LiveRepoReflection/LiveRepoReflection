import math

class Participant:
    def __init__(self, participant_id, reputation, public_key, private_key):
        self.participant_id = participant_id
        self.reputation = reputation
        self.public_key = public_key
        self.private_key = private_key

    def sign_vote(self, proposal_id, vote_decision):
        # Simplistic deterministic signature for demonstration purposes.
        return f"sig{self.participant_id}"

def verify_signature(participant, proposal_id, voter_id, vote_decision, signature):
    # In our simulation, a valid signature is assumed to be "sig{voter_id}"
    # In a real-world scenario, you would use cryptographic signature verification.
    expected_signature = f"sig{voter_id}"
    return signature == expected_signature

def determine_proposal_outcome(participants, votes, proposal_id):
    """
    Determines the outcome of a proposal based on weighted votes with a quadratic weighting mechanism.

    Args:
        participants: list of tuples (participant_id, reputation, public_key, private_key)
        votes: list of tuples (proposal_id, voter_id, vote_decision, signature)
        proposal_id: integer indicating the proposal to be evaluated

    Returns:
        True if the weighted total YES votes is strictly greater than the weighted total NO votes,
        otherwise returns False.
    """
    # Create a dictionary of participants keyed by participant_id.
    participant_dict = {}
    for p in participants:
        participant_id, reputation, public_key, private_key = p
        participant_dict[participant_id] = Participant(participant_id, reputation, public_key, private_key)

    # Process votes: only take the first valid vote per participant for the given proposal_id.
    valid_votes = {}
    for vote in votes:
        vote_proposal_id, voter_id, vote_decision, signature = vote
        if vote_proposal_id != proposal_id:
            continue
        if voter_id not in participant_dict:
            continue
        if voter_id in valid_votes:
            continue
        participant = participant_dict[voter_id]
        if not verify_signature(participant, proposal_id, voter_id, vote_decision, signature):
            continue
        valid_votes[voter_id] = vote_decision.strip().upper()

    yes_total = 0.0
    no_total = 0.0
    for voter_id, decision in valid_votes.items():
        reputation = participant_dict[voter_id].reputation
        effective_weight = math.sqrt(reputation)
        if decision == "YES":
            yes_total += effective_weight
        elif decision == "NO":
            no_total += effective_weight

    return yes_total > no_total