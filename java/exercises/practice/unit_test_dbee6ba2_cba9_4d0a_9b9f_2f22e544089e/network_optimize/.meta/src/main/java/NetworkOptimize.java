package network_optimize;

import java.util.*;

public class NetworkOptimize {

    static final int INF = Integer.MAX_VALUE / 2;

    public static int optimize(int n, int[] capacities, int[] traffic, List<List<Integer>> edges, int[] delays) {
        // Preliminary check: if any source or sink already exceeds its capacity, no solution.
        for (int i = 0; i < n; i++) {
            if (traffic[i] < 0 && -traffic[i] > capacities[i]) return -1;
            if (traffic[i] > 0 && traffic[i] > capacities[i]) return -1;
        }

        // Determine lower bound: at least the maximum inherent load among nodes.
        int lowerBound = 0;
        for (int i = 0; i < n; i++) {
            int inherent = Math.abs(traffic[i]);
            lowerBound = Math.max(lowerBound, inherent);
        }
        // Upper bound: maximum capacity among routers.
        int upperBound = 0;
        for (int cap : capacities) {
            upperBound = Math.max(upperBound, cap);
        }
        int answer = -1;
        while (lowerBound <= upperBound) {
            int mid = lowerBound + (upperBound - lowerBound) / 2;
            if (isFeasible(n, capacities, traffic, edges, delays, mid)) {
                answer = mid;
                upperBound = mid - 1;
            } else {
                lowerBound = mid + 1;
            }
        }
        return answer;
    }

    private static boolean isFeasible(int n, int[] capacities, int[] traffic, List<List<Integer>> edgeList, int[] delays, int candidateLoad) {
        // Build min cost flow network with vertex splitting.
        // Total nodes: S, for each router: in and out, and T.
        // S index = 0, for router i: in = 1 + 2*i, out = 1 + 2*i + 1, T = 1 + 2*n
        int totalNodes = 2 * n + 2;
        int S = 0;
        int T = totalNodes - 1;
        MinCostMaxFlow mcmf = new MinCostMaxFlow(totalNodes, S, T);

        // For each router, add vertex capacity edge from in to out.
        for (int i = 0; i < n; i++) {
            int inNode = 1 + 2 * i;
            int outNode = inNode + 1;
            // The allowed flow for node i is the minimum of candidateLoad and its physical capacity.
            int cap = Math.min(candidateLoad, capacities[i]);
            // Add cost for processing in this router.
            mcmf.addEdge(inNode, outNode, cap, delays[i]);
        }

        // For each original undirected edge, add edges in both directions
        for (List<Integer> pair : edgeList) {
            int u = pair.get(0);
            int v = pair.get(1);
            int uOut = 1 + 2 * u + 1;
            int vIn = 1 + 2 * v;
            int vOut = 1 + 2 * v + 1;
            int uIn = 1 + 2 * u;
            // Use INF capacity edges with cost 0.
            mcmf.addEdge(uOut, vIn, INF, 0);
            mcmf.addEdge(vOut, uIn, INF, 0);
        }

        // Connect super source and sink.
        int totalDemand = 0;
        for (int i = 0; i < n; i++) {
            int inNode = 1 + 2 * i;
            int outNode = inNode + 1;
            if (traffic[i] < 0) {
                // Source: supply -traffic[i]
                int supply = -traffic[i];
                mcmf.addEdge(S, inNode, supply, 0);
                totalDemand += supply;
            } else if (traffic[i] > 0) {
                // Sink: required demand traffic[i]
                int demand = traffic[i];
                mcmf.addEdge(outNode, T, demand, 0);
            }
            // For traffic==0, nothing added.
        }

        // Run min cost max flow
        MinCostMaxFlow.Result result = mcmf.minCostMaxFlow();
        // Feasible if and only if we can send totalDemand flow.
        return result.flow == totalDemand;
    }

    // Implementation of Min Cost Max Flow using successive shortest path algorithm with potentials.
    static class MinCostMaxFlow {
        int N;
        int S, T;
        List<Edge>[] graph;

        public MinCostMaxFlow(int N, int S, int T) {
            this.N = N;
            this.S = S;
            this.T = T;
            graph = new ArrayList[N];
            for (int i = 0; i < N; i++) {
                graph[i] = new ArrayList<>();
            }
        }

        void addEdge(int s, int t, int capacity, int cost) {
            Edge a = new Edge(s, t, capacity, cost);
            Edge b = new Edge(t, s, 0, -cost);
            a.rev = b;
            b.rev = a;
            graph[s].add(a);
            graph[t].add(b);
        }

        Result minCostMaxFlow() {
            int flow = 0;
            int cost = 0;
            int[] dist = new int[N];
            Edge[] prev = new Edge[N];
            int[] potential = new int[N];
            Arrays.fill(potential, 0);

            while (true) {
                // Dijkstra's algorithm
                Arrays.fill(dist, INF);
                dist[S] = 0;
                PriorityQueue<Node> pq = new PriorityQueue<>(Comparator.comparingInt(a -> a.dist));
                pq.offer(new Node(S, 0));
                while (!pq.isEmpty()) {
                    Node cur = pq.poll();
                    if (cur.dist != dist[cur.id]) continue;
                    for (Edge e : graph[cur.id]) {
                        if (e.capacity > 0) {
                            int nd = cur.dist + e.cost + potential[cur.id] - potential[e.to];
                            if (nd < dist[e.to]) {
                                dist[e.to] = nd;
                                prev[e.to] = e;
                                pq.offer(new Node(e.to, nd));
                            }
                        }
                    }
                }
                if (dist[T] == INF) break;
                for (int i = 0; i < N; i++) {
                    if (dist[i] < INF) {
                        potential[i] += dist[i];
                    }
                }
                int addFlow = INF;
                for (int v = T; v != S; ) {
                    Edge e = prev[v];
                    addFlow = Math.min(addFlow, e.capacity);
                    v = e.from;
                }
                for (int v = T; v != S; ) {
                    Edge e = prev[v];
                    e.capacity -= addFlow;
                    e.rev.capacity += addFlow;
                    v = e.from;
                }
                flow += addFlow;
                cost += addFlow * potential[T];
            }
            return new Result(flow, cost);
        }

        static class Result {
            int flow, cost;
            Result(int flow, int cost) {
                this.flow = flow;
                this.cost = cost;
            }
        }

        static class Node {
            int id, dist;
            Node(int id, int dist) {
                this.id = id;
                this.dist = dist;
            }
        }

        static class Edge {
            int from, to, capacity, cost;
            Edge rev;
            Edge(int from, int to, int capacity, int cost) {
                this.from = from;
                this.to = to;
                this.capacity = capacity;
                this.cost = cost;
            }
        }
    }
}