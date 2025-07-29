package network_flow;

import java.util.ArrayList;
import java.util.LinkedList;
import java.util.List;
import java.util.Queue;

public class NetworkFlow {

    static class Edge {
        int from, to, capacity, flow;
        Edge rev;

        Edge(int from, int to, int capacity) {
            this.from = from;
            this.to = to;
            this.capacity = capacity;
            this.flow = 0;
        }

        public int remainingCapacity() {
            return capacity - flow;
        }
    }

    static class Dinic {
        private final int n;
        private final List<Edge>[] graph;
        private int[] level;
        private int[] next;
        private final int source, sink;
        private final int INF = Integer.MAX_VALUE;

        @SuppressWarnings("unchecked")
        public Dinic(int n, int source, int sink) {
            this.n = n;
            this.source = source;
            this.sink = sink;
            graph = new ArrayList[n];
            for (int i = 0; i < n; i++) {
                graph[i] = new ArrayList<>();
            }
        }

        public void addEdge(int from, int to, int capacity) {
            Edge forward = new Edge(from, to, capacity);
            Edge backward = new Edge(to, from, 0);
            forward.rev = backward;
            backward.rev = forward;
            graph[from].add(forward);
            graph[to].add(backward);
        }

        private boolean bfs() {
            level = new int[n];
            for (int i = 0; i < n; i++) {
                level[i] = -1;
            }
            Queue<Integer> q = new LinkedList<>();
            level[source] = 0;
            q.add(source);
            while (!q.isEmpty()) {
                int u = q.poll();
                for (Edge edge : graph[u]) {
                    if (level[edge.to] < 0 && edge.remainingCapacity() > 0) {
                        level[edge.to] = level[u] + 1;
                        q.add(edge.to);
                    }
                }
            }
            return level[sink] != -1;
        }

        private int dfs(int u, int flow) {
            if (u == sink) return flow;
            for (; next[u] < graph[u].size(); next[u]++) {
                Edge edge = graph[u].get(next[u]);
                if (level[edge.to] == level[u] + 1 && edge.remainingCapacity() > 0) {
                    int bottleNeck = dfs(edge.to, Math.min(flow, edge.remainingCapacity()));
                    if (bottleNeck > 0) {
                        edge.flow += bottleNeck;
                        edge.rev.flow -= bottleNeck;
                        return bottleNeck;
                    }
                }
            }
            return 0;
        }

        public int maxFlow() {
            int flow = 0;
            while (bfs()) {
                next = new int[n];
                int currentFlow;
                while ((currentFlow = dfs(source, INF)) > 0) {
                    flow += currentFlow;
                }
            }
            return flow;
        }
    }

    /**
     * Computes the maximum possible flow from source nodes to sink nodes in a given network.
     *
     * The network is defined with an initial number of nodes 'n', a list of directed edges,
     * a list of source node indices, a list of sink node indices, and a bandwidth limit for each node.
     *
     * Each node is split into two nodes (in and out) with an edge connecting them that limits the
     * flow through the node to its given bandwidth. For each original edge from node u to v, an edge
     * is added from u's "out" node to v's "in" node.
     *
     * A super source is connected to each source node's "in" node with infinite capacity.
     * Similarly, each sink node's "out" node is connected to a super sink with infinite capacity.
     *
     * @param n              the number of original nodes
     * @param edges          a 2D array representing directed edges in the format [u, v, capacity]
     * @param sources        an array of source node indices
     * @param sinks          an array of sink node indices
     * @param nodeBandwidths an array where the i-th element is the maximum bandwidth for node i
     * @return the maximum flow from the given source nodes to the sink nodes while respecting edge capacities and node bandwidth limits
     */
    public static int maxFlow(int n, int[][] edges, int[] sources, int[] sinks, int[] nodeBandwidths) {
        // Total nodes after splitting: each original node becomes two nodes (in and out)
        // plus super source (S) and super sink (T)
        // Mapping: for original node i:
        //    in-node index = i
        //    out-node index = i + n
        // super source index = 2*n, super sink index = 2*n + 1
        int totalNodes = 2 * n + 2;
        int superSource = 2 * n;
        int superSink = 2 * n + 1;

        Dinic dinic = new Dinic(totalNodes, superSource, superSink);
        int INF = Integer.MAX_VALUE;

        // Add edge from in-node to out-node for each original node with capacity equals node bandwidth.
        for (int i = 0; i < n; i++) {
            dinic.addEdge(i, i + n, nodeBandwidths[i]);
        }

        // Add original edges: from u_out to v_in with given capacity.
        for (int[] edge : edges) {
            int u = edge[0];
            int v = edge[1];
            int capacity = edge[2];
            dinic.addEdge(u + n, v, capacity);
        }

        // Connect super source to each source node (to its in-node) with infinite capacity.
        for (int s : sources) {
            dinic.addEdge(superSource, s, INF);
        }

        // Connect each sink node (from its out-node) to super sink with infinite capacity.
        for (int t : sinks) {
            dinic.addEdge(t + n, superSink, INF);
        }

        return dinic.maxFlow();
    }
}