import java.util.ArrayList;
import java.util.LinkedList;
import java.util.List;
import java.util.Queue;

public class NetworkFlow {

    // Edge class representing an edge in the flow network.
    static class Edge {
        int from, to;
        int capacity;
        int flow;
        Edge rev;

        Edge(int from, int to, int capacity) {
            this.from = from;
            this.to = to;
            this.capacity = capacity;
            this.flow = 0;
        }
    }

    // Dinic algorithm implementation.
    static class Dinic {
        int n;
        ArrayList<Edge>[] graph;
        int[] level;
        int[] ptr;
        int source;
        int sink;
        final int INF = Integer.MAX_VALUE;

        @SuppressWarnings("unchecked")
        Dinic(int n, int source, int sink) {
            this.n = n;
            this.source = source;
            this.sink = sink;
            graph = new ArrayList[n];
            for (int i = 0; i < n; i++) {
                graph[i] = new ArrayList<>();
            }
            level = new int[n];
            ptr = new int[n];
        }

        void addEdge(int from, int to, int capacity) {
            Edge forward = new Edge(from, to, capacity);
            Edge backward = new Edge(to, from, 0);
            forward.rev = backward;
            backward.rev = forward;
            graph[from].add(forward);
            graph[to].add(backward);
        }

        boolean bfs() {
            for (int i = 0; i < n; i++) {
                level[i] = -1;
            }
            Queue<Integer> queue = new LinkedList<>();
            level[source] = 0;
            queue.add(source);
            while (!queue.isEmpty()) {
                int node = queue.poll();
                for (Edge edge : graph[node]) {
                    if (edge.capacity - edge.flow > 0 && level[edge.to] == -1) {
                        level[edge.to] = level[node] + 1;
                        queue.add(edge.to);
                    }
                }
            }
            return level[sink] != -1;
        }

        int dfs(int node, int pushed) {
            if (pushed == 0) return 0;
            if (node == sink) return pushed;
            for (; ptr[node] < graph[node].size(); ptr[node]++) {
                Edge edge = graph[node].get(ptr[node]);
                if (level[node] + 1 != level[edge.to] || edge.capacity - edge.flow == 0) continue;
                int tr = dfs(edge.to, Math.min(pushed, edge.capacity - edge.flow));
                if (tr > 0) {
                    edge.flow += tr;
                    edge.rev.flow -= tr;
                    return tr;
                }
            }
            return 0;
        }

        int maxFlow() {
            int flow = 0;
            while (bfs()) {
                for (int i = 0; i < n; i++) {
                    ptr[i] = 0;
                }
                while (true) {
                    int pushed = dfs(source, INF);
                    if (pushed == 0) break;
                    // Accumulate the flow from the source.
                    flow += pushed;
                }
            }
            return flow;
        }
    }

    /**
     * Computes the maximum flow of data from a single source to multiple destination nodes.
     *
     * @param n             the number of data center nodes.
     * @param edges         a list of edges (u, v, capacity).
     * @param source        the source node index.
     * @param destinations  a list of destination node indices.
     * @return              the maximum total flow from the source to all designated destinations.
     */
    public static int maxFlow(int n, List<int[]> edges, int source, List<Integer> destinations) {
        // If the only destination is the source itself, return 0.
        if (destinations.size() == 1 && destinations.get(0) == source) {
            return 0;
        }
        
        // Create a super sink node.
        int superSink = n;
        int totalNodes = n + 1;

        // Initialize Dinic with totalNodes.
        Dinic dinic = new Dinic(totalNodes, source, superSink);

        // Add original edges.
        for (int[] edge : edges) {
            // Edge format: {u, v, capacity}
            int u = edge[0];
            int v = edge[1];
            int capacity = edge[2];
            // Add edge even if multiple edges exist between same nodes.
            dinic.addEdge(u, v, capacity);
        }

        // Use a boolean array to ensure each destination gets only one edge to the super sink.
        boolean[] connectedToSink = new boolean[n];
        for (Integer dest : destinations) {
            if (dest == source) {
                // Skip creating an edge if destination equals source.
                continue;
            }
            if (!connectedToSink[dest]) {
                // Connect destination to superSink with infinite capacity.
                dinic.addEdge(dest, superSink, dinic.INF);
                connectedToSink[dest] = true;
            }
        }

        // Calculate maximum flow from source to superSink.
        return dinic.maxFlow();
    }
}