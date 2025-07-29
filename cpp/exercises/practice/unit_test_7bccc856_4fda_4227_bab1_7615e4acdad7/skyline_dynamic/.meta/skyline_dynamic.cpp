#include "skyline_dynamic.h"
#include <sstream>
#include <map>
#include <algorithm>

namespace skyline_dynamic {

void Skyline::add(int left, int right, int height) {
    // For left point, use true to indicate start of building
    changes_[left].insert({height, true});
    // For right point, use false to indicate end of building
    changes_[right].insert({height, false});
}

std::vector<std::pair<int, int>> Skyline::query() const {
    std::vector<std::pair<int, int>> result;
    std::multiset<int, std::greater<int>> active_heights;
    int prev_height = 0;
    
    // Process all height changes by x-coordinate
    for (const auto& point : changes_) {
        int x = point.first;
        for (const auto& change : point.second) {
            if (change.second) {
                // Add height to active set for building start
                active_heights.insert(change.first);
            } else {
                // Remove height from active set for building end
                auto it = active_heights.find(change.first);
                if (it != active_heights.end()) {
                    active_heights.erase(it);
                }
            }
        }
        
        // Get current maximum height
        int curr_height = active_heights.empty() ? 0 : *active_heights.begin();
        
        // Add to result if the height has changed
        if (curr_height != prev_height) {
            result.push_back({x, curr_height});
            prev_height = curr_height;
        }
    }
    
    return result;
}

std::string Skyline::process_command(const std::string& command) {
    std::istringstream iss(command);
    std::string cmd;
    iss >> cmd;
    
    if (cmd == "add") {
        int left, right, height;
        iss >> left >> right >> height;
        add(left, right, height);
        return "";
    } else if (cmd == "query") {
        auto skyline = query();
        std::ostringstream oss;
        bool first = true;
        
        for (const auto& point : skyline) {
            if (!first) {
                oss << " ";
            }
            oss << "(" << point.first << ", " << point.second << ")";
            first = false;
        }
        
        return oss.str();
    }
    
    return "Invalid command";
}

}  // namespace skyline_dynamic