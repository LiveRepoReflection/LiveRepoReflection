import java.util.*;

public class NetworkFlowOptimization {

    // Edge class for Dinic's algorithm
    static class Edge {
        int to, rev;
        int cap;
        final int initCap; // store initial capacity for later checking
        
        Edge(int to, int rev, int cap) {
            this.to = to;
            this.rev = rev;
            this.cap = cap;
            this.initCap = cap;
        }
    }

    // Graph represented as an array of lists of edges
    private List<Edge>[] graph;
    private int[] level;
    private int[] iter;
    private int V; // number of vertices in the flow network

    // Adds an edge from 'from' to 'to' with capacity cap
    private void addEdge(int from, int to, int cap) {
        graph[from].add(new Edge(to, graph[to].size(), cap));
        graph[to].add(new Edge(from, graph[from].size()-1, 0));
    }

    // Build level graph using BFS
    private void bfs(int s) {
        level = new int[V];
        Arrays.fill(level, -1);
        Queue<Integer> queue = new ArrayDeque<>();
        level[s] = 0;
        queue.offer(s);
        while(!queue.isEmpty()){
            int v = queue.poll();
            for(Edge e : graph[v]){
                if(e.cap > 0 && level[e.to] < 0){
                    level[e.to] = level[v] + 1;
                    queue.offer(e.to);
                }
            }
        }
    }

    // DFS to find augmenting flow
    private int dfs(int v, int t, int upTo) {
        if(v == t) return upTo;
        for(; iter[v] < graph[v].size(); iter[v]++){
            Edge e = graph[v].get(iter[v]);
            if(e.cap > 0 && level[v] < level[e.to]){
                int d = dfs(e.to, t, Math.min(upTo, e.cap));
                if(d > 0){
                    e.cap -= d;
                    graph[e.to].get(e.rev).cap += d;
                    return d;
                }
            }
        }
        return 0;
    }

    // Dinic's algorithm to compute maximum flow from s to t
    private int maxFlowDinic(int s, int t) {
        int flow = 0;
        final int INF = Integer.MAX_VALUE;
        while (true) {
            bfs(s);
            if (level[t] < 0) break;
            iter = new int[V];
            while (true) {
                int f = dfs(s, t, INF);
                if (f == 0) break;
                flow += f;
            }
        }
        return flow;
    }

    /**
     * Computes the maximum flow from source to sink subject to:
     * - For each vertex i (represented by an edge from i_in to i_out), the flow passing through does not exceed supplies[i].
     * - For each vertex i (except the source), the flow passing through (i_in -> i_out) is at least demands[i].
     * 
     * The transformation uses vertex splitting:
     * For each original node i, we create two nodes: i_in = i and i_out = i + N.
     * An edge from i_in to i_out is added with capacity = supplies[i].
     * For every original edge from u to v with capacity c, an edge is added from u_out to v_in with capacity c.
     * The source of the flow is the original source's in-vertex (source) and the sink is the original sink's out-vertex (sink + N).
     *
     * After computing the maximum flow, the mandatory demand constraints are verified.
     * If for any node i (except the source) the flow passing through (i_in -> i_out) is less than demands[i],
     * then the function returns -1 to indicate that no feasible flow exists.
     *
     * @param N         the number of nodes
     * @param links     a list of int arrays, each representing [u, v, capacity]
     * @param source    the source node
     * @param sink      the sink node
     * @param demands   a list of int arrays, each representing [node, demand]
     * @param supplies  a list of int arrays, each representing [node, supply]
     * @return          the maximum flow from source to sink if all demand constraints are met; otherwise, -1
     */
    public int maxFlow(int N, List<int[]> links, int source, int sink, List<int[]> demands, List<int[]> supplies) {
        // Initialize demand and supply arrays
        int[] demandArr = new int[N];
        int[] supplyArr = new int[N];
        for (int i = 0; i < N; i++) {
            demandArr[i] = 0;
            supplyArr[i] = Integer.MAX_VALUE; // default large value if not specified
        }
        for (int[] arr : supplies) {
            int node = arr[0];
            int supply = arr[1];
            supplyArr[node] = supply;
        }
        for (int[] arr : demands) {
            int node = arr[0];
            int demand = arr[1];
            demandArr[node] = demand;
        }
        // Check feasibility: for any node, supply must be at least its demand.
        for (int i = 0; i < N; i++) {
            if(supplyArr[i] < demandArr[i]) {
                return -1;
            }
        }

        // Total vertices after vertex splitting: each node becomes two nodes.
        // i_in: i, i_out: i + N, total = 2*N.
        V = 2 * N;
        graph = new ArrayList[V];
        for (int i = 0; i < V; i++) {
            graph[i] = new ArrayList<>();
        }

        // Add vertex capacity edges: from i_in to i_out with capacity = supply[i].
        // In our formulation, the flow passing through node i is the flow on edge (i -> i+N).
        for (int i = 0; i < N; i++) {
            addEdge(i, i + N, supplyArr[i]);
        }

        // Add edges for the original links: from u_out to v_in with capacity = link capacity.
        for (int[] link : links) {
            int u = link[0];
            int v = link[1];
            int cap = link[2];
            // Check nodes range
            if(u < 0 || u >= N || v < 0 || v >= N) continue;
            addEdge(u + N, v, cap);
        }

        // Set source as source_in (i.e., source) and sink as sink_out (i.e., sink + N)
        int s = source;
        int t = sink + N;

        int flow = maxFlowDinic(s, t);

        // After computing the max flow, verify that for each node (except the source)
        // the flow passing through (i -> i+N) is at least the demand.
        // The flow passed through node i is (original capacity on edge (i -> i+N) - residual capacity).
        for (int i = 0; i < N; i++) {
            // Skip source: its demand does not need to be enforced.
            if (i == source) continue;
            // Find the edge from i (in) to i+N (out)
            int passed = 0;
            for (Edge e : graph[i]) {
                if (e.to == i + N) {
                    passed = e.initCap - e.cap;
                    break;
                }
            }
            if (passed < demandArr[i]) {
                return -1;
            }
        }
        return flow;
    }

    // For local testing purposes (can be removed in production)
    public static void main(String[] args) {
        // Sample test: basic network with 2 nodes, direct link.
        int N = 2;
        List<int[]> links = new ArrayList<>();
        links.add(new int[]{0, 1, 10});
        int source = 0;
        int sink = 1;
        List<int[]> demands = new ArrayList<>();
        demands.add(new int[]{0, 0});
        demands.add(new int[]{1, 0});
        List<int[]> supplies = new ArrayList<>();
        supplies.add(new int[]{0, 10});
        supplies.add(new int[]{1, 10});

        NetworkFlowOptimization solver = new NetworkFlowOptimization();
        int maxFlow = solver.maxFlow(N, links, source, sink, demands, supplies);
        System.out.println("Max Flow: " + maxFlow);
    }
}