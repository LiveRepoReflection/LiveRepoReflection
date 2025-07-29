import java.util.*;

public class NetworkFlow {

    private int n; // original number of nodes
    private int totalNodes; // total nodes in the split graph (2 * n)
    private List<Edge>[] graph;
    private int source; // index for the source in the new graph (source_out)
    private int sink;   // index for the sink in the new graph (sink_in)

    public NetworkFlow(int n, int[][] edges, int[] nodeCapacities, int originalSource, int originalSink) {
        this.n = n;
        this.totalNodes = 2 * n;
        // In the split graph:
        // For every original node i, i_in is i and i_out is i + n.
        // We designate new source as originalSource_out and new sink as originalSink_in.
        this.source = originalSource + n;
        this.sink = originalSink;
        buildGraph(n, edges, nodeCapacities, originalSource, originalSink);
    }

    private void buildGraph(int n, int[][] edges, int[] nodeCapacities, int originalSource, int originalSink) {
        graph = new ArrayList[totalNodes];
        for (int i = 0; i < totalNodes; i++) {
            graph[i] = new ArrayList<>();
        }
        // Split nodes: add an edge from i_in to i_out with capacity = nodeCapacities[i].
        // For source and sink, set the capacity to Integer.MAX_VALUE.
        for (int i = 0; i < n; i++) {
            int cap = nodeCapacities[i];
            if (i == originalSource || i == originalSink) {
                cap = Integer.MAX_VALUE;
            }
            addEdge(i, i + n, cap);
        }
        // Add original edges: from u_out to v_in with given capacity.
        for (int[] edge : edges) {
            int u = edge[0];
            int v = edge[1];
            int cap = edge[2];
            addEdge(u + n, v, cap);
        }
    }

    private void addEdge(int u, int v, int cap) {
        Edge forward = new Edge(u, v, cap);
        Edge backward = new Edge(v, u, 0);
        forward.residual = backward;
        backward.residual = forward;
        graph[u].add(forward);
        graph[v].add(backward);
    }

    public int maxFlow() {
        int flow = 0;
        while (true) {
            Edge[] parentEdge = new Edge[totalNodes];
            int newFlow = bfs(parentEdge);
            if (newFlow == 0) {
                break;
            }
            flow += newFlow;
            int cur = sink;
            while (cur != source) {
                Edge edge = parentEdge[cur];
                edge.augment(newFlow);
                cur = edge.from;
            }
        }
        return flow;
    }

    private int bfs(Edge[] parentEdge) {
        int[] flows = new int[totalNodes];
        Arrays.fill(flows, 0);
        Queue<Integer> queue = new LinkedList<>();
        queue.add(source);
        flows[source] = Integer.MAX_VALUE;

        while (!queue.isEmpty()) {
            int current = queue.poll();
            for (Edge edge : graph[current]) {
                if (flows[edge.to] == 0 && edge.remainingCapacity() > 0) {
                    parentEdge[edge.to] = edge;
                    flows[edge.to] = Math.min(flows[current], edge.remainingCapacity());
                    queue.add(edge.to);
                    if (edge.to == sink) {
                        return flows[sink];
                    }
                }
            }
        }
        return 0;
    }

    private static class Edge {
        int from;
        int to;
        int capacity;
        int flow;
        Edge residual;

        public Edge(int from, int to, int capacity) {
            this.from = from;
            this.to = to;
            this.capacity = capacity;
            this.flow = 0;
        }

        public int remainingCapacity() {
            return capacity - flow;
        }

        public void augment(int bottleNeck) {
            flow += bottleNeck;
            residual.flow -= bottleNeck;
        }
    }
}