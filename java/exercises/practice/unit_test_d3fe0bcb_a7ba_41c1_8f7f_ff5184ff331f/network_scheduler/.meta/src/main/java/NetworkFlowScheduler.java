package network_scheduler;

import java.util.*;
import java.lang.reflect.Field;

public class NetworkFlowScheduler {

    public List<Integer> scheduleFlows(int N, int M, int[][] adjMatrix, List<?> flows) {
        int totalNodes = N + M;
        double[][] usage = new double[totalNodes][totalNodes];
        int flowCount = flows.size();
        List<FlowWrapper> flowList = new ArrayList<>();

        // Wrap each flow with its original index and extracted fields using reflection.
        for (int i = 0; i < flowCount; i++) {
            Object flow = flows.get(i);
            try {
                Field fieldSource = flow.getClass().getDeclaredField("source");
                fieldSource.setAccessible(true);
                int source = fieldSource.getInt(flow);

                Field fieldDestination = flow.getClass().getDeclaredField("destination");
                fieldDestination.setAccessible(true);
                int destination = fieldDestination.getInt(flow);

                Field fieldDataSize = flow.getClass().getDeclaredField("dataSize");
                fieldDataSize.setAccessible(true);
                int dataSize = fieldDataSize.getInt(flow);

                Field fieldDeadline = flow.getClass().getDeclaredField("deadline");
                fieldDeadline.setAccessible(true);
                int deadline = fieldDeadline.getInt(flow);

                flowList.add(new FlowWrapper(i, source, destination, dataSize, deadline));
            } catch (NoSuchFieldException | IllegalAccessException e) {
                // Skip flows that do not have the required structure.
                continue;
            }
        }

        // Sort flows by deadline ascending.
        Collections.sort(flowList, Comparator.comparingInt(f -> f.deadline));
        List<Integer> scheduledFlowIndices = new ArrayList<>();

        // Process each flow in order.
        for (FlowWrapper flow : flowList) {
            double[] best = new double[totalNodes];
            int[] parent = new int[totalNodes];
            boolean[] visited = new boolean[totalNodes];
            Arrays.fill(best, Double.POSITIVE_INFINITY);
            Arrays.fill(parent, -1);
            best[flow.source] = 0.0;

            PriorityQueue<NodeEntry> pq = new PriorityQueue<>(Comparator.comparingDouble(ne -> ne.cost));
            pq.offer(new NodeEntry(flow.source, 0.0));

            while (!pq.isEmpty()) {
                NodeEntry current = pq.poll();
                int u = current.node;
                if (visited[u]) continue;
                visited[u] = true;
                if (u == flow.destination) break;
                for (int v = 0; v < totalNodes; v++) {
                    if (adjMatrix[u][v] > 0) {
                        double edgeCost = (usage[u][v] + 1) / (double) adjMatrix[u][v];
                        double candidate = Math.max(best[u], edgeCost);
                        if (candidate < best[v]) {
                            best[v] = candidate;
                            parent[v] = u;
                            pq.offer(new NodeEntry(v, best[v]));
                        }
                    }
                }
            }

            if (best[flow.destination] == Double.POSITIVE_INFINITY) {
                continue; // No valid path found.
            }

            double completionTime = flow.dataSize * best[flow.destination];
            if (completionTime <= flow.deadline) {
                List<int[]> pathEdges = new ArrayList<>();
                int cur = flow.destination;
                while (parent[cur] != -1) {
                    int prev = parent[cur];
                    pathEdges.add(new int[]{prev, cur});
                    cur = prev;
                }
                Collections.reverse(pathEdges);
                for (int[] edge : pathEdges) {
                    int u = edge[0], v = edge[1];
                    usage[u][v] += 1.0;
                }
                scheduledFlowIndices.add(flow.index);
            }
        }
        return scheduledFlowIndices;
    }

    // Helper class to encapsulate flow data.
    private static class FlowWrapper {
        int index;
        int source;
        int destination;
        int dataSize;
        int deadline;

        FlowWrapper(int index, int source, int destination, int dataSize, int deadline) {
            this.index = index;
            this.source = source;
            this.destination = destination;
            this.dataSize = dataSize;
            this.deadline = deadline;
        }
    }

    // Helper class for the minimax Dijkstra algorithm.
    private static class NodeEntry {
        int node;
        double cost;

        NodeEntry(int node, double cost) {
            this.node = node;
            this.cost = cost;
        }
    }
}