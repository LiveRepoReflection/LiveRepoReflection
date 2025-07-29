import time
from threading import Thread

class Participant:
    def prepare(self):
        raise NotImplementedError("This method should be implemented by a subclass.")

    def commit(self):
        raise NotImplementedError("This method should be implemented by a subclass.")

    def abort(self):
        raise NotImplementedError("This method should be implemented by a subclass.")


class ByzantineCoordinator:
    def __init__(self, participants, f, faulty_indices=None, faulty_coordinator=False):
        self.participants = participants
        self.f = f
        self.n = len(participants)
        self.faulty_indices = faulty_indices if faulty_indices is not None else []
        self.faulty_coordinator = faulty_coordinator
        self.final_decision = None

    def run_transaction(self):
        # Phase 1: Prepare phase - gather responses from each participant
        responses = {}
        threads = []
        def call_prepare(p, idx):
            try:
                # call prepare and store response; if no response or delay, treat as None
                responses[idx] = p.prepare()
            except Exception:
                responses[idx] = None

        for idx, participant in enumerate(self.participants):
            t = Thread(target=call_prepare, args=(participant, idx))
            t.start()
            threads.append(t)
        # Wait for all threads to complete. In a synchronous model, we assume responses come within time bound.
        for t in threads:
            t.join(timeout=1)

        # Determine number of positive prepare responses.
        positive_count = 0
        for idx, resp in responses.items():
            if resp == True:
                positive_count += 1

        # If enough participants are ready, then intended decision is "commit", else "abort".
        if positive_count >= (self.n - self.f):
            intended = "commit"
        else:
            intended = "abort"

        # Phase 2: Broadcast decision to each participant.
        # If coordinator is non-faulty, send the same instruction to all.
        if not self.faulty_coordinator:
            for participant in self.participants:
                if intended == "commit":
                    participant.commit()
                else:
                    participant.abort()
            self.final_decision = intended
        else:
            # Coordinator is faulty: send conflicting instructions.
            for participant in self.participants:
                # For faulty coordinator simulation, even-indexed participants receive the intended decision,
                # odd-indexed participants receive the opposite decision.
                if participant.__dict__.get("id", None) is not None and participant.id % 2 == 0:
                    if intended == "commit":
                        participant.commit()
                    else:
                        participant.abort()
                else:
                    # For participants with odd id or no id attribute, send opposite decision.
                    if intended == "commit":
                        participant.abort()
                    else:
                        participant.commit()
            # Correction phase: honest participants communicate to resolve conflicts.
            # We assume that honest participants (those whose id is not in faulty_indices)
            # can exchange their received decisions and take a majority vote.
            honest_decisions = []
            for participant in self.participants:
                if participant.__dict__.get("id", None) not in self.faulty_indices:
                    # Only include decisions that have been set.
                    if participant.decision is not None:
                        honest_decisions.append(participant.decision)
            # Count the occurrences
            commit_count = sum(1 for d in honest_decisions if d == "commit")
            abort_count = sum(1 for d in honest_decisions if d == "abort")
            if commit_count >= abort_count:
                corrected = "commit"
            else:
                corrected = "abort"
            # Update all honest participants with the corrected decision.
            for participant in self.participants:
                if participant.__dict__.get("id", None) not in self.faulty_indices:
                    if corrected == "commit":
                        participant.commit()
                    else:
                        participant.abort()
            self.final_decision = corrected