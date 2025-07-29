import threading
import math
import time
from collections import defaultdict
from typing import Dict, List, Set

class DAOReputationSystem:
    def __init__(self, base_reputation: int = 10):
        self.base_reputation = base_reputation
        self.reputation: Dict[str, float] = defaultdict(lambda: float(base_reputation))
        self.staked_tokens: Dict[str, int] = defaultdict(int)
        self.last_active: Dict[str, float] = defaultdict(lambda: time.time())
        self.locks: Dict[str, threading.Lock] = defaultdict(threading.Lock)
        self.global_lock = threading.Lock()
        self.vote_history: Dict[str, Dict[str, bool]] = defaultdict(dict)
        self.proposal_history: Dict[str, List[str]] = defaultdict(list)

    def update_reputation(self, member_id: str, reputation_change: float) -> None:
        with self.locks[member_id]:
            new_rep = self.reputation[member_id] + reputation_change
            self.reputation[member_id] = max(0, min(1000, new_rep))
            self.last_active[member_id] = time.time()

    def get_reputation(self, member_id: str) -> float:
        with self.locks[member_id]:
            return self.reputation[member_id]

    def handle_proposal_success(self, proposer_id: str, project_impact: float, co_proposers: int) -> None:
        if co_proposers < 0:
            raise ValueError("Number of co-proposers cannot be negative")
        
        impact_factor = math.log10(project_impact + 1)
        co_proposer_factor = 1 / (co_proposers + 1)
        rep_gain = 5 * impact_factor * co_proposer_factor
        
        self.update_reputation(proposer_id, rep_gain)
        self.proposal_history[proposer_id].append(str(time.time()))

    def handle_vote(self, member_id: str, proposal_id: str, vote: bool, 
                   project_success: bool, voting_margin: float) -> None:
        if voting_margin < 0 or voting_margin > 1:
            raise ValueError("Voting margin must be between 0 and 1")
        
        self.vote_history[member_id][proposal_id] = vote
        
        if vote == project_success:
            # Reward for correct vote (higher reward for closer margins)
            rep_change = 2 * (1 - voting_margin)
        else:
            # Penalty for incorrect vote
            rep_change = -3 * (1 - voting_margin)
            
        self.update_reputation(member_id, rep_change)

    def handle_staking(self, member_id: str, staked_amount: int) -> None:
        if staked_amount < 0:
            raise ValueError("Staked amount cannot be negative")
            
        with self.locks[member_id]:
            old_staked = self.staked_tokens[member_id]
            self.staked_tokens[member_id] = staked_amount
            
            # Logarithmic reputation boost from staking
            old_boost = math.log10(old_staked + 1) if old_staked > 0 else 0
            new_boost = math.log10(staked_amount + 1) if staked_amount > 0 else 0
            rep_change = new_boost - old_boost
            
            self.reputation[member_id] += rep_change
            self.reputation[member_id] = max(0, min(1000, self.reputation[member_id]))
            self.last_active[member_id] = time.time()

    def handle_report(self, reporter_id: str, reported_id: str, is_valid: bool) -> None:
        if reporter_id == reported_id:
            raise ValueError("Member cannot report themselves")
            
        if is_valid:
            # Penalize reported member
            self.update_reputation(reported_id, -20)
            # Reward reporter
            self.update_reputation(reporter_id, 5)
        else:
            # Penalize false reporter
            self.update_reputation(reporter_id, -10)

    def apply_time_decay(self) -> None:
        current_time = time.time()
        decay_rate = 0.95  # 5% decay per period
        
        with self.global_lock:
            for member_id in list(self.reputation.keys()):
                with self.locks[member_id]:
                    time_elapsed = current_time - self.last_active[member_id]
                    decay_periods = time_elapsed / (30 * 24 * 3600)  # 30-day periods
                    
                    if decay_periods > 0:
                        decay_factor = decay_rate ** decay_periods
                        self.reputation[member_id] *= decay_factor
                        self.last_active[member_id] = current_time