from .byzantine_paxos import ByzantinePaxosSimulator

def run_example_simulation():
    # Example configuration
    n = 4
    f = 1
    proposals = [
        [1, 1, 1],
        [1, 1, 1],
        [2, 2, 2],  # Byzantine node
        [1, 1, 1]
    ]
    byzantine_nodes = {2}
    
    simulator = ByzantinePaxosSimulator(n, f, proposals, byzantine_nodes)
    commitments = simulator.run()
    
    print("Commitments:")
    for i, node_commitments in enumerate(commitments):
        print(f"Node {i}: {node_commitments}")

if __name__ == "__main__":
    run_example_simulation()