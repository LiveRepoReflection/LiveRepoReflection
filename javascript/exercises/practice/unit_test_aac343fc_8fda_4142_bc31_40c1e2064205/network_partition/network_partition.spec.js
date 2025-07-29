const { describe, test, expect } = require('@jest/globals');
const { networkPartition } = require('./network_partition');

describe('networkPartition', () => {
  test('Complete graph, k=1', () => {
    const n = 4;
    const edges = [
      [0, 1, 3],
      [0, 2, 5],
      [0, 3, 4],
      [1, 2, 2],
      [1, 3, 6],
      [2, 3, 7]
    ];
    const k = 1;
    // When the graph is complete and k = 1, all nodes form a single clique.
    // The maximum latency is the maximum weight among all edges in the clique, which is 7.
    expect(networkPartition(n, edges, k)).toBe(7);
  });

  test('Singleton clusters, k = n', () => {
    const n = 4;
    // A connected chain graph where not all non-adjacent nodes are directly connected.
    const edges = [
      [0, 1, 3],
      [1, 2, 4],
      [2, 3, 5]
    ];
    const k = 4;
    // Partitioning every node into its own cluster yields a maximum latency of 0 for each.
    expect(networkPartition(n, edges, k)).toBe(0);
  });

  test('Valid partition into two cliques', () => {
    const n = 5;
    // Construct a graph with two cliques:
    // Clique 1: Nodes [0, 1, 2] with full connectivity:
    //   (0,1)=3, (0,2)=6, (1,2)=4
    // Clique 2: Nodes [3, 4] with a single edge:
    //   (3,4)=5
    // Additional edges to ensure the graph is connected:
    //   (2,3)=100, (1,4)=100
    const edges = [
      [0, 1, 3],
      [0, 2, 6],
      [1, 2, 4],
      [3, 4, 5],
      [2, 3, 100],
      [1, 4, 100]
    ];
    const k = 2;
    // Optimal partition is {0, 1, 2} and {3, 4}.
    // Clique {0,1,2} maximum latency is 6, and clique {3,4} maximum latency is 5.
    // Overall maximum latency is max(6, 5) = 6.
    expect(networkPartition(n, edges, k)).toBe(6);
  });

  test('Optimal partition selection in a non-complete graph', () => {
    const n = 3;
    // Graph with two edges:
    //   (0,1)=5 and (0,2)=100. No direct edge between 1 and 2.
    // The graph is connected via node 0.
    // Partitioning into {0,1} and {2} produces a valid clique {0,1} with maximum latency 5,
    // while singleton {2} contributes 0. The overall maximum latency is 5.
    const edges = [
      [0, 1, 5],
      [0, 2, 100]
    ];
    const k = 2;
    expect(networkPartition(n, edges, k)).toBe(5);
  });

  test('Partition impossible due to lack of clique formation', () => {
    const n = 4;
    // Create a star graph with center node 0 and leaves 1, 2, 3.
    // Edges: (0,1)=3, (0,2)=4, (0,3)=5.
    // For k=2, any partition forces at least one cluster to have two leaves,
    // but leaves are not directly connected, leading to an infinite latency scenario.
    // Hence, a valid partition is impossible.
    const edges = [
      [0, 1, 3],
      [0, 2, 4],
      [0, 3, 5]
    ];
    const k = 2;
    expect(networkPartition(n, edges, k)).toBe(-1);
  });
});