package network_opt;

import java.util.*;

public class NetworkOptSolver {

    private static final int INF = 1000000000;

    public static double minAveragePath(int n, int[][] edges, int k) {
        List<Edge> allEdges = new ArrayList<>();
        for (int[] arr : edges) {
            allEdges.add(new Edge(arr[0], arr[1], arr[2]));
        }

        // If k equals or exceeds all available edges, use full graph
        if (k >= allEdges.size()) {
            double fullGraphAvg = computeAverage(n, allEdges);
            return fullGraphAvg;
        }

        // Build a Minimum Spanning Tree (MST) to ensure connectivity using the smallest (n-1) edges.
        Collections.sort(allEdges, Comparator.comparingInt(e -> e.cost));
        List<Edge> selected = new ArrayList<>();
        UnionFind uf = new UnionFind(n);
        for (Edge edge : allEdges) {
            if (uf.union(edge.u, edge.v)) {
                selected.add(edge);
            }
            if (selected.size() == n - 1) {
                break;
            }
        }
        if (selected.size() != n - 1) {
            // Graph is disconnected even in full graph
            return Double.MAX_VALUE;
        }
        double currentAvg = computeAverage(n, selected);
        
        // If MST already uses k edges, return its average
        if (selected.size() == k) {
            return currentAvg;
        }
        
        // Use a set for quick lookup of selected edges
        Set<Edge> selectedSet = new HashSet<>(selected);

        // Greedy augmentation: try to add one extra edge at a time that maximally improves the average distance
        boolean improvementFound = true;
        while (selected.size() < k && improvementFound) {
            improvementFound = false;
            Edge bestEdgeToAdd = null;
            double bestAvg = currentAvg;
            for (Edge candidate : allEdges) {
                if (selectedSet.contains(candidate)) {
                    continue;
                }
                List<Edge> temp = new ArrayList<>(selected);
                temp.add(candidate);
                double candidateAvg = computeAverage(n, temp);
                if (candidateAvg < bestAvg) {
                    bestAvg = candidateAvg;
                    bestEdgeToAdd = candidate;
                }
            }
            if (bestEdgeToAdd != null) {
                selected.add(bestEdgeToAdd);
                selectedSet.add(bestEdgeToAdd);
                currentAvg = bestAvg;
                improvementFound = true;
            }
        }
        return currentAvg;
    }

    private static double computeAverage(int n, List<Edge> edges) {
        int[][] dist = new int[n][n];
        for (int i = 0; i < n; i++) {
            Arrays.fill(dist[i], INF);
            dist[i][i] = 0;
        }
        for (Edge edge : edges) {
            dist[edge.u][edge.v] = Math.min(dist[edge.u][edge.v], edge.cost);
            dist[edge.v][edge.u] = Math.min(dist[edge.v][edge.u], edge.cost);
        }

        // Floyd-Warshall algorithm to compute all pairs shortest paths
        for (int mid = 0; mid < n; mid++) {
            for (int i = 0; i < n; i++) {
                for (int j = 0; j < n; j++) {
                    if (dist[i][mid] + dist[mid][j] < dist[i][j]) {
                        dist[i][j] = dist[i][mid] + dist[mid][j];
                    }
                }
            }
        }

        double sum = 0;
        int count = 0;
        for (int i = 0; i < n; i++) {
            for (int j = i+1; j < n; j++) {
                if (dist[i][j] >= INF) {
                    return Double.MAX_VALUE;
                }
                sum += dist[i][j];
                count++;
            }
        }
        return count == 0 ? 0.0 : sum / count;
    }

    static class Edge {
        int u;
        int v;
        int cost;

        Edge(int a, int b, int cost) {
            if (a < b) {
                this.u = a;
                this.v = b;
            } else {
                this.u = b;
                this.v = a;
            }
            this.cost = cost;
        }

        @Override
        public boolean equals(Object obj) {
            if (this == obj) return true;
            if (!(obj instanceof Edge)) return false;
            Edge other = (Edge) obj;
            return this.u == other.u && this.v == other.v && this.cost == other.cost;
        }

        @Override
        public int hashCode() {
            return Objects.hash(u, v, cost);
        }
    }

    static class UnionFind {
        int[] parent;
        int[] rank;

        UnionFind(int n) {
            parent = new int[n];
            rank = new int[n];
            for (int i = 0; i < n; i++) {
                parent[i] = i;
                rank[i] = 0;
            }
        }

        int find(int x) {
            if (parent[x] != x) {
                parent[x] = find(parent[x]);
            }
            return parent[x];
        }

        boolean union(int x, int y) {
            int rootX = find(x);
            int rootY = find(y);
            if (rootX == rootY) {
                return false;
            }
            if (rank[rootX] < rank[rootY]) {
                parent[rootX] = rootY;
            } else if (rank[rootX] > rank[rootY]) {
                parent[rootY] = rootX;
            } else {
                parent[rootY] = rootX;
                rank[rootX]++;
            }
            return true;
        }
    }
}