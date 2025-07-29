import random

def reconcile(datasets):
    # This function simulates a complex and computationally expensive reconciliation.
    # For simplicity, it selects the dataset that appears most frequently.
    frequency = {}
    for ds in datasets:
        key = tuple(ds)
        frequency[key] = frequency.get(key, 0) + 1
    max_count = max(frequency.values())
    for key, count in frequency.items():
        if count == max_count:
            return list(key)
    # Fallback (should not happen as there is always at least one dataset)
    return datasets[0]

class Bank:
    def __init__(self, bank_id, is_byzantine=False):
        self.id = bank_id
        self.is_byzantine = is_byzantine
        # Honest banks start with a uniform, agreed base dataset.
        if not is_byzantine:
            self.dataset = [1, 2, 3]
        else:
            # Byzantine banks start with a divergent and malicious dataset.
            # We simulate malicious behavior by adding a unique element.
            self.dataset = [bank_id, 999]
        self.messages = []

    def broadcast(self, banks, round_id):
        for bank in banks:
            if bank.id == self.id:
                continue
            msg = self.create_message(round_id)
            bank.receive_message(msg)

    def create_message(self, round_id):
        # Honest banks send their current dataset.
        # Byzantine banks may send a manipulated dataset.
        if self.is_byzantine:
            # Byzantine behavior: randomize the dataset to confuse consensus.
            manipulated = self.dataset.copy()
            # Introduce a random noise element between 1000 and 2000.
            manipulated.append(random.randint(1000, 2000))
            return {"sender": self.id, "dataset": manipulated, "round": round_id}
        else:
            return {"sender": self.id, "dataset": self.dataset, "round": round_id}

    def receive_message(self, message):
        self.messages.append(message)

    def process_messages(self):
        # Honest banks update their dataset using the reconciliation of all received datasets.
        if not self.is_byzantine:
            collected = [msg["dataset"] for msg in self.messages]
            # Include own dataset in the reconciliation
            collected.append(self.dataset)
            self.dataset = reconcile(collected)
        else:
            # Byzantine banks do not attempt to reach consensus;
            # they may keep their original dataset or continue to behave maliciously.
            self.dataset = self.dataset
        # Clear messages after processing
        self.messages = []

def simulate_protocol(num_banks, byzantine_count):
    # Check for impossible configurations: Byzantine fault tolerance requires n > 3f.
    if num_banks <= 3 * byzantine_count:
        raise ValueError("n must be greater than 3f")
    # For consistency in simulation, assign the first 'byzantine_count' banks as Byzantine.
    banks = [Bank(i, is_byzantine=(i < byzantine_count)) for i in range(num_banks)]
    
    # Simulate a fixed number of synchronous rounds where banks exchange messages.
    rounds = 3
    for round_id in range(rounds):
        # Each bank broadcasts its message to all others.
        for bank in banks:
            bank.broadcast(banks, round_id)
        # After broadcasting, each bank processes the messages received.
        for bank in banks:
            bank.process_messages()
    return banks