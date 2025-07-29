#ifndef NETWORK_ROUTING_H
#define NETWORK_ROUTING_H

#include <vector>
#include <unordered_map>
#include <set>
#include <queue>
#include <limits>

class NetworkRouting {
public:
    NetworkRouting(int N, const std::vector<int>& capacities);
    void addEdge(int u, int v, int w, int t);
    void removeEdge(int u, int v, int t);
    std::vector<int> route(int src, int dest, int t);

private:
    struct Edge {
        int to;
        int weight;
        int start_time;
        int end_time;
        Edge(int t, int w, int st, int et) : to(t), weight(w), start_time(st), end_time(et) {}
    };

    struct Node {
        int capacity;
        int used;
        std::vector<Edge> edges;
        Node(int c) : capacity(c), used(0) {}
    };

    struct PathNode {
        int id;
        int dist;
        std::vector<int> path;
        PathNode(int i, int d, const std::vector<int>& p) : id(i), dist(d), path(p) {}
        bool operator>(const PathNode& other) const {
            return dist > other.dist;
        }
    };

    std::vector<Node> nodes;
    std::unordered_map<int, std::unordered_map<int, std::set<std::pair<int, int>>>> edge_timestamps;

    bool isEdgeActive(int u, int v, int t) const;
    void updateNodeUsage(const std::vector<int>& path, bool increment);
};

#endif // NETWORK_ROUTING_H