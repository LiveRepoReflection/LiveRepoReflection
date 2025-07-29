#if !defined(SKYLINE_DYNAMIC_H)
#define SKYLINE_DYNAMIC_H

#include <vector>
#include <utility>
#include <string>
#include <sstream>
#include <map>
#include <set>

namespace skyline_dynamic {

class Skyline {
public:
    // Add a building to the skyline
    void add(int left, int right, int height);
    
    // Get the current skyline as a list of (x, y) points
    std::vector<std::pair<int, int>> query() const;
    
    // Process a command string ("add L R H" or "query")
    std::string process_command(const std::string& command);

private:
    // Use a map to store height changes at each x-coordinate
    std::map<int, std::multiset<std::pair<int, bool>>> changes_;
};

}  // namespace skyline_dynamic

#endif // SKYLINE_DYNAMIC_H