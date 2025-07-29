import java.util.ArrayList;
import java.util.List;
import java.util.PriorityQueue;
import java.util.Random;

public class TrafficSync {

    // Edge class to represent a road between intersections.
    private static class Edge {
        int to;
        int travelTime;
        public Edge(int to, int travelTime) {
            this.to = to;
            this.travelTime = travelTime;
        }
    }

    // Graph representation for the city.
    private static List<Edge>[] buildGraph(int N, int[][] edges) {
        List<Edge>[] graph = new ArrayList[N];
        for (int i = 0; i < N; i++) {
            graph[i] = new ArrayList<>();
        }
        for (int[] edge : edges) {
            int u = edge[0];
            int v = edge[1];
            int t = edge[2];
            graph[u].add(new Edge(v, t));
        }
        return graph;
    }

    // Waiting time function for a given intersection based on arrival time.
    private static double waitingTime(double arrivalTime, int offset, int red, int yellow, int green) {
        int cycle = red + yellow + green;
        // Compute relative time in the cycle
        int relative = (int)((((long)Math.round(arrivalTime) - offset) % cycle + cycle) % cycle);
        if (relative < red) {
            return red - relative;
        } else if (relative < red + yellow) {
            return red + yellow - relative;
        } else {
            return 0;
        }
    }

    // Dijkstra's algorithm modified to account for waiting times at intersections.
    // start: starting intersection, offsets: current offsets solution,
    // cycleDuration and colorTimings arrays provided for waiting time calculation.
    private static double[] dijkstra(int start, int N, List<Edge>[] graph, int[] offsets, int[] cycleDuration, int[][] colorTimings) {
        double[] dist = new double[N];
        for (int i = 0; i < N; i++) {
            dist[i] = Double.MAX_VALUE;
        }
        // Starting node: no waiting time to depart.
        dist[start] = 0.0;
        PriorityQueue<Node> pq = new PriorityQueue<>();
        pq.offer(new Node(start, 0.0));

        while (!pq.isEmpty()) {
            Node curr = pq.poll();
            if (curr.time > dist[curr.id]) continue;
            // Relaxation to neighbors.
            for (Edge edge : graph[curr.id]) {
                int next = edge.to;
                double arrivalTime = curr.time + edge.travelTime;
                // When arriving at the destination intersection, calculate waiting time
                int red = colorTimings[next][0];
                int yellow = colorTimings[next][1];
                int green = colorTimings[next][2];
                double wait = waitingTime(arrivalTime, offsets[next], red, yellow, green);
                double newTime = arrivalTime + wait;
                if (newTime < dist[next]) {
                    dist[next] = newTime;
                    pq.offer(new Node(next, newTime));
                }
            }
        }
        return dist;
    }

    // Node for Dijkstra's priority queue.
    private static class Node implements Comparable<Node> {
        int id;
        double time;
        public Node(int id, double time) {
            this.id = id;
            this.time = time;
        }
        public int compareTo(Node other) {
            return Double.compare(this.time, other.time);
        }
    }

    // Evaluate solution by computing average travel time between all pairs (s != t)
    private static double evaluateSolution(int N, List<Edge>[] graph, int[] offsets, int[] cycleDuration, int[][] colorTimings) {
        double totalTime = 0.0;
        int count = 0;
        for (int s = 0; s < N; s++) {
            double[] dist = dijkstra(s, N, graph, offsets, cycleDuration, colorTimings);
            for (int t = 0; t < N; t++) {
                if (s != t && dist[t] < Double.MAX_VALUE) {
                    totalTime += dist[t];
                    count++;
                }
            }
        }
        if (count == 0) return Double.MAX_VALUE;
        return totalTime / count;
    }

    // Simulated annealing to optimize offsets for minimizing average travel time.
    public static int[] optimizeOffsets(int N, int[][] edges, int[] cycleDuration, int[][] colorTimings) {
        List<Edge>[] graph = buildGraph(N, edges);
        Random rand = new Random();

        // Initial solution: all offsets set to 0.
        int[] bestOffsets = new int[N];
        int[] currentOffsets = new int[N];
        for (int i = 0; i < N; i++) {
            bestOffsets[i] = 0;
            currentOffsets[i] = 0;
        }
        double bestScore = evaluateSolution(N, graph, bestOffsets, cycleDuration, colorTimings);
        double currentScore = bestScore;

        // Simulated annealing parameters.
        double temperature = 1000.0;
        double coolingRate = 0.995; // Cooling factor per iteration.
        int iterations = 10000;

        for (int iter = 0; iter < iterations; iter++) {
            // Pick a random intersection to change its offset.
            int idx = rand.nextInt(N);
            int oldOffset = currentOffsets[idx];
            // New offset is random within valid range
            int newOffset = rand.nextInt(cycleDuration[idx]);
            currentOffsets[idx] = newOffset;

            double newScore = evaluateSolution(N, graph, currentOffsets, cycleDuration, colorTimings);

            double delta = newScore - currentScore;
            if (delta < 0) {
                // Accept improvement.
                currentScore = newScore;
                if (newScore < bestScore) {
                    bestScore = newScore;
                    System.arraycopy(currentOffsets, 0, bestOffsets, 0, N);
                }
            } else {
                // Accept worse solution with probability e^(-delta/temperature)
                if (rand.nextDouble() < Math.exp(-delta / temperature)) {
                    currentScore = newScore;
                } else {
                    // Revert change.
                    currentOffsets[idx] = oldOffset;
                }
            }
            temperature *= coolingRate;
            if (temperature < 1e-3) {
                temperature = 1e-3;
            }
        }
        return bestOffsets;
    }
}