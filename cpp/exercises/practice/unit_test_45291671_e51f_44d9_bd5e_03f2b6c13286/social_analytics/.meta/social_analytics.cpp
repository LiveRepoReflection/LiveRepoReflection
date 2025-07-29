#include "social_analytics.h"
#include <sstream>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <queue>
#include <iostream>

namespace social_analytics {

class SocialNetwork {
public:
    // Graph represented as a mapping from user ID to set of friend user IDs.
    std::unordered_map<int, std::unordered_set<int>> graph;

    // Add a user if not exists.
    void addUser(int userId) {
        if (graph.find(userId) == graph.end()) {
            graph[userId] = std::unordered_set<int>();
        }
    }

    // Remove user and remove their connections from friends' lists.
    void removeUser(int userId) {
        auto it = graph.find(userId);
        if(it == graph.end()) return;
        // Remove this user from friends' connections.
        for (int friendId : it->second) {
            graph[friendId].erase(userId);
        }
        // Remove user from graph.
        graph.erase(it);
    }

    // Add undirected connection between two users.
    void addConnection(int userId1, int userId2) {
        if (graph.find(userId1) == graph.end() || graph.find(userId2) == graph.end()) {
            return;
        }
        graph[userId1].insert(userId2);
        graph[userId2].insert(userId1);
    }

    // Remove undirected connection between two users.
    void removeConnection(int userId1, int userId2) {
        if (graph.find(userId1) != graph.end()) {
            graph[userId1].erase(userId2);
        }
        if (graph.find(userId2) != graph.end()) {
            graph[userId2].erase(userId1);
        }
    }

    // Check if two users are reachable using BFS.
    bool areReachable(int userId1, int userId2) {
        if (graph.find(userId1) == graph.end() || graph.find(userId2) == graph.end()) {
            return false;
        }
        if (userId1 == userId2) return true;
        std::unordered_set<int> visited;
        std::queue<int> q;
        q.push(userId1);
        visited.insert(userId1);
        while (!q.empty()) {
            int current = q.front();
            q.pop();
            if (current == userId2) return true;
            for (int neighbor : graph[current]) {
                if (visited.find(neighbor) == visited.end()) {
                    visited.insert(neighbor);
                    q.push(neighbor);
                }
            }
        }
        return false;
    }

    // Calculate influence score: number of users reachable within k hops (excluding self)
    int influenceScore(int userId, int degree) {
        if (graph.find(userId) == graph.end() || degree < 1) {
            return 0;
        }
        std::unordered_set<int> visited;
        std::queue<std::pair<int, int>> q; // pair: (current node, current depth)
        q.push({userId, 0});
        visited.insert(userId);
        int count = 0;
        while (!q.empty()) {
            auto front = q.front();
            q.pop();
            int currentNode = front.first;
            int currentDepth = front.second;
            // Do not process further if reached max degree.
            if (currentDepth >= degree) continue;
            for (int neighbor : graph[currentNode]) {
                if (visited.find(neighbor) == visited.end()) {
                    visited.insert(neighbor);
                    q.push({neighbor, currentDepth + 1});
                    count++;
                }
            }
        }
        return count;
    }
};

void processCommands(std::istream& in, std::ostream& out) {
    SocialNetwork network;
    std::string line;
    while (std::getline(in, line)) {
        if (line.empty()) {
            continue;
        }
        std::istringstream ss(line);
        std::string command;
        ss >> command;
        if (command == "ADD_USER") {
            int userId;
            ss >> userId;
            network.addUser(userId);
        } else if (command == "REMOVE_USER") {
            int userId;
            ss >> userId;
            network.removeUser(userId);
        } else if (command == "ADD_CONNECTION") {
            int userId1, userId2;
            ss >> userId1 >> userId2;
            network.addConnection(userId1, userId2);
        } else if (command == "REMOVE_CONNECTION") {
            int userId1, userId2;
            ss >> userId1 >> userId2;
            network.removeConnection(userId1, userId2);
        } else if (command == "ARE_REACHABLE") {
            int userId1, userId2;
            ss >> userId1 >> userId2;
            bool reachable = network.areReachable(userId1, userId2);
            out << (reachable ? "TRUE" : "FALSE") << "\n";
        } else if (command == "INFLUENCE_SCORE") {
            int userId, degree;
            ss >> userId >> degree;
            int score = network.influenceScore(userId, degree);
            out << score << "\n";
        }
    }
}

} // namespace social_analytics