#include "skyline_dynamic.h"
#include <iostream>
#include <string>

int main() {
    skyline_dynamic::Skyline skyline;
    int n;
    std::string command;
    
    // Read the number of operations
    std::cin >> n;
    std::cin.ignore(); // Clear the newline
    
    // Process each operation
    for (int i = 0; i < n; ++i) {
        std::getline(std::cin, command);
        std::string result = skyline.process_command(command);
        if (!result.empty()) {
            std::cout << result << std::endl;
        }
    }
    
    return 0;
}