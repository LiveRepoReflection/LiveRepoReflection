#include "network_optimize.h"
#include <sstream>
#include <string>
#include <vector>
#include <queue>
#include <limits>
#include <unordered_map>
#include <cstdlib>

namespace network_optimize {

const double INF = std::numeric_limits<double>::max();
// Constant overhead per routing (for splitting into two subpackets)
const int OVERHEAD = 1000; 
// Threshold for unsatisfactory packets in low-bandwidth links (if packet > THRESHOLD, require high bandwidth)
const int SIZE_THRESHOLD = 1600;

struct Edge {
    int u;
    int v;
    int bandwidth; // bytes per second
    int latency;   // seconds
};

class Graph {
public:
    // graph represented using adjacency list: node -> vector of Edge
    std::unordered_map<int, std::vector<Edge>> adj;
    
    void addLink(int u, int v, int bandwidth, int latency) {
        Edge e1{u, v, bandwidth, latency};
        Edge e2{v, u, bandwidth, latency};
        adj[u].push_back(e1);
        adj[v].push_back(e2);
    }
    
    void removeLink(int u, int v) {
        removeOneDirection(u, v);
        removeOneDirection(v, u);
    }
    
    void updateBandwidth(int u, int v, int bandwidth) {
        updateOneDirection(u, v, bandwidth);
        updateOneDirection(v, u, bandwidth);
    }
    
    void linkFailure(int u, int v) {
        // On link failure, remove the link
        removeLink(u, v);
    }
    
    // Finds the shortest path (min sum latency) from source to destination.
    // Also computes the bottleneck bandwidth (minimum bandwidth along that path).
    // Returns true if a path exists. The path is stored in 'path' (from source to dest)
    bool dijkstra(int source, int destination, std::vector<int> &path, int &bottleneck) {
        // Maps node to latency and previous node
        std::unordered_map<int, double> dist;
        std::unordered_map<int, int> prev;
        // For bottleneck: store the minimum bandwidth so far along the path.
        std::unordered_map<int, int> minBw;
        
        typedef std::pair<double, int> NodePair; // (distance, node)
        std::priority_queue<NodePair, std::vector<NodePair>, std::greater<NodePair>> pq;
        
        dist[source] = 0;
        minBw[source] = std::numeric_limits<int>::max();
        pq.push({0, source});
        
        while(!pq.empty()){
            auto [d, cur] = pq.top();
            pq.pop();
            if(d > dist[cur]) continue;
            if(cur == destination) break;
            
            if(adj.find(cur) == adj.end()) continue;
            
            for(auto &edge : adj[cur]){
                int nxt = edge.v;
                double nd = d + edge.latency;
                if(dist.find(nxt) == dist.end() || nd < dist[nxt]){
                    dist[nxt] = nd;
                    prev[nxt] = cur;
                    // update bottleneck: the new bottleneck is minimum of current minBw and edge.bandwidth
                    int curMin = (minBw.find(cur) != minBw.end() ? minBw[cur] : edge.bandwidth);
                    int newMin = std::min(curMin, edge.bandwidth);
                    minBw[nxt] = newMin;
                    pq.push({nd, nxt});
                }
            }
        }
        
        if(dist.find(destination) == dist.end()){
            return false;
        }
        
        // Build path by backtracking from destination to source.
        std::vector<int> rev;
        int cur = destination;
        while(cur != source){
            rev.push_back(cur);
            cur = prev[cur];
        }
        rev.push_back(source);
        // Reverse the path to get source->destination
        path.assign(rev.rbegin(), rev.rend());
        bottleneck = minBw[destination];
        return true;
    }
    
private:
    void removeOneDirection(int u, int v) {
        if(adj.find(u) == adj.end()) return;
        auto &vec = adj[u];
        for(auto it = vec.begin(); it != vec.end(); ) {
            if(it->v == v) {
                it = vec.erase(it);
            } else {
                ++it;
            }
        }
    }
    
    void updateOneDirection(int u, int v, int bandwidth) {
        if(adj.find(u) == adj.end()) return;
        for(auto &edge : adj[u]) {
            if(edge.v == v) {
                edge.bandwidth = bandwidth;
            }
        }
    }
};

void processCommands(std::istream &in, std::ostream &out) {
    Graph graph;
    std::string line;
    while(std::getline(in, line)){
        if(line.empty()) continue;
        std::istringstream iss(line);
        std::string cmd;
        iss >> cmd;
        if(cmd == "add_link"){
            int u, v, bandwidth, latency;
            iss >> u >> v >> bandwidth >> latency;
            graph.addLink(u, v, bandwidth, latency);
        } else if(cmd == "remove_link"){
            int u, v;
            iss >> u >> v;
            graph.removeLink(u, v);
        } else if(cmd == "update_bandwidth"){
            int u, v, bandwidth;
            iss >> u >> v >> bandwidth;
            graph.updateBandwidth(u, v, bandwidth);
        } else if(cmd == "link_failure"){
            int u, v;
            iss >> u >> v;
            graph.linkFailure(u, v);
            // For this simulation, we do not output anything on link failure.
        } else if(cmd == "route"){
            int source, destination;
            int packet_size;
            int deadline;
            iss >> source >> destination >> packet_size >> deadline;
            // Find shortest path in terms of latency.
            std::vector<int> path;
            int bottleneck = 0;
            if(!graph.dijkstra(source, destination, path, bottleneck)){
                out << "ERROR: Deadline cannot be met." << "\n";
                continue;
            }
            // Sum latencies along the path.
            int total_latency = 0;
            for(size_t i = 0; i < path.size()-1; i++){
                int u = path[i], v = path[i+1];
                // find edge latency from u to v
                bool found = false;
                if(graph.adj.find(u) != graph.adj.end()){
                    for(auto &edge : graph.adj[u]){
                        if(edge.v == v){
                            total_latency += edge.latency;
                            found = true;
                            break;
                        }
                    }
                }
                if(!found){
                    // Should not happen.
                    total_latency += 0;
                }
            }
            // We assume always splitting into 2 subpackets.
            int subpackets = 2;
            // According to our simulation, if packet_size exceeds threshold and bottleneck is low, route fails.
            if(packet_size > SIZE_THRESHOLD && bottleneck < 1000){
                out << "ERROR: Deadline cannot be met." << "\n";
                continue;
            }
            // Calculate finish time: total latency + transmission time.
            // Transmission time is computed as: (packet_size + overhead) divided by bottleneck bandwidth.
            double finish_time = total_latency + double(packet_size + OVERHEAD) / bottleneck;
            if(finish_time <= deadline){
                out << subpackets << "\n";
                // Print the route for each subpacket.
                std::ostringstream routeStream;
                for(size_t i = 0; i < path.size(); i++){
                    routeStream << path[i];
                    if(i < path.size()-1) routeStream << " ";
                }
                out << routeStream.str() << "\n";
                out << routeStream.str() << "\n";
            } else {
                out << "ERROR: Deadline cannot be met." << "\n";
            }
        }
    }
}

} // namespace network_optimize