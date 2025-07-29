#include "distributed_tx.h"
#include <iostream>
#include <string>

int main() {
    int numShards;
    std::cout << "Enter number of shards: ";
    std::cin >> numShards;
    std::cin.ignore(); // Consume newline
    
    TransactionManager txManager(numShards);
    
    std::string line;
    while (std::cout << "> " && std::getline(std::cin, line) && !line.empty()) {
        if (line == "exit" || line == "quit") {
            break;
        }
        
        std::string result = txManager.processCommand(line);
        if (!result.empty()) {
            std::cout << result << std::endl;
        }
    }
    
    return 0;
}